from sqlmodel import create_engine, SQLModel, select
from config import DB_PATH
from utils.models import Messages

engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_latest_message_id(session, thread_id):
    msg = select(Messages.id).where(Messages.thread_id == str(thread_id)).order_by(Messages.timestamp.desc()).limit(1)
    return session.exec(msg).first()