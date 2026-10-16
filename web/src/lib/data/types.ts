export interface ActivitySummary {
activity_id: string
aerobic_te: (number | null)
anaerobic_te: (number | null)
avg_hr: (number | null)
body_battery_impact: (number | null)
cadence: (number | null)
date: string
dew_point_c: (number | null)
distance_km: (number | null)
duration_min: (number | null)
elevation_gain_m: (number | null)
feel: (number | null)
feels_like_c: (number | null)
gap_pace_s_km: (number | null)
ground_contact_ms: (number | null)
has_gps: boolean
heat_adjusted_pace_s_km: (number | null)
heat_slowdown_pct: (number | null)
humidity_pct: (number | null)
max_hr: (number | null)
meters_per_beat: (number | null)
name: (string | null)
pace_s_km: (number | null)
performance_condition: (number | null)
power_w: (number | null)
recovery_hr: (number | null)
rpe: (number | null)
sport: string
start_local: string
stride_m: (number | null)
temperature_c: (number | null)
training_effect_label: (string | null)
training_load: (number | null)
type_key: string
vertical_oscillation_cm: (number | null)
vertical_ratio_pct: (number | null)
zone_minutes: number[]
}

export interface ActivityDetail {
laps: Lap[]
streams: Streams
summary: ActivitySummary
weather: Weather
zones: ZoneTime[]
}

export interface Lap {
avg_hr: (number | null)
cadence: (number | null)
distance_m: (number | null)
duration_s: (number | null)
elevation_gain_m: (number | null)
elevation_loss_m: (number | null)
gap_pace_s_km: (number | null)
ground_contact_ms: (number | null)
lap: number
max_hr: (number | null)
pace_s_km: (number | null)
power_w: (number | null)
stride_m: (number | null)
}

export interface Streams {
cadence: (number | null)[]
distance_m: (number | null)[]
elapsed_s: (number | null)[]
elevation: (number | null)[]
gap_pace_s_km: (number | null)[]
grade_pct: (number | null)[]
hr: (number | null)[]
lat: (number | null)[]
lon: (number | null)[]
pace_s_km: (number | null)[]
performance_condition: (number | null)[]
power: (number | null)[]
}

export interface Weather {
description: (string | null)
dew_point_c: (number | null)
feels_like_c: (number | null)
humidity_pct: (number | null)
temperature_c: (number | null)
wind_kmh: (number | null)
}

export interface ZoneTime {
ceiling_bpm: (number | null)
floor_bpm: (number | null)
seconds: number
zone: number
}

export interface Today {
date: string
illness: IllnessWatch
last_activity_id: (string | null)
readiness: (Readiness | null)
signals: Signal[]
tiles: BaselineTile[]
training_status: (string | null)
week: WeekDay[]
}

export interface BaselineTile {
band_high: (number | null)
band_low: (number | null)
baseline_label: string
delta_display: string
display: string
key: string
label: string
spark: SparkPoint[]
status: ("good" | "typical" | "attention" | "bad" | "unknown")
status_label: string
value: (number | null)
}

export interface IllnessSignal {
flagged: boolean
key: string
label: string
median: (number | null)
unit: string
value: (number | null)
z: (number | null)
}

export interface IllnessWatch {
message: string
reference_nights: number
signals: IllnessSignal[]
status: ("ok" | "watch" | "alert" | "insufficient")
}

export interface Readiness {
date: string
factors: ReadinessFactor[]
feedback: (string | null)
level: (string | null)
recovery_time_h: (number | null)
score: number
}

export interface ReadinessFactor {
key: string
label: string
pct: number
}

export interface Signal {
detail: string
display: string
key: string
label: string
status: ("good" | "typical" | "attention" | "bad" | "unknown")
}

export interface SparkPoint {
date: string
value: (number | null)
}

export interface WeekActivity {
activity_id: string
distance_km: (number | null)
duration_min: (number | null)
sport: string
training_load: (number | null)
}

export interface WeekDay {
activities: WeekActivity[]
date: string
}

export interface Intraday {
body_battery: IntradayPoint[]
body_battery_charged: (number | null)
body_battery_drained: (number | null)
body_battery_high: (number | null)
body_battery_low: (number | null)
date: string
end_ms: number
hr: IntradayPoint[]
hr_max: (number | null)
hr_min: (number | null)
hr_resting: (number | null)
last_sample_ms: (number | null)
spans: DaySpan[]
start_ms: number
steps: StepBucket[]
steps_total: (number | null)
stress: IntradayPoint[]
stress_avg: (number | null)
stress_shares: StressShare[]
}

export interface DaySpan {
activity_id: (string | null)
end_ms: number
kind: ("sleep" | "activity" | "motion")
label: string
start_ms: number
}

export interface IntradayPoint {
ts_ms: number
value: (number | null)
}

export interface StepBucket {
end_ms: number
start_ms: number
steps: number
}

export interface StressShare {
key: ("rest" | "low" | "medium" | "high")
label: string
minutes: number
}

export interface Load {
calendar: CalendarDay[]
days: LoadDay[]
focus: FocusRow[]
summary: LoadSummary
weeks: WeekLoad[]
}

export interface CalendarDay {
date: string
load: number
sports: string[]
}

export interface FocusRow {
focus: string
label: string
load: (number | null)
status: ("good" | "typical" | "attention" | "bad" | "unknown")
target_max: (number | null)
target_min: (number | null)
}

export interface LoadDay {
acute: (number | null)
acwr: (number | null)
chronic: (number | null)
chronic_max: (number | null)
chronic_min: (number | null)
daily_load: number
date: string
fatigue: number
fitness: number
form: number
}

export interface LoadSummary {
detail: string
easy_line: (string | null)
headline: string
status: ("good" | "typical" | "attention" | "bad" | "unknown")
}

export interface WeekLoad {
easy_min: number
easy_pct: (number | null)
hard_min: number
km: number
load: number
minutes_football: number
minutes_gym: number
minutes_other: number
minutes_run: number
moderate_min: number
monotony: (number | null)
runs: number
strain: (number | null)
verdict: (string | null)
week: string
}

export interface Meta {
activity_count: number
days: string[]
device: (string | null)
first_day: (string | null)
generated_at: string
last_activity_date: (string | null)
last_day: (string | null)
today: string
}

export interface Performance {
efficiency: EfficiencyPoint[]
efficiency_trend: (TrendLine | null)
fitness_age: (FitnessAge | null)
form: FormMetric[]
form_window_days: number
heat_adjusted_trend: (TrendLine | null)
projection_note: string
races: RaceDistance[]
records: RecordRow[]
vo2max: SeriesPoint[]
vo2max_per_30_days: (number | null)
vo2max_projection: (SeriesPoint[] | null)
}

export interface EfficiencyPoint {
activity_id: string
avg_hr: (number | null)
date: string
distance_km: (number | null)
feels_like_c: (number | null)
heat_adjusted_meters_per_beat: (number | null)
heat_adjusted_pace_s_km: (number | null)
heat_slowdown_pct: (number | null)
meters_per_beat: number
pace_s_km: (number | null)
}

export interface FitnessAge {
achievable_age: (number | null)
chronological_age: (number | null)
fitness_age: (number | null)
vigorous_days_per_week: (number | null)
vigorous_days_target: (number | null)
vigorous_minutes_per_week: (number | null)
vigorous_minutes_target: (number | null)
}

export interface FormMetric {
current: (number | null)
digits: number
earlier_count: number
fit_intercept: (number | null)
fit_slope: (number | null)
key: string
label: string
lower_is_better: (boolean | null)
points: FormPoint[]
recent_count: number
recent_delta: (number | null)
reference_speed_kmh: (number | null)
unit: string
verdict: string
}

export interface FormPoint {
adjusted: (number | null)
date: string
recent: boolean
speed_kmh: number
value: number
}

export interface RaceDistance {
current_seconds: number
delta_8w_seconds: (number | null)
distance: string
km: number
label: string
projection: (SeriesPoint[] | null)
record_seconds: (number | null)
riegel_seconds: (number | null)
series: SeriesPoint[]
}

export interface RecordRow {
activity_id: (string | null)
date: (string | null)
label: string
type_id: number
value: number
value_display: string
}

export interface SeriesPoint {
date: string
value: number
}

export interface TrendLine {
end_date: string
end_value: number
per_30_days: number
start_date: string
start_value: number
}

export interface Recovery {
glance: GlanceDay[]
glance_labels: string[]
glance_metrics: string[]
nights: Night[]
trends: RecoveryTrend[]
}

export interface GlanceCell {
display: string
key: string
status: ("good" | "typical" | "attention" | "bad" | "unknown")
value: (number | null)
z: (number | null)
}

export interface GlanceDay {
cells: GlanceCell[]
date: string
}

export interface Night {
awake_h: (number | null)
bedtime: (string | null)
bedtime_minutes: (number | null)
date: string
deep_h: (number | null)
feedback: (string | null)
light_h: (number | null)
need_h: (number | null)
rem_h: (number | null)
respiration: (number | null)
score: (number | null)
sleep_h: (number | null)
wake_minutes: (number | null)
wake_time: (string | null)
}

export interface RecoveryTrend {
digits: number
help: string
higher_is_better: (boolean | null)
key: string
label: string
points: TrendPoint[]
unit: string
}

export interface TrendPoint {
band_high: (number | null)
band_low: (number | null)
date: string
mean7: (number | null)
value: (number | null)
}

export interface Routes {
privacy: (Privacy | null)
routes: RouteTrace[]
}

export interface Privacy {
lat: number
lon: number
radius_m: number
}

export interface RouteTrace {
activity_id: string
date: string
distance_km: (number | null)
pace_s_km: (number | null)
points: (number | null)[][]
}

export interface SleepNight {
body_battery: SleepSeriesPoint[]
date: string
hr: SleepSeriesPoint[]
hrv: SleepSeriesPoint[]
night: Night
stages: SleepStage[]
stress: SleepSeriesPoint[]
}

export interface SleepSeriesPoint {
ts_ms: number
value: number
}

export interface SleepStage {
end_ms: number
stage: string
start_ms: number
}

export interface Sports {
football: FootballSession[]
gear: GearItem[]
gym: GymSession[]
muscles: MuscleGroupSets[]
progress: StrengthProgress[]
}

export interface ExerciseSummary {
category: string
estimated_1rm_kg: (number | null)
exercise: (string | null)
max_weight_kg: (number | null)
reps: number
sets: number
volume_kg: number
}

export interface FootballSession {
activity_id: string
aerobic_te: (number | null)
anaerobic_te: (number | null)
avg_hr: (number | null)
date: string
distance_km: (number | null)
duration_min: (number | null)
high_speed_m: number
max_hr: (number | null)
max_speed_kmh: (number | null)
positions: number[][]
sprints: number
training_load: (number | null)
zone_minutes: number[]
}

export interface GearItem {
distance_km: number
gear_id: string
gear_type: (string | null)
max_km: (number | null)
name: string
status: (string | null)
}

export interface GymSession {
activity_id: string
avg_hr: (number | null)
date: string
duration_min: (number | null)
exercises: ExerciseSummary[]
reps: number
sets: number
training_load: (number | null)
volume_kg: number
}

export interface MuscleGroupSets {
group: string
label: string
sets_28d: number
sets_7d: number
}

export interface StrengthProgress {
category: string
label: string
points: SeriesPoint[]
}
