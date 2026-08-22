"""Test data helpers for AI engine tests."""

from datetime import date, timedelta


def make_normal_records(employee_id: str = "EMP001", days: int = 10) -> list[dict]:
    base = date.today() - timedelta(days=days)
    records = []
    for i in range(days):
        d = base + timedelta(days=i)
        records.append(
            {
                "employee_id": employee_id,
                "employee_name": "Jane Doe",
                "date": d.isoformat(),
                "check_in_time": "09:00",
                "check_out_time": "17:00",
                "working_hours": 8.0,
                "is_late": False,
                "status": "PRESENT",
            }
        )
    return records


def make_anomalous_records(employee_id: str = "EMP002", days: int = 10) -> list[dict]:
    base = date.today() - timedelta(days=days)
    records = []
    for i in range(days):
        d = base + timedelta(days=i)
        late = i >= days - 4
        records.append(
            {
                "employee_id": employee_id,
                "employee_name": "John Anomaly",
                "date": d.isoformat(),
                "check_in_time": "11:30" if late else "09:00",
                "check_out_time": "14:00" if late else "17:00",
                "working_hours": 2.5 if late else 8.0,
                "is_late": late,
                "status": "ABSENT" if i == days - 1 else "PRESENT",
            }
        )
    return records
