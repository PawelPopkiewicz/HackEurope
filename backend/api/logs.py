import json
import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/stream")
async def stream_cowrie_logs(request: Request):
    """
    SSE endpoint for real-time Cowrie JSON logs.
    """
    async def log_generator():
        while True:
            if await request.is_disconnected():
                logger.info("Client disconnected from /logs/stream")
                break
                
            demo_data = {
                "type": "cowrie_log",
                "eventid": "cowrie.session.connect",
                "src_ip": "192.168.1.100",
                "message": "New connection attempt detected",
                "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            yield f"data: {json.dumps(demo_data)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(log_generator(), media_type="text/event-stream")
