from datetime import date, timedelta

import pytest

from passada.calc.activities import distance_m, grades, home_privacy
from passada.calc.heat import heat_adjusted_pace, heat_slowdown_pct
from passada.calc.stats import robust_z
from passada.calc.today import illness_watch


def test_heat_slowdown_follows_the_hadley_table():
    assert heat_slowdown_pct(10.0, 5.0) == 0.0
    assert heat_slowdown_pct(25.0, 22.8) == pytest.approx(4.5, abs=0.05)
    assert heat_adjusted_pace(314, 4.5) == 300


def test_heat_slowdown_needs_both_temperature_and_dew_point():
    assert heat_slowdown_pct(25.0, None) is None
    assert heat_adjusted_pace(314, None) is None


def test_robust_z_uses_the_minimum_spread_when_values_are_constant():
    assert robust_z(16, [14] * 20) is None
    assert robust_z(16, [14] * 20, minimum_spread=0.5) == 4


def make_days(today: date, overrides: dict[str, float]) -> dict:
    days = {}
    for back in range(0, 31):
        day = str(today - timedelta(days=back))
        row = {"date": day, "resting_hr": 48.0 + back % 2, "hrv_last_night": 65.0 + back % 5, "sleep_respiration": 14.0}
        if back == 0:
            row.update(overrides)
        days[day] = row
    return days


def test_illness_watch_alerts_only_when_two_signals_agree():
    today = date(2026, 10, 15)
    calm = illness_watch(make_days(today, {}), today)
    single = illness_watch(make_days(today, {"hrv_last_night": 40.0}), today)
    double = illness_watch(make_days(today, {"hrv_last_night": 40.0, "resting_hr": 56.0}), today)
    assert (calm.status, single.status, double.status) == ("ok", "watch", "alert")


def test_illness_watch_needs_enough_reference_nights():
    today = date(2026, 10, 15)
    days = {key: value for key, value in make_days(today, {}).items() if key >= str(today - timedelta(days=8))}
    assert illness_watch(days, today).status == "insufficient"


def test_grades_use_a_trailing_distance_window():
    distances = [0, 25, 50, 75, 100]
    elevations = [10, 10.5, 11, 11.5, 12]
    assert grades(distances, elevations) == [None, 2.0, 2.0, 2.0, 2.0]


class Point(dict):
    pass


def track(lat: float, lon: float) -> list[Point]:
    return [Point(lat=lat, lon=lon), Point(lat=lat + 0.01, lon=lon), Point(lat=lat + 0.0001, lon=lon)]


def test_home_privacy_finds_the_place_most_runs_start_and_end():
    tracks = [track(-22.9674, -43.2038) for _ in range(3)] + [track(-22.90, -43.10)]
    privacy = home_privacy(tracks)
    assert privacy is not None
    assert distance_m((privacy.lat, privacy.lon), (-22.9674, -43.2038)) < 50


def test_home_privacy_needs_repeated_visits():
    assert home_privacy([track(-22.9, -43.2)]) is None
