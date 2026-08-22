"""Authentication routes."""

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: SignupRequest, db: DBSession):
    user = auth_service.signup(db, payload)
    return auth_service.get_me(db, user)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: DBSession):
    return auth_service.login(db, payload.email, payload.password)


@router.get("/me", response_model=UserResponse)
def me(db: DBSession, current_user: CurrentUser):
    return auth_service.get_me(db, current_user)
