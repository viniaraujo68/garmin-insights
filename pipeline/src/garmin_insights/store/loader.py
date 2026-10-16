import json
import sqlite3
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from garmin_insights import config

SCHEMA = Path(__file__).with_name("schema.sql")
SLEEP_LEVELS = {0: "deep", 1: "light", 2: "rem", 3: "awake"}
SLEEP_SERIES = {
    "sleepHeartRate": "hr",
    "hrvData": "hrv",
    "sleepBodyBattery": "body_battery",
    "sleepStress": "stress",
}
RACE_DISTANCES = {"time5K": "5K", "time10K": "10K", "timeHalfMarathon": "21K", "timeMarathon": "42K"}
SAMPLE_METRICS = {
    "elapsed_s": "sumElapsedDuration",
    "distance_m": "sumDistance",
    "lat": "directLatitude",
    "lon": "directLongitude",
    "speed": "directSpeed",
    "gap_speed": "directGradeAdjustedSpeed",
    "hr": "directHeartRate",
    "cadence": "directDoubleCadence",
    "power": "directPower",
    "elevation": "directElevation",
    "performance_condition": "directPerformanceCondition",
    "stride_m": "directStrideLength",
    "ground_contact_ms": "directGroundContactTime",
    "vertical_oscillation_cm": "directVerticalOscillation",
    "vertical_ratio_pct": "directVerticalRatio",
    "body_battery": "directBodyBattery",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text()) if path.exists() else None


def fahrenheit_to_celsius(value: float | None) -> float | None:
    return None if value is None else round((value - 32) * 5 / 9, 1)


def centimeters_to_meters(value: float | None) -> float | None:
    return None if not value else value / 100


def first_value(mapping: dict | None) -> Any:
    return next(iter(mapping.values()), None) if mapping else None


def local_time(timestamp_ms: int | None) -> str | None:
    if timestamp_ms is None:
        return None
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=config.TIMEZONE).isoformat(timespec="minutes")


def sport_of(type_key: str) -> str:
    if type_key in config.RUNNING_TYPES:
        return "run"
    if type_key in config.FOOTBALL_TYPES:
        return "football"
    if type_key in config.STRENGTH_TYPES:
        return "gym"
    return "other"


def activity_row(activity_dir: Path) -> dict[str, Any]:
    activity = read_json(activity_dir / "summary.json")
    summary = activity["summaryDTO"]
    type_key = activity["activityTypeDTO"]["typeKey"]
    weather = read_json(activity_dir / "weather.json") or {}
    zones = {zone["zoneNumber"]: zone["secsInZone"] for zone in read_json(activity_dir / "hr_zones.json") or []}
    rpe = summary.get("directWorkoutRpe")
    wind_mph = weather.get("windSpeed")
    return {
        "activity_id": activity_dir.name,
        "start_local": summary["startTimeLocal"],
        "date": summary["startTimeLocal"][:10],
        "type_key": type_key,
        "sport": sport_of(type_key),
        "name": activity.get("activityName"),
        "distance_m": summary.get("distance"),
        "duration_s": summary.get("duration"),
        "moving_s": summary.get("movingDuration"),
        "elapsed_s": summary.get("elapsedDuration"),
        "avg_speed": summary.get("averageSpeed"),
        "max_speed": summary.get("maxSpeed"),
        "gap_speed": summary.get("avgGradeAdjustedSpeed"),
        "avg_hr": summary.get("averageHR"),
        "max_hr": summary.get("maxHR"),
        "min_hr": summary.get("minHR"),
        "recovery_hr": summary.get("recoveryHeartRate"),
        "cadence": summary.get("averageRunCadence"),
        "stride_m": centimeters_to_meters(summary.get("strideLength")),
        "ground_contact_ms": summary.get("groundContactTime"),
        "vertical_oscillation_cm": summary.get("verticalOscillation"),
        "vertical_ratio_pct": summary.get("verticalRatio"),
        "power_w": summary.get("averagePower"),
        "normalized_power_w": summary.get("normalizedPower"),
        "training_load": summary.get("activityTrainingLoad"),
        "aerobic_te": summary.get("trainingEffect"),
        "anaerobic_te": summary.get("anaerobicTrainingEffect"),
        "training_effect_label": summary.get("trainingEffectLabel"),
        "calories": summary.get("calories"),
        "moderate_minutes": summary.get("moderateIntensityMinutes"),
        "vigorous_minutes": summary.get("vigorousIntensityMinutes"),
        "body_battery_impact": summary.get("differenceBodyBattery"),
        "elevation_gain_m": summary.get("elevationGain"),
        "elevation_loss_m": summary.get("elevationLoss"),
        "rpe": None if rpe is None else rpe / 10,
        "feel": summary.get("directWorkoutFeel"),
        "steps": summary.get("steps"),
        "temperature_c": fahrenheit_to_celsius(weather.get("temp")),
        "feels_like_c": fahrenheit_to_celsius(weather.get("apparentTemp")),
        "dew_point_c": fahrenheit_to_celsius(weather.get("dewPoint")),
        "humidity_pct": weather.get("relativeHumidity"),
        "wind_kmh": None if wind_mph is None else round(wind_mph * 1.609, 1),
        "weather": (weather.get("weatherTypeDTO") or {}).get("desc"),
        **{f"z{zone}_s": zones.get(zone, 0.0) for zone in range(1, 6)},
        "has_gps": int(summary.get("startLatitude") is not None),
    }


def lap_rows(activity_dir: Path) -> Iterator[dict[str, Any]]:
    for number, lap in enumerate((read_json(activity_dir / "splits.json") or {}).get("lapDTOs", []), start=1):
        yield {
            "activity_id": activity_dir.name,
            "lap": number,
            "distance_m": lap.get("distance"),
            "duration_s": lap.get("duration"),
            "avg_speed": lap.get("averageSpeed"),
            "gap_speed": lap.get("avgGradeAdjustedSpeed"),
            "avg_hr": lap.get("averageHR"),
            "max_hr": lap.get("maxHR"),
            "cadence": lap.get("averageRunCadence"),
            "stride_m": centimeters_to_meters(lap.get("strideLength")),
            "ground_contact_ms": lap.get("groundContactTime"),
            "vertical_oscillation_cm": lap.get("verticalOscillation"),
            "vertical_ratio_pct": lap.get("verticalRatio"),
            "power_w": lap.get("averagePower"),
            "elevation_gain_m": lap.get("elevationGain"),
            "elevation_loss_m": lap.get("elevationLoss"),
        }


def sample_rows(activity_dir: Path) -> Iterator[dict[str, Any]]:
    details = read_json(activity_dir / "details.json")
    if not details:
        return
    index = {metric["key"]: metric["metricsIndex"] for metric in details.get("metricDescriptors", [])}
    for position, point in enumerate(details.get("activityDetailMetrics") or []):
        values = point["metrics"]
        row = {"activity_id": activity_dir.name, "idx": position}
        for column, key in SAMPLE_METRICS.items():
            row[column] = values[index[key]] if key in index else None
        row["stride_m"] = centimeters_to_meters(row["stride_m"])
        yield row


def exercise_set_rows(activity_dir: Path) -> Iterator[dict[str, Any]]:
    payload = read_json(activity_dir / "exercise_sets.json") or {}
    for position, item in enumerate(payload.get("exerciseSets") or []):
        exercise = (item.get("exercises") or [{}])[0]
        weight = item.get("weight")
        yield {
            "activity_id": activity_dir.name,
            "set_idx": position,
            "set_type": item.get("setType"),
            "category": exercise.get("category"),
            "exercise": exercise.get("name"),
            "reps": item.get("repetitionCount"),
            "weight_kg": None if weight is None else weight / 1000,
            "duration_s": item.get("duration"),
        }


def morning_readiness(entries: list[dict] | None) -> dict:
    if not entries:
        return {}
    morning = [entry for entry in entries if entry.get("inputContext") == config.MORNING_READINESS_CONTEXT]
    return (morning or sorted(entries, key=lambda entry: entry["timestamp"]))[0]


def daily_row(day_dir: Path) -> dict[str, Any]:
    sleep = read_json(day_dir / "sleep.json") or {}
    dto = sleep.get("dailySleepDTO") or {}
    hrv = (read_json(day_dir / "hrv.json") or {}).get("hrvSummary") or {}
    baseline = hrv.get("baseline") or {}
    readiness = morning_readiness(read_json(day_dir / "readiness.json"))
    stats = read_json(day_dir / "stats.json") or {}
    stress_avg = stats.get("averageStressLevel")
    stress_max = stats.get("maxStressLevel")
    return {
        "date": day_dir.name,
        "sleep_score": ((dto.get("sleepScores") or {}).get("overall") or {}).get("value"),
        "sleep_s": dto.get("sleepTimeSeconds"),
        "deep_s": dto.get("deepSleepSeconds"),
        "light_s": dto.get("lightSleepSeconds"),
        "rem_s": dto.get("remSleepSeconds"),
        "awake_s": dto.get("awakeSleepSeconds"),
        "sleep_start_local": local_time(dto.get("sleepStartTimestampGMT")),
        "sleep_end_local": local_time(dto.get("sleepEndTimestampGMT")),
        "sleep_need_min": (dto.get("sleepNeed") or {}).get("actual"),
        "sleep_feedback": dto.get("sleepScoreFeedback"),
        "sleep_respiration": dto.get("averageRespirationValue"),
        "sleep_avg_hr": dto.get("avgHeartRate"),
        "sleep_stress": dto.get("avgSleepStress"),
        "restless_moments": sleep.get("restlessMomentsCount"),
        "resting_hr": sleep.get("restingHeartRate") or stats.get("restingHeartRate"),
        "hrv_last_night": hrv.get("lastNightAvg"),
        "hrv_weekly_avg": hrv.get("weeklyAvg"),
        "hrv_balanced_low": baseline.get("balancedLow"),
        "hrv_balanced_high": baseline.get("balancedUpper"),
        "hrv_status": hrv.get("status"),
        "readiness_score": readiness.get("score"),
        "readiness_level": readiness.get("level"),
        "readiness_feedback": readiness.get("feedbackShort"),
        "readiness_sleep_pct": readiness.get("sleepScoreFactorPercent"),
        "readiness_sleep_history_pct": readiness.get("sleepHistoryFactorPercent"),
        "readiness_recovery_pct": readiness.get("recoveryTimeFactorPercent"),
        "readiness_load_pct": readiness.get("acwrFactorPercent"),
        "readiness_stress_pct": readiness.get("stressHistoryFactorPercent"),
        "readiness_hrv_pct": readiness.get("hrvFactorPercent"),
        "recovery_time_min": readiness.get("recoveryTime"),
        "steps": stats.get("totalSteps"),
        "step_goal": stats.get("dailyStepGoal"),
        "walk_distance_m": stats.get("totalDistanceMeters"),
        "active_kcal": stats.get("activeKilocalories"),
        "total_kcal": stats.get("totalKilocalories"),
        "moderate_minutes": stats.get("moderateIntensityMinutes"),
        "vigorous_minutes": stats.get("vigorousIntensityMinutes"),
        "stress_avg": stress_avg if stress_avg is not None and stress_avg >= 0 else None,
        "stress_max": stress_max if stress_max is not None and stress_max >= 0 else None,
        "stress_rest_s": stats.get("restStressDuration"),
        "stress_low_s": stats.get("lowStressDuration"),
        "stress_medium_s": stats.get("mediumStressDuration"),
        "stress_high_s": stats.get("highStressDuration"),
        "body_battery_high": stats.get("bodyBatteryHighestValue"),
        "body_battery_low": stats.get("bodyBatteryLowestValue"),
        "body_battery_charged": stats.get("bodyBatteryChargedValue"),
        "body_battery_drained": stats.get("bodyBatteryDrainedValue"),
        "spo2_avg": stats.get("averageSpo2"),
        "waking_respiration": stats.get("avgWakingRespirationValue"),
        "sedentary_s": stats.get("sedentarySeconds"),
        "active_s": stats.get("activeSeconds"),
        "highly_active_s": stats.get("highlyActiveSeconds"),
    }


def gmt_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace(".0", "") + "+00:00").timestamp() * 1000)


def sleep_stage_rows(day_dir: Path) -> Iterator[dict[str, Any]]:
    for level in (read_json(day_dir / "sleep.json") or {}).get("sleepLevels") or []:
        yield {
            "date": day_dir.name,
            "start_ms": gmt_ms(level["startGMT"]),
            "end_ms": gmt_ms(level["endGMT"]),
            "stage": SLEEP_LEVELS.get(int(level["activityLevel"]), "awake"),
        }


def sleep_series_rows(day_dir: Path) -> Iterator[dict[str, Any]]:
    sleep = read_json(day_dir / "sleep.json") or {}
    for key, metric in SLEEP_SERIES.items():
        seen = set()
        for point in sleep.get(key) or []:
            if point.get("value") is None or point["startGMT"] in seen:
                continue
            seen.add(point["startGMT"])
            yield {"date": day_dir.name, "metric": metric, "ts_ms": int(point["startGMT"]), "value": point["value"]}


def day_series_rows(day_dir: Path) -> Iterator[dict[str, Any]]:
    heart_rate = read_json(day_dir / "heart_rate.json") or {}
    stress = read_json(day_dir / "stress.json") or {}
    series = {
        "hr": ((point[0], point[1]) for point in heart_rate.get("heartRateValues") or []),
        "stress": ((point[0], point[1]) for point in stress.get("stressValuesArray") or []),
        "body_battery": ((point[0], point[2]) for point in stress.get("bodyBatteryValuesArray") or [] if len(point) > 2),
    }
    for metric, points in series.items():
        seen = set()
        for timestamp, value in points:
            if value is None or timestamp in seen:
                continue
            seen.add(timestamp)
            yield {"date": day_dir.name, "metric": metric, "ts_ms": int(timestamp), "value": value}


def day_step_rows(day_dir: Path) -> Iterator[dict[str, Any]]:
    for bucket in read_json(day_dir / "steps.json") or []:
        if bucket.get("steps") is None:
            continue
        yield {
            "date": day_dir.name,
            "start_ms": gmt_ms(bucket["startGMT"]),
            "end_ms": gmt_ms(bucket["endGMT"]),
            "steps": bucket["steps"],
            "level": bucket.get("primaryActivityLevel"),
        }


def load_daily_rows(raw: Path) -> Iterator[dict[str, Any]]:
    payload = read_json(raw / "ranges" / "training_status_weekly.json") or {}
    report = ((payload.get("weeklyTrainingStatus") or {}).get("payload") or {}).get("reportData") or {}
    for entry in first_value(report) or []:
        acute = entry.get("acuteTrainingLoadDTO") or {}
        yield {
            "date": entry["calendarDate"],
            "acute": acute.get("dailyTrainingLoadAcute"),
            "chronic": acute.get("dailyTrainingLoadChronic"),
            "chronic_min": acute.get("minTrainingLoadChronic"),
            "chronic_max": acute.get("maxTrainingLoadChronic"),
            "acwr": acute.get("dailyAcuteChronicWorkloadRatio"),
            "acwr_status": acute.get("acwrStatus"),
            "training_status": entry.get("trainingStatusFeedbackPhrase"),
        }


def vo2max_rows(raw: Path) -> Iterator[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for entry in read_json(raw / "ranges" / "max_metrics.json") or []:
        generic = entry.get("generic") or {}
        acclimation = entry.get("heatAltitudeAcclimation") or {}
        day = generic.get("calendarDate") or acclimation.get("calendarDate")
        if not day:
            continue
        row = by_date.setdefault(day, {"date": day, "vo2max": None, "heat_acclimation_pct": None})
        row["vo2max"] = generic.get("vo2MaxPreciseValue") or row["vo2max"]
        row["heat_acclimation_pct"] = acclimation.get("heatAcclimationPercentage", row["heat_acclimation_pct"])
    yield from sorted(by_date.values(), key=lambda row: row["date"])


def race_prediction_rows(raw: Path) -> Iterator[dict[str, Any]]:
    payload = read_json(raw / "ranges" / "race_predictions.json")
    entries = payload if isinstance(payload, list) else [payload] if payload else []
    for entry in entries:
        for key, distance in RACE_DISTANCES.items():
            if entry.get(key):
                yield {"date": entry["calendarDate"][:10], "distance": distance, "seconds": entry[key]}


def weekly_intensity_rows(raw: Path) -> Iterator[dict[str, Any]]:
    for entry in read_json(raw / "ranges" / "weekly_intensity.json") or []:
        yield {
            "week": entry["calendarDate"],
            "moderate": entry.get("moderateValue") or 0,
            "vigorous": entry.get("vigorousValue") or 0,
            "goal": entry.get("weeklyGoal"),
        }


def record_rows(raw: Path) -> Iterator[dict[str, Any]]:
    for record in read_json(raw / "profile" / "personal_records.json") or []:
        when = record.get("activityStartDateTimeLocalFormatted") or record.get("prStartTimeLocalFormatted") or ""
        yield {
            "type_id": record["typeId"],
            "value": record["value"],
            "activity_id": str(record["activityId"]) if record.get("activityId") else None,
            "date": when[:10] or None,
        }


def hr_zone_rows(raw: Path) -> Iterator[dict[str, Any]]:
    zones = read_json(raw / "profile" / "hr_zones.json") or []
    default = next((zone for zone in zones if zone.get("sport") == "DEFAULT"), zones[0] if zones else None)
    if not default:
        return
    floors = [default.get(f"zone{zone}Floor") for zone in range(1, 6)]
    for zone, floor in enumerate(floors, start=1):
        ceiling = floors[zone] if zone < 5 else default.get("maxHeartRateUsed")
        yield {"zone": zone, "floor_bpm": floor, "ceiling_bpm": ceiling}


def profile_rows(raw: Path) -> Iterator[dict[str, Any]]:
    fitness = read_json(raw / "profile" / "fitness_age.json") or {}
    components = fitness.get("components") or {}
    zones = read_json(raw / "profile" / "hr_zones.json") or [{}]
    devices = read_json(raw / "profile" / "devices.json") or [{}]
    values = {
        "fitness_age": fitness.get("fitnessAge"),
        "achievable_fitness_age": fitness.get("achievableFitnessAge"),
        "chronological_age": fitness.get("chronologicalAge"),
        "vigorous_days_per_week": (components.get("vigorousDaysAvg") or {}).get("value"),
        "vigorous_days_target": (components.get("vigorousDaysAvg") or {}).get("targetValue"),
        "vigorous_minutes_per_week": (components.get("vigorousMinutesAvg") or {}).get("value"),
        "vigorous_minutes_target": (components.get("vigorousMinutesAvg") or {}).get("targetValue"),
        "max_hr": zones[0].get("maxHeartRateUsed"),
        "lactate_threshold_hr": zones[0].get("lactateThresholdHeartRateUsed"),
        "resting_hr_used": zones[0].get("restingHeartRateUsed"),
        "device": devices[0].get("productDisplayName") if devices else None,
    }
    for key, value in values.items():
        yield {"key": key, "value": None if value is None else json.dumps(value)}


def load_focus_rows(raw: Path) -> Iterator[dict[str, Any]]:
    status = read_json(raw / "profile" / "training_status.json") or {}
    balance = first_value((status.get("mostRecentTrainingLoadBalance") or {}).get("metricsTrainingLoadBalanceDTOMap")) or {}
    for focus, prefix in (("aerobic_low", "monthlyLoadAerobicLow"), ("aerobic_high", "monthlyLoadAerobicHigh"), ("anaerobic", "monthlyLoadAnaerobic")):
        if prefix in balance:
            yield {
                "focus": focus,
                "load": balance.get(prefix),
                "target_min": balance.get(f"{prefix}TargetMin"),
                "target_max": balance.get(f"{prefix}TargetMax"),
                "as_of": balance.get("calendarDate"),
            }


def gear_rows(raw: Path) -> Iterator[dict[str, Any]]:
    for item in read_json(raw / "profile" / "gear.json") or []:
        yield {
            "gear_id": item.get("uuid"),
            "name": item.get("displayName") or item.get("customMakeModel"),
            "gear_type": item.get("gearTypeName"),
            "distance_m": item.get("totalDistance") or item.get("distance"),
            "max_distance_m": item.get("maximumMeters"),
            "status": item.get("gearStatusName"),
        }


def insert(connection: sqlite3.Connection, table: str, rows: Iterable[dict[str, Any]]) -> int:
    rows = list(rows)
    if not rows:
        return 0
    columns = list(rows[0])
    placeholders = ", ".join("?" for _ in columns)
    connection.executemany(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [tuple(row[column] for column in columns) for row in rows],
    )
    return len(rows)


def activity_dirs(raw: Path) -> list[Path]:
    root = raw / "activities"
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "summary.json").exists()) if root.exists() else []


def day_dirs(raw: Path) -> list[Path]:
    root = raw / "daily"
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and path.name >= str(config.HISTORY_START))


def build_database(raw: Path, db_path: Path) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    partial = db_path.with_name(db_path.name + ".part")
    partial.unlink(missing_ok=True)
    connection = sqlite3.connect(partial)
    try:
        connection.executescript(SCHEMA.read_text())
        activities = activity_dirs(raw)
        days = day_dirs(raw)
        counts = {
            "activities": insert(connection, "activities", (activity_row(path) for path in activities)),
            "laps": insert(connection, "laps", (row for path in activities for row in lap_rows(path))),
            "samples": insert(connection, "samples", (row for path in activities for row in sample_rows(path))),
            "exercise_sets": insert(connection, "exercise_sets", (row for path in activities for row in exercise_set_rows(path))),
            "daily": insert(connection, "daily", (daily_row(path) for path in days)),
            "sleep_stages": insert(connection, "sleep_stages", (row for path in days for row in sleep_stage_rows(path))),
            "sleep_series": insert(connection, "sleep_series", (row for path in days for row in sleep_series_rows(path))),
            "day_series": insert(connection, "day_series", (row for path in days for row in day_series_rows(path))),
            "day_steps": insert(connection, "day_steps", (row for path in days for row in day_step_rows(path))),
            "load_daily": insert(connection, "load_daily", load_daily_rows(raw)),
            "vo2max": insert(connection, "vo2max", vo2max_rows(raw)),
            "race_predictions": insert(connection, "race_predictions", race_prediction_rows(raw)),
            "weekly_intensity": insert(connection, "weekly_intensity", weekly_intensity_rows(raw)),
            "records": insert(connection, "records", record_rows(raw)),
            "hr_zones": insert(connection, "hr_zones", hr_zone_rows(raw)),
            "profile": insert(connection, "profile", profile_rows(raw)),
            "load_focus": insert(connection, "load_focus", load_focus_rows(raw)),
            "gear": insert(connection, "gear", gear_rows(raw)),
        }
        connection.commit()
    finally:
        connection.close()
    partial.replace(db_path)
    return counts
