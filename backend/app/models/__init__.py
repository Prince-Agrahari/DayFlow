"""ORM model registry."""

from app.models.activity_log import ActivityLog
from app.models.attendance import Attendance
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.leave_request import LeaveBalance, LeaveRequest
from app.models.notification import Notification
from app.models.payroll import Payroll
from app.models.user import User

__all__ = [
    "User",
    "EmployeeProfile",
    "Department",
    "Attendance",
    "LeaveRequest",
    "LeaveBalance",
    "Payroll",
    "Notification",
    "ActivityLog",
]
