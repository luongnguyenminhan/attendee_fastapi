import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    """WebSocket endpoint for admin dashboard"""
    await manager.connect(websocket, "admin", {"role": "admin"})

    try:
        # Send initial connection success message
        await manager.send_personal_json(
            {
                "type": "connection_status",
                "status": "connected",
                "connection_type": "admin",
                "message": "Successfully connected to admin WebSocket",
            },
            websocket,
        )

        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_json(
                        {"type": "pong", "timestamp": message.get("timestamp")},
                        websocket,
                    )

                elif message.get("type") == "get_stats":
                    stats = manager.get_connection_stats()
                    await manager.send_personal_json({"type": "stats", "data": stats}, websocket)

                else:
                    # Echo unknown messages for debugging
                    await manager.send_personal_json({"type": "echo", "original_message": message}, websocket)

            except json.JSONDecodeError:
                await manager.send_personal_json({"type": "error", "message": "Invalid JSON format"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Admin WebSocket disconnected")


@router.websocket("/ws/bot/{bot_id}")
async def websocket_bot_monitor(websocket: WebSocket, bot_id: str):
    """WebSocket endpoint for monitoring specific bot"""
    await manager.connect(websocket, "bot_monitor", {"bot_id": bot_id})

    try:
        # Send initial connection message
        await manager.send_personal_json(
            {
                "type": "connection_status",
                "status": "connected",
                "connection_type": "bot_monitor",
                "bot_id": bot_id,
                "message": f"Connected to bot {bot_id} monitoring",
            },
            websocket,
        )

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal_json(
                        {
                            "type": "pong",
                            "bot_id": bot_id,
                            "timestamp": message.get("timestamp"),
                        },
                        websocket,
                    )

                elif message.get("type") == "bot_command":
                    # Handle bot commands (start, stop, etc.)
                    command = message.get("command")
                    await manager.send_personal_json(
                        {
                            "type": "bot_command_received",
                            "bot_id": bot_id,
                            "command": command,
                            "status": "acknowledged",
                        },
                        websocket,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_json({"type": "error", "message": "Invalid JSON format"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Bot monitor WebSocket disconnected for bot {bot_id}")


@router.websocket("/ws/transcription")
async def websocket_transcription(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription updates"""
    await manager.connect(websocket, "transcription", {"role": "transcription_monitor"})

    try:
        await manager.send_personal_json(
            {
                "type": "connection_status",
                "status": "connected",
                "connection_type": "transcription",
                "message": "Connected to transcription updates",
            },
            websocket,
        )

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal_json(
                        {"type": "pong", "timestamp": message.get("timestamp")},
                        websocket,
                    )

                elif message.get("type") == "subscribe_bot":
                    bot_id = message.get("bot_id")
                    await manager.send_personal_json(
                        {
                            "type": "subscription_confirmed",
                            "bot_id": bot_id,
                            "message": f"Subscribed to transcriptions for bot {bot_id}",
                        },
                        websocket,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_json({"type": "error", "message": "Invalid JSON format"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Transcription WebSocket disconnected")


@router.websocket("/ws/webhooks")
async def websocket_webhooks(websocket: WebSocket):
    """WebSocket endpoint for webhook delivery status updates"""
    await manager.connect(websocket, "webhook_status", {"role": "webhook_monitor"})

    try:
        await manager.send_personal_json(
            {
                "type": "connection_status",
                "status": "connected",
                "connection_type": "webhook_status",
                "message": "Connected to webhook status updates",
            },
            websocket,
        )

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal_json(
                        {"type": "pong", "timestamp": message.get("timestamp")},
                        websocket,
                    )

                elif message.get("type") == "get_webhook_stats":
                    # TODO: Implement webhook statistics when webhook models are ready
                    await manager.send_personal_json(
                        {
                            "type": "webhook_stats",
                            "data": {
                                "total_deliveries": 0,
                                "successful": 0,
                                "failed": 0,
                                "pending": 0,
                            },
                        },
                        websocket,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_json({"type": "error", "message": "Invalid JSON format"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Webhook status WebSocket disconnected")


# Utility functions for broadcasting events from other parts of the application


async def broadcast_bot_status_change(bot_id: str, old_status: str, new_status: str):
    """Broadcast bot status change to all connected clients"""
    await manager.broadcast_bot_event(bot_id, "status_change", {"old_status": old_status, "new_status": new_status})


async def broadcast_new_transcription(bot_id: str, transcription_text: str, speaker: str = None):
    """Broadcast new transcription to connected clients"""
    await manager.broadcast_transcription_update(
        bot_id,
        {"text": transcription_text, "speaker": speaker, "type": "new_transcription"},
    )


async def broadcast_webhook_delivery(webhook_id: str, status: str, response_code: int = None):
    """Broadcast webhook delivery result"""
    await manager.broadcast_webhook_status(
        webhook_id,
        status,
        {"response_code": response_code, "delivered_at": None},  # Add timestamp
    )
