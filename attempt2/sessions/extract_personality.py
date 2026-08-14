from sqlmodel import Session
from sqlmodel import select

from utils.db_utils import engine
from sessions.extract_memories import get_pending_sessions, build_session_transcript
from sessions.extract_personality_llm import extract_session_traits, consolidate_traits
from utils.models import Memories


def build_traits_input(thread_id):
    with Session(engine) as db:
        traits = db.exec(select(Memories).where(Memories.thread_id == thread_id, Memories.type == "trait").order_by(
            Memories.session)).all()

        lines = []

        for t in traits:
            category = t.tags[0] if t.tags else "uncategorized"
            lines.append(f"[session {t.session}, {category}] {t.content}")

        return "\n".join(lines)

def extract_personality(thread_id):
    traits_changed = False

    for session in get_pending_sessions(thread_id, field="traits_done"):
        trascript = build_session_transcript(thread_id, session)
        extract_session_traits(thread_id, session, trascript)
        traits_changed = True

    if traits_changed:
        traits_input = build_traits_input(thread_id)
        consolidate_traits(thread_id, traits_input)