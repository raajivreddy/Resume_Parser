from fastapi import APIRouter
from app.utils.config import settings

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

@router.get("/version", tags=["System"])
async def get_version():
    return {
        "version": settings.app_version
    }
