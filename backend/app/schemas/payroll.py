"""Payroll schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SalaryStructure(BaseModel):
    basic: Decimal
    hra: Decimal
    allowances: Decimal
    deductions: Decimal


class PayrollResponse(BaseModel):
    employee_id: str
    employee_name: str | None = None
    base_salary: Decimal
    currency: str
    pay_frequency: str
    structure: SalaryStructure
    net_salary: Decimal

    model_config = {"from_attributes": True}


class PayrollUpdateRequest(BaseModel):
    base_salary: Decimal | None = None
    basic: Decimal | None = None
    hra: Decimal | None = None
    allowances: Decimal | None = None
    deductions: Decimal | None = None
    net_salary: Decimal | None = None


class PaginatedPayroll(BaseModel):
    items: list[PayrollResponse]
    total: int
    page: int
    page_size: int


class PayrollHistoryItem(BaseModel):
    id: int
    month: str
    net_salary: Decimal
    status: str = "PAID"
