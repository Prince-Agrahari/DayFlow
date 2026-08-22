"""Shared fixtures for AI engine API tests."""

from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[2]
for sub in ("backend", "ai-engine"):
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.enums import UserRole
from app.models.user import User


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(Department(name="Engineering"))
    session.flush()
    dept = session.query(Department).first()
    admin = User(email="admin@test.com", password_hash=hash_password("admin123"), full_name="Admin", role=UserRole.ADMIN)
    employee = User(email="emp@test.com", password_hash=hash_password("emp12345"), full_name="Employee", role=UserRole.EMPLOYEE)
    session.add_all([admin, employee])
    session.flush()
    session.add_all([
        EmployeeProfile(user_id=admin.id, employee_id="EMP000", department="HR", department_id=dept.id, designation="Admin", joining_date=date.today(), salary=Decimal("100000")),
        EmployeeProfile(user_id=employee.id, employee_id="EMP001", department="Engineering", department_id=dept.id, designation="Engineer", joining_date=date.today(), salary=Decimal("80000")),
    ])
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client) -> dict[str, str]:
    res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def employee_headers(client) -> dict[str, str]:
    res = client.post("/api/auth/login", json={"email": "emp@test.com", "password": "emp12345"})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
