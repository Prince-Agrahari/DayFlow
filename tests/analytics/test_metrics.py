"""Analytics metrics tests."""

from datetime import date, timedelta

from metrics import get_dashboard_metrics
from priority_queue import generate_priority_queue
from team_availability import calculate_team_availability


def test_dashboard_metrics(sample_employees, sample_attendance, sample_leaves):
    data = {
        "employees": sample_employees,
        "attendance_records": sample_attendance,
        "leave_requests": sample_leaves,
        "payroll_records": [{"base_salary": 90000, "net_salary": 85000}, {"base_salary": 80000, "net_salary": 76000}],
        "today": date.today().isoformat(),
        "anomalies": [{"severity": "HIGH"}, {"severity": "MEDIUM"}],
        "risk_signals": [{"risk_level": "HIGH"}, {"risk_level": "LOW"}],
    }
    result = get_dashboard_metrics(data)
    assert result["total_employees"] == 3
    assert 0 <= result["attendance_rate"] <= 1
    assert "payroll_summary" in result
    assert result["risk_distribution"]["HIGH"] >= 1
    assert result["anomaly_distribution"]["HIGH"] >= 1


def test_priority_queue_ranking():
    items = generate_priority_queue(
        anomalies=[{"employee_id": "EMP002", "employee_name": "John", "severity": "HIGH", "reason": "Late pattern", "recommendation": "Review"}],
        risk_signals=[{"employee_id": "EMP002", "employee_name": "John", "risk_level": "HIGH", "reasons": ["Absence up"], "recommendations": ["Check-in"]}],
        leave_conflicts=[{"conflict_level": "MEDIUM", "employee_id": "EMP001", "employee_name": "Jane", "reasons": ["Low availability"], "recommendation": "Plan coverage"}],
        pending_actions=[{"priority": "LOW", "title": "Pending leaves", "description": "2 pending", "recommended_action": "Review"}],
    )
    assert items[0]["priority"] == "HIGH"
    assert all(k in items[0] for k in ("title", "description", "employee_id", "reason", "recommended_action"))


def test_team_availability_heatmap(sample_employees, sample_attendance, sample_leaves):
    today = date.today()
    result = calculate_team_availability(
        "Engineering",
        today.isoformat(),
        (today + timedelta(days=6)).isoformat(),
        sample_employees,
        sample_leaves,
        sample_attendance,
    )
    assert result["total_employees"] == 2
    assert len(result["daily_availability"]) == 7
    assert "heatmap" in result
    assert result["daily_availability"][0]["availability_rate"] <= 1.0
