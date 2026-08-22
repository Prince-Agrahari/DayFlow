"""Leave management routes — paths match docs/api-contract.md (/leave/*)."""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentEmployee, CurrentUser, DBSession, RequireAdmin
from app.models.enums import LeaveStatus, UserRole
from app.schemas.leave import LeaveActionRequest, LeaveBalanceResponse, LeaveCreateRequest, LeaveResponse, PaginatedLeaves
from app.services import leave_service

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.post("", response_model=LeaveResponse, status_code=201)
def apply_leave(payload: LeaveCreateRequest, db: DBSession, profile: CurrentEmployee, current_user: CurrentUser):
    req = leave_service.apply_leave(db, profile, payload, current_user)
    return leave_service._to_response(req)


@router.get("/me", response_model=list[LeaveResponse])
def my_leaves(db: DBSession, profile: CurrentEmployee):
    return [leave_service._to_response(r) for r in leave_service.get_my_leaves(db, profile)]


@router.get("/balances", response_model=list[LeaveBalanceResponse])
def leave_balances(db: DBSession, profile: CurrentEmployee):
    return leave_service.get_leave_balances(db, profile)


@router.get("", response_model=PaginatedLeaves)
def list_leaves(
    db: DBSession,
    current_user: CurrentUser,
    status_filter: LeaveStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    items = leave_service.list_leaves(db, status_filter=status_filter)
    total = len(items)
    start = (page - 1) * page_size
    page_items = items[start : start + page_size]
    return PaginatedLeaves(
        items=[leave_service._to_response(r) for r in page_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(leave_id: int, db: DBSession, current_user: CurrentUser):
    from app.models.employee import EmployeeProfile

    req = leave_service.get_leave(db, leave_id)
    if current_user.role != UserRole.ADMIN:
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == current_user.id).first()
        if not profile or req.employee_id != profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return leave_service._to_response(req)


@router.put("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(leave_id: int, payload: LeaveActionRequest, db: DBSession, admin: RequireAdmin):
    req = leave_service.approve_leave(db, leave_id, payload.comment, admin)
    return leave_service._to_response(req)


@router.put("/{leave_id}/reject", response_model=LeaveResponse)
def reject_leave(leave_id: int, payload: LeaveActionRequest, db: DBSession, admin: RequireAdmin):
    req = leave_service.reject_leave(db, leave_id, payload.comment, admin)
    return leave_service._to_response(req)
