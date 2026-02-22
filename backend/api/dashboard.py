"""
Dashboard API endpoints for real-time threat intelligence streaming.
Aggregates logs, classifications, and remediation updates.
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Union, List, Dict, Any
from fastapi import APIRouter, Request, Body
from fastapi.responses import StreamingResponse

from backend.api.bus import dashboard_bus
from backend.constants import SSE_MEDIA_TYPE

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _now() -> str:
    """Get current UTC timestamp in HH:MM:SS format."""
    return datetime.now(tz=timezone.utc).strftime("%H:%M:%S")


# ── Endpoint: Push Data ────────────────────────────────────────────────────────

@router.post("/send_honeypot_json")
async def send_honeypot_json(data: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(...)) -> Dict[str, Any]:
    """
    Receive and broadcast honeypot logs to all connected dashboard clients.
    Triggers background MITRE classification.
    
    Args:
        data: Single log entry or list of log entries
    
    Returns:
        Status information about the broadcast
    """
    subs = len(dashboard_bus.subscribers)
    
    if not isinstance(data, list):
        data = [data]

    # 1. Immediate Broadcast of raw logs
    count = 0
    for item in data:
        if isinstance(item, dict) and "timestamp" not in item:
            item["timestamp"] = _now()
        await dashboard_bus.emit(item)
        count += 1

    # 2. Background Classification
    async def run_and_emit_classification(log_data: List[Dict[str, Any]]) -> None:
        """Run classification and emit results to dashboard."""
        logger.info(f"Background classification task started for {len(log_data)} logs.")
        try:
            # Import here to avoid circular imports and to allow optional components
            from backend.agents.mitre_classifier.main import classify_logs, correlate_logs, generate_agent_ticket, submit_agent_ticket
            try:
                from scripts.agent import create_github_issue
            except Exception:
                create_github_issue = None

            # 1. Classification
            results = await classify_logs(log_data)
            if results:
                for res in results:
                    res["timestamp"] = _now()
                    await dashboard_bus.emit(res)
                logger.info(f"Emitted {len(results)} individual classifications.")
                if create_github_issue:
                    try:
                        results_with_context = (
                            "In the following data, the MITRE classifier identified the following techniques and provided fix suggestions for each log entry:\n"
                            + json.dumps(results, indent=2)
                        )
                        create_github_issue("MITRE Classification Results", results_with_context, labels=["honeypot"])
                    except Exception:
                        logger.exception("Failed to create github issue from classification results.")
            else:
                logger.warning("Classification results was empty or None.")

            # 2. Correlation (Multi-stage Analysis)
            correlation = await correlate_logs(log_data)
            if correlation:
                if "timestamp" not in correlation:
                    correlation["timestamp"] = _now()
                if "detected_at" not in correlation:
                    correlation["detected_at"] = _now()
                await dashboard_bus.emit(correlation)
                logger.info("Attack correlation emitted to dashboard bus.")

            # 3. Generate an agent ticket for highest-severity result (best-effort)
            high_risk_results = [r for r in (results or []) if str(r.get("severity", "")).upper() in ["CRITICAL", "HIGH"]]
            if high_risk_results:
                target_result = high_risk_results[0]
                try:
                    ticket = await generate_agent_ticket(target_result)
                    if ticket:
                        # Enrich ticket with metadata
                        ticket["id"] = 100 + len(log_data)
                        ticket["timestamp"] = _now()
                        if log_data and isinstance(log_data, list) and len(log_data) > 0:
                            ticket["src_ip"] = log_data[0].get("src_ip")

                        # Try to submit via helper; if not available or fails, emit directly
                        submitted = False
                        try:
                            submitted = await submit_agent_ticket(ticket)
                        except Exception:
                            logger.debug("submit_agent_ticket not available or failed.")

                        if not submitted:
                            await dashboard_bus.emit(ticket)
                            logger.info("AI-generated Agent ticket emitted to dashboard bus (fallback).")
                        else:
                            logger.info("AI-generated Agent ticket submitted to dashboard endpoint.")
                    else:
                        logger.warning("Failed to generate AI Agent ticket.")
                except Exception as e:
                    logger.error(f"Failed to generate/submit agent ticket: {e}")

            # 4. Signal completion
            await dashboard_bus.emit({
                "type": "pipeline_finished",
                "timestamp": _now(),
                "status": "success",
                "items_processed": len(log_data)
            })
            logger.info("Pipeline finished event emitted.")

        except Exception as e:
            logger.error(f"Classification background task failed: {e}", exc_info=True)
            await dashboard_bus.emit({
                "type": "pipeline_finished",
                "timestamp": _now(),
                "status": "failed",
                "error": str(e)
            })

    # Fire and forget
    asyncio.create_task(run_and_emit_classification(data))

    return {"status": "broadcasted", "items": count, "subscribers": subs}


@router.post("/tickets")
async def receive_agent_ticket(ticket: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Receive an agent ticket (from classifier or other services) and broadcast it to dashboard clients."""
    try:
        if isinstance(ticket, dict) and "timestamp" not in ticket:
            ticket["timestamp"] = _now()
        await dashboard_bus.emit(ticket)
        logger.info("Received and emitted agent ticket to dashboard bus.")
        return {"status": "ok", "ticket_emitted": True}
    except Exception as e:
        logger.error(f"Failed to receive/emit agent ticket: {e}")
        return {"status": "error", "error": str(e)}


# ── Endpoint: Consolidated Stream ──────────────────────────────────────────────

@router.get("/stream")
async def stream_dashboard_events(request: Request) -> StreamingResponse:
    """
    SSE stream for all dashboard-related events.
    Aggregates logs, classifications, and remediation updates.
    
    Returns:
        StreamingResponse: Server-Sent Events stream with all dashboard updates
    """
    queue = await dashboard_bus.subscribe()
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"New dashboard subscriber connected from {client_ip}. Total: {len(dashboard_bus.subscribers)}")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate dashboard events for connected client."""
        try:
            while True:
                if await request.is_disconnected():
                    logger.info(f"Dashboard client {client_ip} disconnected.")
                    break
                
                try:
                    # Use a timeout so we can check for disconnection periodically
                    msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield msg
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            logger.error(f"Error in dashboard stream for {client_ip}: {e}")
        finally:
            dashboard_bus.unsubscribe(queue)
            logger.info(f"Unsubscribed client {client_ip}. Remaining: {len(dashboard_bus.subscribers)}")

    return StreamingResponse(
        event_generator(),
        media_type=SSE_MEDIA_TYPE,
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

