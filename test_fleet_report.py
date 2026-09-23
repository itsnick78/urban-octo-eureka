# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_handles_missing_reading():
    # A car with no last-service reading (like VOS-7788 in fleet_sample.json) must not
    # crash the report, must still be counted, and must not be treated as due.
    fleet = SAMPLE + [{"id": "VOS-7788", "odometer": 92000}]
    result = fleet_summary(fleet)
    assert result["count"] == 3
    assert result["due"] == 1
    assert "average_wear" in result
