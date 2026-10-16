import json

from garminconnect import GarminConnectTooManyRequestsError

from garmin_insights.collect.client import RawStore


def make_store(tmp_path):
    waits = []
    return RawStore(tmp_path, pause_seconds=0, retry_wait_seconds=5, max_attempts=3, sleep=waits.append), waits


def test_fetch_caches_and_skips_the_call_next_time(tmp_path):
    store, _ = make_store(tmp_path)
    calls = []
    store.fetch("a/b.json", lambda: calls.append(1) or {"v": 1})
    store.fetch("a/b.json", lambda: calls.append(1) or {"v": 2})
    assert calls == [1]
    assert json.loads((tmp_path / "a/b.json").read_text()) == {"v": 1}
    assert store.counters == {"fetched": 1, "cached": 1, "failed": 0}


def test_refresh_overwrites_the_cached_copy(tmp_path):
    store, _ = make_store(tmp_path)
    store.fetch("x.json", lambda: {"v": 1})
    assert store.fetch("x.json", lambda: {"v": 2}, refresh=True) == {"v": 2}


def test_rate_limit_waits_and_retries(tmp_path):
    store, waits = make_store(tmp_path)
    attempts = iter([GarminConnectTooManyRequestsError("429"), {"ok": True}])

    def call():
        outcome = next(attempts)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    assert store.fetch("r.json", call) == {"ok": True}
    assert 5 in waits


def test_failed_refresh_keeps_the_previous_copy_and_counts_the_failure(tmp_path):
    store, _ = make_store(tmp_path)
    store.fetch("k.json", lambda: {"v": 1})

    def broken():
        raise RuntimeError("boom")

    assert store.fetch("k.json", broken, refresh=True) == {"v": 1}
    assert json.loads((tmp_path / "k.json").read_text()) == {"v": 1}
    assert store.counters["failed"] == 1
    assert not list(tmp_path.glob("*.part"))
