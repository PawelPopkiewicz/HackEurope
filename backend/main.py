import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pen Test Agent Backend",
    description="Modular backend for Honeypot monitoring, threat classification, and AI remediation.",
    version="1.0.0"
)

# Enable CORS — restrict to known origins (M1051 - Limit Access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
