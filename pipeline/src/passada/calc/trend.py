from collections.abc import Sequence
from datetime import date, timedelta
from statistics import median

PROJECTION_MIN_SPAN_DAYS = 56
PROJECTION_MIN_POINTS = 6
PROJECTION_DAMPING = 0.5


def theil_sen(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float] | None:
    slopes = [
        (ys[j] - ys[i]) / (xs[j] - xs[i])
        for i in range(len(xs))
        for j in range(i + 1, len(xs))
        if xs[j] != xs[i]
    ]
    if not slopes:
        return None
    slope = median(slopes)
    intercept = median(y - slope * x for x, y in zip(xs, ys))
    return slope, intercept


def ordinal(day: str) -> int:
    return date.fromisoformat(day).toordinal()


def trend_per_30_days(points: Sequence[tuple[str, float]]) -> float | None:
    if len(points) < 4:
        return None
    fit = theil_sen([ordinal(day) for day, _ in points], [value for _, value in points])
    return None if fit is None else fit[0] * 30


def projection(points: Sequence[tuple[str, float]], horizons_days: Sequence[int]) -> list[tuple[str, float]] | None:
    if len(points) < PROJECTION_MIN_POINTS:
        return None
    first, last = ordinal(points[0][0]), ordinal(points[-1][0])
    if last - first < PROJECTION_MIN_SPAN_DAYS:
        return None
    fit = theil_sen([ordinal(day) for day, _ in points], [value for _, value in points])
    if fit is None:
        return None
    slope, intercept = fit
    anchor = slope * last + intercept
    projected = [(points[-1][0], round(anchor, 2))]
    for horizon in horizons_days:
        day = date.fromordinal(last) + timedelta(days=horizon)
        projected.append((str(day), round(anchor + slope * horizon * PROJECTION_DAMPING, 2)))
    return projected


def linear_fit(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float] | None:
    if len(xs) < 3:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    spread = sum((x - mean_x) ** 2 for x in xs)
    if spread == 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / spread
    return slope, mean_y - slope * mean_x
