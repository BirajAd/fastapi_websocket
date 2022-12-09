from requests import Session
from app.authentication import authenticate_user, email_from_token, get_current_user, get_query, hash_password, create_access_token
from app.database import get_db
from app.schemas import Connection, CreateUser, LoginUser, Room, UserOutput, UserInfo
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from . import models
from fastapi.security import OAuth2PasswordBearer
from .connection_manager import ConnectionManager
from .services.message_service import persist_message
from app.routings.messaging import router

app = FastAPI(docs_url=None)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

manager = ConnectionManager()

@app.websocket("/test/{conn_id}")
async def test(websocket: WebSocket, db: Session = Depends(get_db), conn_id = Depends(get_query)):
    # connection_valid = db.query(models.Connection).get(conn_id)
    # print(connection_valid)
    # if conn_id and connection_valid:
    await manager.connect(websocket, conn_id)
    # else:
    #     return "No connection id provided"
    try:
        while True:
            if conn_id:
                request = await websocket.receive_json()
                if(manager.is_authenticated(websocket, conn_id)):
                    print("already authenticated")
                    for con in manager.active_connections[conn_id]:
                        if con['socket'] == websocket:
                            active_user = con['user']
                    persist_message(db, active_user, conn_id, request["message"])
                    await manager.broadcast(request, conn_id, active_user)
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

        new_user = new_user.__dict__
        new_user["token"] = create_access_token(data={"sub": user.email})
        
        return {
            "status": True,
            "details": UserOutput(**new_user)
        }

    except Exception as e:
        print(str(e))

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
        status, user = get_current_user(db, email["sub"])
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

app.mount("/messaging", router)

# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True)