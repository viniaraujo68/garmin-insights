import sqlite3
from datetime import datetime

from garmin_insights.calc.stats import mean, robust_z, rounded
from garmin_insights.publish.contract import (
    GlanceCell,
    GlanceDay,
    Night,
    Recovery,
    RecoveryTrend,
    SleepNight,
    SleepSeriesPoint,
    SleepStage,
    TrendPoint,
)

MEAN_WINDOW = 7
MEAN_MIN_VALUES = 3
GLANCE_WINDOW = 28
GLANCE_MIN_REFERENCE = 7
EVENING_START_MINUTES = 18 * 60

TRENDS = (
    ("hrv_last_night", "Overnight HRV", "ms", 0, True, "Variation between heartbeats during sleep. Within the range = recovered; below it for consecutive days = fatigue or illness."),
    ("resting_hr", "Resting HR", "bpm", 0, False, "Drops with fitness. A rise of 5 bpm or more for consecutive days calls for attention."),
    ("sleep_score", "Sleep Score", "", 0, True, "0 to 100: 80 or more is good."),
    ("sleep_h", "Sleep duration", "h", 1, True, "Time asleep, not counting awake periods."),
    ("readiness_score", "Training Readiness", "", 0, True, "Morning reading, 0 to 100. Below 50: easy training."),
    ("body_battery_high", "Body Battery high", "", 0, True, "The energy peak of the day, usually at wake-up."),
    ("stress_avg", "Average stress", "", 0, False, "Estimated from HRV during the day, 0 to 100."),
    ("sleep_respiration", "Sleep respiration", "brpm", 1, None, "Breaths per minute while asleep. An unusual rise can signal illness."),
    ("steps", "Steps", "", 0, True, "Steps in the day."),
)
GLANCE = (
    ("resting_hr", "Resting HR", False, 1.0, 0),
    ("hrv_last_night", "HRV", True, 2.0, 0),
    ("sleep_score", "Sleep", True, 3.0, 0),
    ("readiness_score", "Readiness", True, 5.0, 0),
    ("body_battery_high", "Body Battery", True, 5.0, 0),
    ("stress_avg", "Stress", False, 2.0, 0),
    ("steps", "Steps", True, 500.0, 0),
)


def daily_values(row: sqlite3.Row, key: str) -> float | None:
    if key == "sleep_h":
        return None if row["sleep_s"] is None else round(row["sleep_s"] / 3600, 2)
    return row[key]


def trend(rows: list[sqlite3.Row], key: str, label: str, unit: str, digits: int, higher: bool | None, help_text: str) -> RecoveryTrend:
    values = [daily_values(row, key) for row in rows]
    points = []
    for index, row in enumerate(rows):
        window = [value for value in values[max(0, index - MEAN_WINDOW + 1): index + 1] if value is not None]
        points.append(TrendPoint(
            date=row["date"],
            value=values[index],
            mean7=rounded(mean(window), 2) if len(window) >= MEAN_MIN_VALUES else None,
            band_low=row["hrv_balanced_low"] if key == "hrv_last_night" else None,
            band_high=row["hrv_balanced_high"] if key == "hrv_last_night" else None,
        ))
    return RecoveryTrend(key=key, label=label, unit=unit, digits=digits, higher_is_better=higher, help=help_text, points=points)


def clock_text(value: str | None) -> str | None:
    return None if value is None else value[11:16]


def minutes_of(value: str | None) -> int | None:
    if value is None:
        return None
    moment = datetime.fromisoformat(value)
    return moment.hour * 60 + moment.minute


def night_of(row: sqlite3.Row) -> Night:
    hours = lambda seconds: None if seconds is None else round(seconds / 3600, 2)
    bedtime = minutes_of(row["sleep_start_local"])
    return Night(
        date=row["date"],
        score=row["sleep_score"],
        sleep_h=hours(row["sleep_s"]),
        deep_h=hours(row["deep_s"]),
        light_h=hours(row["light_s"]),
        rem_h=hours(row["rem_s"]),
        awake_h=hours(row["awake_s"]),
        need_h=None if row["sleep_need_min"] is None else round(row["sleep_need_min"] / 60, 2),
        bedtime=clock_text(row["sleep_start_local"]),
        wake_time=clock_text(row["sleep_end_local"]),
        bedtime_minutes=None if bedtime is None else (bedtime - EVENING_START_MINUTES) % (24 * 60),
        wake_minutes=minutes_of(row["sleep_end_local"]),
        feedback=row["sleep_feedback"],
        respiration=row["sleep_respiration"],
    )


def glance_status(z: float | None, higher_is_better: bool) -> str:
    if z is None:
        return "unknown"
    better = z if higher_is_better else -z
    if better >= 1:
        return "good"
    if better <= -2:
        return "bad"
    if better <= -1:
        return "attention"
    return "typical"


def glance_days(rows: list[sqlite3.Row]) -> list[GlanceDay]:
    days = []
    for index, row in enumerate(rows):
        cells = []
        for key, _, higher, minimum_spread, digits in GLANCE:
            value = row[key]
            reference = [item[key] for item in rows[max(0, index - GLANCE_WINDOW): index] if item[key] is not None]
            z = robust_z(value, reference, minimum_spread) if value is not None and len(reference) >= GLANCE_MIN_REFERENCE else None
            display = "—" if value is None else f"{value:,.{digits}f}"
            cells.append(GlanceCell(key=key, value=value, display=display, z=rounded(z), status=glance_status(z, higher)))
        days.append(GlanceDay(date=row["date"], cells=cells))
    return days


def recovery_document(connection: sqlite3.Connection) -> Recovery:
    rows = connection.execute("SELECT * FROM daily ORDER BY date").fetchall()
    return Recovery(
        trends=[trend(rows, *spec) for spec in TRENDS],
        nights=[night_of(row) for row in rows if row["sleep_s"] is not None],
        glance_metrics=[key for key, *_ in GLANCE],
        glance_labels=[label for _, label, *_ in GLANCE],
        glance=glance_days(rows),
    )


def sleep_nights(connection: sqlite3.Connection) -> dict[str, SleepNight]:
    rows = {row["date"]: row for row in connection.execute("SELECT * FROM daily WHERE sleep_s IS NOT NULL")}
    stages: dict[str, list[SleepStage]] = {}
    for row in connection.execute("SELECT * FROM sleep_stages ORDER BY date, start_ms"):
        stages.setdefault(row["date"], []).append(SleepStage(start_ms=row["start_ms"], end_ms=row["end_ms"], stage=row["stage"]))
    series: dict[tuple[str, str], list[SleepSeriesPoint]] = {}
    for row in connection.execute("SELECT * FROM sleep_series ORDER BY date, metric, ts_ms"):
        series.setdefault((row["date"], row["metric"]), []).append(SleepSeriesPoint(ts_ms=row["ts_ms"], value=row["value"]))
    return {
        day: SleepNight(
            date=day,
            night=night_of(row),
            stages=stages.get(day, []),
            hr=series.get((day, "hr"), []),
            hrv=series.get((day, "hrv"), []),
            body_battery=series.get((day, "body_battery"), []),
            stress=series.get((day, "stress"), []),
        )
        for day, row in rows.items()
    }
