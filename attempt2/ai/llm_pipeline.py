from typing import Optional, Literal

import instructor
from openai import OpenAI
from pydantic import BaseModel
from sqlmodel import Field, select, Session

from config import OPENROUTER_API_KEY, OPENROUTER_URL, ORCHESTRATOR_MODEL, MEMORY_MODEL, TONE_MODEL, GUARD_MODEL, \
    ORCHESTRATOR_PROMPT, MEMORY_LOOKUP_PROMPT, TONE_SYSTEM_PROMPT, GUARD_PROMPT
from utils.db_utils import engine
from utils.models import Messages, Facts, Memories

client = instructor.from_openai(OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_URL),
                                mode=instructor.Mode.JSON, )


class Intent(BaseModel):
    reply_to: Optional[str] = Field(None,
                                    description="short id like 'm3' this addresses, or None if it's not answering one specific message")
    intent: Optional[str] = Field(..., description="plain instruction for what to communicate, not literal wording")


class OrchestratorDecision(BaseModel):
    needs_memory: bool = Field(..., description="True only if you can't decide the reply without more context, "
                                                "use as much as possible when needed")
    memory_question: Optional[str] = Field(None, description="Required if needs_memory is true")

    intents: list[Intent] = Field(default_factory=list,
                                  description="one entry per distinct thing that needs addressing; empty if nothing in the burst needs a response ")


class MemoryLookup(BaseModel):
    lookup: Literal["facts", "memories", "messages"]
    search_terms: str


class ToneItem(BaseModel):
    kind: Literal["message", "reaction"]
    text: Optional[str] = None
    emoji: Optional[str] = None
    reply_to: Optional[str] = None


class ToneOutput(BaseModel):
    items: list[ToneItem]


class GuardResult(BaseModel):
    approved: bool
    reason: Optional[str] = None


def _content(m):
    if m.text:
        return m.text
    if m.media_ai_summary:
        return m.media_ai_summary
    return f"<{m.media_type or 'media'}, no summary available>"


def build_short_ids(turn_messages: list[Messages]):
    id_map, lines = {}, []

    for i, m in enumerate(turn_messages, start=1):
        sid = f"m{i}"
        id_map[sid] = m.id
        who = "You" if m.is_sent_by_viewer else "Them"

        line = f"[{sid}] {who}: {_content(m)}"
        if m.reply_id and m.replied_to:
            line += f' (replying to: "{_content(m.replied_to)}")'

        lines.append(line)

    return "\n".join(lines), id_map


# orchestrator and memory

def run_orchestrator(turn_text: str, memory_answer=None):
    user_content = turn_text if not memory_answer else f"{turn_text}\n\nMemory says: {memory_answer}"

    return client.chat.completions.create(  # type: ignore
        model=ORCHESTRATOR_MODEL, response_model=OrchestratorDecision,
        messages=[{"role": "system", "content": ORCHESTRATOR_PROMPT}, {"role": "user", "content": user_content}])


def query_memory(thread_id, kind, terms, db):
    if kind == "facts":
        return db.exec(select(Facts).where(Facts.thread_id == thread_id, Facts.content.contains(terms))).all()

    elif kind == "memories":
        return db.exec(select(Memories).where(Memories.thread_id == thread_id, Memories.content.contains(terms))).all()

    return db.exec(select(Messages).where(Messages.thread_id == thread_id, Messages.text.contains(terms))).all()


def ask_memory(thread_id, question):
    lookup = client.chat.completions.create(  # type: ignore
        model=MEMORY_MODEL, response_model=MemoryLookup, messages=[{"role": "system", "content": MEMORY_LOOKUP_PROMPT},
            {"role": "user", "content": f"Question: {question}"}, ], )

    with Session(engine) as db:
        rows = query_memory(thread_id, lookup.lookup, lookup.search_terms, db)
        if not rows and lookup.lookup != "messages":
            rows = query_memory(thread_id, "messages", lookup.search_terms, db)

        if not rows:
            return "Nothing found in memory"

        return "\n".join(getattr(r, "content", None) or getattr(r, "text", "") for r in rows)


def get_decision(thread_id, turn_text):
    decision = run_orchestrator(turn_text)

    if decision.needs_memory:
        answer = ask_memory(thread_id, decision.memory_question)
        decision = run_orchestrator(turn_text, memory_answer=answer)

    return decision


# tone and guard


def run_tone(intents, personality):

    system = TONE_SYSTEM_PROMPT.format(style_guide=personality)

    intent_lines = "\n".join(
        f"- ({'replying to ' + i.reply_to if i.reply_to else 'general, not a specific message'}): {i.intent}"
        for i in intents
    )

    return client.chat.completions.create(  # type: ignore
        model=TONE_MODEL, response_model=ToneOutput, messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"What to communicate this turn:\n{intent_lines}"},
        ],)


def run_guard(recent_context, draft):
    user_content = f"Recent conversation:\n{recent_context}\n\nDraft:\n{draft.model_dump_json()}"

    return client.chat.completions.create(  # type: ignore
        model=GUARD_MODEL, response_model=GuardResult, messages=[
            {"role": "system", "content": GUARD_PROMPT},
            {"role": "user", "content": user_content},
        ],)


def run_turn(thread_id, turn_messages, personality, max_retries=2):
    turn_text, id_map = build_short_ids(turn_messages)

    for _ in range(max_retries + 1):

        decision = get_decision(thread_id, turn_text)

        if not decision.intents:
            return None

        draft = run_tone(decision.intents, personality)
        guard = run_guard(turn_text, draft)

        if guard.approved:
            for item in draft.items:
                if item.reply_to:
                    item.reply_to = id_map.get(item.reply_to)

            return draft

    return None
