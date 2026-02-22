from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Returns a simple health status for the service."""
    return {"status": "ok"}
