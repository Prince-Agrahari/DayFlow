"""Analytics API contract routes."""

from fastapi import APIRouter, Query

from app.api.deps import DBSession, RequireAdmin
from app.schemas.analytics import AnalyticsDashboardResponse, TeamAvailabilityResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def analytics_dashboard(db: DBSession, _: RequireAdmin):
    return analytics_service.get_dashboard_stats(db)


@router.get("/team-availability", response_model=TeamAvailabilityResponse)
def team_availability(db: DBSession, _: RequireAdmin, department: str = Query("Engineering")):
    return analytics_service.get_team_availability(db, department)
