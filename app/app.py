from requests import Session
from app.database import get_db
from app.schemas import CreateUser, CreateUserOutput
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
import uvicorn
from typing import List
from . import models

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
        for conn in self.active_connections:
            await conn.send_text(message["message"])
    
manager = ConnectionManager()

@app.websocket("/test")
async def test(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            request = await websocket.receive_json()
            print(request)
            await manager.broadcast(request)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("someone left the chat")

@app.post("/create_user")
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
        user_count = db.query(models.User).filter(models.User.email==user.email).count()
        if(user_count):
            return {
                'status': False,
                'details': 'User with the email already exists'
            }
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        response = new_user.__dict__
        del response['password']
        
        return {
            "status": True,
            "details": response
        }

    except Exception as e:
        print(str(e))

    return new_user

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)