"""Analytics API routes."""

from fastapi import APIRouter, Query

from app.api.deps import DBSession, RequireAdmin
from app.schemas.analytics import AnalyticsDashboardResponse, TeamAvailabilityResponse
from app.services import analytics_service
from app.services.ai_bridge import get_engine
from app.services.analytics_bridge import build_report

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def analytics_dashboard(db: DBSession, _: RequireAdmin):
    return analytics_service.get_dashboard_stats(db)


@router.get("/team-availability", response_model=TeamAvailabilityResponse)
def team_availability(
    db: DBSession,
    _: RequireAdmin,
    department: str = Query("Engineering"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
):
    return analytics_service.get_team_availability(db, department, start_date, end_date)


@router.get("/reports/{report_type}")
def analytics_report(report_type: str, db: DBSession, _: RequireAdmin):
    data = analytics_service._collect_structured_data(db)
    ai = get_engine()
    data["anomalies"] = [a.model_dump() for a in ai.detect_anomalies(analytics_service.fetch_attendance_for_ai(db))]
    data["risk_signals"] = analytics_service.compute_risk_signals(db)
    return build_report(report_type, data)
