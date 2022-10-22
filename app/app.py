from datetime import datetime
from requests import Session
from app.authentication import authenticate_user, email_from_token, get_current_user, get_query, get_user, hash_password
from app.database import get_db
from app.schemas import Connection, CreateUser, LoginUser, Room, UserOutput, UserInfo
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import EmailStr
import uvicorn
from typing import List, Dict
from . import models
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
                    await webs["socket"].send_json(message)
    
manager = ConnectionManager()

@app.websocket("/test/{conn_id}")
async def test(websocket: WebSocket, conn_id = Depends(get_query)):
    if conn_id:
        await manager.connect(websocket, conn_id)
    else:
        return "No connection id provided"
    try:
        while True:
            if conn_id:
                request = await websocket.receive_json()
                if(manager.is_authenticated(websocket, conn_id)):
                    print("already authenticated")
                    await manager.broadcast(request, conn_id)
                else:
                    status, email = email_from_token(request["token"])
                    if status:
                        manager.mark_authenticated(websocket, conn_id, email["sub"])
                    else:
                        manager.disconnect(websocket, conn_id)
    except WebSocketDisconnect:
        print("exception")
        manager.disconnect(websocket, conn_id)
        # await manager.broadcast("someone left the chat")

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
        
@app.post("/room")
async def userinfo(connection: Connection, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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
        new_room = models.Connection(group_name=connection.group_name)
        print(new_room)
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return {
            'status': True,
            'details': Room(**new_room.__dict__)
        }
    except Exception as e:
        print(str(e))

@app.get("/room")
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
        rooms = db.query(models.Connection).all()
        return {
            'status': True,
            'details': [Room(**room.__dict__) for room in rooms]
        }
    except Exception as e:
        print(str(e))

# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True)