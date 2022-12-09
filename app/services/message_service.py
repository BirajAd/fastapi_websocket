from requests import Session
from ..authentication import get_user
from ..models import Message, Connection

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

