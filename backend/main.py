import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# M1003 - Firewall: simple in-memory rate limiting per client IP
_rate_limit_store: defaultdict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW = 60       # seconds
_RATE_LIMIT_MAX_REQUESTS = 100  # max requests per window per IP


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Reject requests that exceed the per-IP rate limit (M1003 - Firewall)."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW

    # Discard timestamps outside the current window
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if ts > window_start
    ]

    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests. Please slow down."},
            headers={"Retry-After": str(_RATE_LIMIT_WINDOW)},
        )

    _rate_limit_store[client_ip].append(now)
    return await call_next(request)

# Enable CORS
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
