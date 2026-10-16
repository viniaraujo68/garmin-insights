import sqlite3
from collections import defaultdict
from datetime import date

from garmin_insights.calc.stats import rounded
from garmin_insights.publish.contract import (
    ActivitySummary,
    ExerciseSummary,
    FootballSession,
    GearItem,
    GymSession,
    MuscleGroupSets,
    SeriesPoint,
    Sports,
    StrengthProgress,
)

SPRINT_SPEED_MS = 5.0
SPRINT_MIN_SAMPLES = 2
HIGH_SPEED_MS = 15 / 3.6
POSITION_STEP = 5
EPLEY_DIVISOR = 30
MUSCLE_LABELS = {
    "chest": "Peito",
    "back": "Costas",
    "shoulders": "Ombros",
    "biceps": "Bíceps",
    "triceps": "Tríceps",
    "core": "Abdômen e core",
    "glutes": "Glúteos",
    "quads": "Quadríceps",
    "hamstrings": "Posteriores da coxa",
    "calves": "Panturrilhas",
}
CATEGORY_MUSCLES = {
    "BENCH_PRESS": ("chest", "triceps", "shoulders"),
    "PUSH_UP": ("chest", "triceps", "shoulders"),
    "FLYE": ("chest",),
    "ROW": ("back", "biceps"),
    "PULL_UP": ("back", "biceps"),
    "SHRUG": ("back",),
    "HYPEREXTENSION": ("back", "glutes", "hamstrings"),
    "SHOULDER_PRESS": ("shoulders", "triceps"),
    "LATERAL_RAISE": ("shoulders",),
    "SHOULDER_STABILITY": ("shoulders",),
    "CURL": ("biceps",),
    "TRICEPS_EXTENSION": ("triceps",),
    "CRUNCH": ("core",),
    "SIT_UP": ("core",),
    "PLANK": ("core",),
    "CORE": ("core",),
    "LEG_RAISE": ("core",),
    "CHOP": ("core",),
    "SQUAT": ("quads", "glutes"),
    "LUNGE": ("quads", "glutes"),
    "DEADLIFT": ("hamstrings", "glutes", "back"),
    "LEG_CURL": ("hamstrings",),
    "HIP_RAISE": ("glutes", "hamstrings"),
    "HIP_STABILITY": ("glutes",),
    "HIP_SWING": ("glutes", "hamstrings"),
    "CALF_RAISE": ("calves",),
    "OLYMPIC_LIFT": ("quads", "glutes", "back", "shoulders"),
    "TOTAL_BODY": ("quads", "back", "chest", "core"),
}
CATEGORY_LABELS = {
    "BENCH_PRESS": "Supino",
    "PUSH_UP": "Flexão",
    "FLYE": "Crucifixo",
    "ROW": "Remada",
    "PULL_UP": "Barra fixa",
    "SHOULDER_PRESS": "Desenvolvimento",
    "LATERAL_RAISE": "Elevação lateral",
    "CURL": "Rosca",
    "TRICEPS_EXTENSION": "Tríceps",
    "SQUAT": "Agachamento",
    "LUNGE": "Avanço",
    "DEADLIFT": "Levantamento terra",
    "LEG_CURL": "Flexora",
    "CALF_RAISE": "Panturrilha",
    "HIP_RAISE": "Elevação de quadril",
    "PLANK": "Prancha",
    "CRUNCH": "Abdominal",
}


def sprint_stats(samples: list[sqlite3.Row]) -> tuple[float | None, int, float]:
    speeds = [row["speed"] for row in samples]
    present = [speed for speed in speeds if speed is not None]
    sprints = 0
    run = 0
    high_speed = 0.0
    previous_distance = None
    for row in samples:
        speed, distance = row["speed"], row["distance_m"]
        if speed is not None and speed >= SPRINT_SPEED_MS:
            run += 1
            if run == SPRINT_MIN_SAMPLES:
                sprints += 1
        else:
            run = 0
        if speed is not None and speed >= HIGH_SPEED_MS and distance is not None and previous_distance is not None:
            high_speed += max(0.0, distance - previous_distance)
        if distance is not None:
            previous_distance = distance
    return (round(max(present) * 3.6, 1) if present else None), sprints, round(high_speed)


def football_sessions(summaries: list[ActivitySummary], samples: dict[str, list[sqlite3.Row]]) -> list[FootballSession]:
    sessions = []
    for summary in summaries:
        if summary.sport != "football":
            continue
        rows = samples.get(summary.activity_id, [])
        max_speed, sprints, high_speed = sprint_stats(rows)
        positions = [
            [round(row["lat"], 6), round(row["lon"], 6)]
            for row in rows[::POSITION_STEP]
            if row["lat"] is not None and row["lon"] is not None
        ]
        sessions.append(FootballSession(
            activity_id=summary.activity_id,
            date=summary.date,
            duration_min=summary.duration_min,
            distance_km=summary.distance_km,
            avg_hr=summary.avg_hr,
            max_hr=summary.max_hr,
            training_load=summary.training_load,
            aerobic_te=summary.aerobic_te,
            anaerobic_te=summary.anaerobic_te,
            zone_minutes=summary.zone_minutes,
            max_speed_kmh=max_speed,
            sprints=sprints,
            high_speed_m=high_speed,
            positions=positions,
        ))
    return sessions


def epley(weight_kg: float | None, reps: float | None) -> float | None:
    if not weight_kg or not reps:
        return None
    return round(weight_kg * (1 + reps / EPLEY_DIVISOR), 1)


def gym_sessions(connection: sqlite3.Connection, summaries: list[ActivitySummary]) -> list[GymSession]:
    sets_by_activity: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in connection.execute("SELECT * FROM exercise_sets WHERE set_type IS NULL OR set_type != 'REST' ORDER BY activity_id, set_idx"):
        sets_by_activity[row["activity_id"]].append(row)
    sessions = []
    for summary in summaries:
        if summary.sport != "gym":
            continue
        grouped: dict[tuple[str, str | None], list[sqlite3.Row]] = defaultdict(list)
        for row in sets_by_activity.get(summary.activity_id, []):
            grouped[(row["category"] or "UNKNOWN", row["exercise"])].append(row)
        exercises = []
        for (category, exercise), rows in grouped.items():
            weights = [row["weight_kg"] for row in rows if row["weight_kg"]]
            estimates = [value for value in (epley(row["weight_kg"], row["reps"]) for row in rows) if value is not None]
            exercises.append(ExerciseSummary(
                category=category,
                exercise=exercise,
                sets=len(rows),
                reps=sum(row["reps"] or 0 for row in rows),
                volume_kg=round(sum((row["weight_kg"] or 0) * (row["reps"] or 0) for row in rows), 1),
                max_weight_kg=max(weights) if weights else None,
                estimated_1rm_kg=max(estimates) if estimates else None,
            ))
        sessions.append(GymSession(
            activity_id=summary.activity_id,
            date=summary.date,
            duration_min=summary.duration_min,
            avg_hr=summary.avg_hr,
            training_load=summary.training_load,
            sets=sum(item.sets for item in exercises),
            reps=sum(item.reps for item in exercises),
            volume_kg=round(sum(item.volume_kg for item in exercises), 1),
            exercises=exercises,
        ))
    return sessions


def muscle_sets(sessions: list[GymSession], today: date) -> list[MuscleGroupSets]:
    recent = {group: 0.0 for group in MUSCLE_LABELS}
    month = {group: 0.0 for group in MUSCLE_LABELS}
    for session in sessions:
        age = (today - date.fromisoformat(session.date)).days
        for exercise in session.exercises:
            groups = CATEGORY_MUSCLES.get(exercise.category, ())
            for position, group in enumerate(groups):
                weight = 1.0 if position == 0 else 0.5
                if age < 28:
                    month[group] += exercise.sets * weight
                if age < 7:
                    recent[group] += exercise.sets * weight
    return [
        MuscleGroupSets(group=group, label=label, sets_7d=recent[group], sets_28d=month[group])
        for group, label in MUSCLE_LABELS.items()
    ]


def strength_progress(sessions: list[GymSession]) -> list[StrengthProgress]:
    by_category: dict[str, dict[str, float]] = defaultdict(dict)
    for session in sessions:
        for exercise in session.exercises:
            if exercise.estimated_1rm_kg is None:
                continue
            best = by_category[exercise.category].get(session.date, 0.0)
            by_category[exercise.category][session.date] = max(best, exercise.estimated_1rm_kg)
    return [
        StrengthProgress(
            category=category,
            label=CATEGORY_LABELS.get(category, category.replace("_", " ").capitalize()),
            points=[SeriesPoint(date=day, value=value) for day, value in sorted(points.items())],
        )
        for category, points in sorted(by_category.items())
        if len(points) >= 2
    ]


def gear_items(connection: sqlite3.Connection) -> list[GearItem]:
    return [
        GearItem(
            gear_id=row["gear_id"],
            name=row["name"] or "Sem nome",
            gear_type=row["gear_type"],
            distance_km=round((row["distance_m"] or 0) / 1000, 1),
            max_km=rounded((row["max_distance_m"] or 0) / 1000, 0) or None,
            status=row["status"],
        )
        for row in connection.execute("SELECT * FROM gear ORDER BY distance_m DESC")
        if row["gear_id"]
    ]


def sports_document(
    connection: sqlite3.Connection,
    summaries: list[ActivitySummary],
    samples: dict[str, list[sqlite3.Row]],
    today: date,
) -> Sports:
    gym = gym_sessions(connection, summaries)
    return Sports(
        football=football_sessions(summaries, samples),
        gym=gym,
        muscles=muscle_sets(gym, today),
        progress=strength_progress(gym),
        gear=gear_items(connection),
    )
