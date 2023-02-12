from fastapi import APIRouter, Depends
from requests import Session
from app.database import get_db
import app.models as models
from app.authentication import email_from_token, get_current_user, get_query
from app.schemas import Room
from app.services.message_service import message_by_room
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import column

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.get("/conversations", tags=["messaging"])
async def userinfo(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        status, email = email_from_token(token)
        if not status:
            return {
                'status': False, 
                'details': "Invalid token"
            }
        status, user = get_current_user(db, email["sub"])
        unique_rooms = db.query(models.Message).distinct('connection')
        room_conversations = {}
        # message => { 'user': <email:str>, 'content': <message:str>, 'sent_at': <datetime> }
        # user_list = db.query(models.User)
        for msg in unique_rooms:
            users = db.query(models.Message, models.User).join(models.User, models.User.id == models.Message.sender)#.values(column('email'))
            print(users)
            # filter_by(connection=msg.connection)\
            #     .order_by(models.Message.sent_at).values(models.Message.id, models.User.email, models.Message.content, models.Message.sent_at)
            room_conversations[msg.connection] = users.all()
        return room_conversations     
    except Exception as e:
        print(str(e))

@router.get("/conversations/{room_id}", tags=["messaging"])
async def getMessageFromRoom(room_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        status, email = email_from_token(token)
        if not status:
            return {
                'status': False, 
                'details': "Invalid token"
            }
        status, user = get_current_user(db, email["sub"])

        print(user.email)
        print('get: ', room_id)
        messages = message_by_room(db, room_id, user.email)

        return messages
    except Exception as e:
        return {
            'status': False,
            'details': str(e)
        }