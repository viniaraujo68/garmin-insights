from collections.abc import Sequence
from statistics import median


def mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def robust_z(value: float, reference: Sequence[float], minimum_spread: float = 0.0) -> float | None:
    if len(reference) < 2:
        return None
    center = median(reference)
    spread = max(median(abs(item - center) for item in reference) * 1.4826, minimum_spread)
    if spread == 0:
        return None
    return (value - center) / spread


def rounded(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def pace_seconds(speed: float | None) -> int | None:
    return None if not speed or speed <= 0 else round(1000 / speed)
