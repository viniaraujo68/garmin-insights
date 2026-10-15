import sqlite3

from passada.publish.contract import ActivitySummary


def pace_seconds(speed: float | None) -> int | None:
    return None if not speed else round(1000 / speed)


def rounded(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def activity_summaries(connection: sqlite3.Connection) -> list[ActivitySummary]:
    rows = connection.execute("SELECT * FROM activities ORDER BY start_local").fetchall()
    summaries = []
    for row in rows:
        is_run = row["sport"] == "run"
        speed, hr = row["avg_speed"], row["avg_hr"]
        summaries.append(ActivitySummary(
            activity_id=row["activity_id"],
            date=row["date"],
            start_local=row["start_local"],
            sport=row["sport"],
            type_key=row["type_key"],
            name=row["name"],
            distance_km=rounded((row["distance_m"] or 0) / 1000, 2) if row["distance_m"] else None,
            duration_min=rounded((row["moving_s"] or row["duration_s"] or 0) / 60),
            pace_s_km=pace_seconds(speed) if is_run else None,
            gap_pace_s_km=pace_seconds(row["gap_speed"]) if is_run else None,
            avg_hr=hr,
            max_hr=row["max_hr"],
            meters_per_beat=round(speed * 60 / hr, 3) if is_run and speed and hr else None,
            training_load=rounded(row["training_load"]),
            aerobic_te=rounded(row["aerobic_te"]),
            anaerobic_te=rounded(row["anaerobic_te"]),
            training_effect_label=row["training_effect_label"],
            feels_like_c=row["feels_like_c"],
            dew_point_c=row["dew_point_c"],
            humidity_pct=row["humidity_pct"],
            rpe=row["rpe"],
            has_gps=bool(row["has_gps"]),
        ))
    return summaries
