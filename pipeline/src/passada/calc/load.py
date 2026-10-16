import math
import sqlite3
from datetime import date, timedelta
from statistics import median, pstdev

from passada import config
from passada.calc.stats import rounded
from passada.publish.contract import ActivitySummary, CalendarDay, FocusRow, Load, LoadDay, LoadSummary, WeekLoad

FITNESS_DAYS = 42
FATIGUE_DAYS = 7
EASY_MIN_PCT = 65
EASY_MAX_PCT = 92
FOCUS_LABELS = {"aerobic_low": "Aeróbico leve", "aerobic_high": "Aeróbico forte", "anaerobic": "Anaeróbico"}
EASY_TARGET_PCT = 80
SUMMARY_WEEKS = 4
TYPICAL_RUN_DAYS = 56


def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def daily_loads(summaries: list[ActivitySummary], start: date, end: date) -> dict[str, float]:
    loads = {str(start + timedelta(days=offset)): 0.0 for offset in range((end - start).days + 1)}
    for summary in summaries:
        if summary.date in loads:
            loads[summary.date] += summary.training_load or 0
    return loads


def load_days(connection: sqlite3.Connection, loads: dict[str, float]) -> list[LoadDay]:
    garmin = {row["date"]: row for row in connection.execute("SELECT * FROM load_daily")}
    fitness = fatigue = 0.0
    days = []
    for day, load in loads.items():
        form = fitness - fatigue
        fitness += (load - fitness) / FITNESS_DAYS
        fatigue += (load - fatigue) / FATIGUE_DAYS
        row = garmin.get(day)
        days.append(LoadDay(
            date=day,
            daily_load=round(load, 1),
            acute=row["acute"] if row else None,
            chronic=row["chronic"] if row else None,
            chronic_min=rounded(row["chronic_min"]) if row else None,
            chronic_max=rounded(row["chronic_max"]) if row else None,
            acwr=row["acwr"] if row else None,
            fitness=round(fitness, 1),
            fatigue=round(fatigue, 1),
            form=round(form, 1),
        ))
    return days


def verdict(easy_pct: float | None) -> str | None:
    if easy_pct is None:
        return None
    if easy_pct < EASY_MIN_PCT:
        return "intenso demais"
    if easy_pct > EASY_MAX_PCT:
        return "leve demais"
    return "equilibrado"


def weeks_of(summaries: list[ActivitySummary], loads: dict[str, float], start: date, end: date) -> list[WeekLoad]:
    weeks = []
    current = monday(start)
    while current <= end:
        days = [str(current + timedelta(days=offset)) for offset in range(7)]
        activities = [summary for summary in summaries if summary.date in days]
        minutes = {sport: sum(item.duration_min or 0 for item in activities if item.sport == sport) for sport in ("run", "football", "gym", "other")}
        zones = [sum(item.zone_minutes[zone] for item in activities if len(item.zone_minutes) == 5) for zone in range(5)]
        easy, moderate, hard = zones[0] + zones[1], zones[2], zones[3] + zones[4]
        total = easy + moderate + hard
        week_loads = [loads.get(day, 0.0) for day in days if day <= str(end)]
        average = sum(week_loads) / len(week_loads) if week_loads else 0
        spread = pstdev(week_loads) if len(week_loads) > 1 else 0
        monotony = average / spread if spread > 0 else None
        easy_pct = round(easy / total * 100, 1) if total else None
        weeks.append(WeekLoad(
            week=str(current),
            km=round(sum(item.distance_km or 0 for item in activities if item.sport == "run"), 1),
            runs=sum(1 for item in activities if item.sport == "run"),
            minutes_run=round(minutes["run"]),
            minutes_football=round(minutes["football"]),
            minutes_gym=round(minutes["gym"]),
            minutes_other=round(minutes["other"]),
            load=round(sum(week_loads), 1),
            easy_min=round(easy),
            moderate_min=round(moderate),
            hard_min=round(hard),
            easy_pct=easy_pct,
            verdict=verdict(easy_pct),
            monotony=rounded(monotony, 2),
            strain=None if monotony is None else round(sum(week_loads) * monotony),
        ))
        current += timedelta(days=7)
    return weeks


def focus_rows(connection: sqlite3.Connection) -> list[FocusRow]:
    rows = []
    for row in connection.execute("SELECT * FROM load_focus"):
        load, low, high = row["load"], row["target_min"], row["target_max"]
        if load is None or low is None or high is None:
            status = "unknown"
        elif load < low:
            status = "attention"
        elif load > high:
            status = "attention"
        else:
            status = "good"
        rows.append(FocusRow(focus=row["focus"], label=FOCUS_LABELS.get(row["focus"], row["focus"]), load=rounded(load, 0), target_min=low, target_max=high, status=status))
    order = list(FOCUS_LABELS)
    return sorted(rows, key=lambda row: order.index(row.focus) if row.focus in order else len(order))


def calendar_of(summaries: list[ActivitySummary], loads: dict[str, float]) -> list[CalendarDay]:
    return [
        CalendarDay(
            date=day,
            load=round(load, 1),
            sports=sorted({summary.sport for summary in summaries if summary.date == day}),
        )
        for day, load in loads.items()
    ]


def typical_run_load(summaries: list[ActivitySummary], today: date) -> float | None:
    runs = [summary.training_load for summary in summaries if summary.sport == "run" and summary.training_load]
    recent = [
        summary.training_load
        for summary in summaries
        if summary.sport == "run" and summary.training_load and summary.date >= str(today - timedelta(days=TYPICAL_RUN_DAYS))
    ]
    pool = recent or runs
    return median(pool) if pool else None


def load_verdict(days: list[LoadDay], typical: float | None) -> tuple[str, str, str]:
    latest = next((day for day in reversed(days) if day.acute is not None and day.chronic_min is not None and day.chronic_max is not None), None)
    if latest is None:
        return "unknown", "Ainda sem carga da Garmin", "A Garmin precisa de algumas semanas de treino para calcular a faixa recomendada."
    acute, low, high = round(latest.acute), round(latest.chronic_min), round(latest.chronic_max)
    if acute < low:
        runs = None if not typical else max(1, math.ceil((low - acute) / typical))
        hint = "" if runs is None else f" Cerca de {runs} {'corrida' if runs == 1 else 'corridas'} como as suas de costume nos próximos dias te {'coloca' if runs == 1 else 'colocam'} de volta nela."
        return "attention", "Você está treinando menos do que aguenta", f"A carga dos últimos 7 dias é {acute}, abaixo da faixa recomendada ({low}–{high}). Dá para aumentar sem risco.{hint}"
    if acute > high:
        return "bad", "Você está treinando mais do que está acostumado", f"A carga dos últimos 7 dias é {acute}, acima da faixa recomendada ({low}–{high}). Acima dela o risco de lesão sobe: segure alguns dias."
    return "good", "Carga na medida certa", f"A carga dos últimos 7 dias é {acute}, dentro da faixa recomendada ({low}–{high}). É assim que você evolui sem exagero."


def easy_line(weeks: list[WeekLoad]) -> str | None:
    recent = weeks[-SUMMARY_WEEKS:]
    easy = sum(week.easy_min for week in recent)
    total = sum(week.easy_min + week.moderate_min + week.hard_min for week in recent)
    if not total:
        return None
    share = round(easy / total * 100)
    if share < EASY_MIN_PCT:
        advice = "Está forte demais: corra mais devagar na maior parte dos treinos."
    elif share > EASY_MAX_PCT:
        advice = "Dá para incluir um treino mais forte por semana."
    else:
        advice = "Boa mistura."
    return f"Nas últimas {len(recent)} semanas, {share}% do tempo correndo foi leve (meta: uns {EASY_TARGET_PCT}%). {advice}"


def load_document(connection: sqlite3.Connection, summaries: list[ActivitySummary], today: date) -> Load:
    loads = daily_loads(summaries, config.HISTORY_START, today)
    days = load_days(connection, loads)
    weeks = weeks_of(summaries, loads, config.HISTORY_START, today)
    focus = focus_rows(connection)
    status, headline, detail = load_verdict(days, typical_run_load(summaries, today))
    return Load(
        summary=LoadSummary(status=status, headline=headline, detail=detail, easy_line=easy_line(weeks)),
        days=days,
        weeks=weeks,
        focus=focus,
        calendar=calendar_of(summaries, loads),
    )
