import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time communication"""

    def __init__(self):
        # Active connections organized by type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "admin": set(),
            "bot_monitor": set(),
            "transcription": set(),
            "webhook_status": set(),
        }

        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(
        self, websocket: WebSocket, connection_type: str, metadata: Dict = None
    ):
        """Accept new WebSocket connection"""
        await websocket.accept()

        # Add to appropriate connection pool
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = set()

        self.active_connections[connection_type].add(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "type": connection_type,
            "metadata": metadata or {},
            "connected_at": None,  # You can add timestamp here
        }

        logger.info(
            f"WebSocket connected: type={connection_type}, total={len(self.active_connections[connection_type])}"
        )

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        # Find and remove from all connection pools
        for connection_type, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                logger.info(
                    f"WebSocket disconnected: type={connection_type}, remaining={len(connections)}"
                )
                break

        # Remove metadata
        self.connection_metadata.pop(websocket, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def send_personal_json(self, data: dict, websocket: WebSocket):
        """Send JSON data to specific WebSocket"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send personal JSON: {e}")
            self.disconnect(websocket)

    async def broadcast_to_type(self, message: str, connection_type: str):
        """Broadcast message to all connections of specific type"""
        if connection_type not in self.active_connections:
            return

        disconnected = []
        for websocket in self.active_connections[connection_type].copy():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_type}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_json_to_type(self, data: dict, connection_type: str):
        """Broadcast JSON data to all connections of specific type"""
        if connection_type not in self.active_connections:
            return

        disconnected = []
        for websocket in self.active_connections[connection_type].copy():
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Failed to broadcast JSON to {connection_type}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_bot_event(self, bot_id: str, event_type: str, event_data: dict):
        """Broadcast bot-related events"""
        message = {
            "type": "bot_event",
            "bot_id": bot_id,
            "event_type": event_type,
            "data": event_data,
            "timestamp": None,  # You can add timestamp here
        }

        # Send to admin and bot_monitor connections
        await self.broadcast_json_to_type(message, "admin")
        await self.broadcast_json_to_type(message, "bot_monitor")

    async def broadcast_transcription_update(
        self, bot_id: str, transcription_data: dict
    ):
        """Broadcast transcription updates"""
        message = {
            "type": "transcription_update",
            "bot_id": bot_id,
            "data": transcription_data,
            "timestamp": None,  # You can add timestamp here
        }

        await self.broadcast_json_to_type(message, "transcription")
        await self.broadcast_json_to_type(message, "admin")

    async def broadcast_webhook_status(
        self, webhook_id: str, status: str, details: dict
    ):
        """Broadcast webhook delivery status"""
        message = {
            "type": "webhook_status",
            "webhook_id": webhook_id,
            "status": status,
            "details": details,
            "timestamp": None,  # You can add timestamp here
        }

        await self.broadcast_json_to_type(message, "webhook_status")
        await self.broadcast_json_to_type(message, "admin")

    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            connection_type: len(connections)
            for connection_type, connections in self.active_connections.items()
        }

    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()
