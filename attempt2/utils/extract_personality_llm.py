from typing import Literal

import instructor
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import delete
from sqlmodel import Session

from config import OPENROUTER_API_KEY, OPENROUTER_URL, STYLE_CONSOLIDATION_PROMPT
from config import PERSONALITY_EXTRACTION_MODEL, STYLE_EXTRACTION_PROMPT
from utils.db_utils import engine
from utils.models import Memories
from utils.models import PersonalityProfile
from utils.sessionizer import change_session_status

client = instructor.from_openai(OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_URL),
                                mode=instructor.Mode.JSON, )

TraitCategory = Literal[
    "cadence_burst", "capitalization_punctuation", "code_switching", "emoji_usage", "sentence_structure_grammar", "tone_register", "humor_style", "context_shifts", "vocabulary_phrasing"]


class TraitItem(BaseModel):
    category: TraitCategory
    content: str


class SessionTraitExtraction(BaseModel):
    items: list[TraitItem]


class TraitSection(BaseModel):
    category: TraitCategory
    content: str


class PersonalityConsolidation(BaseModel):
    sections: list[TraitSection]


def extract_session_traits(thread_id, session, transcript):
    extraction = client.chat.completions.create(  # type: ignore
        model=PERSONALITY_EXTRACTION_MODEL, response_model=SessionTraitExtraction,
        messages=[{"role": "user", "content": f"{STYLE_EXTRACTION_PROMPT}\n\n{transcript}"}], )

    with Session(engine) as db:
        with db.begin():
            db.exec(delete(Memories).where(Memories.thread_id == thread_id, Memories.session == session,
                                           Memories.type == "trait"))

            for item in extraction.items:
                db.add(
                    Memories(thread_id=thread_id, session=session, about_viewer=True, type="trait", confidence="high",
                             inferred=False, tags=[item.category], content=item.content))

            change_session_status(db, thread_id, session, True, field="traits_done")


def consolidate_traits(thread_id, traits_input):
    consolidation = client.chat.completions.create(  # type: ignore
        model=PERSONALITY_EXTRACTION_MODEL, response_model=PersonalityConsolidation,
        messages=[{"role": "user", "content": f"{STYLE_CONSOLIDATION_PROMPT}\n\n{traits_input}"}], )

    document = "\n\n".join(f"## {s.category}\n{s.content}" for s in consolidation.sections)

    with Session(engine) as db:
        with db.begin():
            profile = db.get(PersonalityProfile, thread_id)

            if profile:
                profile.content = document
            else:
                db.add(PersonalityProfile(thread_id=thread_id, content=document))
