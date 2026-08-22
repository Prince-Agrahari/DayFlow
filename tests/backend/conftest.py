"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-characters-long"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.department import Department
from app.core.security import hash_password
from app.models.employee import EmployeeProfile
from app.models.enums import UserRole
from app.models.payroll import Payroll
from app.models.user import User
from decimal import Decimal
from datetime import date


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for dept in ["Engineering", "HR", "Finance", "Marketing", "Design"]:
        session.add(Department(name=dept))

    admin = User(email="admin@test.com", password_hash=hash_password("admin123"), full_name="Admin User", role=UserRole.ADMIN)
    employee = User(email="emp@test.com", password_hash=hash_password("emp12345"), full_name="Test Employee", role=UserRole.EMPLOYEE)
    session.add_all([admin, employee])
    session.flush()

    dept = session.query(Department).filter(Department.name == "Engineering").first()
    admin_profile = EmployeeProfile(user_id=admin.id, employee_id="EMP000", department="HR", department_id=session.query(Department).filter(Department.name == "HR").first().id, designation="Admin", joining_date=date.today(), salary=Decimal("100000"))
    emp_profile = EmployeeProfile(user_id=employee.id, employee_id="EMP001", department="Engineering", department_id=dept.id, designation="Engineer", joining_date=date.today(), salary=Decimal("80000"))
    session.add_all([admin_profile, emp_profile])
    session.flush()
    session.add(Payroll(employee_id=emp_profile.id, base_salary=Decimal("80000"), basic=Decimal("52000"), hra=Decimal("14000"), allowances=Decimal("10000"), deductions=Decimal("4000"), net_salary=Decimal("76000")))
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


def auth_header(client, email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
