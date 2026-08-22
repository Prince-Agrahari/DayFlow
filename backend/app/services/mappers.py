"""Map ORM models to API response helpers."""

from app.models.employee import EmployeeProfile
from app.models.enums import UserRole
from app.models.payroll import Payroll
from app.schemas.employee import EmployeeResponse
from app.schemas.payroll import PayrollResponse, SalaryStructure


def employee_to_response(profile: EmployeeProfile) -> EmployeeResponse:
    return EmployeeResponse(
        id=profile.id,
        employee_id=profile.employee_id,
        full_name=profile.user.full_name,
        email=profile.user.email,
        phone=profile.phone,
        address=profile.address,
        department=profile.department,
        designation=profile.designation,
        joining_date=profile.joining_date,
        employment_status=profile.employment_status,
        salary=profile.salary,
        profile_picture=profile.profile_picture,
        role=profile.user.role,
    )


def payroll_to_response(payroll: Payroll, employee_name: str | None = None) -> PayrollResponse:
    return PayrollResponse(
        employee_id=payroll.employee.employee_id,
        employee_name=employee_name or payroll.employee.user.full_name,
        base_salary=payroll.base_salary,
        currency=payroll.currency,
        pay_frequency=payroll.pay_frequency,
        structure=SalaryStructure(
            basic=payroll.basic,
            hra=payroll.hra,
            allowances=payroll.allowances,
            deductions=payroll.deductions,
        ),
        net_salary=payroll.net_salary,
    )
