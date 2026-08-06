from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from datetime import datetime
import json

class Messages(SQLModel, table=True):
    id: str = Field(primary_key=True)
    thread_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None, index=True)

    timestamp: datetime = Field(default=None, index=True)

    is_sent_by_viewer: bool = Field(default=None, index=True)
    item_type: Optional[str] = Field(default=None, index=True)

    text: Optional[str] = Field(default=None, index=True)
    reply_id: Optional[str] = Field(foreign_key="messages.id", index=True)

    reactions: Optional[list] #list
    media #list?

class Reactions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: str = Field(foreign_key="messages.id", index=True)
    emoji: str = Field(default=None, index=True)
    sender_id: Optional[str] = Field(default=None, index=True)
    is_sent_by_viewer: bool = Field(default=None, index=True)
    timestamp: datetime = Field(default=None, index=True)

class Media(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: str = Field(foreign_key="messages.id", index=True)
    media_type ( reel/post, image, video, audio, sticker)
    title
    url [list]
    ai summary
    local_file_path


DB_FILE = "messages.db"

engine = create_engine(f"sqlite:///{DB_FILE}")
SQLModel.metadata.create_all(engine)
