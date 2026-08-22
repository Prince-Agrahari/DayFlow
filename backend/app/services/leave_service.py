"""Leave management service."""

from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction, LeaveStatus, NotificationType
from app.models.leave_request import LeaveBalance, LeaveRequest
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.notification_service import create_notification, notify_admins
from app.schemas.leave import LeaveBalanceResponse, LeaveCreateRequest, LeaveResponse


def _leave_days(start: date, end: date) -> float:
    return float((end - start).days + 1)


def _to_response(req: LeaveRequest) -> LeaveResponse:
    return LeaveResponse(
        id=req.id,
        employee_id=req.employee.employee_id,
        employee_name=req.employee.user.full_name,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        reason=req.reason,
        status=req.status,
        admin_comment=req.admin_comment,
        created_at=req.created_at,
    )


def apply_leave(db: Session, profile: EmployeeProfile, payload: LeaveCreateRequest, actor: User) -> LeaveRequest:
    req = LeaveRequest(
        employee_id=profile.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(req)
    db.flush()

    create_notification(
        db,
        user_id=profile.user_id,
        type=NotificationType.LEAVE_SUBMITTED,
        title="Leave Request Submitted",
        message=f"Your {payload.leave_type.value} leave request for {payload.start_date} to {payload.end_date} is pending.",
        metadata={"leave_id": req.id},
    )
    notify_admins(
        db,
        type=NotificationType.HR_ALERT,
        title="New Leave Request",
        message=f"{profile.user.full_name} submitted a leave request.",
        metadata={"leave_id": req.id, "employee_id": profile.employee_id},
    )
    log_activity(db, user_id=actor.id, action=ActivityAction.LEAVE_APPLIED, description="Leave applied", entity_type="leave", entity_id=str(req.id))
    db.commit()
    db.refresh(req)
    return req


def get_my_leaves(db: Session, profile: EmployeeProfile) -> list[LeaveRequest]:
    return (
        db.query(LeaveRequest)
        .options(joinedload(LeaveRequest.employee).joinedload(EmployeeProfile.user))
        .filter(LeaveRequest.employee_id == profile.id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )


def list_leaves(db: Session, *, status_filter: LeaveStatus | None = None) -> list[LeaveRequest]:
    query = db.query(LeaveRequest).options(joinedload(LeaveRequest.employee).joinedload(EmployeeProfile.user))
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    return query.order_by(LeaveRequest.created_at.desc()).all()


def get_leave(db: Session, leave_id: int) -> LeaveRequest:
    req = (
        db.query(LeaveRequest)
        .options(joinedload(LeaveRequest.employee).joinedload(EmployeeProfile.user))
        .filter(LeaveRequest.id == leave_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    return req


def approve_leave(db: Session, leave_id: int, comment: str, admin: User) -> LeaveRequest:
    req = get_leave(db, leave_id)
    if req.status != LeaveStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave request is not pending")
    req.status = LeaveStatus.APPROVED
    req.admin_comment = comment
    req.reviewed_by = admin.id
    req.reviewed_at = datetime.now(timezone.utc)

    days = _leave_days(req.start_date, req.end_date)
    balance = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == req.employee_id, LeaveBalance.leave_type == req.leave_type, LeaveBalance.year == date.today().year)
        .first()
    )
    if balance:
        balance.used_days = float(balance.used_days) + days

    create_notification(
        db,
        user_id=req.employee.user_id,
        type=NotificationType.LEAVE_APPROVED,
        title="Leave Approved",
        message=f"Your leave request for {req.start_date} to {req.end_date} was approved.",
        metadata={"leave_id": req.id},
    )
    log_activity(db, user_id=admin.id, action=ActivityAction.LEAVE_APPROVED, description=f"Approved leave {req.id}", entity_type="leave", entity_id=str(req.id))
    db.commit()
    db.refresh(req)
    return req


def reject_leave(db: Session, leave_id: int, comment: str, admin: User) -> LeaveRequest:
    req = get_leave(db, leave_id)
    if req.status != LeaveStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave request is not pending")
    req.status = LeaveStatus.REJECTED
    req.admin_comment = comment
    req.reviewed_by = admin.id
    req.reviewed_at = datetime.now(timezone.utc)

    create_notification(
        db,
        user_id=req.employee.user_id,
        type=NotificationType.LEAVE_REJECTED,
        title="Leave Rejected",
        message=f"Your leave request for {req.start_date} to {req.end_date} was rejected.",
        metadata={"leave_id": req.id},
    )
    log_activity(db, user_id=admin.id, action=ActivityAction.LEAVE_REJECTED, description=f"Rejected leave {req.id}", entity_type="leave", entity_id=str(req.id))
    db.commit()
    db.refresh(req)
    return req


def get_leave_balances(db: Session, profile: EmployeeProfile) -> list[LeaveBalanceResponse]:
    year = date.today().year
    balances = db.query(LeaveBalance).filter(LeaveBalance.employee_id == profile.id, LeaveBalance.year == year).all()
    return [
        LeaveBalanceResponse(
            leave_type=b.leave_type,
            total_days=float(b.total_days),
            used_days=float(b.used_days),
            remaining_days=float(b.total_days) - float(b.used_days),
        )
        for b in balances
    ]
