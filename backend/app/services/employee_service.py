"""Employee management service."""

import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction, LeaveType, UserRole
from app.models.leave_request import LeaveBalance
from app.models.payroll import Payroll
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.mappers import employee_to_response
from app.schemas.employee import EmployeeAdminUpdate, EmployeeCreate, EmployeeSelfUpdate


def list_employees(
    db: Session,
    *,
    search: str | None = None,
    department: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[EmployeeProfile], int]:
    query = db.query(EmployeeProfile).options(joinedload(EmployeeProfile.user))
    if search:
        like = f"%{search.lower()}%"
        query = query.join(User).filter(
            (EmployeeProfile.employee_id.ilike(like)) | (User.full_name.ilike(like)) | (User.email.ilike(like))
        )
    if department:
        query = query.filter(EmployeeProfile.department == department)
    total = query.count()
    items = query.order_by(EmployeeProfile.employee_id).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_employee(db: Session, identifier: str) -> EmployeeProfile:
    query = db.query(EmployeeProfile).options(joinedload(EmployeeProfile.user))
    if _is_uuid(identifier):
        profile = query.filter(EmployeeProfile.id == uuid.UUID(identifier)).first()
    else:
        profile = query.filter(EmployeeProfile.employee_id == identifier).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return profile


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def create_employee(db: Session, payload: EmployeeCreate, actor: User) -> EmployeeProfile:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.flush()

    dept = db.query(Department).filter(Department.name == payload.department).first()
    count = db.query(EmployeeProfile).count()
    profile = EmployeeProfile(
        user_id=user.id,
        employee_id=f"EMP{count + 1:03d}",
        phone=payload.phone,
        address=payload.address,
        department=payload.department,
        department_id=dept.id if dept else None,
        designation=payload.designation,
        joining_date=payload.joining_date,
        employment_status=payload.employment_status,
        salary=payload.salary,
        profile_picture=payload.profile_picture,
    )
    db.add(profile)
    db.flush()

    net = payload.salary * Decimal("0.94")
    db.add(
        Payroll(
            employee_id=profile.id,
            base_salary=payload.salary,
            basic=payload.salary * Decimal("0.65"),
            hra=payload.salary * Decimal("0.18"),
            allowances=payload.salary * Decimal("0.12"),
            deductions=payload.salary * Decimal("0.05"),
            net_salary=net,
        )
    )

    from datetime import date

    year = date.today().year
    for lt, total in [(LeaveType.PAID, 20), (LeaveType.SICK, 10), (LeaveType.UNPAID, 5)]:
        db.add(LeaveBalance(employee_id=profile.id, leave_type=lt, total_days=total, used_days=0, year=year))

    log_activity(db, user_id=actor.id, action=ActivityAction.EMPLOYEE_CREATED, description=f"Created employee {profile.employee_id}", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def update_employee_self(db: Session, profile: EmployeeProfile, payload: EmployeeSelfUpdate, actor: User) -> EmployeeProfile:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    log_activity(db, user_id=actor.id, action=ActivityAction.PROFILE_UPDATED, description="Employee updated own profile", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def update_employee_admin(db: Session, profile: EmployeeProfile, payload: EmployeeAdminUpdate, actor: User) -> EmployeeProfile:
    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data:
        profile.user.full_name = data.pop("full_name")
    for field, value in data.items():
        setattr(profile, field, value)
    log_activity(db, user_id=actor.id, action=ActivityAction.PROFILE_UPDATED, description=f"Admin updated employee {profile.employee_id}", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def delete_employee(db: Session, profile: EmployeeProfile, actor: User) -> None:
    if profile.user.role == UserRole.ADMIN:
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the only admin")
    emp_id = profile.employee_id
    db.delete(profile.user)
    log_activity(db, user_id=actor.id, action=ActivityAction.EMPLOYEE_DELETED, description=f"Deleted employee {emp_id}", entity_type="employee", entity_id=emp_id)
    db.commit()
