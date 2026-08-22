"""Backend API integration tests."""

from datetime import date, timedelta


def _login(client, email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_signup(client, db_session):
    res = client.post("/api/auth/signup", json={
        "email": "new@test.com", "password": "password123", "full_name": "New User", "role": "EMPLOYEE",
    })
    assert res.status_code == 201
    assert res.json()["email"] == "new@test.com"


def test_login(client):
    headers = _login(client, "emp@test.com", "emp12345")
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["role"] == "EMPLOYEE"


def test_invalid_login(client):
    res = client.post("/api/auth/login", json={"email": "emp@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_authorization_admin_only(client):
    emp_headers = _login(client, "emp@test.com", "emp12345")
    res = client.get("/api/employees", headers=emp_headers)
    assert res.status_code == 403

    admin_headers = _login(client, "admin@test.com", "admin123")
    res = client.get("/api/employees", headers=admin_headers)
    assert res.status_code == 200


def test_attendance_check_in_out(client):
    headers = _login(client, "emp@test.com", "emp12345")
    res = client.post("/api/attendance/check-in", json={"notes": "Office"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["status"] == "PRESENT"

    res2 = client.post("/api/attendance/check-in", json={}, headers=headers)
    assert res2.status_code == 409

    res3 = client.post("/api/attendance/check-out", headers=headers)
    assert res3.status_code == 200
    assert res3.json()["working_hours"] is not None


def test_checkout_without_checkin(client):
    client.post("/api/auth/signup", json={
        "email": "nocheckin@test.com", "password": "password123", "full_name": "No Checkin", "role": "EMPLOYEE",
    })
    headers = _login(client, "nocheckin@test.com", "password123")
    res = client.post("/api/attendance/check-out", headers=headers)
    assert res.status_code == 400


def test_leave_apply_and_approve(client):
    emp_headers = _login(client, "emp@test.com", "emp12345")
    start = (date.today() + timedelta(days=10)).isoformat()
    end = (date.today() + timedelta(days=12)).isoformat()
    res = client.post("/api/leaves", json={
        "leave_type": "PAID", "start_date": start, "end_date": end, "reason": "Vacation trip",
    }, headers=emp_headers)
    assert res.status_code == 201
    leave_id = res.json()["id"]

    admin_headers = _login(client, "admin@test.com", "admin123")
    res2 = client.put(f"/api/leaves/{leave_id}/approve", json={"comment": "Enjoy!"}, headers=admin_headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "APPROVED"


def test_payroll_authorization(client):
    emp_headers = _login(client, "emp@test.com", "emp12345")
    res = client.get("/api/payroll/my", headers=emp_headers)
    assert res.status_code == 200

    res2 = client.get("/api/payroll/EMP001", headers=emp_headers)
    assert res2.status_code == 200

    res3 = client.get("/api/payroll/EMP000", headers=emp_headers)
    assert res3.status_code == 403

    admin_headers = _login(client, "admin@test.com", "admin123")
    res4 = client.put("/api/payroll/EMP001", json={"base_salary": 85000}, headers=admin_headers)
    assert res4.status_code == 200


def test_employee_data_isolation(client):
    emp_headers = _login(client, "emp@test.com", "emp12345")
    res = client.get("/api/employees/EMP000", headers=emp_headers)
    assert res.status_code == 403

    res2 = client.get("/api/employees/EMP001", headers=emp_headers)
    assert res2.status_code == 200


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
