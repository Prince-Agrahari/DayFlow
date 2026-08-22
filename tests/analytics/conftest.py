"""Shared fixtures for analytics unit tests."""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analytics"))


@pytest.fixture
def sample_employees() -> list[dict]:
    return [
        {"employee_id": "EMP001", "full_name": "Jane Doe", "department": "Engineering", "employment_status": "ACTIVE"},
        {"employee_id": "EMP002", "full_name": "John Smith", "department": "Engineering", "employment_status": "ACTIVE"},
        {"employee_id": "EMP003", "full_name": "Alice Johnson", "department": "HR", "employment_status": "ACTIVE"},
    ]


@pytest.fixture
def sample_attendance(sample_employees) -> list[dict]:
    today = date.today()
    records = []
    for emp in sample_employees:
        for i in range(20):
            d = today - timedelta(days=i)
            if d.weekday() >= 5:
                continue
            late = emp["employee_id"] == "EMP002" and i < 5
            absent = emp["employee_id"] == "EMP002" and i in {1, 4}
            records.append(
                {
                    "employee_id": emp["employee_id"],
                    "date": d.isoformat(),
                    "status": "ABSENT" if absent else "PRESENT",
                    "is_late": late,
                    "working_hours": 3.0 if late else 8.0,
                }
            )
    return records


@pytest.fixture
def sample_leaves() -> list[dict]:
    today = date.today()
    return [
        {
            "employee_id": "EMP001",
            "employee_name": "Jane Doe",
            "leave_type": "PAID",
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "status": "PENDING",
            "reason": "Vacation",
        },
        {
            "employee_id": "EMP002",
            "employee_name": "John Smith",
            "leave_type": "PAID",
            "start_date": (today + timedelta(days=6)).isoformat(),
            "end_date": (today + timedelta(days=8)).isoformat(),
            "status": "APPROVED",
            "reason": "Travel",
        },
    ]
