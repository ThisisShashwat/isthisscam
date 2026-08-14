from datetime import datetime
from typing import Optional

from pydantic import field_validator
from sqlalchemy import Column, JSON, DateTime
from sqlmodel import SQLModel, Field, Relationship


class Messages(SQLModel, table=True):
    id: str = Field(primary_key=True)
    thread_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None)

    timestamp: datetime = Field(index=True)

    is_sent_by_viewer: bool = Field(index=True)
    item_type: Optional[str] = Field(default=None)

    text: Optional[str] = Field(default=None)
    reply_id: Optional[str] = Field(default=None, foreign_key="messages.id", index=True)

    media_type: Optional[str] = Field(default=None)
    media_urls: Optional[list] = Field(default=None, sa_column=Column(JSON))

    media_local_file_paths: Optional[list] = Field(default=None, sa_column=Column(JSON))
    media_ai_summary: Optional[str] = Field(default=None)

    replied_to: Optional["Messages"] = Relationship(sa_relationship_kwargs={"remote_side": "Messages.id"})

    session: Optional[int] = Field(default=None, index=True)

    @field_validator("thread_id", "id", "reply_id", "user_id", mode="before")
    @classmethod
    def coerce_ids_to_str(cls, v):
        return str(v) if v is not None else v


class SessionStatus(SQLModel, table=True):
    thread_id: str = Field(primary_key=True)
    session: int = Field(primary_key=True)
    done: bool = Field(default=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(), onupdate=datetime.now), )


class Memories(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True)
    session: int = Field(index=True)
    about_viewer: Optional[bool] = Field(default=None, index=True)
    type: str = Field(index=True)
    content: str
    confidence: str
    inferred: bool = Field(default=False, index=True)
    tags: Optional[list] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(), onupdate=datetime.now))


class Facts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True)
    about_viewer: Optional[bool] = Field(default=None, index=True)
    content: str
    confidence: str
    last_session: int
    updated_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(), onupdate=datetime.now), )
