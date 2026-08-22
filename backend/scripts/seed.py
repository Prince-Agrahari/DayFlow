"""Demo seed data — 1 admin + 20 employees across 5 departments."""

from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models.attendance import Attendance
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.enums import (
    AttendanceStatus,
    EmploymentStatus,
    LeaveStatus,
    LeaveType,
    NotificationType,
    UserRole,
)
from app.models.leave_request import LeaveBalance, LeaveRequest
from app.models.notification import Notification
from app.models.payroll import Payroll
from app.models.user import User

DEPARTMENTS = ["Engineering", "HR", "Finance", "Marketing", "Design"]

EMPLOYEES = [
    ("Jane Doe", "jane@dayflow.com", "Engineering", "Senior Software Engineer", 95000),
    ("Michael Chen", "michael@dayflow.com", "Engineering", "Tech Lead", 115000),
    ("John Smith", "john@dayflow.com", "Engineering", "Backend Developer", 90000),
    ("Priya Patel", "priya@dayflow.com", "Engineering", "Frontend Developer", 88000),
    ("David Kim", "david@dayflow.com", "Engineering", "DevOps Engineer", 92000),
    ("Lisa Wang", "lisa@dayflow.com", "Engineering", "QA Engineer", 82000),
    ("Alice Johnson", "alice@dayflow.com", "HR", "HR Specialist", 72000),
    ("Tom Harris", "tom@dayflow.com", "HR", "Recruiter", 68000),
    ("Robert Williams", "robert@dayflow.com", "Finance", "Financial Analyst", 88000),
    ("Emily Davis", "emily@dayflow.com", "Finance", "Accountant", 78000),
    ("Sarah Mitchell", "admin@dayflow.com", "HR", "HR Director", 105000),
    ("Chris Brown", "chris@dayflow.com", "Finance", "Controller", 98000),
    ("Maria Garcia", "maria@dayflow.com", "Finance", "Payroll Specialist", 75000),
    ("James Wilson", "james@dayflow.com", "Marketing", "Marketing Manager", 92000),
    ("Olivia Taylor", "olivia@dayflow.com", "Marketing", "Content Strategist", 72000),
    ("Ethan Moore", "ethan@dayflow.com", "Marketing", "SEO Specialist", 70000),
    ("Sophia Lee", "sophia@dayflow.com", "Marketing", "Brand Manager", 85000),
    ("Noah Martinez", "noah@dayflow.com", "Design", "UX Designer", 85000),
    ("Ava Anderson", "ava@dayflow.com", "Design", "UI Designer", 80000),
    ("Liam Thomas", "liam@dayflow.com", "Design", "Product Designer", 87000),
    ("Mia Jackson", "mia@dayflow.com", "Design", "Design Lead", 95000),
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Database already seeded — skipping.")
            return

        for name in DEPARTMENTS:
            db.add(Department(name=name, description=f"{name} department"))

        admin = User(
            email="admin@dayflow.com",
            password_hash=hash_password("admin123"),
            full_name="Sarah Mitchell",
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.flush()

        hr_dept = db.query(Department).filter(Department.name == "HR").first()
        admin_profile = EmployeeProfile(
            user_id=admin.id,
            employee_id="EMP000",
            department="HR",
            department_id=hr_dept.id if hr_dept else None,
            designation="HR Director",
            joining_date=date(2020, 1, 15),
            salary=Decimal("105000"),
        )
        db.add(admin_profile)
        db.flush()

        db.add(Payroll(
            employee_id=admin_profile.id, base_salary=Decimal("105000"),
            basic=Decimal("68000"), hra=Decimal("19000"), allowances=Decimal("13000"),
            deductions=Decimal("5500"), net_salary=Decimal("99500"),
        ))

        emp_num = 1
        today = date.today()
        for full_name, email, dept, designation, salary in EMPLOYEES:
            if email == "admin@dayflow.com":
                continue
            role = UserRole.EMPLOYEE
            user = User(
                email=email,
                password_hash=hash_password("employee123"),
                full_name=full_name,
                role=role,
            )
            db.add(user)
            db.flush()

            department = db.query(Department).filter(Department.name == dept).first()
            profile = EmployeeProfile(
                user_id=user.id,
                employee_id=f"EMP{emp_num:03d}",
                department=dept,
                department_id=department.id if department else None,
                designation=designation,
                joining_date=today - timedelta(days=random.randint(180, 900)),
                employment_status=EmploymentStatus.ACTIVE,
                salary=Decimal(str(salary)),
            )
            db.add(profile)
            db.flush()

            s = Decimal(str(salary))
            db.add(Payroll(
                employee_id=profile.id, base_salary=s,
                basic=s * Decimal("0.65"), hra=s * Decimal("0.18"),
                allowances=s * Decimal("0.12"), deductions=s * Decimal("0.05"),
                net_salary=s * Decimal("0.94"),
            ))

            year = today.year
            for lt, total in [(LeaveType.PAID, 20), (LeaveType.SICK, 10), (LeaveType.UNPAID, 5)]:
                used = random.choice([0, 2, 4, 6])
                db.add(LeaveBalance(employee_id=profile.id, leave_type=lt, total_days=total, used_days=used, year=year))

            for day_offset in range(60):
                d = today - timedelta(days=day_offset)
                if d.weekday() >= 5:
                    continue
                absent = random.random() < 0.07
                if absent:
                    db.add(Attendance(employee_id=profile.id, date=d, status=AttendanceStatus.ABSENT))
                    continue
                check_in = datetime(d.year, d.month, d.day, random.randint(8, 10), random.randint(0, 59), tzinfo=timezone.utc)
                hours = random.uniform(7.5, 9.5)
                check_out = check_in + timedelta(hours=hours)
                is_late = check_in.hour >= 9 and check_in.minute > 15
                db.add(Attendance(
                    employee_id=profile.id, date=d,
                    check_in_time=check_in, check_out_time=check_out,
                    working_hours=Decimal(str(round(hours, 2))),
                    status=AttendanceStatus.PRESENT, is_late=is_late,
                ))

            if random.random() < 0.4:
                start = today + timedelta(days=random.randint(5, 30))
                end = start + timedelta(days=random.randint(1, 3))
                status = random.choice([LeaveStatus.PENDING, LeaveStatus.APPROVED, LeaveStatus.REJECTED])
                db.add(LeaveRequest(
                    employee_id=profile.id, leave_type=LeaveType.PAID,
                    start_date=start, end_date=end,
                    reason=random.choice(["Family vacation", "Medical appointment", "Personal matter", "Travel"]),
                    status=status,
                    admin_comment="Approved" if status == LeaveStatus.APPROVED else ("Rejected due to workload" if status == LeaveStatus.REJECTED else None),
                ))

            db.add(Notification(
                user_id=user.id, type=NotificationType.ATTENDANCE_REMINDER,
                title="Welcome to DayFlow",
                message=f"Welcome {full_name}! Your DayFlow account is ready.",
            ))
            emp_num += 1

        db.commit()
        print(f"Seeded 1 admin + {emp_num - 1} employees with attendance, leave, payroll, and notifications.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
