"""Payroll model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payroll(Base):
    __tablename__ = "payroll"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    pay_frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="MONTHLY")
    basic: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    hra: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("EmployeeProfile", back_populates="payroll")
