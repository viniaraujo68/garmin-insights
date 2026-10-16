import json
from pathlib import Path
from typing import Any


def write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def run_summary(start_local: str = "2026-10-13T20:30:05.0", distance: float = 5000.0, speed: float = 3.2, hr: float = 130.0) -> dict:
    return {
        "activityName": "Easy run",
        "activityTypeDTO": {"typeKey": "running"},
        "summaryDTO": {
            "startTimeLocal": start_local,
            "startLatitude": -22.97,
            "distance": distance,
            "duration": distance / speed,
            "movingDuration": distance / speed,
            "elapsedDuration": distance / speed + 600,
            "averageSpeed": speed,
            "avgGradeAdjustedSpeed": speed,
            "averageHR": hr,
            "maxHR": hr + 30,
            "averageRunCadence": 161.0,
            "strideLength": 118.0,
            "groundContactTime": 268.0,
            "verticalOscillation": 10.2,
            "verticalRatio": 8.8,
            "averagePower": 280.0,
            "activityTrainingLoad": 40.0,
            "trainingEffect": 2.4,
            "anaerobicTrainingEffect": 0.0,
            "trainingEffectLabel": "RECOVERY",
            "directWorkoutRpe": 20,
        },
    }


def details(points: list[tuple[float, float, float, float]]) -> dict:
    keys = ["sumElapsedDuration", "sumDistance", "directLatitude", "directLongitude", "directSpeed", "directHeartRate"]
    return {
        "metricDescriptors": [{"key": key, "metricsIndex": index} for index, key in enumerate(keys)],
        "activityDetailMetrics": [
            {"metrics": [elapsed, distance, -22.97 + distance / 1e5, -43.2, 3.2, hr]}
            for elapsed, distance, _, hr in points
        ],
    }


def sleep_day(score: int = 80, levels: list[tuple[str, str, float]] | None = None) -> dict:
    return {
        "dailySleepDTO": {
            "sleepTimeSeconds": 25200,
            "deepSleepSeconds": 5400,
            "lightSleepSeconds": 14400,
            "remSleepSeconds": 4800,
            "awakeSleepSeconds": 600,
            "sleepScores": {"overall": {"value": score}},
            "averageRespirationValue": 14.0,
        },
        "restingHeartRate": 50,
        "sleepLevels": [{"startGMT": start, "endGMT": end, "activityLevel": level} for start, end, level in levels or []],
        "sleepHeartRate": [{"value": 55, "startGMT": 1791871440000}, {"value": 55, "startGMT": 1791871440000}],
    }


def make_raw(root: Path) -> Path:
    raw = root / "raw"
    write(raw / "activities/1001/summary.json", run_summary())
    write(raw / "activities/1001/hr_zones.json", [{"zoneNumber": 2, "secsInZone": 900.0}, {"zoneNumber": 3, "secsInZone": 300.0}])
    write(raw / "activities/1001/weather.json", {"temp": 77, "apparentTemp": 80, "dewPoint": 73, "relativeHumidity": 89, "windSpeed": 10})
    write(raw / "activities/1001/splits.json", {"lapDTOs": [{"distance": 1000.0, "averageSpeed": 3.2, "averageHR": 120, "strideLength": 117.0}]})
    write(raw / "activities/1001/details.json", details([(0, 0, 0, 100), (60, 190, 0, 120), (120, 380, 0, 130)]))
    write(raw / "daily/2026-10-13/sleep.json", sleep_day(levels=[("2026-10-13T06:04:37.0", "2026-10-13T06:14:37.0", 1.0)]))
    write(raw / "daily/2026-10-13/hrv.json", {"hrvSummary": {"lastNightAvg": 58, "weeklyAvg": 68, "status": "BALANCED", "baseline": {"balancedLow": 61, "balancedUpper": 78}}})
    write(raw / "daily/2026-10-13/readiness.json", [
        {"timestamp": "2026-10-13T22:00:00.0", "inputContext": "UPDATE_REALTIME_VARIABLES", "score": 30},
        {"timestamp": "2026-10-13T06:30:00.0", "inputContext": "AFTER_WAKEUP_RESET", "score": 45, "level": "LOW"},
    ])
    write(raw / "daily/2026-10-13/stats.json", {"totalSteps": 6972, "dailyStepGoal": 4870, "averageStressLevel": -1})
    write(raw / "daily/2026-10-13/heart_rate.json", {"heartRateValues": [[1791860400000, 62], [1791860520000, None], [1791860520000, 64]]})
    write(raw / "daily/2026-10-13/stress.json", {
        "stressValuesArray": [[1791860400000, 30], [1791860580000, -1], [1791860760000, -2], [1791860940000, -2], [1791861120000, 40]],
        "bodyBatteryValuesArray": [[1791860400000, "MEASURED", 55, 3.0], [1791860580000, "MEASURED", None, 3.0]],
    })
    write(raw / "daily/2026-10-13/steps.json", [
        {"startGMT": "2026-10-13T03:00:00.0", "endGMT": "2026-10-13T03:15:00.0", "steps": 120, "primaryActivityLevel": "sedentary"},
    ])
    return raw
