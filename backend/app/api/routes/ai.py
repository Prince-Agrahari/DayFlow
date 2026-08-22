"""AI API contract routes — modular stubs."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentEmployee, CurrentUser, DBSession, RequireAdmin
from app.models.enums import UserRole
from app.schemas.ai import (
    AnomalyItem,
    AssistantRequest,
    AssistantResponse,
    CopilotRequest,
    CopilotResponse,
    LeaveRecommendationRequest,
    LeaveRecommendationResponse,
    RiskSignalItem,
)
from app.services.ai_contract_service import get_ai_engine

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/anomalies", response_model=dict)
def get_anomalies(db: DBSession, _: RequireAdmin):
    engine = get_ai_engine()
    items: list[AnomalyItem] = engine.detect_attendance_anomalies({"source": "backend_stub"})
    return {"items": items}


@router.get("/risk-signals", response_model=dict)
def get_risk_signals(db: DBSession, _: RequireAdmin):
    engine = get_ai_engine()
    items: list[RiskSignalItem] = engine.calculate_risk_signals({"source": "backend_stub"})
    return {"items": items}


@router.post("/leave-recommendation", response_model=LeaveRecommendationResponse)
def leave_recommendation(payload: LeaveRecommendationRequest, db: DBSession, current_user: CurrentUser):
    from app.models.employee import EmployeeProfile

    if current_user.role == UserRole.EMPLOYEE:
        own = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == current_user.id).first()
        if not own or own.employee_id != payload.employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    engine = get_ai_engine()
    return engine.recommend_leave({"employee_id": payload.employee_id, **payload.model_dump()})


@router.post("/copilot", response_model=CopilotResponse)
def copilot(payload: CopilotRequest, db: DBSession, _: RequireAdmin):
    engine = get_ai_engine()
    return engine.ask_copilot(payload.question, {"pending_leaves": True})


@router.post("/assistant", response_model=AssistantResponse)
def assistant(payload: AssistantRequest, db: DBSession, profile: CurrentEmployee):
    engine = get_ai_engine()
    return engine.ask_assistant(payload.question, {"employee_id": profile.employee_id})
