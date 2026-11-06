"""
DisputeShield AI — WebSocket Endpoint

Real-time communication channel between backend and frontend dashboard.
Pushes live updates when disputes are created, agent processes them,
and evidence is submitted.
"""

import json
import logging
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/disputes")
async def dispute_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dispute dashboard updates.

    Message types sent to clients:
    - new_dispute: A new dispute has been received
    - agent_update: Agent is processing (step-by-step reasoning)
    - evidence_submitted: Evidence has been submitted
    - dispute_resolved: Dispute outcome determined
    - risk_alert: Account risk level changed
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"WebSocket connected. Active connections: {len(active_connections)}")

    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or subscription preferences
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(active_connections)}")


async def broadcast_message(message: dict):
    """
    Broadcast a message to all connected WebSocket clients.
    Called by the agent pipeline when disputes are processed.
    """
    dead_connections = set()
    payload = json.dumps(message)

    for ws in active_connections:
        try:
            await ws.send_text(payload)
        except Exception:
            dead_connections.add(ws)

    # Clean up dead connections
    for ws in dead_connections:
        active_connections.discard(ws)


def broadcast_dispute_event(event_type: str, data: dict):
    """
    Synchronous helper to broadcast dispute event messages.
    Callable safely from Celery tasks or background threads.
    """
    import asyncio
    msg = {"type": event_type, **data}
    if not active_connections:
        return
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_message(msg))
        else:
            loop.run_until_complete(broadcast_message(msg))
    except RuntimeError:
        asyncio.run(broadcast_message(msg))
    except Exception as exc:
        logger.debug(f"Broadcast dispute event exception: {exc}")

