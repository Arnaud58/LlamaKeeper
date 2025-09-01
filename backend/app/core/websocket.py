import json
from typing import Dict, List

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.story_subscriptions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection
        """
        self.active_connections.remove(websocket)

        # Remove from any story subscriptions
        for story_id, connections in list(self.story_subscriptions.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.story_subscriptions[story_id]

    async def subscribe_to_story(self, websocket: WebSocket, story_id: str):
        """
        Subscribe a WebSocket to updates for a specific story
        """
        if story_id not in self.story_subscriptions:
            self.story_subscriptions[story_id] = []

        if websocket not in self.story_subscriptions[story_id]:
            self.story_subscriptions[story_id].append(websocket)

    async def unsubscribe_from_story(self, websocket: WebSocket, story_id: str):
        """
        Unsubscribe a WebSocket from a specific story
        """
        if (
            story_id in self.story_subscriptions
            and websocket in self.story_subscriptions[story_id]
        ):
            self.story_subscriptions[story_id].remove(websocket)

            # Clean up if no more subscribers
            if not self.story_subscriptions[story_id]:
                del self.story_subscriptions[story_id]

    async def broadcast(self, message: Dict):
        """
        Broadcast a message to all connected clients
        """
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_to_story(self, story_id: str, message: Dict):
        """
        Broadcast a message to all subscribers of a specific story
        """
        if story_id in self.story_subscriptions:
            for connection in self.story_subscriptions[story_id]:
                await connection.send_json(message)


# Global WebSocket connection manager
websocket_manager = ConnectionManager()


async def handle_websocket_events(websocket: WebSocket, session: AsyncSession):
    """
    Handle incoming WebSocket events
    """
    try:
        await websocket_manager.connect(websocket)

        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "subscribe":
                story_id = data.get("story_id")
                if story_id:
                    await websocket_manager.subscribe_to_story(websocket, story_id)
                    await websocket.send_json(
                        {"type": "subscription_confirmed", "story_id": story_id}
                    )

            elif event_type == "unsubscribe":
                story_id = data.get("story_id")
                if story_id:
                    await websocket_manager.unsubscribe_from_story(websocket, story_id)
                    await websocket.send_json(
                        {"type": "unsubscription_confirmed", "story_id": story_id}
                    )

            elif event_type == "action":
                # Handle story action events
                story_id = data.get("story_id")
                action_data = data.get("action", {})

                if story_id:
                    # Broadcast action to story subscribers
                    await websocket_manager.broadcast_to_story(
                        story_id,
                        {
                            "type": "story_update",
                            "story_id": story_id,
                            "action": action_data,
                        },
                    )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
