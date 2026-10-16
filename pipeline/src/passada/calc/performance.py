import json
import sqlite3
from datetime import date, timedelta
from statistics import median

from passada.calc.stats import mean, rounded
from passada.calc.trend import linear_fit, ordinal, projection, theil_sen, trend_per_30_days
from passada.calc.trend import PROJECTION_MIN_SPAN_DAYS
from passada.publish.contract import (
    ActivitySummary,
    EfficiencyPoint,
    FitnessAge,
    FormMetric,
    FormPoint,
    Performance,
    RaceDistance,
    RecordRow,
    SeriesPoint,
    TrendLine,
)

FORM_WINDOW_DAYS = 42
FORM_MIN_RUNS = 3
FORM_CURRENT_RUNS = 3
FORM_SPEED_STEP_KMH = 0.5
RIEGEL_EXPONENT = 1.06
PROJECTION_HORIZONS = (30, 90)
RACES = (("5K", "5 km", 5.0), ("10K", "10 km", 10.0), ("21K", "Meia maratona", 21.0975), ("42K", "Maratona", 42.195))
RECORD_TYPES = {
    1: ("1 km", "time", 1.0),
    2: ("1 milha", "time", 1.609),
    3: ("5 km", "time", 5.0),
    4: ("10 km", "time", 10.0),
    5: ("Meia maratona", "time", 21.0975),
    6: ("Maratona", "time", 42.195),
    7: ("Corrida mais longa", "distance", None),
    12: ("Mais passos em um dia", "steps", None),
    13: ("Mais passos em uma semana", "steps", None),
    14: ("Mais passos em um mês", "steps", None),
    15: ("Maior sequência de metas de passos", "days", None),
    16: ("Sequência atual de metas de passos", "days", None),
}
RECORD_TO_RACE = {3: "5K", 4: "10K", 5: "21K", 6: "42K"}
FORM_METRICS = (
    ("cadence", "Cadência", "ppm", 0, False),
    ("stride_m", "Passada", "m", 2, None),
    ("ground_contact_ms", "Contato com o solo", "ms", 0, True),
    ("vertical_oscillation_cm", "Oscilação vertical", "cm", 1, True),
    ("vertical_ratio_pct", "Razão vertical", "%", 1, True),
    ("power_w", "Potência", "W", 0, True),
)


def clock(seconds: float) -> str:
    total = round(seconds)
    hours, minutes, secs = total // 3600, (total % 3600) // 60, total % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def trend_line(points: list[tuple[str, float]]) -> TrendLine | None:
    if len(points) < 4:
        return None
    xs = [ordinal(day) for day, _ in points]
    fit = theil_sen(xs, [value for _, value in points])
    if fit is None:
        return None
    slope, intercept = fit
    return TrendLine(
        start_date=points[0][0],
        end_date=points[-1][0],
        start_value=round(slope * xs[0] + intercept, 4),
        end_value=round(slope * xs[-1] + intercept, 4),
        per_30_days=round(slope * 30, 4),
    )


def efficiency_points(runs: list[ActivitySummary]) -> list[EfficiencyPoint]:
    points = []
    for run in runs:
        if run.meters_per_beat is None:
            continue
        adjusted = None
        if run.heat_slowdown_pct is not None:
            adjusted = round(run.meters_per_beat * (1 + run.heat_slowdown_pct / 100), 3)
        points.append(EfficiencyPoint(
            activity_id=run.activity_id,
            date=run.date,
            distance_km=run.distance_km,
            pace_s_km=run.pace_s_km,
            heat_adjusted_pace_s_km=run.heat_adjusted_pace_s_km,
            avg_hr=run.avg_hr,
            meters_per_beat=run.meters_per_beat,
            heat_adjusted_meters_per_beat=adjusted,
            feels_like_c=run.feels_like_c,
            heat_slowdown_pct=run.heat_slowdown_pct,
        ))
    return points


def series(connection: sqlite3.Connection, sql: str) -> list[tuple[str, float]]:
    return [(row[0], row[1]) for row in connection.execute(sql) if row[1] is not None]


def as_points(values: list[tuple[str, float]] | None) -> list[SeriesPoint] | None:
    return None if values is None else [SeriesPoint(date=day, value=value) for day, value in values]


def record_rows(connection: sqlite3.Connection) -> list[RecordRow]:
    rows = []
    for row in connection.execute("SELECT * FROM records ORDER BY type_id"):
        if row["type_id"] not in RECORD_TYPES:
            continue
        label, kind, _ = RECORD_TYPES[row["type_id"]]
        value = row["value"]
        display = {
            "time": lambda: clock(value),
            "distance": lambda: f"{value / 1000:.2f} km".replace(".", ","),
            "steps": lambda: f"{round(value):,}".replace(",", "."),
            "days": lambda: f"{round(value)} dias",
        }[kind]()
        rows.append(RecordRow(type_id=row["type_id"], label=label, value=value, value_display=display, date=row["date"], activity_id=row["activity_id"]))
    return rows


def riegel(seconds: float, from_km: float, to_km: float) -> float:
    return seconds * (to_km / from_km) ** RIEGEL_EXPONENT


def races(connection: sqlite3.Connection, records: list[RecordRow]) -> list[RaceDistance]:
    by_race = {RECORD_TO_RACE[record.type_id]: record.value for record in records if record.type_id in RECORD_TO_RACE}
    timed = [(record.value, RECORD_TYPES[record.type_id][2]) for record in records if RECORD_TYPES[record.type_id][1] == "time"]
    reference = max(timed, key=lambda item: item[1] or 0) if timed else None
    result = []
    for distance, label, km in RACES:
        points = series(connection, f"SELECT date, seconds FROM race_predictions WHERE distance = '{distance}' ORDER BY date")
        if not points:
            continue
        current_day, current = points[-1]
        cutoff = str(date.fromisoformat(current_day) - timedelta(days=56))
        before = [value for day, value in points if day <= cutoff]
        result.append(RaceDistance(
            distance=distance,
            label=label,
            km=km,
            current_seconds=current,
            delta_8w_seconds=None if not before else current - before[-1],
            series=[SeriesPoint(date=day, value=value) for day, value in points],
            projection=as_points(projection(points, PROJECTION_HORIZONS)),
            record_seconds=by_race.get(distance),
            riegel_seconds=None if reference is None or reference[1] == km else round(riegel(reference[0], reference[1], km)),
        ))
    return result


def reference_speed(speeds: list[float]) -> float | None:
    if not speeds:
        return None
    return round(median(speeds) / FORM_SPEED_STEP_KMH) * FORM_SPEED_STEP_KMH


def at_reference(fit: tuple[float, float] | None, reference: float | None, speed: float, value: float, digits: int) -> float | None:
    if fit is None or reference is None:
        return None
    return round(value - fit[0] * (speed - reference), digits + 1)


def form_metrics(runs: list[ActivitySummary], today: date) -> list[FormMetric]:
    cutoff = str(today - timedelta(days=FORM_WINDOW_DAYS))
    metrics = []
    for key, label, unit, digits, lower_is_better in FORM_METRICS:
        usable = [run for run in runs if getattr(run, key) is not None and run.pace_s_km]
        speeds = [round(3600 / run.pace_s_km, 2) for run in usable]
        values = [getattr(run, key) for run in usable]
        fit = linear_fit(speeds, values)
        reference = reference_speed(speeds)
        points = sorted(
            (
                FormPoint(date=run.date, speed_kmh=speed, value=value, adjusted=at_reference(fit, reference, speed, value, digits), recent=run.date > cutoff)
                for run, speed, value in zip(usable, speeds, values)
            ),
            key=lambda point: point.date,
        )
        recent = [point for point in points if point.recent]
        earlier = [point for point in points if not point.recent]
        delta = None
        verdict = f"Precisa de {FORM_MIN_RUNS} corridas antes e {FORM_MIN_RUNS} nas últimas {FORM_WINDOW_DAYS // 7} semanas para comparar."
        if fit is not None and len(recent) >= FORM_MIN_RUNS and len(earlier) >= FORM_MIN_RUNS:
            delta = mean([point.adjusted for point in recent]) - mean([point.adjusted for point in earlier])
            magnitude = f"{abs(delta):.{digits}f}".replace(".", ",")
            if round(delta, digits) == 0:
                verdict = "Igual às semanas anteriores."
            else:
                direction = "menos" if delta < 0 else "mais"
                verdict = f"{magnitude} {unit} a {direction} que nas semanas anteriores"
                if lower_is_better is None:
                    verdict += "."
                else:
                    verdict += f": {'melhorou' if (delta < 0) == lower_is_better else 'piorou'}."
        latest = [point.adjusted for point in points[-FORM_CURRENT_RUNS:] if point.adjusted is not None]
        metrics.append(FormMetric(
            key=key,
            label=label,
            unit=unit,
            digits=digits,
            lower_is_better=lower_is_better,
            recent_delta=rounded(delta, digits + 1),
            recent_count=len(recent),
            earlier_count=len(earlier),
            verdict=verdict,
            fit_slope=None if fit is None else round(fit[0], 4),
            fit_intercept=None if fit is None else round(fit[1], 4),
            reference_speed_kmh=reference,
            current=rounded(mean(latest), digits + 1) if latest else None,
            points=points,
        ))
    return metrics


def fitness_age(connection: sqlite3.Connection) -> FitnessAge | None:
    values = {row["key"]: json.loads(row["value"]) for row in connection.execute("SELECT * FROM profile") if row["value"] is not None}
    if "fitness_age" not in values:
        return None
    return FitnessAge(
        fitness_age=rounded(values.get("fitness_age"), 0),
        chronological_age=values.get("chronological_age"),
        achievable_age=rounded(values.get("achievable_fitness_age"), 0),
        vigorous_days_per_week=values.get("vigorous_days_per_week"),
        vigorous_days_target=values.get("vigorous_days_target"),
        vigorous_minutes_per_week=rounded(values.get("vigorous_minutes_per_week")),
        vigorous_minutes_target=values.get("vigorous_minutes_target"),
    )


def performance_document(connection: sqlite3.Connection, summaries: list[ActivitySummary], today: date) -> Performance:
    runs = [summary for summary in summaries if summary.sport == "run"]
    efficiency = efficiency_points(runs)
    vo2 = series(connection, "SELECT date, vo2max FROM vo2max ORDER BY date")
    vo2_projection = projection(vo2, PROJECTION_HORIZONS)
    span = (ordinal(vo2[-1][0]) - ordinal(vo2[0][0])) if vo2 else 0
    records = record_rows(connection)
    return Performance(
        efficiency=efficiency,
        efficiency_trend=trend_line([(point.date, point.meters_per_beat) for point in efficiency]),
        heat_adjusted_trend=trend_line([
            (point.date, point.heat_adjusted_meters_per_beat) for point in efficiency if point.heat_adjusted_meters_per_beat is not None
        ]),
        vo2max=[SeriesPoint(date=day, value=value) for day, value in vo2],
        vo2max_per_30_days=rounded(trend_per_30_days(vo2), 2),
        vo2max_projection=as_points(vo2_projection),
        projection_note=(
            "Projeção pela tendência robusta (Theil-Sen), amortecida pela metade: o ganho desacelera com o tempo."
            if vo2_projection
            else f"A projeção aparece com {PROJECTION_MIN_SPAN_DAYS // 7} semanas de histórico; hoje há {span // 7}."
        ),
        races=races(connection, records),
        form_window_days=FORM_WINDOW_DAYS,
        form=form_metrics(runs, today),
        records=records,
        fitness_age=fitness_age(connection),
    )
