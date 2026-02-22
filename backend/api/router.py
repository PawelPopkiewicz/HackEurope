from fastapi import APIRouter
from backend.api import logs, classification, fixer, dashboard, health

api_router = APIRouter()

api_router.include_router(logs.router)
api_router.include_router(classification.router)
api_router.include_router(fixer.router)
api_router.include_router(dashboard.router)
api_router.include_router(health.router)
