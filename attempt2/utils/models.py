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


    # media_caption: Optional[str] = Field(default=None)
    # reactions: list["Reactions"] = Relationship(back_populates="message")
    # media: list["Media"] = Relationship(back_populates="message")

    @field_validator("thread_id", "id", "reply_id", "user_id", mode="before")
    @classmethod
    def coerce_ids_to_str(cls, v):
        return str(v) if v is not None else v
#
# class Reactions(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     message_id: str = Field(foreign_key="messages.id", index=True)
#
#     sender_id: str = Field(default=None, index=True)
#     is_sent_by_viewer: bool = Field(index=True)
#
#     emoji: str = Field(index=True)
#     timestamp: datetime = Field(index=True)
#
#     message: Optional[Messages] = Relationship(back_populates="reactions")
#
#     @field_validator("message_id", "sender_id", mode="before")
#     @classmethod
#     def coerce_ids_to_str(cls, v):
#         return str(v) if v is not None else v
#
# class Media(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     message_id: str = Field(foreign_key="messages.id", index=True)
#
#
#     item_type: str = Field(default=None, index=True)
#     title: Optional[str] = Field(default=None)
#     url: list = Field(default=None, sa_column=Column(JSON))
#     ai_summary: Optional[str] = Field(default=None)
#     local_file_path: Optional[str] = Field(default=None)
#
#     message: Optional[Messages] = Relationship(back_populates="media")
#
#     @field_validator("message_id", mode="before")
#     @classmethod
#     def coerce_ids_to_str(cls, v):
#         return str(v) if v is not None else v