import math
import sqlite3

from passada import config
from passada.calc.heat import heat_adjusted_pace, heat_slowdown_pct
from passada.calc.stats import mean, pace_seconds, rounded
from passada.publish.contract import (
    ActivityDetail,
    ActivitySummary,
    Lap,
    Privacy,
    Routes,
    RouteTrace,
    Streams,
    Weather,
    ZoneTime,
)

SLOWEST_STREAM_PACE_S_KM = 900
GRADE_WINDOW_M = 50
PERFORMANCE_CONDITION_SKIP_S = 360
ROUTE_STEP_M = 20
HOME_NEIGHBOR_M = 300
HOME_MIN_VISITS = 3
EARTH_RADIUS_M = 6_371_000


def stream_pace(speed: float | None) -> float | None:
    if speed is None or speed <= 0:
        return None
    return min(round(1000 / speed), SLOWEST_STREAM_PACE_S_KM)


def samples_by_activity(connection: sqlite3.Connection) -> dict[str, list[sqlite3.Row]]:
    grouped: dict[str, list[sqlite3.Row]] = {}
    for row in connection.execute("SELECT * FROM samples ORDER BY activity_id, idx"):
        grouped.setdefault(row["activity_id"], []).append(row)
    return grouped


def performance_condition(samples: list[sqlite3.Row]) -> float | None:
    values = [
        row["performance_condition"]
        for row in samples
        if row["performance_condition"] is not None and (row["elapsed_s"] or 0) >= PERFORMANCE_CONDITION_SKIP_S
    ]
    return rounded(mean(values))


def summary_of(row: sqlite3.Row, samples: list[sqlite3.Row]) -> ActivitySummary:
    is_run = row["sport"] == "run"
    speed, hr = row["avg_speed"], row["avg_hr"]
    pace = pace_seconds(speed) if is_run else None
    slowdown = heat_slowdown_pct(row["temperature_c"], row["dew_point_c"]) if is_run else None
    return ActivitySummary(
        activity_id=row["activity_id"],
        date=row["date"],
        start_local=row["start_local"],
        sport=row["sport"],
        type_key=row["type_key"],
        name=row["name"],
        distance_km=rounded(row["distance_m"] / 1000, 2) if row["distance_m"] else None,
        duration_min=rounded((row["moving_s"] or row["duration_s"] or 0) / 60),
        pace_s_km=pace,
        gap_pace_s_km=pace_seconds(row["gap_speed"]) if is_run else None,
        heat_adjusted_pace_s_km=heat_adjusted_pace(pace, slowdown),
        heat_slowdown_pct=slowdown,
        avg_hr=row["avg_hr"],
        max_hr=row["max_hr"],
        recovery_hr=row["recovery_hr"],
        meters_per_beat=round(speed * 60 / hr, 3) if is_run and speed and hr else None,
        cadence=rounded(row["cadence"], 0),
        stride_m=rounded(row["stride_m"], 2),
        ground_contact_ms=rounded(row["ground_contact_ms"], 0),
        vertical_oscillation_cm=rounded(row["vertical_oscillation_cm"]),
        vertical_ratio_pct=rounded(row["vertical_ratio_pct"]),
        power_w=rounded(row["power_w"], 0),
        elevation_gain_m=rounded(row["elevation_gain_m"], 0),
        performance_condition=performance_condition(samples),
        training_load=rounded(row["training_load"]),
        aerobic_te=rounded(row["aerobic_te"]),
        anaerobic_te=rounded(row["anaerobic_te"]),
        training_effect_label=row["training_effect_label"],
        zone_minutes=[round((row[f"z{zone}_s"] or 0) / 60, 1) for zone in range(1, 6)],
        temperature_c=row["temperature_c"],
        feels_like_c=row["feels_like_c"],
        dew_point_c=row["dew_point_c"],
        humidity_pct=row["humidity_pct"],
        rpe=row["rpe"],
        feel=row["feel"],
        body_battery_impact=row["body_battery_impact"],
        has_gps=bool(row["has_gps"]),
    )


def activity_summaries(connection: sqlite3.Connection, samples: dict[str, list[sqlite3.Row]]) -> list[ActivitySummary]:
    rows = connection.execute("SELECT * FROM activities ORDER BY start_local").fetchall()
    return [summary_of(row, samples.get(row["activity_id"], [])) for row in rows]


def grades(distances: list[float | None], elevations: list[float | None]) -> list[float | None]:
    result: list[float | None] = []
    start = 0
    for index, (distance, elevation) in enumerate(zip(distances, elevations)):
        if distance is None or elevation is None:
            result.append(None)
            continue
        while start < index and (distances[start] is None or distance - distances[start] > GRADE_WINDOW_M):
            start += 1
        base_distance, base_elevation = distances[start], elevations[start]
        span = distance - base_distance if base_distance is not None else 0
        if base_elevation is None or span < GRADE_WINDOW_M / 2:
            result.append(None)
            continue
        result.append(round((elevation - base_elevation) / span * 100, 1))
    return result


def streams_of(samples: list[sqlite3.Row]) -> Streams:
    def column(name: str, digits: int | None = None) -> list[float | None]:
        values = [row[name] for row in samples]
        return values if digits is None else [rounded(value, digits) for value in values]

    distances = column("distance_m", 1)
    elevations = column("elevation", 1)
    return Streams(
        elapsed_s=column("elapsed_s", 0),
        distance_m=distances,
        lat=column("lat", 6),
        lon=column("lon", 6),
        pace_s_km=[stream_pace(row["speed"]) for row in samples],
        gap_pace_s_km=[stream_pace(row["gap_speed"]) for row in samples],
        hr=column("hr", 0),
        cadence=column("cadence", 0),
        power=column("power", 0),
        elevation=elevations,
        grade_pct=grades(distances, elevations),
        performance_condition=column("performance_condition", 0),
    )


def laps_of(connection: sqlite3.Connection, activity_id: str) -> list[Lap]:
    return [
        Lap(
            lap=row["lap"],
            distance_m=rounded(row["distance_m"], 0),
            duration_s=rounded(row["duration_s"], 0),
            pace_s_km=pace_seconds(row["avg_speed"]),
            gap_pace_s_km=pace_seconds(row["gap_speed"]),
            avg_hr=row["avg_hr"],
            max_hr=row["max_hr"],
            cadence=rounded(row["cadence"], 0),
            stride_m=rounded(row["stride_m"], 2),
            ground_contact_ms=rounded(row["ground_contact_ms"], 0),
            power_w=rounded(row["power_w"], 0),
            elevation_gain_m=rounded(row["elevation_gain_m"], 0),
            elevation_loss_m=rounded(row["elevation_loss_m"], 0),
        )
        for row in connection.execute("SELECT * FROM laps WHERE activity_id = ? ORDER BY lap", (activity_id,))
    ]


def zones_of(connection: sqlite3.Connection, row: sqlite3.Row) -> list[ZoneTime]:
    bounds = {zone["zone"]: zone for zone in connection.execute("SELECT * FROM hr_zones")}
    return [
        ZoneTime(
            zone=zone,
            floor_bpm=bounds[zone]["floor_bpm"] if zone in bounds else None,
            ceiling_bpm=bounds[zone]["ceiling_bpm"] if zone in bounds else None,
            seconds=row[f"z{zone}_s"] or 0,
        )
        for zone in range(1, 6)
    ]


def activity_details(
    connection: sqlite3.Connection,
    summaries: list[ActivitySummary],
    samples: dict[str, list[sqlite3.Row]],
) -> dict[str, ActivityDetail]:
    rows = {row["activity_id"]: row for row in connection.execute("SELECT * FROM activities")}
    details = {}
    for summary in summaries:
        row = rows[summary.activity_id]
        details[summary.activity_id] = ActivityDetail(
            summary=summary,
            laps=laps_of(connection, summary.activity_id),
            zones=zones_of(connection, row),
            streams=streams_of(samples.get(summary.activity_id, [])),
            weather=Weather(
                temperature_c=row["temperature_c"],
                feels_like_c=row["feels_like_c"],
                dew_point_c=row["dew_point_c"],
                humidity_pct=row["humidity_pct"],
                wind_kmh=row["wind_kmh"],
                description=row["weather"],
            ),
        )
    return details


def distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def gps_points(samples: list[sqlite3.Row]) -> list[sqlite3.Row]:
    return [row for row in samples if row["lat"] is not None and row["lon"] is not None]


def home_privacy(tracks: list[list[sqlite3.Row]]) -> Privacy | None:
    endpoints = [(row["lat"], row["lon"]) for points in tracks if points for row in (points[0], points[-1])]
    best: list[tuple[float, float]] = []
    for candidate in endpoints:
        neighbors = [point for point in endpoints if distance_m(candidate, point) <= HOME_NEIGHBOR_M]
        if len(neighbors) > len(best):
            best = neighbors
    if len(best) < HOME_MIN_VISITS:
        return None
    return Privacy(
        lat=round(sum(point[0] for point in best) / len(best), 4),
        lon=round(sum(point[1] for point in best) / len(best), 4),
        radius_m=config.PRIVACY_RADIUS_M,
    )


def simplified(points: list[sqlite3.Row]) -> list[list[float | None]]:
    kept, last = [], None
    for row in points:
        traveled = row["distance_m"]
        if last is not None and traveled is not None and traveled - last < ROUTE_STEP_M:
            continue
        last = traveled
        kept.append([round(row["lat"], 5), round(row["lon"], 5), stream_pace(row["speed"])])
    return kept


def routes_document(summaries: list[ActivitySummary], samples: dict[str, list[sqlite3.Row]]) -> Routes:
    runs = [summary for summary in summaries if summary.sport == "run" and summary.has_gps]
    tracks = {summary.activity_id: gps_points(samples.get(summary.activity_id, [])) for summary in runs}
    return Routes(
        privacy=home_privacy(list(tracks.values())),
        routes=[
            RouteTrace(
                activity_id=summary.activity_id,
                date=summary.date,
                distance_km=summary.distance_km,
                pace_s_km=summary.pace_s_km,
                points=simplified(tracks[summary.activity_id]),
            )
            for summary in runs
            if tracks[summary.activity_id]
        ],
    )
