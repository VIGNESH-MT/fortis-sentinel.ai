"""
FORTIS SENTINEL - WebSocket API Router

Real-time event streaming for anomaly feed, agent status updates,
and governance check results.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

router = APIRouter()


# ---------------------------------------------------------------------------
# Connection Manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Manages active WebSocket connections with channel-based subscriptions."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "anomalies": [],
            "agents": [],
            "governance": [],
            "all": [],
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        self.active_connections["all"].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        for ch in self.active_connections.values():
            if websocket in ch:
                ch.remove(websocket)

    async def broadcast(self, message: dict, channel: str = "all"):
        """Send a message to all connections on a channel."""
        connections = self.active_connections.get(channel, [])
        dead = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn, channel)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections.get("all", []))


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# WebSocket Endpoints
# ---------------------------------------------------------------------------

@router.websocket("/feed")
async def websocket_feed(
    websocket: WebSocket,
    channel: str = Query("all", description="Channel: all, anomalies, agents, governance"),
):
    """
    Real-time event feed.

    Connect to receive live events. Optionally specify a channel to filter:
    - `all`: All events
    - `anomalies`: Anomaly detections only
    - `agents`: Agent status changes only
    - `governance`: Governance check results only
    """
    await manager.connect(websocket, channel)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "channel": channel,
        "message": f"Connected to FORTIS SENTINEL real-time feed ({channel})",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": manager.connection_count,
    })

    try:
        while True:
            # Wait for incoming messages (ping/pong or commands)
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif msg_type == "subscribe":
                    new_channel = msg.get("channel", "all")
                    if new_channel in manager.active_connections:
                        manager.active_connections[new_channel].append(websocket)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": new_channel,
                            "timestamp": datetime.utcnow().isoformat(),
                        })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.get("/connections")
async def websocket_info():
    """Get current WebSocket connection stats."""
    return {
        "total_connections": manager.connection_count,
        "channels": {
            ch: len(conns) for ch, conns in manager.active_connections.items()
        },
    }


# ---------------------------------------------------------------------------
# Broadcast helper (used by other modules)
# ---------------------------------------------------------------------------

async def broadcast_event(event_type: str, data: dict, channel: str = "all"):
    """Broadcast an event to connected WebSocket clients.

    Called by governance check, anomaly detection, and agent status change
    code paths to push real-time updates.
    """
    message = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(message, channel)
    # Also always broadcast to 'all'
    if channel != "all":
        await manager.broadcast(message, "all")
