"""AI intelligence API routes."""

import json

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentEmployee, CurrentUser, DBSession, RequireAdmin
from app.models.employee import EmployeeProfile
from app.models.enums import UserRole
from app.schemas.ai import AnomalyRequest, AnomalyResponse, AssistantBody, CopilotBody, LeaveRecommendationBody
from app.services.ai_bridge import build_leave_request, get_engine

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


@router.post("/anomaly", response_model=AnomalyResponse)
def detect_anomalies(payload: AnomalyRequest, _: RequireAdmin):
    if not payload.attendance_records:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="attendance_records required")
    engine = get_engine()
    items = [r.model_dump() for r in engine.detect_anomalies(payload.attendance_records)]
    return AnomalyResponse(items=items)


@router.get("/anomalies", response_model=AnomalyResponse)
def list_anomalies(db: DBSession, _: RequireAdmin):
    from app.services import analytics_service

    records = analytics_service.fetch_attendance_for_ai(db)
    engine = get_engine()
    items = [r.model_dump() for r in engine.detect_anomalies(records)]
    return AnomalyResponse(items=items)


@router.get("/employee/{employee_id}/risk")
def employee_risk(
    employee_id: str,
    _: RequireAdmin,
    metrics: str | None = Query(default=None, description="Optional JSON metrics payload"),
):
    data: dict = {}
    if metrics:
        try:
            data = json.loads(metrics)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid metrics JSON") from exc
    data.setdefault("employee_name", employee_id)
    engine = get_engine()
    result = engine.calculate_risk(employee_id, data)
    return result.model_dump()


@router.get("/risk-signals")
def risk_signals(db: DBSession, _: RequireAdmin):
    from app.services import analytics_service

    signals = analytics_service.compute_risk_signals(db)
    return {"items": signals}


@router.post("/leave-recommendation")
def leave_recommendation(payload: LeaveRecommendationBody, db: DBSession, current_user: CurrentUser):
    if current_user.role == UserRole.EMPLOYEE:
        own = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == current_user.id).first()
        if not own or own.employee_id != payload.employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    engine = get_engine()
    request = build_leave_request(payload.model_dump())
    result = engine.recommend_leave(request)
    return result.model_dump()


@router.post("/copilot")
def copilot(payload: CopilotBody, db: DBSession, _: RequireAdmin):
    from app.services import analytics_service

    if not payload.structured_context:
        payload.structured_context = analytics_service.build_copilot_context(db)
    engine = get_engine()
    result = engine.ask_copilot(payload.question, payload.structured_context)
    return result.model_dump()


@router.post("/assistant")
def assistant(payload: AssistantBody, db: DBSession, current_user: CurrentUser, profile: CurrentEmployee):
    from app.services import analytics_service

    if payload.employee_context:
        ctx_employee = payload.employee_context.get("employee_id")
        if current_user.role == UserRole.EMPLOYEE and ctx_employee and ctx_employee != profile.employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to other employee data")
        context = payload.employee_context
    else:
        context = analytics_service.build_employee_context(db, profile)
    engine = get_engine()
    result = engine.ask_assistant(payload.question, context)
    return result.model_dump()
