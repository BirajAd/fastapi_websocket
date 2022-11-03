from datetime import datetime
from app.database import get_db
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict = {}
        """
            {
                "conn_id1": [{ "socket": <WebSocket>, "authenticated": <bool>, "joined": <datetime> }, ...]
                "conn_id2": [{ "socket": <WebSocket>, "authenticated": <bool>, "joined": <datetime> }, ...]
            }
        """

    async def connect(self, websocket: WebSocket, conn_id: int):
        await websocket.accept()
        if conn_id in self.active_connections:
            self.active_connections[conn_id].append({ "socket": websocket, "authenticated": False, "joined": datetime.now(), "user": None })
        else:
            self.active_connections[conn_id] = [{ "socket": websocket, "authenticated": False, "joined": datetime.now(), "user": None }]

    def disconnect(self, websocket: WebSocket, conn_id: int):
        if conn_id not in self.active_connections:
            return
        for conn in self.active_connections[conn_id]:
            if(conn["socket"] == websocket):
                print(websocket, " disconnected")
                del self.active_connections[conn_id]
    
    def is_authenticated(self, websocket: WebSocket, conn_id: int):
        if conn_id in self.active_connections:
            for webs in self.active_connections[conn_id]:
                if(webs["socket"] == websocket):
                    return webs["authenticated"]
        else:
            return False
    
    def mark_authenticated(self, websocket: WebSocket, conn_id: int, email: str):
        if conn_id not in self.active_connections:
            return
        else:
            connection = self.active_connections[conn_id]
            for c in connection:
                if(c["socket"] == websocket):
                    c["authenticated"] = True
                    c["user"] = email

    async def broadcast(self, message: str, conn_id: int):
        if conn_id not in self.active_connections:
            print("Connection id doesn't exist")
        else:
            for webs in self.active_connections[conn_id]:
                if webs["authenticated"]:
                    message["user"] = webs.get("user")
                    await webs["socket"].send_json(message)