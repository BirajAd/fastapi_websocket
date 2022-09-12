from imp import reload
from time import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from typing import List
import time

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        print(self.active_connections)
        for conn in self.active_connections:
            await conn.send_text(message)
    
manager = ConnectionManager()

@app.websocket("/test")
async def test(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            request = await websocket.receive_text()
            print(request)
            await manager.broadcast(request)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("one guy just left the chat")

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)