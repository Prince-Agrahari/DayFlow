"""Attendance routes — paths match docs/api-contract.md."""

from fastapi import APIRouter, Query

from app.api.deps import CurrentEmployee, CurrentUser, DBSession, RequireAdmin
from app.schemas.attendance import AttendancePeriodResponse, AttendanceResponse, CheckInRequest, PaginatedAttendance
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in", response_model=AttendanceResponse, status_code=201)
def check_in(payload: CheckInRequest, db: DBSession, profile: CurrentEmployee, current_user: CurrentUser):
    record = attendance_service.check_in(db, profile, current_user, payload.notes)
    return attendance_service._attendance_response(record)


@router.post("/check-out", response_model=AttendanceResponse)
def check_out(db: DBSession, profile: CurrentEmployee, current_user: CurrentUser):
    record = attendance_service.check_out(db, profile, current_user)
    return attendance_service._attendance_response(record)


@router.get("/me", response_model=AttendancePeriodResponse)
def my_attendance(db: DBSession, profile: CurrentEmployee, period: str = Query("weekly", pattern="^(daily|weekly|monthly)$")):
    return attendance_service.get_attendance_for_profile(db, profile, period)


@router.get("/summary", response_model=AttendancePeriodResponse)
def attendance_summary(db: DBSession, profile: CurrentEmployee, period: str = Query("monthly", pattern="^(daily|weekly|monthly)$")):
    return attendance_service.get_attendance_for_profile(db, profile, period)


@router.get("", response_model=PaginatedAttendance)
def list_attendance(
    db: DBSession,
    _: RequireAdmin,
    employee_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    items, total = attendance_service.list_all_attendance(db, employee_code=employee_id, page=page, page_size=page_size)
    return PaginatedAttendance(
        items=[attendance_service._attendance_response(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/all", response_model=PaginatedAttendance)
def all_attendance(
    db: DBSession,
    _: RequireAdmin,
    employee_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    items, total = attendance_service.list_all_attendance(db, employee_code=employee_id, page=page, page_size=page_size)
    return PaginatedAttendance(
        items=[attendance_service._attendance_response(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{employee_id}", response_model=AttendancePeriodResponse)
def employee_attendance(employee_id: str, db: DBSession, _: RequireAdmin, period: str = Query("monthly", pattern="^(daily|weekly|monthly)$")):
    return attendance_service.get_employee_attendance(db, employee_id, period)
