import sqlite3
from datetime import date

from builders import details, run_summary, write

from passada.calc.recovery import glance_status, minutes_of
from passada.calc.sports import epley, sprint_stats
from passada.publish.site import publish_site
from passada.store.loader import build_database


class Row(dict):
    pass


def test_sprints_need_two_consecutive_fast_samples():
    speeds = [3.0, 5.5, 3.0, 5.5, 6.0, 6.2, 3.0, 4.5, 4.5]
    rows = [Row(speed=speed, distance_m=index * 5.0) for index, speed in enumerate(speeds)]
    max_speed, sprints, high_speed = sprint_stats(rows)
    assert max_speed == round(6.2 * 3.6, 1)
    assert sprints == 1
    assert high_speed == 30


def test_epley_estimates_one_rep_max():
    assert epley(60, 10) == 80.0
    assert epley(None, 10) is None


def test_bedtime_minutes_and_glance_status():
    assert minutes_of("2026-10-15T02:44-03:00") == 164
    assert glance_status(2.5, higher_is_better=False) == "bad"
    assert glance_status(1.2, higher_is_better=True) == "good"
    assert glance_status(None, higher_is_better=True) == "unknown"


def make_sports_raw(root):
    raw = root / "raw"
    football = run_summary("2026-10-14T19:00:00.0", distance=6000, speed=1.8, hr=150)
    football["activityTypeDTO"]["typeKey"] = "soccer"
    write(raw / "activities/2001/summary.json", football)
    write(raw / "activities/2001/details.json", details([(0, 0, 0, 120), (1, 6, 0, 170), (2, 12, 0, 172)]))
    gym = run_summary("2026-10-13T08:00:00.0", distance=0, speed=1, hr=110)
    gym["activityTypeDTO"]["typeKey"] = "strength_training"
    gym["summaryDTO"]["distance"] = None
    write(raw / "activities/2002/summary.json", gym)
    write(raw / "activities/2002/exercise_sets.json", {"exerciseSets": [
        {"setType": "ACTIVE", "repetitionCount": 10, "weight": 60000, "exercises": [{"category": "BENCH_PRESS", "name": "BARBELL_BENCH_PRESS"}]},
        {"setType": "REST", "duration": 90},
        {"setType": "ACTIVE", "repetitionCount": 8, "weight": 80000, "exercises": [{"category": "SQUAT", "name": "BARBELL_SQUAT"}]},
    ]})
    write(raw / "daily/2026-10-14/sleep.json", {"dailySleepDTO": {"sleepTimeSeconds": 25000}})
    return raw


def test_sports_document_from_raw(tmp_path):
    db_path = tmp_path / "passada.db"
    build_database(make_sports_raw(tmp_path), db_path)
    publish_site(db_path, tmp_path / "site", date(2026, 10, 15))
    import json

    sports = json.loads((tmp_path / "site" / "sports.json").read_text())
    assert [session["activity_id"] for session in sports["football"]] == ["2001"]
    gym = sports["gym"][0]
    assert (gym["sets"], gym["volume_kg"]) == (2, 1240.0)
    muscles = {item["group"]: item for item in sports["muscles"]}
    assert muscles["chest"]["sets_7d"] == 1.0 and muscles["quads"]["sets_7d"] == 1.0 and muscles["triceps"]["sets_7d"] == 0.5
    connection = sqlite3.connect(db_path)
    assert connection.execute("SELECT count(*) FROM exercise_sets").fetchone()[0] == 3
