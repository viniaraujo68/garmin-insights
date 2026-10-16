from typing import Literal

from pydantic import BaseModel, ConfigDict

Status = Literal["good", "typical", "attention", "bad", "unknown"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Meta(Contract):
    generated_at: str
    today: str
    first_day: str | None
    last_day: str | None
    last_activity_date: str | None
    activity_count: int
    device: str | None


class ActivitySummary(Contract):
    activity_id: str
    date: str
    start_local: str
    sport: str
    type_key: str
    name: str | None
    distance_km: float | None
    duration_min: float | None
    pace_s_km: int | None
    gap_pace_s_km: int | None
    heat_adjusted_pace_s_km: int | None
    heat_slowdown_pct: float | None
    avg_hr: float | None
    max_hr: float | None
    recovery_hr: float | None
    meters_per_beat: float | None
    cadence: float | None
    stride_m: float | None
    ground_contact_ms: float | None
    vertical_oscillation_cm: float | None
    vertical_ratio_pct: float | None
    power_w: float | None
    elevation_gain_m: float | None
    performance_condition: float | None
    training_load: float | None
    aerobic_te: float | None
    anaerobic_te: float | None
    training_effect_label: str | None
    zone_minutes: list[float]
    temperature_c: float | None
    feels_like_c: float | None
    dew_point_c: float | None
    humidity_pct: float | None
    rpe: float | None
    feel: float | None
    body_battery_impact: float | None
    has_gps: bool


class Lap(Contract):
    lap: int
    distance_m: float | None
    duration_s: float | None
    pace_s_km: int | None
    gap_pace_s_km: int | None
    avg_hr: float | None
    max_hr: float | None
    cadence: float | None
    stride_m: float | None
    ground_contact_ms: float | None
    power_w: float | None
    elevation_gain_m: float | None
    elevation_loss_m: float | None


class ZoneTime(Contract):
    zone: int
    floor_bpm: float | None
    ceiling_bpm: float | None
    seconds: float


class Streams(Contract):
    elapsed_s: list[float | None]
    distance_m: list[float | None]
    lat: list[float | None]
    lon: list[float | None]
    pace_s_km: list[float | None]
    gap_pace_s_km: list[float | None]
    hr: list[float | None]
    cadence: list[float | None]
    power: list[float | None]
    elevation: list[float | None]
    grade_pct: list[float | None]
    performance_condition: list[float | None]


class Weather(Contract):
    temperature_c: float | None
    feels_like_c: float | None
    dew_point_c: float | None
    humidity_pct: float | None
    wind_kmh: float | None
    description: str | None


class ActivityDetail(Contract):
    summary: ActivitySummary
    laps: list[Lap]
    zones: list[ZoneTime]
    streams: Streams
    weather: Weather


class ReadinessFactor(Contract):
    key: str
    label: str
    pct: float


class Readiness(Contract):
    date: str
    score: float
    level: str | None
    feedback: str | None
    recovery_time_h: float | None
    factors: list[ReadinessFactor]


class SparkPoint(Contract):
    date: str
    value: float | None


class BaselineTile(Contract):
    key: str
    label: str
    value: float | None
    display: str
    baseline_label: str
    delta_display: str
    status: Status
    status_label: str
    band_low: float | None
    band_high: float | None
    spark: list[SparkPoint]


class IllnessSignal(Contract):
    key: str
    label: str
    unit: str
    value: float | None
    median: float | None
    z: float | None
    flagged: bool


class IllnessWatch(Contract):
    status: Literal["ok", "watch", "alert", "insufficient"]
    message: str
    reference_nights: int
    signals: list[IllnessSignal]


class WeekActivity(Contract):
    activity_id: str
    sport: str
    distance_km: float | None
    duration_min: float | None
    training_load: float | None


class WeekDay(Contract):
    date: str
    activities: list[WeekActivity]


class Signal(Contract):
    key: str
    label: str
    display: str
    detail: str
    status: Status


class Today(Contract):
    date: str
    readiness: Readiness | None
    training_status: str | None
    tiles: list[BaselineTile]
    illness: IllnessWatch
    week: list[WeekDay]
    signals: list[Signal]
    last_activity_id: str | None


class Privacy(Contract):
    lat: float
    lon: float
    radius_m: float


class RouteTrace(Contract):
    activity_id: str
    date: str
    distance_km: float | None
    pace_s_km: int | None
    points: list[list[float | None]]


class Routes(Contract):
    privacy: Privacy | None
    routes: list[RouteTrace]


class SeriesPoint(Contract):
    date: str
    value: float


class TrendLine(Contract):
    start_date: str
    end_date: str
    start_value: float
    end_value: float
    per_30_days: float


class EfficiencyPoint(Contract):
    activity_id: str
    date: str
    distance_km: float | None
    pace_s_km: int | None
    heat_adjusted_pace_s_km: int | None
    avg_hr: float | None
    meters_per_beat: float
    heat_adjusted_meters_per_beat: float | None
    feels_like_c: float | None
    heat_slowdown_pct: float | None


class RaceDistance(Contract):
    distance: str
    label: str
    km: float
    current_seconds: float
    delta_8w_seconds: float | None
    series: list[SeriesPoint]
    projection: list[SeriesPoint] | None
    record_seconds: float | None
    riegel_seconds: float | None


class FormPoint(Contract):
    date: str
    speed_kmh: float
    value: float
    recent: bool


class FormMetric(Contract):
    key: str
    label: str
    unit: str
    digits: int
    lower_is_better: bool | None
    recent_delta: float | None
    recent_count: int
    earlier_count: int
    verdict: str
    fit_slope: float | None
    fit_intercept: float | None
    points: list[FormPoint]


class RecordRow(Contract):
    type_id: int
    label: str
    value: float
    value_display: str
    date: str | None
    activity_id: str | None


class FitnessAge(Contract):
    fitness_age: float | None
    chronological_age: float | None
    achievable_age: float | None
    vigorous_days_per_week: float | None
    vigorous_days_target: float | None
    vigorous_minutes_per_week: float | None
    vigorous_minutes_target: float | None


class Performance(Contract):
    efficiency: list[EfficiencyPoint]
    efficiency_trend: TrendLine | None
    heat_adjusted_trend: TrendLine | None
    vo2max: list[SeriesPoint]
    vo2max_per_30_days: float | None
    vo2max_projection: list[SeriesPoint] | None
    projection_note: str
    races: list[RaceDistance]
    form_window_days: int
    form: list[FormMetric]
    records: list[RecordRow]
    fitness_age: FitnessAge | None


class LoadDay(Contract):
    date: str
    daily_load: float
    acute: float | None
    chronic: float | None
    chronic_min: float | None
    chronic_max: float | None
    acwr: float | None
    fitness: float
    fatigue: float
    form: float


class WeekLoad(Contract):
    week: str
    km: float
    runs: int
    minutes_run: float
    minutes_football: float
    minutes_gym: float
    minutes_other: float
    load: float
    easy_min: float
    moderate_min: float
    hard_min: float
    easy_pct: float | None
    verdict: str | None
    monotony: float | None
    strain: float | None


class FocusRow(Contract):
    focus: str
    label: str
    load: float | None
    target_min: float | None
    target_max: float | None
    status: Status


class CalendarDay(Contract):
    date: str
    load: float
    sports: list[str]


class Load(Contract):
    days: list[LoadDay]
    weeks: list[WeekLoad]
    focus: list[FocusRow]
    calendar: list[CalendarDay]


DOCUMENTS: dict[str, type[Contract]] = {
    "meta": Meta,
    "activities": ActivitySummary,
    "activity": ActivityDetail,
    "today": Today,
    "routes": Routes,
    "performance": Performance,
    "load": Load,
}
