"""Authentication service."""

from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction, LeaveType, UserRole
from app.models.leave_request import LeaveBalance
from app.models.payroll import Payroll
from app.models.user import User
from app.services.activity_service import log_activity
from app.schemas.auth import LoginResponse, SignupRequest, UserResponse


def signup(db: Session, payload: SignupRequest) -> User:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.flush()

    dept_name = "HR" if payload.role == UserRole.ADMIN else "Engineering"
    department = db.query(Department).filter(Department.name == dept_name).first()
    count = db.query(EmployeeProfile).count()
    emp_code = "EMP000" if payload.role == UserRole.ADMIN else f"EMP{count + 1:03d}"

    profile = EmployeeProfile(
        user_id=user.id,
        employee_id=emp_code,
        department=dept_name,
        department_id=department.id if department else None,
        designation="HR Admin" if payload.role == UserRole.ADMIN else "Employee",
        joining_date=date.today(),
        salary=Decimal("95000") if payload.role == UserRole.ADMIN else Decimal("75000"),
    )
    db.add(profile)
    db.flush()

    salary = profile.salary
    db.add(
        Payroll(
            employee_id=profile.id,
            base_salary=salary,
            basic=salary * Decimal("0.65"),
            hra=salary * Decimal("0.18"),
            allowances=salary * Decimal("0.12"),
            deductions=salary * Decimal("0.05"),
            net_salary=salary * Decimal("0.94"),
        )
    )

    year = date.today().year
    for lt, total in [(LeaveType.PAID, 20), (LeaveType.SICK, 10), (LeaveType.UNPAID, 5)]:
        db.add(LeaveBalance(employee_id=profile.id, leave_type=lt, total_days=total, used_days=0, year=year))

    log_activity(db, user_id=user.id, action=ActivityAction.EMPLOYEE_CREATED, description=f"User signed up: {user.email}")
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> LoginResponse:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    log_activity(db, user_id=user.id, action=ActivityAction.LOGIN, description=f"User logged in: {user.email}")
    db.commit()

    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    user_data = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        employee_id=profile.employee_id if profile else None,
        created_at=user.created_at,
    )
    return LoginResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_data,
    )


def get_me(db: Session, user: User) -> UserResponse:
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        employee_id=profile.employee_id if profile else None,
        created_at=user.created_at,
    )
