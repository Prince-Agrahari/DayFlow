"""Health check routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check — no authentication required."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": "not_connected",  # Updated when DB layer is implemented
    }
