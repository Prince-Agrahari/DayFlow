"""Health check routes."""

from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()


@router.get("/health")
async def health_check():
    db_status = "not_connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "not_connected"

    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": db_status,
    }
