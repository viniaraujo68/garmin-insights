import sqlite3
from datetime import date, timedelta
from statistics import median

from garmin_insights import config
from garmin_insights.calc.stats import mean, robust_z, rounded
from garmin_insights.publish.contract import (
    ActivitySummary,
    BaselineTile,
    IllnessSignal,
    IllnessWatch,
    Readiness,
    ReadinessFactor,
    Signal,
    SparkPoint,
    Today,
    WeekActivity,
    WeekDay,
)

SPARK_DAYS = 14
BASELINE_DAYS = 7
READINESS_FACTORS = (
    ("sleep", "Sleep", "readiness_sleep_pct"),
    ("sleep_history", "Sleep History", "readiness_sleep_history_pct"),
    ("recovery", "Recovery Time", "readiness_recovery_pct"),
    ("load", "Acute Load", "readiness_load_pct"),
    ("stress", "Stress History", "readiness_stress_pct"),
    ("hrv", "HRV Status", "readiness_hrv_pct"),
)
TRAINING_STATUS = {
    "PRODUCTIVE": "Productive",
    "MAINTAINING": "Maintaining",
    "RECOVERY": "Recovery",
    "UNPRODUCTIVE": "Unproductive",
    "DETRAINING": "Detraining",
    "PEAKING": "Peaking",
    "OVERREACHING": "Overreaching",
    "STRAINED": "Strained",
    "NO_STATUS": "No Status",
}


def number(value: float | None, digits: int = 0, suffix: str = "") -> str:
    if value is None:
        return "—"
    text = f"{value:,.{digits}f}"
    return f"{text}{suffix}"


def signed(value: float | None, digits: int = 0, suffix: str = "") -> str:
    if value is None:
        return "—"
    text = number(abs(value), digits, suffix)
    return text if round(value, digits) == 0 else f"{'+' if value > 0 else '−'}{text}"


def hours_minutes(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    minutes = round(seconds / 60)
    return f"{minutes // 60}h{minutes % 60:02d}"


def daily_rows(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {row["date"]: row for row in connection.execute("SELECT * FROM daily ORDER BY date")}


def window(days: dict[str, sqlite3.Row], end: date, length: int, offset: int = 0) -> list[sqlite3.Row]:
    wanted = [str(end - timedelta(days=offset + back)) for back in range(length - 1, -1, -1)]
    return [days[day] for day in wanted if day in days]


def values(rows: list[sqlite3.Row], column: str) -> list[float]:
    return [row[column] for row in rows if row[column] is not None]


def spark(days: dict[str, sqlite3.Row], end: date, column: str) -> list[SparkPoint]:
    return [SparkPoint(date=row["date"], value=row[column]) for row in window(days, end, SPARK_DAYS)]


def readiness_of(days: dict[str, sqlite3.Row], day: date) -> Readiness | None:
    for back in range(2):
        row = days.get(str(day - timedelta(days=back)))
        if row is not None and row["readiness_score"] is not None:
            factors = [
                ReadinessFactor(key=key, label=label, pct=row[column])
                for key, label, column in READINESS_FACTORS
                if row[column] is not None
            ]
            recovery = row["recovery_time_min"]
            return Readiness(
                date=row["date"],
                score=row["readiness_score"],
                level=row["readiness_level"],
                feedback=row["readiness_feedback"],
                recovery_time_h=None if recovery is None else round(recovery / 60),
                factors=sorted(factors, key=lambda factor: factor.pct),
            )
    return None


def hrv_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    row = days.get(str(day))
    value = row["hrv_last_night"] if row else None
    low = row["hrv_balanced_low"] if row else None
    high = row["hrv_balanced_high"] if row else None
    weekly = row["hrv_weekly_avg"] if row else None
    if value is None or low is None or high is None:
        status, label = "unknown", "no range set"
    elif value < low:
        status, label = "attention", "below your range"
    elif value > high:
        status, label = "typical", "above your range"
    else:
        status, label = "good", "within your range"
    return BaselineTile(
        key="hrv",
        label="Overnight HRV",
        value=value,
        display=number(value, 0, " ms"),
        baseline_label=f"7-night average {number(weekly, 0, ' ms')}",
        delta_display=signed(None if value is None or weekly is None else value - weekly, 0, " ms"),
        status=status,
        status_label=label,
        band_low=low,
        band_high=high,
        spark=spark(days, day, "hrv_last_night"),
    )


def resting_hr_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    row = days.get(str(day))
    value = row["resting_hr"] if row else None
    baseline = mean(values(window(days, day, BASELINE_DAYS, offset=1), "resting_hr"))
    delta = None if value is None or baseline is None else value - baseline
    if delta is None:
        status, label = "unknown", "no baseline"
    elif delta > 3:
        status, label = "attention", "above your normal"
    elif delta < -3:
        status, label = "good", "below your normal"
    else:
        status, label = "typical", "at your normal"
    return BaselineTile(
        key="resting_hr",
        label="Resting HR",
        value=value,
        display=number(value, 0, " bpm"),
        baseline_label=f"7-day average {number(baseline, 0, ' bpm')}",
        delta_display=signed(delta, 0, " bpm"),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, day, "resting_hr"),
    )


def sleep_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    row = days.get(str(day))
    score = row["sleep_score"] if row else None
    slept = row["sleep_s"] if row else None
    need = row["sleep_need_min"] if row else None
    if score is None:
        status, label = "unknown", "no sleep data"
    elif score >= 80:
        status, label = "good", "good sleep"
    elif score >= 60:
        status, label = "typical", "fair sleep"
    else:
        status, label = "attention", "poor sleep"
    return BaselineTile(
        key="sleep",
        label="Sleep",
        value=score,
        display=f"{number(score)} · {hours_minutes(slept)}",
        baseline_label=f"needed {hours_minutes(need * 60)}" if need else "no sleep need set",
        delta_display=signed(None if slept is None or need is None else (slept / 60 - need) / 60, 1, " h"),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, day, "sleep_score"),
    )


def body_battery_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    row = days.get(str(day))
    value = row["body_battery_high"] if row else None
    baseline = mean(values(window(days, day, BASELINE_DAYS, offset=1), "body_battery_high"))
    if value is None:
        status, label = "unknown", "no data"
    elif value >= 75:
        status, label = "good", "charged"
    elif value >= 50:
        status, label = "typical", "half charged"
    else:
        status, label = "attention", "low energy"
    return BaselineTile(
        key="body_battery",
        label="Body Battery at wake-up",
        value=value,
        display=number(value),
        baseline_label=f"7-day average {number(baseline)}",
        delta_display=signed(None if value is None or baseline is None else value - baseline),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, day, "body_battery_high"),
    )


def stress_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    yesterday = day - timedelta(days=1)
    row = days.get(str(yesterday))
    value = row["stress_avg"] if row else None
    baseline = mean(values(window(days, yesterday, BASELINE_DAYS, offset=1), "stress_avg"))
    if value is None:
        status, label = "unknown", "no data"
    elif value <= 25:
        status, label = "good", "rest"
    elif value <= 50:
        status, label = "typical", "low"
    elif value <= 75:
        status, label = "attention", "medium"
    else:
        status, label = "bad", "high"
    return BaselineTile(
        key="stress",
        label="Yesterday's stress",
        value=value,
        display=number(value),
        baseline_label=f"7-day average {number(baseline)}",
        delta_display=signed(None if value is None or baseline is None else value - baseline),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, yesterday, "stress_avg"),
    )


def steps_tile(days: dict[str, sqlite3.Row], day: date) -> BaselineTile:
    yesterday = day - timedelta(days=1)
    row = days.get(str(yesterday))
    value = row["steps"] if row else None
    goal = row["step_goal"] if row else None
    if value is None or not goal:
        status, label = "unknown", "no goal"
    elif value >= goal:
        status, label = "good", "goal reached"
    else:
        status, label = "typical", f"{round(value / goal * 100)}% of goal"
    return BaselineTile(
        key="steps",
        label="Yesterday's steps",
        value=value,
        display=number(value),
        baseline_label=f"goal {number(goal)}",
        delta_display=signed(None if value is None or goal is None else value - goal),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, yesterday, "steps"),
    )


ILLNESS_SIGNALS = (
    ("resting_hr", "Resting HR", "bpm", "resting_hr", 1, 3.0, 1.0),
    ("hrv", "Overnight HRV", "ms", "hrv_last_night", -1, 0.0, 2.0),
    ("respiration", "Sleep respiration", "brpm", "sleep_respiration", 1, 1.0, 0.5),
)


def illness_watch(days: dict[str, sqlite3.Row], day: date) -> IllnessWatch:
    reference = [
        days[str(day - timedelta(days=back))]
        for back in range(config.ILLNESS_REFERENCE_LAST_DAY, config.ILLNESS_REFERENCE_FIRST_DAY + 1)
        if str(day - timedelta(days=back)) in days
    ]
    row = days.get(str(day))
    signals = []
    for key, label, unit, column, direction, minimum_change, minimum_spread in ILLNESS_SIGNALS:
        history = values(reference, column)
        value = row[column] if row else None
        z = robust_z(value, history, minimum_spread) if value is not None and len(history) >= config.ILLNESS_MIN_REFERENCE_NIGHTS else None
        center = median(history) if history else None
        flagged = (
            z is not None
            and center is not None
            and z * direction >= config.ILLNESS_Z
            and (value - center) * direction >= minimum_change
        )
        signals.append(IllnessSignal(key=key, label=label, unit=unit, value=value, median=rounded(center), z=rounded(z), flagged=flagged))
    nights = min((len(values(reference, signal[3])) for signal in ILLNESS_SIGNALS), default=0)
    flags = sum(signal.flagged for signal in signals)
    if nights < config.ILLNESS_MIN_REFERENCE_NIGHTS:
        status, message = "insufficient", f"Needs {config.ILLNESS_MIN_REFERENCE_NIGHTS} reference nights; there are {nights}."
    elif flags >= 2:
        status, message = "alert", "Two or more signals outside your normal at the same time: it could be the start of an illness or accumulated fatigue. Take it easy today."
    elif flags == 1:
        status, message = "watch", "One signal outside your normal. On its own it does not mean much; worth watching tomorrow."
    else:
        status, message = "ok", "Resting HR, HRV and respiration within your normal."
    return IllnessWatch(status=status, message=message, reference_nights=nights, signals=signals)


def week_of(summaries: list[ActivitySummary], day: date) -> list[WeekDay]:
    week = []
    for back in range(6, -1, -1):
        current = str(day - timedelta(days=back))
        week.append(WeekDay(
            date=current,
            activities=[
                WeekActivity(
                    activity_id=summary.activity_id,
                    sport=summary.sport,
                    distance_km=summary.distance_km,
                    duration_min=summary.duration_min,
                    training_load=summary.training_load,
                )
                for summary in summaries
                if summary.date == current
            ],
        ))
    return week


def run_km(summaries: list[ActivitySummary], start: date, end: date) -> float:
    return sum(
        summary.distance_km or 0
        for summary in summaries
        if summary.sport == "run" and str(start) <= summary.date <= str(end)
    )


def signals_of(connection: sqlite3.Connection, summaries: list[ActivitySummary], day: date) -> list[Signal]:
    signals = []
    load = connection.execute(
        "SELECT * FROM load_daily WHERE acwr IS NOT NULL AND date <= ? ORDER BY date DESC LIMIT 1", (str(day),)
    ).fetchone()
    if load:
        ratio = load["acwr"]
        if ratio < 0.8:
            status, detail = "attention", "below 0.8: you can safely increase the load"
        elif ratio <= 1.3:
            status, detail = "good", "between 0.8 and 1.3: safe progression"
        elif ratio <= 1.5:
            status, detail = "attention", "above 1.3: beware of sudden increases"
        else:
            status, detail = "bad", "above 1.5: high injury risk"
        signals.append(Signal(key="acwr", label="Acute:Chronic load ratio", display=number(ratio, 1), detail=detail, status=status))
    recent = run_km(summaries, day - timedelta(days=6), day)
    prior = run_km(summaries, day - timedelta(days=34), day - timedelta(days=7)) / 4
    signals.append(Signal(
        key="weekly_km",
        label="Km in the last 7 days",
        display=number(recent, 1),
        detail=f"average of the previous 4 weeks: {number(prior, 1)} km",
        status="typical",
    ))
    runs = [summary for summary in summaries if summary.sport == "run" and summary.date <= str(day)]
    if runs:
        last = runs[-1]
        since = (day - date.fromisoformat(last.date)).days
        signals.append(Signal(
            key="days_since_run",
            label="Since last run",
            display="today" if since == 0 else f"{since} day{'s' if since > 1 else ''}",
            detail=f"{number(last.distance_km, 1)} km on {date.fromisoformat(last.date):%b} {int(last.date[8:10])}",
            status="attention" if since >= 5 else "typical",
        ))
        window_start = str(date.fromisoformat(last.date) - timedelta(days=30))
        previous = [run.distance_km or 0 for run in runs[:-1] if run.date >= window_start]
        longest = max(previous, default=0)
        spike = longest > 0 and (last.distance_km or 0) > longest * 1.1
        signals.append(Signal(
            key="long_run",
            label="Longest run",
            display=number(max(longest, last.distance_km or 0), 1, " km"),
            detail=(
                f"the last run was over 10% longer than the longest of the 30 days before it ({number(longest, 1)} km): build up gradually"
                if spike
                else "longest run of the last 30 days"
            ),
            status="attention" if spike else "typical",
        ))
    return signals


def training_status_label(connection: sqlite3.Connection, day: date) -> str | None:
    row = connection.execute(
        "SELECT training_status FROM load_daily WHERE training_status IS NOT NULL AND date <= ? ORDER BY date DESC LIMIT 1",
        (str(day),),
    ).fetchone()
    if not row:
        return None
    key = row[0].rsplit("_", 1)[0] if row[0].rsplit("_", 1)[-1].isdigit() else row[0]
    return TRAINING_STATUS.get(key, key.replace("_", " ").capitalize())


def day_document(connection: sqlite3.Connection, summaries: list[ActivitySummary], days: dict[str, sqlite3.Row], day: date) -> Today:
    until = [summary for summary in summaries if summary.date <= str(day)]
    return Today(
        date=str(day),
        readiness=readiness_of(days, day),
        training_status=training_status_label(connection, day),
        tiles=[
            hrv_tile(days, day),
            resting_hr_tile(days, day),
            sleep_tile(days, day),
            body_battery_tile(days, day),
            stress_tile(days, day),
            steps_tile(days, day),
        ],
        illness=illness_watch(days, day),
        week=week_of(summaries, day),
        signals=signals_of(connection, summaries, day),
        last_activity_id=until[-1].activity_id if until else None,
    )


def day_documents(connection: sqlite3.Connection, summaries: list[ActivitySummary]) -> dict[str, Today]:
    days = daily_rows(connection)
    return {day: day_document(connection, summaries, days, date.fromisoformat(day)) for day in days}
