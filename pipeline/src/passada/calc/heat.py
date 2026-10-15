HADLEY_SLOWDOWN = (
    (100, 0.0),
    (110, 0.5),
    (120, 1.0),
    (130, 2.0),
    (140, 3.0),
    (150, 4.5),
    (160, 6.0),
    (170, 8.0),
    (180, 10.0),
)


def celsius_to_fahrenheit(value: float) -> float:
    return value * 9 / 5 + 32


def heat_slowdown_pct(temperature_c: float | None, dew_point_c: float | None) -> float | None:
    if temperature_c is None or dew_point_c is None:
        return None
    combined = celsius_to_fahrenheit(temperature_c) + celsius_to_fahrenheit(dew_point_c)
    if combined <= HADLEY_SLOWDOWN[0][0]:
        return 0.0
    for (low, low_pct), (high, high_pct) in zip(HADLEY_SLOWDOWN, HADLEY_SLOWDOWN[1:]):
        if combined <= high:
            return round(low_pct + (combined - low) / (high - low) * (high_pct - low_pct), 2)
    return HADLEY_SLOWDOWN[-1][1]


def heat_adjusted_pace(pace_s_km: int | None, slowdown_pct: float | None) -> int | None:
    if pace_s_km is None or slowdown_pct is None:
        return None
    return round(pace_s_km / (1 + slowdown_pct / 100))
