"""AI API endpoint tests."""

import json

from helpers import make_anomalous_records, make_normal_records


def test_anomaly_endpoint_requires_auth(client):
    response = client.post("/api/ai/anomaly", json={"attendance_records": make_normal_records()})
    assert response.status_code == 401


def test_anomaly_endpoint_admin(client, admin_headers):
    records = make_normal_records() + make_anomalous_records()
    response = client.post(
        "/api/ai/anomaly",
        headers=admin_headers,
        json={"attendance_records": records},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


def test_anomaly_invalid_input(client, admin_headers):
    response = client.post("/api/ai/anomaly", headers=admin_headers, json={"attendance_records": []})
    assert response.status_code == 400


def test_risk_endpoint(client, admin_headers):
    metrics = json.dumps({"attendance_rate": 0.7, "late_rate": 0.35, "absence_trend_delta": 0.2})
    response = client.get("/api/ai/employee/EMP003/risk", headers=admin_headers, params={"metrics": metrics})
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in {"LOW", "MEDIUM", "HIGH"}


def test_leave_recommendation_employee_self(client, employee_headers):
    response = client.post(
        "/api/ai/leave-recommendation",
        headers=employee_headers,
        json={
            "employee_id": "EMP001",
            "start_date": "2026-04-01",
            "end_date": "2026-04-02",
            "leave_type": "PAID",
            "leave_balances": [{"leave_type": "PAID", "remaining_days": 5}],
        },
    )
    assert response.status_code == 200
    assert "conflict_level" in response.json()


def test_leave_recommendation_denied_other_employee(client, employee_headers):
    response = client.post(
        "/api/ai/leave-recommendation",
        headers=employee_headers,
        json={
            "employee_id": "EMP999",
            "start_date": "2026-04-01",
            "end_date": "2026-04-02",
            "leave_type": "PAID",
        },
    )
    assert response.status_code == 403


def test_copilot_admin_only(client, employee_headers, admin_headers):
    assert client.post("/api/ai/copilot", headers=employee_headers, json={"question": "What should I prioritize?"}).status_code == 403
    response = client.post(
        "/api/ai/copilot",
        headers=admin_headers,
        json={"question": "What should I prioritize today?", "structured_context": {"pending_leaves": []}},
    )
    assert response.status_code == 200
    assert "answer" in response.json()


def test_assistant_unauthorized_other_employee(client, employee_headers):
    response = client.post(
        "/api/ai/assistant",
        headers=employee_headers,
        json={
            "question": "What is my salary?",
            "employee_context": {"employee_id": "EMP999", "payroll": {"net_salary": 9999}},
        },
    )
    assert response.status_code == 403


def test_assistant_own_data(client, employee_headers):
    response = client.post(
        "/api/ai/assistant",
        headers=employee_headers,
        json={
            "question": "How many leaves do I have?",
            "employee_context": {
                "employee_id": "EMP001",
                "leave_balances": [{"leave_type": "PAID", "remaining_days": 6}],
            },
        },
    )
    assert response.status_code == 200
    assert "6" in response.json()["answer"]


def test_assistant_builds_context_when_missing(client, employee_headers):
    response = client.post(
        "/api/ai/assistant",
        headers=employee_headers,
        json={"question": "Show my attendance"},
    )
    assert response.status_code == 200
    assert "answer" in response.json()
