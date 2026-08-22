"""HR-specific routes."""

from fastapi import APIRouter

from app.api.deps import DBSession, RequireAdmin
from app.schemas.employee import Employee360Response
from app.services import analytics_service, employee_service

router = APIRouter(prefix="/hr", tags=["HR"])


@router.get("/priority-queue")
def priority_queue(db: DBSession, _: RequireAdmin):
    """WHAT NEEDS YOUR ATTENTION TODAY — ranked HR priority queue."""
    return analytics_service.get_priority_queue(db)


@router.get("/employees/{employee_id}/360", response_model=Employee360Response)
def employee_360(employee_id: str, db: DBSession, _: RequireAdmin):
    """Employee 360 — profile, trends, anomalies, risk signals, recommendations."""
    return employee_service.get_employee_360(db, employee_id)
