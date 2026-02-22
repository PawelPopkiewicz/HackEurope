from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.logger import setup_logging
from backend.config import settings
from backend.constants import API_TITLE, API_DESCRIPTION, API_VERSION
from backend.api.router import api_router

# Setup logging
logger = setup_logging(__name__, level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

# Validate configuration on startup
if not settings.validate():
    logger.warning("Configuration validation found issues. Some features may not work.")

# Log startup information
settings.log_config()

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Rate limiter (M1033 - System Access Control: limit request rates to prevent brute-force)
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS with restricted origins (M1033 - System Access Control)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Pen Test Agent Backend",
        "endpoints": [
            "/api/v1/logs/stream",
            "/api/v1/classification/stream",
            "/api/v1/fixing/stream"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )
