import json
from datetime import date

import pytest
from builders import make_raw
from pydantic import ValidationError

from passada.publish.site import publish_site, verify_site
from passada.store.loader import build_database


@pytest.fixture
def site(tmp_path):
    db_path = tmp_path / "passada.db"
    build_database(make_raw(tmp_path), db_path)
    site_dir = tmp_path / "site"
    publish_site(db_path, site_dir, date(2026, 10, 15))
    return site_dir


def test_publish_writes_valid_documents(site):
    meta = json.loads((site / "meta.json").read_text())
    activities = json.loads((site / "activities.json").read_text())
    assert meta["activity_count"] == len(activities) == 1
    assert activities[0]["pace_s_km"] == 312
    assert (site / "schema.json").exists()
    verify_site(site)


def test_verify_rejects_an_unexpected_field(site):
    activities = json.loads((site / "activities.json").read_text())
    activities[0]["surprise"] = 1
    (site / "activities.json").write_text(json.dumps(activities))
    with pytest.raises(ValidationError):
        verify_site(site)


def test_verify_rejects_a_count_mismatch(site):
    meta = json.loads((site / "meta.json").read_text())
    meta["activity_count"] = 7
    (site / "meta.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError):
        verify_site(site)


def test_each_day_gets_a_briefing_that_ignores_later_activities(tmp_path):
    from builders import write

    raw = make_raw(tmp_path)
    write(raw / "daily/2026-10-12/stats.json", {"totalSteps": 4000, "dailyStepGoal": 5000})
    db_path = tmp_path / "passada.db"
    build_database(raw, db_path)
    site_dir = tmp_path / "site"
    publish_site(db_path, site_dir, date(2026, 10, 15))
    meta = json.loads((site_dir / "meta.json").read_text())
    assert meta["days"] == ["2026-10-12", "2026-10-13"]
    before = json.loads((site_dir / "day" / "2026-10-12.json").read_text())
    after = json.loads((site_dir / "day" / "2026-10-13.json").read_text())
    assert before["last_activity_id"] is None
    assert after["last_activity_id"] == "1001"


def test_intraday_breaks_stress_at_motion_and_marks_spans(site):
    intraday = json.loads((site / "intraday" / "2026-10-13.json").read_text())
    assert [point["value"] for point in intraday["stress"]] == [30, None, None, None, 40]
    motion = [span for span in intraday["spans"] if span["kind"] == "motion"]
    assert len(motion) == 1 and motion[0]["end_ms"] - motion[0]["start_ms"] == 2 * 180_000
    activity = [span for span in intraday["spans"] if span["kind"] == "activity"]
    assert activity[0]["activity_id"] == "1001"
    assert activity[0]["end_ms"] - activity[0]["start_ms"] == round((5000 / 3.2 + 600) * 1000)
    assert intraday["steps"][0]["steps"] == 120
    assert intraday["end_ms"] - intraday["start_ms"] == 86_400_000
    assert intraday["last_sample_ms"] == 1791861120000
