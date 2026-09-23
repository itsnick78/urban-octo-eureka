# fleet_utils.py
# Shared helpers for the nightly fleet report.

MILES_PER_KM = 0.621371                 # 1 km = 0.621371 miles


def km_to_miles(km: float) -> float:
    """Convert km to miles for the UK partner garage's nightly report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-percent string, e.g. '80%'."""
    return f"{value:.0f}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of values, or 0 for an empty list."""
    if not values:
        return 0
    return sum(values) / len(values)
