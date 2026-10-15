from pydantic import BaseModel, ConfigDict


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
    avg_hr: float | None
    max_hr: float | None
    meters_per_beat: float | None
    training_load: float | None
    aerobic_te: float | None
    anaerobic_te: float | None
    training_effect_label: str | None
    feels_like_c: float | None
    dew_point_c: float | None
    humidity_pct: float | None
    rpe: float | None
    has_gps: bool


DOCUMENTS: dict[str, type[Contract]] = {
    "meta": Meta,
    "activities": ActivitySummary,
}
