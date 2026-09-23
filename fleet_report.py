# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float | None:
    """Return wear percent for a car, or None if it has no last-service reading."""
    last = car.get("last_service_km")
    if last is None:
        return None
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Summarize fleet wear: car count, cars due, and average wear.

    Cars with no last-service reading count toward "count" but are excluded
    from the average (their wear is unknown, not zero).
    """
    wears = []
    due = 0
    for car in fleet:
        wear = car_wear(car)
        if wear is not None:
            wears.append(wear)
        if needs_service(car):
            due += 1
    average = fleet_utils.mean(wears)
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list[dict]) -> None:
    """Log the report title, then print the nightly fleet-health summary."""
    settings = load_settings()
    log(settings.get("report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {fleet_utils.format_percent(s['average_wear'])}")
    total_km = sum(car["odometer"] for car in fleet)
    # The partner garage in England wants the distance in miles (since 2015).
    print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    flush_log(settings.get("log_file", "km_wachter.log"))
