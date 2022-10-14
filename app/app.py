from requests import Session
from app.authentication import authenticate_user, email_from_token, get_current_user, get_user, hash_password
from app.database import get_db
from app.schemas import CreateUser, LoginUser, UserOutput, UserInfo
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import EmailStr
import uvicorn
from typing import List, Set
from . import models
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in self.active_connections:
            print(message)
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
        user_count = db.query(models.User).filter((models.User.email==user.email) | (models.User.username==user.username)).count()
        if(user_count):
            return {
                'status': False,
                'details': 'User with the email/username already exists'
            }
        user.password = hash_password(user.password)
        
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": True,
            "details": UserOutput(**new_user.__dict__)
        }

    except Exception as e:
        print(str(e))

    return new_user

@app.post("/login")
async def login(user: LoginUser, db: Session = Depends(get_db)):
    try:
        status, msg = authenticate_user(db, user.email, user.password)
        if not status:
            return {
                "status": False,
                "details": msg
            }
        else:
            return {
                "status": True,
                "details": UserOutput(**msg.__dict__)
            }
    except Exception as e:
        print(str(e))

@app.get("/userinfo")
async def userinfo(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        status, email = email_from_token(token)
        if not status:
            return {
                'status': False, 
                'details': "Invalid token"
            }
        status, user = get_current_user(db, email)
        if not status:
            return {
                'status': False,
                'details': "User not found"
            }
        return {
            'status': True,
            'details': UserInfo(**user.__dict__)
        }
    except Exception as e:
        print(str(e))
        


# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True)