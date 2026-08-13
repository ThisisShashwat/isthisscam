from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, JSON
from pydantic import field_validator


class Messages(SQLModel, table=True):
    id: str = Field(primary_key=True)
    thread_id: str = Field()
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

    replied_to: Optional["Messages"] = Relationship(sa_relationship_kwargs={"remote_side":"Messages.id"})

    session: Optional[int] = Field(default=None)

    @field_validator("thread_id", "id", "reply_id", "user_id", mode="before")
    @classmethod
    def coerce_ids_to_str(cls, v):
        return str(v) if v is not None else v