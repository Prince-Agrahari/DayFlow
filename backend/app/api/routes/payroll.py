"""Payroll routes."""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentEmployee, CurrentUser, DBSession, RequireAdmin
from app.models.enums import UserRole
from app.schemas.payroll import PaginatedPayroll, PayrollHistoryItem, PayrollResponse, PayrollUpdateRequest
from app.services import payroll_service
from app.services.mappers import payroll_to_response

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.get("/my", response_model=PayrollResponse)
def my_payroll(db: DBSession, profile: CurrentEmployee):
    payroll = payroll_service.get_payroll_by_profile(db, profile)
    return payroll_to_response(payroll)


@router.get("/me/history", response_model=list[PayrollHistoryItem])
def my_payroll_history(db: DBSession, profile: CurrentEmployee):
    return [PayrollHistoryItem(**item) for item in payroll_service.get_payroll_history(db, profile)]


@router.get("", response_model=PaginatedPayroll)
def list_payroll(db: DBSession, _: RequireAdmin, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    items, total = payroll_service.list_payroll(db, page=page, page_size=page_size)
    return PaginatedPayroll(
        items=[payroll_to_response(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{employee_id}", response_model=PayrollResponse)
def get_payroll(employee_id: str, db: DBSession, current_user: CurrentUser, profile: CurrentEmployee):
    if current_user.role == UserRole.EMPLOYEE and profile.employee_id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    payroll = payroll_service.get_payroll_by_code(db, employee_id)
    return payroll_to_response(payroll)


@router.put("/{employee_id}", response_model=PayrollResponse)
def update_payroll(employee_id: str, payload: PayrollUpdateRequest, db: DBSession, admin: RequireAdmin):
    payroll = payroll_service.update_payroll(db, employee_id, payload, admin)
    return payroll_to_response(payroll)
