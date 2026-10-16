from datetime import date

from garmin_insights import config
from garmin_insights.collect.client import RawStore
from garmin_insights.collect.sync import refresh_window_start


def test_window_starts_at_history_start_on_first_sync(tmp_path):
    assert refresh_window_start(RawStore(tmp_path), date(2026, 10, 15)) == config.HISTORY_START


def test_window_reaches_back_lookback_days_from_the_last_synced_day(tmp_path):
    (tmp_path / "daily/2026-10-10").mkdir(parents=True)
    (tmp_path / "daily/2026-09-01").mkdir(parents=True)
    start = refresh_window_start(RawStore(tmp_path), date(2026, 10, 15))
    assert start == date(2026, 10, 10 - config.LOOKBACK_DAYS)
