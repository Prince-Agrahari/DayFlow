"""Leave request and balance models."""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import LeaveStatus, LeaveType


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(Enum(LeaveType, name="leave_type", native_enum=False), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeaveStatus] = mapped_column(Enum(LeaveStatus, name="leave_status", native_enum=False), nullable=False, default=LeaveStatus.PENDING)
    admin_comment: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("EmployeeProfile", back_populates="leave_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("employee_id", "leave_type", "year", name="uq_leave_balance"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    leave_type: Mapped[LeaveType] = mapped_column(Enum(LeaveType, name="leave_type", native_enum=False), nullable=False)
    total_days: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False, default=0)
    used_days: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False, default=0)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    employee = relationship("EmployeeProfile", back_populates="leave_balances")
