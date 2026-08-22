"""Minimal auth dependencies for AI routes only."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class TokenUser(BaseModel):
    id: str
    role: str
    employee_id: str | None = None


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenUser:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
        return TokenUser(
            id=str(user_id),
            role=str(payload.get("role", "EMPLOYEE")),
            employee_id=payload.get("employee_id"),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUser = Annotated[TokenUser, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> TokenUser:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


RequireAdmin = Annotated[TokenUser, Depends(require_admin)]
