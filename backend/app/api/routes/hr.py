"""HR-specific routes."""

from fastapi import APIRouter

from app.api.deps import DBSession, RequireAdmin
from app.services import analytics_service

router = APIRouter(prefix="/hr", tags=["HR"])


@router.get("/priority-queue")
def priority_queue(db: DBSession, _: RequireAdmin):
    """WHAT NEEDS YOUR ATTENTION TODAY — ranked HR priority queue."""
    return analytics_service.get_priority_queue(db)
