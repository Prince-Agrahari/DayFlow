"""HR-specific routes."""

from fastapi import APIRouter

from app.api.deps import DBSession, RequireAdmin
from app.schemas.analytics import AnalyticsDashboardResponse

router = APIRouter(prefix="/hr", tags=["HR"])


@router.get("/priority-queue")
def priority_queue(db: DBSession, _: RequireAdmin):
    """Stub priority queue — full ranking delegated to analytics module."""
    from datetime import datetime

    from app.services import analytics_service

    stats = analytics_service.get_dashboard_stats(db)
    items = []
    if stats.pending_leaves:
        items.append({
            "priority": "MEDIUM",
            "title": "Pending Leave Requests",
            "description": f"{stats.pending_leaves} leave requests awaiting review",
            "employee_id": "N/A",
            "employee_name": "Multiple",
            "reason": "Administrative backlog",
            "recommended_action": "Review and respond to pending leave requests",
        })
    return {"generated_at": datetime.utcnow().isoformat() + "Z", "items": items}
