import sqlite3

from builders import make_raw

from passada.store.loader import build_database


def query(db_path, sql):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(sql).fetchall()
    finally:
        connection.close()


def test_build_database_loads_activity_with_converted_units(tmp_path):
    db_path = tmp_path / "passada.db"
    counts = build_database(make_raw(tmp_path), db_path)
    assert counts["activities"] == 1 and counts["laps"] == 1 and counts["samples"] == 3
    activity = query(db_path, "SELECT * FROM activities")[0]
    assert activity["sport"] == "run"
    assert activity["stride_m"] == 1.18
    assert activity["temperature_c"] == 25.0
    assert activity["rpe"] == 2.0
    assert activity["z2_s"] == 900.0 and activity["z5_s"] == 0.0


def test_daily_row_uses_the_morning_readiness_and_drops_negative_stress(tmp_path):
    db_path = tmp_path / "passada.db"
    build_database(make_raw(tmp_path), db_path)
    day = query(db_path, "SELECT * FROM daily")[0]
    assert day["readiness_score"] == 45
    assert day["stress_avg"] is None
    assert day["hrv_balanced_low"] == 61


def test_sleep_series_drops_duplicate_timestamps(tmp_path):
    db_path = tmp_path / "passada.db"
    build_database(make_raw(tmp_path), db_path)
    assert len(query(db_path, "SELECT * FROM sleep_series WHERE metric = 'hr'")) == 1
    assert query(db_path, "SELECT stage FROM sleep_stages")[0]["stage"] == "light"


def test_rebuild_replaces_the_previous_database(tmp_path):
    db_path = tmp_path / "passada.db"
    raw = make_raw(tmp_path)
    build_database(raw, db_path)
    build_database(raw, db_path)
    assert len(query(db_path, "SELECT * FROM activities")) == 1
    assert not (tmp_path / "passada.db.part").exists()
