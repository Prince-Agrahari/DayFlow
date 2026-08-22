"""Cross-module integration tests."""

from datetime import date, timedelta

from app.models.attendance import Attendance
from app.models.enums import AttendanceStatus, LeaveStatus, LeaveType
from app.models.leave_request import LeaveRequest


def _login(client, email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_analytics_dashboard_admin(client, db_session):
    admin_headers = _login(client, "admin@test.com", "admin123")
    res = client.get("/api/analytics/dashboard", headers=admin_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_employees"] >= 1
    assert "attendance_rate" in body
    assert "risk_distribution" in body
    assert "anomaly_distribution" in body


def test_analytics_forbidden_for_employee(client):
    emp_headers = _login(client, "emp@test.com", "emp12345")
    res = client.get("/api/analytics/dashboard", headers=emp_headers)
    assert res.status_code == 403


def test_team_availability(client):
    admin_headers = _login(client, "admin@test.com", "admin123")
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=6)).isoformat()
    res = client.get(
        f"/api/analytics/team-availability?department=Engineering&start_date={start}&end_date={end}",
        headers=admin_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["department"] == "Engineering"
    assert len(body["daily_availability"]) == 7


def test_priority_queue(client, db_session):
    from app.models.employee import EmployeeProfile

    profile = db_session.query(EmployeeProfile).filter(EmployeeProfile.employee_id == "EMP001").first()
    for i in range(5):
        d = date.today() - timedelta(days=i)
        db_session.add(Attendance(employee_id=profile.id, date=d, status=AttendanceStatus.ABSENT))
    db_session.add(LeaveRequest(
        employee_id=profile.id, leave_type=LeaveType.PAID,
        start_date=date.today() + timedelta(days=3),
        end_date=date.today() + timedelta(days=5),
        reason="Overlap test", status=LeaveStatus.PENDING,
    ))
    db_session.commit()

    admin_headers = _login(client, "admin@test.com", "admin123")
    res = client.get("/api/hr/priority-queue", headers=admin_headers)
    assert res.status_code == 200
    body = res.json()
    assert "generated_at" in body
    assert isinstance(body["items"], list)


def test_ai_anomalies_schema(client, db_session):
    from app.models.employee import EmployeeProfile

    profile = db_session.query(EmployeeProfile).filter(EmployeeProfile.employee_id == "EMP001").first()
    for i in range(8):
        d = date.today() - timedelta(days=i)
        db_session.add(Attendance(
            employee_id=profile.id, date=d, status=AttendanceStatus.PRESENT,
            working_hours=2.0 if i < 3 else 8.0, is_late=i < 3,
        ))
    db_session.commit()

    admin_headers = _login(client, "admin@test.com", "admin123")
    res = client.get("/api/ai/anomalies", headers=admin_headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_analytics_report(client):
    admin_headers = _login(client, "admin@test.com", "admin123")
    res = client.get("/api/analytics/reports/payroll", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["report_type"] == "payroll"
