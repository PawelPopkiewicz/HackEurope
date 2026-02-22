from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

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
    version=API_VERSION,
    # Disable the interactive docs in production to reduce attack surface
    docs_url="/docs" if settings.API_DEBUG else None,
    redoc_url="/redoc" if settings.API_DEBUG else None,
)

# Restrict accepted Host headers to prevent Host-header injection
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", settings.API_HOST]
    if settings.API_DEBUG
    else ["localhost", "127.0.0.1", settings.API_HOST],
)

# Enable CORS with explicit allow-list (never wildcard in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
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
