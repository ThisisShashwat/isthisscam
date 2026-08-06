from sqlmodel import SQLModel, Field, create_engine, Relationship
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, JSON


class Messages(SQLModel, table=True):
    id: str = Field(primary_key=True)
    thread_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None, index=True)

    timestamp: datetime = Field(index=True)

    is_sent_by_viewer: bool = Field(index=True)
    item_type: Optional[str] = Field(default=None, index=True)

    text: Optional[str] = Field(default=None)
    reply_id: Optional[str] = Field(default=None, foreign_key="messages.id", index=True)

    reactions: list["Reactions"] = Relationship(back_populates="message")
    media: list["Media"] = Relationship(back_populates="message")


class Reactions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: str = Field(foreign_key="messages.id", index=True)

    sender_id: Optional[str] = Field(default=None, index=True)
    is_sent_by_viewer: bool = Field(index=True)

    emoji: str = Field(index=True)
    timestamp: datetime = Field(index=True)

    message: Optional[Messages] = Relationship(back_populates="reactions")


class Media(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: str = Field(foreign_key="messages.id", index=True)


    item_type: Optional[str] = Field(default=None, index=True)
    title: Optional[str] = Field(default=None)
    url: Optional[list] = Field(default=None, sa_column=Column(JSON))
    ai_summary: Optional[str] = Field(default=None)
    local_file_path: Optional[str] = Field(default=None)

    message: Optional[Messages] = Relationship(back_populates="media")