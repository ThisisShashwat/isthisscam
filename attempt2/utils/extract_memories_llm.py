from typing import Literal, Optional

import instructor
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import delete
from sqlmodel import Session

from config import OPENROUTER_API_KEY, OPENROUTER_URL, EXTRACTION_PROMPT, MEMORY_EXTRACTION_MODEL, CONSOLIDATION_PROMPT
from utils.db_utils import engine
from utils.models import Memories, Facts
from utils.sessionizer import change_session_status

client = instructor.from_openai(OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_URL),
                                mode=instructor.Mode.JSON, )

MemoryType = Literal["summary", "log", "memory", "event"]
Confidence = Literal["low", "medium", "high"]


class MemoryItem(BaseModel):
    about_viewer: Optional[bool]
    type: MemoryType
    content: str
    confidence: Confidence
    inferred: bool
    tags: Optional[list[str]] = None


class FactItem(BaseModel):
    about_viewer: Optional[bool]
    content: str
    confidence: Confidence
    last_session: int


class SessionExtraction(BaseModel):
    items: list[MemoryItem]


class FactsConsolidation(BaseModel):
    facts: list[FactItem]


def extract_session_memories(thread_id, session, transcript):
    extraction = client.chat.completions.create(  # type: ignore
        model=MEMORY_EXTRACTION_MODEL, response_model=SessionExtraction,
        messages=[{"role": "user", "content": f"{EXTRACTION_PROMPT}\n\n{transcript}"}], )

    with Session(engine) as db:
        with db.begin():
            db.exec(delete(Memories).where(Memories.thread_id == thread_id, Memories.session == session))

            for item in extraction.items:
                db.add(Memories(thread_id=thread_id, session=session, **item.model_dump()))

            change_session_status(db, thread_id, session, True)


def consolidate_facts(thread_id, facts_input):
    consolidation = client.chat.completions.create(  # type: ignore
        model=MEMORY_EXTRACTION_MODEL, response_model=FactsConsolidation,
        messages=[{"role": "user", "content": f"{CONSOLIDATION_PROMPT}\n\n{facts_input}"}], )

    with Session(engine) as db, db.begin():
        db.exec(delete(Facts).where(Facts.thread_id == thread_id))

        for fact in consolidation.facts:
            db.add(Facts(thread_id=thread_id, **fact.model_dump()))
