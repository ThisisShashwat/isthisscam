from sqlmodel import create_engine, SQLModel
from config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    SQLModel.metadata.create_all(engine)

