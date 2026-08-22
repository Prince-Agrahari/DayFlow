"""Payroll service."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction
from app.models.payroll import Payroll
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.mappers import payroll_to_response
from app.schemas.payroll import PayrollUpdateRequest


def get_payroll_by_profile(db: Session, profile: EmployeeProfile) -> Payroll:
    payroll = db.query(Payroll).options(joinedload(Payroll.employee).joinedload(EmployeeProfile.user)).filter(Payroll.employee_id == profile.id).first()
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll record not found")
    return payroll


def get_payroll_by_code(db: Session, employee_code: str) -> Payroll:
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_code).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return get_payroll_by_profile(db, profile)


def list_payroll(db: Session, page: int = 1, page_size: int = 50) -> tuple[list[Payroll], int]:
    query = db.query(Payroll).options(joinedload(Payroll.employee).joinedload(EmployeeProfile.user))
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def update_payroll(db: Session, employee_code: str, payload: PayrollUpdateRequest, admin: User) -> Payroll:
    payroll = get_payroll_by_code(db, employee_code)
    data = payload.model_dump(exclude_unset=True)
    for field in ("base_salary", "basic", "hra", "allowances", "deductions", "net_salary"):
        if field in data and data[field] is not None:
            setattr(payroll, field, Decimal(str(data[field])))

    if payload.net_salary is None and any(k in data for k in ("basic", "hra", "allowances", "deductions")):
        payroll.net_salary = payroll.basic + payroll.hra + payroll.allowances - payroll.deductions

    log_activity(
        db,
        user_id=admin.id,
        action=ActivityAction.PAYROLL_UPDATED,
        description=f"Updated payroll for {employee_code}",
        entity_type="payroll",
        entity_id=employee_code,
    )
    db.commit()
    db.refresh(payroll)
    return payroll
