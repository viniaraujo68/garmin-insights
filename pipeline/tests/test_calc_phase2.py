from datetime import date, timedelta

import pytest

from garmin_insights.calc.load import easy_line, load_verdict, verdict, weeks_of
from garmin_insights.calc.performance import form_metrics, riegel
from garmin_insights.calc.trend import projection, theil_sen
from garmin_insights.publish.contract import ActivitySummary, LoadDay


def summary(day: str, **values) -> ActivitySummary:
    base = dict(
        activity_id=day.replace("-", ""), date=day, start_local=f"{day}T20:00:00.0", sport="run", type_key="running",
        name=None, distance_km=5.0, duration_min=30.0, pace_s_km=330, gap_pace_s_km=330, heat_adjusted_pace_s_km=320,
        heat_slowdown_pct=3.0, avg_hr=140.0, max_hr=160.0, recovery_hr=None, meters_per_beat=1.3, cadence=160.0,
        stride_m=1.1, ground_contact_ms=270.0, vertical_oscillation_cm=10.0, vertical_ratio_pct=9.0, power_w=280.0,
        elevation_gain_m=5.0, performance_condition=0.0, training_load=50.0, aerobic_te=3.0, anaerobic_te=0.0,
        training_effect_label="AEROBIC_BASE", zone_minutes=[0.0, 24.0, 6.0, 0.0, 0.0], temperature_c=24.0,
        feels_like_c=25.0, dew_point_c=20.0, humidity_pct=80.0, rpe=3.0, feel=75.0, body_battery_impact=-8.0, has_gps=True,
    )
    base.update(values)
    return ActivitySummary(**base)


def test_theil_sen_ignores_a_single_outlier():
    slope, intercept = theil_sen([0, 1, 2, 3, 4], [0, 1, 2, 30, 4])
    assert slope == pytest.approx(1.0)
    assert intercept == pytest.approx(0.0)


def test_projection_needs_eight_weeks_of_history():
    start = date(2026, 8, 1)
    short = [(str(start + timedelta(days=7 * week)), 50 + week) for week in range(7)]
    long = [(str(start + timedelta(days=7 * week)), 50 + week) for week in range(9)]
    assert projection(short, (30,)) is None
    projected = projection(long, (30,))
    assert projected is not None and projected[1][1] > projected[0][1]


def test_riegel_scales_time_with_distance():
    assert riegel(1500, 5, 10) == pytest.approx(1500 * 2 ** 1.06)


def test_week_verdict_follows_the_easy_share():
    assert (verdict(None), verdict(50), verdict(80), verdict(95)) == (None, "intenso demais", "equilibrado", "leve demais")


def test_weeks_split_minutes_by_sport_and_intensity():
    runs = [summary("2026-10-13"), summary("2026-10-14", sport="football", distance_km=None, zone_minutes=[0, 10, 10, 20, 5])]
    loads = {"2026-10-13": 50.0, "2026-10-14": 50.0}
    week = weeks_of(runs, loads, date(2026, 10, 13), date(2026, 10, 14))[0]
    assert (week.km, week.runs, week.minutes_football) == (5.0, 1, 30)
    assert (week.easy_min, week.moderate_min, week.hard_min) == (34, 16, 25)


def test_form_compares_recent_runs_at_the_same_pace():
    today = date(2026, 10, 15)
    earlier = [summary(str(today - timedelta(days=60 + n)), pace_s_km=330 - n * 5, ground_contact_ms=280.0) for n in range(3)]
    recent = [summary(str(today - timedelta(days=5 + n)), pace_s_km=330 - n * 5, ground_contact_ms=270.0) for n in range(3)]
    contact = next(metric for metric in form_metrics(earlier + recent, today) if metric.key == "ground_contact_ms")
    assert contact.recent_delta == pytest.approx(-10.0)
    assert contact.verdict.endswith("melhorou.")
    cadence = next(metric for metric in form_metrics(earlier + recent, today) if metric.key == "cadence")
    assert "melhorou" not in cadence.verdict and "piorou" not in cadence.verdict


def test_form_adjusts_each_run_to_the_reference_speed():
    today = date(2026, 10, 15)
    runs = [summary(str(today - timedelta(days=n)), pace_s_km=pace, cadence=cadence) for n, (pace, cadence) in enumerate([(400, 150.0), (360, 155.0), (300, 165.0)])]
    cadence = next(metric for metric in form_metrics(runs, today) if metric.key == "cadence")
    assert cadence.reference_speed_kmh == 10.0
    assert [point.adjusted for point in cadence.points] == pytest.approx([155.0, 155.0, 155.0], abs=0.1)
    assert [point.date for point in cadence.points] == sorted(point.date for point in cadence.points)
    assert cadence.lower_is_better is False


def load_day(acute: float | None, low: float | None = 100.0, high: float | None = 200.0) -> LoadDay:
    return LoadDay(date="2026-10-15", daily_load=0.0, acute=acute, chronic=150.0, chronic_min=low, chronic_max=high, acwr=None, fitness=0.0, fatigue=0.0, form=0.0)


def test_load_verdict_counts_typical_runs_to_reach_the_band():
    status, headline, detail = load_verdict([load_day(40.0)], typical=25.0)
    assert status == "attention" and "menos" in headline
    assert "Cerca de 3 corridas" in detail
    assert load_verdict([load_day(150.0)], typical=25.0)[0] == "good"
    assert load_verdict([load_day(260.0)], typical=25.0)[0] == "bad"
    assert load_verdict([load_day(None)], typical=25.0)[0] == "unknown"


def test_easy_line_sums_the_last_four_calendar_weeks():
    runs = [
        summary("2026-09-01", zone_minutes=[0.0, 0.0, 0.0, 40.0, 0.0]),
        summary("2026-10-06", zone_minutes=[0.0, 30.0, 10.0, 0.0, 0.0]),
        summary("2026-10-13", zone_minutes=[0.0, 30.0, 10.0, 0.0, 0.0]),
    ]
    weeks = weeks_of(runs, {}, date(2026, 8, 31), date(2026, 10, 14))
    line = easy_line(weeks)
    assert line is not None and line.startswith("Nas últimas 4 semanas, 75%")

