"""Shared enumerations."""

import enum


class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"


class LeaveType(str, enum.Enum):
    PAID = "PAID"
    SICK = "SICK"
    UNPAID = "UNPAID"


class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class NotificationType(str, enum.Enum):
    LEAVE_SUBMITTED = "LEAVE_SUBMITTED"
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    ATTENDANCE_REMINDER = "ATTENDANCE_REMINDER"
    HR_ALERT = "HR_ALERT"
    AI_ALERT = "AI_ALERT"


class ActivityAction(str, enum.Enum):
    LOGIN = "LOGIN"
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    LEAVE_APPLIED = "LEAVE_APPLIED"
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    PAYROLL_UPDATED = "PAYROLL_UPDATED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    EMPLOYEE_CREATED = "EMPLOYEE_CREATED"
    EMPLOYEE_DELETED = "EMPLOYEE_DELETED"
