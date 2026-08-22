"""Basic analytics aggregations from database (contract stubs)."""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.employee import EmployeeProfile
from app.models.enums import AttendanceStatus, EmploymentStatus, LeaveStatus
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.schemas.analytics import AnalyticsDashboardResponse, DepartmentStat, TeamAvailabilityDay, TeamAvailabilityResponse, TrendPoint


def get_dashboard_stats(db: Session) -> AnalyticsDashboardResponse:
    today = date.today()
    total = db.query(EmployeeProfile).filter(EmployeeProfile.employment_status == EmploymentStatus.ACTIVE).count()

    present_today = (
        db.query(Attendance)
        .filter(Attendance.date == today, Attendance.status == AttendanceStatus.PRESENT)
        .count()
    )
    absent_today = (
        db.query(Attendance)
        .filter(Attendance.date == today, Attendance.status == AttendanceStatus.ABSENT)
        .count()
    )
    on_leave = db.query(LeaveRequest).filter(
        LeaveRequest.status == LeaveStatus.APPROVED,
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today,
    ).count()
    pending = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.PENDING).count()

    month_start = today.replace(day=1)
    month_records = db.query(Attendance).filter(Attendance.date >= month_start, Attendance.date <= today).count()
    month_present = (
        db.query(Attendance)
        .filter(Attendance.date >= month_start, Attendance.date <= today, Attendance.status == AttendanceStatus.PRESENT)
        .count()
    )
    attendance_rate = (month_present / month_records) if month_records else 0.0

    dept_stats = (
        db.query(EmployeeProfile.department, func.count(EmployeeProfile.id))
        .group_by(EmployeeProfile.department)
        .all()
    )
    department_absenteeism = [
        DepartmentStat(department=d, rate=round(absent_today / max(total, 1) * 0.1, 2), count=c)
        for d, c in dept_stats
    ]

    payroll_total = db.query(func.coalesce(func.sum(Payroll.net_salary), 0)).scalar() or 0
    avg_salary = db.query(func.coalesce(func.avg(Payroll.base_salary), 0)).scalar() or 0

    return AnalyticsDashboardResponse(
        total_employees=total,
        attendance_rate=round(attendance_rate, 2),
        present_today=present_today,
        absent_today=absent_today,
        on_leave_today=on_leave,
        pending_leaves=pending,
        department_absenteeism=department_absenteeism,
        monthly_attendance_trend=[TrendPoint(month=today.strftime("%Y-%m"), rate=attendance_rate)],
        leave_trend=[TrendPoint(month=today.strftime("%Y-%m"), count=pending)],
        payroll_summary={"total_monthly": float(payroll_total), "average_salary": float(avg_salary)},
        risk_distribution={"LOW": max(total - 4, 0), "MEDIUM": 3, "HIGH": 1},
        anomaly_distribution={"LOW": max(total - 2, 0), "MEDIUM": 1, "HIGH": 1},
    )


def get_team_availability(db: Session, department: str, days: int = 7) -> TeamAvailabilityResponse:
    today = date.today()
    dept_employees = db.query(EmployeeProfile).filter(EmployeeProfile.department == department).count() or 1
    daily: list[TeamAvailabilityDay] = []

    for i in range(days):
        d = today + timedelta(days=i)
        on_leave = db.query(LeaveRequest).join(EmployeeProfile).filter(
            EmployeeProfile.department == department,
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.start_date <= d,
            LeaveRequest.end_date >= d,
        ).count()
        absent = db.query(Attendance).join(EmployeeProfile).filter(
            EmployeeProfile.department == department,
            Attendance.date == d,
            Attendance.status == AttendanceStatus.ABSENT,
        ).count()
        available = max(dept_employees - on_leave - absent, 0)
        daily.append(
            TeamAvailabilityDay(
                date=d.isoformat(),
                available=available,
                on_leave=on_leave,
                absent=absent,
                availability_rate=round(available / dept_employees, 2),
            )
        )

    return TeamAvailabilityResponse(
        department=department,
        start_date=today.isoformat(),
        end_date=(today + timedelta(days=days - 1)).isoformat(),
        total_employees=dept_employees,
        daily_availability=daily,
    )
