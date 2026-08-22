"""AI intelligence API routes."""

import json

from fastapi import APIRouter, HTTPException, Query, status

from app.api.ai_auth import CurrentUser, RequireAdmin
from app.schemas.ai import (
    AnomalyRequest,
    AnomalyResponse,
    AssistantBody,
    CopilotBody,
    LeaveRecommendationBody,
)
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
def list_anomalies(_: RequireAdmin):
    """Contract-compatible GET — supply records via POST /anomaly for detection."""
    return AnomalyResponse(items=[])


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
def risk_signals(_: RequireAdmin):
    return {"items": []}


@router.post("/leave-recommendation")
def leave_recommendation(payload: LeaveRecommendationBody, current_user: CurrentUser):
    if current_user.role != "ADMIN" and current_user.employee_id != payload.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    engine = get_engine()
    request = build_leave_request(payload.model_dump())
    result = engine.recommend_leave(request)
    return result.model_dump()


@router.post("/copilot")
def copilot(payload: CopilotBody, _: RequireAdmin):
    engine = get_engine()
    result = engine.ask_copilot(payload.question, payload.structured_context)
    return result.model_dump()


@router.post("/assistant")
def assistant(payload: AssistantBody, current_user: CurrentUser):
    if not payload.employee_context:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="employee_context required")
    ctx_employee = payload.employee_context.get("employee_id")
    if current_user.role != "ADMIN":
        if ctx_employee and current_user.employee_id and ctx_employee != current_user.employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to other employee data")
        payload.employee_context["employee_id"] = current_user.employee_id or ctx_employee
    engine = get_engine()
    result = engine.ask_assistant(payload.question, payload.employee_context)
    return result.model_dump()
