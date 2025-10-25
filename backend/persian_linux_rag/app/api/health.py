from fastapi import APIRouter
from ..core.config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True, "app": settings.APP_NAME, "mode": settings.MODE}
