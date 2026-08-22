"""Shared fixtures for AI engine tests."""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AI_ENGINE = os.path.join(ROOT, "ai-engine")
BACKEND = os.path.join(ROOT, "backend")

for path in (AI_ENGINE, BACKEND):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.core.security import create_access_token
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_headers() -> dict[str, str]:
    token = create_access_token({"sub": "admin-1", "role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_headers() -> dict[str, str]:
    token = create_access_token({"sub": "emp-user-1", "role": "EMPLOYEE", "employee_id": "EMP001"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_employee_headers() -> dict[str, str]:
    token = create_access_token({"sub": "emp-user-2", "role": "EMPLOYEE", "employee_id": "EMP002"})
    return {"Authorization": f"Bearer {token}"}


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
