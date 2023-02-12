from requests import Session
from ..authentication import get_user
from ..models import Message, Connection, User
from app.schemas import OutputMessage

def persist_message(db: Session, email: str, conn_id: int, msg: str):
    status, user = get_user(db, email)
    # conn = db.query(Connection).get(conn_id)
    if status:
        new_msg = Message(content=msg, connection=conn_id, sender=user.id)
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        return True
    return False

def message_by_room(db: Session, room_id: int, email: str):
    messages = db.query(Message, User).filter(User.id == Message.sender, Message.connection == int(room_id)).order_by(Message.sent_at).all()
    output_msg = []
    for msg, usr in messages:
        self_user = email == usr.email
        temp_msg = {
            'content': { 'message': msg.content },
            'user': usr.email,
            'read_at': msg.read_at,
            'sent_at': msg.sent_at,
            'self': self_user,
        }
        output_msg.append(temp_msg)

    return output_msg



