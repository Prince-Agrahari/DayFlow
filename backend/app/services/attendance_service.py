"""Attendance business logic."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.attendance import Attendance
from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction, AttendanceStatus
from app.models.user import User
from app.services.activity_service import log_activity
from app.schemas.attendance import AttendancePeriodResponse, AttendanceResponse, AttendanceSummary

WORK_START_HOUR = 9
WORK_START_MINUTE = 15


def _attendance_response(record: Attendance) -> AttendanceResponse:
    return AttendanceResponse(
        id=record.id,
        employee_id=record.employee.employee_id,
        date=record.date,
        check_in_time=record.check_in_time,
        check_out_time=record.check_out_time,
        working_hours=record.working_hours,
        status=record.status,
        is_late=record.is_late,
        notes=record.notes,
    )


def check_in(db: Session, profile: EmployeeProfile, actor: User, notes: str | None = None) -> Attendance:
    today = date.today()
    existing = db.query(Attendance).filter(Attendance.employee_id == profile.id, Attendance.date == today).first()
    if existing and existing.check_in_time:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already checked in today")

    now = datetime.now(timezone.utc)
    is_late = now.hour > WORK_START_HOUR or (now.hour == WORK_START_HOUR and now.minute > WORK_START_MINUTE)

    if existing:
        existing.check_in_time = now
        existing.status = AttendanceStatus.PRESENT
        existing.is_late = is_late
        existing.notes = notes
        record = existing
    else:
        record = Attendance(
            employee_id=profile.id,
            date=today,
            check_in_time=now,
            status=AttendanceStatus.PRESENT,
            is_late=is_late,
            notes=notes,
        )
        db.add(record)

    log_activity(db, user_id=actor.id, action=ActivityAction.CHECK_IN, description=f"Check-in for {profile.employee_id}", entity_type="attendance", entity_id=profile.employee_id)
    db.commit()
    db.refresh(record)
    return record


def check_out(db: Session, profile: EmployeeProfile, actor: User) -> Attendance:
    today = date.today()
    record = db.query(Attendance).filter(Attendance.employee_id == profile.id, Attendance.date == today).first()
    if not record or not record.check_in_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No check-in found for today")
    if record.check_out_time:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already checked out today")

    now = datetime.now(timezone.utc)
    record.check_out_time = now
    check_in = record.check_in_time
    if check_in.tzinfo is None:
        check_in = check_in.replace(tzinfo=timezone.utc)
    delta = now - check_in
    record.working_hours = Decimal(str(round(delta.total_seconds() / 3600, 2)))

    log_activity(db, user_id=actor.id, action=ActivityAction.CHECK_OUT, description=f"Check-out for {profile.employee_id}", entity_type="attendance", entity_id=profile.employee_id)
    db.commit()
    db.refresh(record)
    return record


def _period_range(period: str, ref: date | None = None) -> tuple[date, date]:
    ref = ref or date.today()
    if period == "daily":
        return ref, ref
    if period == "weekly":
        start = ref - timedelta(days=ref.weekday())
        return start, ref
    start = ref.replace(day=1)
    return start, ref


def get_attendance_for_profile(db: Session, profile: EmployeeProfile, period: str = "weekly") -> AttendancePeriodResponse:
    start, end = _period_range(period)
    records = (
        db.query(Attendance)
        .options(joinedload(Attendance.employee).joinedload(EmployeeProfile.user))
        .filter(Attendance.employee_id == profile.id, Attendance.date >= start, Attendance.date <= end)
        .order_by(Attendance.date.desc())
        .all()
    )
    summary = _build_summary(records)
    return AttendancePeriodResponse(
        period=period,
        start_date=start,
        end_date=end,
        records=[_attendance_response(r) for r in records],
        summary=summary,
    )


def _build_summary(records: list[Attendance]) -> AttendanceSummary:
    present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    half = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)
    leave = sum(1 for r in records if r.status == AttendanceStatus.LEAVE)
    hours = sum(float(r.working_hours or 0) for r in records)
    late = sum(1 for r in records if r.is_late)
    return AttendanceSummary(
        total_days=len(records),
        present=present,
        absent=absent,
        half_day=half,
        leave=leave,
        total_working_hours=round(hours, 2),
        late_count=late,
    )


def list_all_attendance(db: Session, *, employee_code: str | None = None, page: int = 1, page_size: int = 50) -> tuple[list[Attendance], int]:
    query = db.query(Attendance).options(joinedload(Attendance.employee).joinedload(EmployeeProfile.user))
    if employee_code:
        query = query.join(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_code)
    total = query.count()
    items = query.order_by(Attendance.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_employee_attendance(db: Session, employee_code: str, period: str = "monthly") -> AttendancePeriodResponse:
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_code).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return get_attendance_for_profile(db, profile, period)
