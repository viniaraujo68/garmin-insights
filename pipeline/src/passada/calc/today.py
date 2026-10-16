import sqlite3
from datetime import date, timedelta
from statistics import median

from passada import config
from passada.calc.stats import mean, robust_z, rounded
from passada.publish.contract import (
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
    ("sleep", "Sono da noite", "readiness_sleep_pct"),
    ("sleep_history", "Sono dos últimos dias", "readiness_sleep_history_pct"),
    ("recovery", "Tempo de recuperação", "readiness_recovery_pct"),
    ("load", "Carga aguda", "readiness_load_pct"),
    ("stress", "Histórico de estresse", "readiness_stress_pct"),
    ("hrv", "VFC", "readiness_hrv_pct"),
)
TRAINING_STATUS = {
    "PRODUCTIVE": "Produtivo",
    "MAINTAINING": "Mantendo",
    "RECOVERY": "Recuperação",
    "UNPRODUCTIVE": "Improdutivo",
    "DETRAINING": "Destreinando",
    "PEAKING": "No pico",
    "OVERREACHING": "Excesso",
    "STRAINED": "Sobrecarregado",
    "NO_STATUS": "Sem status",
}


def number(value: float | None, digits: int = 0, suffix: str = "") -> str:
    if value is None:
        return "—"
    text = f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")
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
        status, label = "unknown", "sem faixa definida"
    elif value < low:
        status, label = "attention", "abaixo da sua faixa"
    elif value > high:
        status, label = "typical", "acima da sua faixa"
    else:
        status, label = "good", "dentro da sua faixa"
    return BaselineTile(
        key="hrv",
        label="VFC da noite",
        value=value,
        display=number(value, 0, " ms"),
        baseline_label=f"média de 7 noites {number(weekly, 0, ' ms')}",
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
        status, label = "unknown", "sem referência"
    elif delta > 3:
        status, label = "attention", "acima do seu normal"
    elif delta < -3:
        status, label = "good", "abaixo do seu normal"
    else:
        status, label = "typical", "no seu normal"
    return BaselineTile(
        key="resting_hr",
        label="FC de repouso",
        value=value,
        display=number(value, 0, " bpm"),
        baseline_label=f"média de 7 dias {number(baseline, 0, ' bpm')}",
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
        status, label = "unknown", "sem dado de sono"
    elif score >= 80:
        status, label = "good", "sono bom"
    elif score >= 60:
        status, label = "typical", "sono razoável"
    else:
        status, label = "attention", "sono ruim"
    return BaselineTile(
        key="sleep",
        label="Sono",
        value=score,
        display=f"{number(score)} · {hours_minutes(slept)}",
        baseline_label=f"precisava de {hours_minutes(need * 60)}" if need else "sem meta de sono",
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
        status, label = "unknown", "sem dado"
    elif value >= 75:
        status, label = "good", "carregado"
    elif value >= 50:
        status, label = "typical", "meia carga"
    else:
        status, label = "attention", "pouca energia"
    return BaselineTile(
        key="body_battery",
        label="Body Battery ao acordar",
        value=value,
        display=number(value),
        baseline_label=f"média de 7 dias {number(baseline)}",
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
        status, label = "unknown", "sem dado"
    elif value <= 25:
        status, label = "good", "descanso"
    elif value <= 50:
        status, label = "typical", "baixo"
    elif value <= 75:
        status, label = "attention", "médio"
    else:
        status, label = "bad", "alto"
    return BaselineTile(
        key="stress",
        label="Estresse de ontem",
        value=value,
        display=number(value),
        baseline_label=f"média de 7 dias {number(baseline)}",
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
        status, label = "unknown", "sem meta"
    elif value >= goal:
        status, label = "good", "meta batida"
    else:
        status, label = "typical", f"{round(value / goal * 100)}% da meta"
    return BaselineTile(
        key="steps",
        label="Passos de ontem",
        value=value,
        display=number(value),
        baseline_label=f"meta {number(goal)}",
        delta_display=signed(None if value is None or goal is None else value - goal),
        status=status,
        status_label=label,
        band_low=None,
        band_high=None,
        spark=spark(days, yesterday, "steps"),
    )


ILLNESS_SIGNALS = (
    ("resting_hr", "FC de repouso", "bpm", "resting_hr", 1, 3.0, 1.0),
    ("hrv", "VFC da noite", "ms", "hrv_last_night", -1, 0.0, 2.0),
    ("respiration", "Respiração no sono", "rpm", "sleep_respiration", 1, 1.0, 0.5),
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
        status, message = "insufficient", f"Precisa de {config.ILLNESS_MIN_REFERENCE_NIGHTS} noites de referência; há {nights}."
    elif flags >= 2:
        status, message = "alert", "Dois ou mais sinais fora do seu normal ao mesmo tempo: pode ser o começo de uma doença ou cansaço acumulado. Pegue leve hoje."
    elif flags == 1:
        status, message = "watch", "Um sinal fora do seu normal. Sozinho não quer dizer muito; vale observar amanhã."
    else:
        status, message = "ok", "FC de repouso, VFC e respiração dentro do seu normal."
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
            status, detail = "attention", "abaixo de 0,8: dá para aumentar a carga com segurança"
        elif ratio <= 1.3:
            status, detail = "good", "entre 0,8 e 1,3: evolução segura"
        elif ratio <= 1.5:
            status, detail = "attention", "acima de 1,3: cuidado com aumentos bruscos"
        else:
            status, detail = "bad", "acima de 1,5: risco alto de lesão"
        signals.append(Signal(key="acwr", label="Carga aguda ÷ crônica", display=number(ratio, 1), detail=detail, status=status))
    recent = run_km(summaries, day - timedelta(days=6), day)
    prior = run_km(summaries, day - timedelta(days=34), day - timedelta(days=7)) / 4
    signals.append(Signal(
        key="weekly_km",
        label="Km nos últimos 7 dias",
        display=number(recent, 1),
        detail=f"média das 4 semanas anteriores: {number(prior, 1)} km",
        status="typical",
    ))
    runs = [summary for summary in summaries if summary.sport == "run" and summary.date <= str(day)]
    if runs:
        last = runs[-1]
        since = (day - date.fromisoformat(last.date)).days
        signals.append(Signal(
            key="days_since_run",
            label="Desde a última corrida",
            display="hoje" if since == 0 else f"{since} dia{'s' if since > 1 else ''}",
            detail=f"{number(last.distance_km, 1)} km em {last.date[8:10]}/{last.date[5:7]}",
            status="attention" if since >= 5 else "typical",
        ))
        window_start = str(date.fromisoformat(last.date) - timedelta(days=30))
        previous = [run.distance_km or 0 for run in runs[:-1] if run.date >= window_start]
        longest = max(previous, default=0)
        spike = longest > 0 and (last.distance_km or 0) > longest * 1.1
        signals.append(Signal(
            key="long_run",
            label="Longão",
            display=number(max(longest, last.distance_km or 0), 1, " km"),
            detail=(
                f"a última corrida passou 10% da maior dos 30 dias antes ({number(longest, 1)} km): aumente aos poucos"
                if spike
                else "maior corrida dos últimos 30 dias"
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
