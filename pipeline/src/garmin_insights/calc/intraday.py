import sqlite3
from datetime import date, datetime, time, timedelta

from garmin_insights import config
from garmin_insights.publish.contract import DaySpan, Intraday, IntradayPoint, StepBucket, StressShare

STRESS_SAMPLE_MS = 3 * 60 * 1000
STRESS_NO_DATA = -1
STRESS_MOTION = -2
MOTION_MERGE_MS = 2 * STRESS_SAMPLE_MS
STRESS_SHARES = (
    ("rest", "descanso", "stress_rest_s"),
    ("low", "baixo", "stress_low_s"),
    ("medium", "médio", "stress_medium_s"),
    ("high", "alto", "stress_high_s"),
)


def column(daily: sqlite3.Row | None, name: str) -> float | None:
    return None if daily is None else daily[name]


def day_bounds(day: str) -> tuple[int, int]:
    start = datetime.combine(date.fromisoformat(day), time(), config.TIMEZONE)
    return int(start.timestamp() * 1000), int((start + timedelta(days=1)).timestamp() * 1000)


def local_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace(".0", "")).replace(tzinfo=config.TIMEZONE).timestamp() * 1000)


def clipped(kind: str, start_ms: int, end_ms: int, bounds: tuple[int, int], label: str, activity_id: str | None = None) -> DaySpan | None:
    start, end = max(start_ms, bounds[0]), min(end_ms, bounds[1])
    if end <= start:
        return None
    return DaySpan(kind=kind, start_ms=start, end_ms=end, label=label, activity_id=activity_id)


def motion_spans(raw_stress: list[tuple[int, float]], bounds: tuple[int, int]) -> list[DaySpan]:
    merged: list[list[int]] = []
    for timestamp, value in raw_stress:
        if value != STRESS_MOTION:
            continue
        if merged and timestamp - merged[-1][1] <= MOTION_MERGE_MS:
            merged[-1][1] = timestamp + STRESS_SAMPLE_MS
        else:
            merged.append([timestamp, timestamp + STRESS_SAMPLE_MS])
    return [span for start, end in merged if (span := clipped("motion", start, end, bounds, "em movimento"))]


def sleep_spans(connection: sqlite3.Connection, day: str, bounds: tuple[int, int]) -> list[DaySpan]:
    following = str(date.fromisoformat(day) + timedelta(days=1))
    rows = connection.execute(
        "SELECT date, min(start_ms) AS start_ms, max(end_ms) AS end_ms FROM sleep_stages WHERE date IN (?, ?) GROUP BY date",
        (day, following),
    )
    return [span for row in rows if (span := clipped("sleep", row["start_ms"], row["end_ms"], bounds, "sono"))]


def activity_spans(connection: sqlite3.Connection, bounds: tuple[int, int]) -> list[DaySpan]:
    spans = []
    query = "SELECT activity_id, start_local, coalesce(elapsed_s, duration_s) AS seconds, name FROM activities WHERE coalesce(elapsed_s, duration_s) IS NOT NULL"
    for row in connection.execute(query):
        start = local_ms(row["start_local"])
        span = clipped("activity", start, start + int(row["seconds"] * 1000), bounds, row["name"] or "atividade", row["activity_id"])
        if span:
            spans.append(span)
    return spans


def intraday_document(connection: sqlite3.Connection, day: str, series: dict[str, list[tuple[int, float]]], daily: sqlite3.Row | None) -> Intraday:
    bounds = day_bounds(day)
    raw_stress = series.get("stress", [])
    hr = [IntradayPoint(ts_ms=timestamp, value=value) for timestamp, value in series.get("hr", [])]
    stress = [IntradayPoint(ts_ms=timestamp, value=value if value >= 0 else None) for timestamp, value in raw_stress]
    body_battery = [IntradayPoint(ts_ms=timestamp, value=value) for timestamp, value in series.get("body_battery", [])]
    steps = [
        StepBucket(start_ms=row["start_ms"], end_ms=row["end_ms"], steps=row["steps"])
        for row in connection.execute("SELECT * FROM day_steps WHERE date = ? ORDER BY start_ms", (day,))
    ]
    samples = [timestamp for values in series.values() for timestamp, _ in values]
    hr_values = [point.value for point in hr if point.value is not None]
    steps_total = column(daily, "steps")
    spans = sleep_spans(connection, day, bounds) + activity_spans(connection, bounds) + motion_spans(raw_stress, bounds)
    return Intraday(
        date=day,
        start_ms=bounds[0],
        end_ms=bounds[1],
        last_sample_ms=max(samples) if samples else None,
        hr=hr,
        stress=stress,
        body_battery=body_battery,
        steps=steps,
        spans=sorted(spans, key=lambda span: span.start_ms),
        hr_min=min(hr_values) if hr_values else None,
        hr_max=max(hr_values) if hr_values else None,
        hr_resting=column(daily, "resting_hr"),
        stress_avg=column(daily, "stress_avg"),
        stress_shares=[
            StressShare(key=key, label=label, minutes=round(column(daily, name) / 60))
            for key, label, name in STRESS_SHARES
            if column(daily, name) is not None
        ],
        steps_total=None if steps_total is None else int(steps_total),
        body_battery_high=column(daily, "body_battery_high"),
        body_battery_low=column(daily, "body_battery_low"),
        body_battery_charged=column(daily, "body_battery_charged"),
        body_battery_drained=column(daily, "body_battery_drained"),
    )


def intraday_documents(connection: sqlite3.Connection) -> dict[str, Intraday]:
    series: dict[str, dict[str, list[tuple[int, float]]]] = {}
    for row in connection.execute("SELECT date, metric, ts_ms, value FROM day_series ORDER BY date, metric, ts_ms"):
        series.setdefault(row["date"], {}).setdefault(row["metric"], []).append((row["ts_ms"], row["value"]))
    daily = {row["date"]: row for row in connection.execute("SELECT * FROM daily")}
    return {day: intraday_document(connection, day, values, daily.get(day)) for day, values in series.items()}
