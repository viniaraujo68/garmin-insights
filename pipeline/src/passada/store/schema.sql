PRAGMA user_version = 1;

CREATE TABLE activities (
    activity_id TEXT PRIMARY KEY,
    start_local TEXT NOT NULL,
    date TEXT NOT NULL,
    type_key TEXT NOT NULL,
    sport TEXT NOT NULL,
    name TEXT,
    distance_m REAL,
    duration_s REAL,
    moving_s REAL,
    elapsed_s REAL,
    avg_speed REAL,
    max_speed REAL,
    gap_speed REAL,
    avg_hr REAL,
    max_hr REAL,
    min_hr REAL,
    recovery_hr REAL,
    cadence REAL,
    stride_m REAL,
    ground_contact_ms REAL,
    vertical_oscillation_cm REAL,
    vertical_ratio_pct REAL,
    power_w REAL,
    normalized_power_w REAL,
    training_load REAL,
    aerobic_te REAL,
    anaerobic_te REAL,
    training_effect_label TEXT,
    calories REAL,
    moderate_minutes REAL,
    vigorous_minutes REAL,
    body_battery_impact REAL,
    elevation_gain_m REAL,
    elevation_loss_m REAL,
    rpe REAL,
    feel REAL,
    steps REAL,
    temperature_c REAL,
    feels_like_c REAL,
    dew_point_c REAL,
    humidity_pct REAL,
    wind_kmh REAL,
    weather TEXT,
    z1_s REAL, z2_s REAL, z3_s REAL, z4_s REAL, z5_s REAL,
    has_gps INTEGER NOT NULL
);

CREATE TABLE laps (
    activity_id TEXT NOT NULL REFERENCES activities (activity_id),
    lap INTEGER NOT NULL,
    distance_m REAL,
    duration_s REAL,
    avg_speed REAL,
    gap_speed REAL,
    avg_hr REAL,
    max_hr REAL,
    cadence REAL,
    stride_m REAL,
    ground_contact_ms REAL,
    vertical_oscillation_cm REAL,
    vertical_ratio_pct REAL,
    power_w REAL,
    elevation_gain_m REAL,
    elevation_loss_m REAL,
    PRIMARY KEY (activity_id, lap)
);

CREATE TABLE samples (
    activity_id TEXT NOT NULL REFERENCES activities (activity_id),
    idx INTEGER NOT NULL,
    elapsed_s REAL,
    distance_m REAL,
    lat REAL,
    lon REAL,
    speed REAL,
    gap_speed REAL,
    hr REAL,
    cadence REAL,
    power REAL,
    elevation REAL,
    performance_condition REAL,
    stride_m REAL,
    ground_contact_ms REAL,
    vertical_oscillation_cm REAL,
    vertical_ratio_pct REAL,
    body_battery REAL,
    PRIMARY KEY (activity_id, idx)
);

CREATE TABLE exercise_sets (
    activity_id TEXT NOT NULL REFERENCES activities (activity_id),
    set_idx INTEGER NOT NULL,
    set_type TEXT,
    category TEXT,
    exercise TEXT,
    reps REAL,
    weight_kg REAL,
    duration_s REAL,
    PRIMARY KEY (activity_id, set_idx)
);

CREATE TABLE daily (
    date TEXT PRIMARY KEY,
    sleep_score REAL,
    sleep_s REAL,
    deep_s REAL,
    light_s REAL,
    rem_s REAL,
    awake_s REAL,
    sleep_start_local TEXT,
    sleep_end_local TEXT,
    sleep_need_min REAL,
    sleep_feedback TEXT,
    sleep_respiration REAL,
    sleep_avg_hr REAL,
    sleep_stress REAL,
    restless_moments REAL,
    resting_hr REAL,
    hrv_last_night REAL,
    hrv_weekly_avg REAL,
    hrv_balanced_low REAL,
    hrv_balanced_high REAL,
    hrv_status TEXT,
    readiness_score REAL,
    readiness_level TEXT,
    readiness_feedback TEXT,
    readiness_sleep_pct REAL,
    readiness_sleep_history_pct REAL,
    readiness_recovery_pct REAL,
    readiness_load_pct REAL,
    readiness_stress_pct REAL,
    readiness_hrv_pct REAL,
    recovery_time_min REAL,
    steps REAL,
    step_goal REAL,
    walk_distance_m REAL,
    active_kcal REAL,
    total_kcal REAL,
    moderate_minutes REAL,
    vigorous_minutes REAL,
    stress_avg REAL,
    stress_max REAL,
    stress_rest_s REAL,
    stress_low_s REAL,
    stress_medium_s REAL,
    stress_high_s REAL,
    body_battery_high REAL,
    body_battery_low REAL,
    body_battery_charged REAL,
    body_battery_drained REAL,
    spo2_avg REAL,
    waking_respiration REAL,
    sedentary_s REAL,
    active_s REAL,
    highly_active_s REAL
);

CREATE TABLE sleep_stages (
    date TEXT NOT NULL,
    start_ms INTEGER NOT NULL,
    end_ms INTEGER NOT NULL,
    stage TEXT NOT NULL,
    PRIMARY KEY (date, start_ms)
);

CREATE TABLE sleep_series (
    date TEXT NOT NULL,
    metric TEXT NOT NULL,
    ts_ms INTEGER NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (date, metric, ts_ms)
);

CREATE TABLE day_series (
    date TEXT NOT NULL,
    metric TEXT NOT NULL,
    ts_ms INTEGER NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (date, metric, ts_ms)
);

CREATE TABLE day_steps (
    date TEXT NOT NULL,
    start_ms INTEGER NOT NULL,
    end_ms INTEGER NOT NULL,
    steps INTEGER NOT NULL,
    level TEXT,
    PRIMARY KEY (date, start_ms)
);

CREATE TABLE load_daily (
    date TEXT PRIMARY KEY,
    acute REAL,
    chronic REAL,
    chronic_min REAL,
    chronic_max REAL,
    acwr REAL,
    acwr_status TEXT,
    training_status TEXT
);

CREATE TABLE vo2max (
    date TEXT PRIMARY KEY,
    vo2max REAL,
    heat_acclimation_pct REAL
);

CREATE TABLE race_predictions (
    date TEXT NOT NULL,
    distance TEXT NOT NULL,
    seconds REAL NOT NULL,
    PRIMARY KEY (date, distance)
);

CREATE TABLE weekly_intensity (
    week TEXT PRIMARY KEY,
    moderate REAL,
    vigorous REAL,
    goal REAL
);

CREATE TABLE records (
    type_id INTEGER PRIMARY KEY,
    value REAL NOT NULL,
    activity_id TEXT,
    date TEXT
);

CREATE TABLE hr_zones (
    zone INTEGER PRIMARY KEY,
    floor_bpm REAL NOT NULL,
    ceiling_bpm REAL
);

CREATE TABLE profile (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE load_focus (
    focus TEXT PRIMARY KEY,
    load REAL,
    target_min REAL,
    target_max REAL,
    as_of TEXT
);

CREATE TABLE gear (
    gear_id TEXT PRIMARY KEY,
    name TEXT,
    gear_type TEXT,
    distance_m REAL,
    max_distance_m REAL,
    status TEXT
);
