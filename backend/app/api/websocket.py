from typing import List, Dict, Any
import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcasts a JSON message to all connected clients.
        Expected schema: {"agent_id": "str", "action": "str", "message": "str", "sprite_state": "str"}
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message to a client: {e}")
                self.disconnect(connection)

# Global connection manager instance
manager = ConnectionManager()
