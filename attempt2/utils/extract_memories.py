from sqlmodel import Session, select

from utils.db_utils import engine
from utils.models import Messages, SessionStatus


def build_session_transcript(thread_id, session):
    with Session(engine) as db:
        messages = db.exec(
            select(Messages).where(Messages.thread_id == thread_id, Messages.session == session).order_by(
                Messages.timestamp)).all()

        reply_ids = {m.reply_id for m in messages if m.reply_id}

        originals = (db.exec(select(Messages).where(Messages.id.in_(reply_ids))).all() if reply_ids else [])

        by_id = {m.id: m for m in originals}

        lines = []
        block_sender = None

        for i, msg in enumerate(messages):
            is_reply = msg.reply_id is not None
            prev_was_reply = i > 0 and messages[i - 1].reply_id is not None

            if is_reply or prev_was_reply or msg.is_sent_by_viewer != block_sender:
                speaker = "Me" if msg.is_sent_by_viewer else "Them"
                lines.append(f"\n{speaker}:")
                block_sender = msg.is_sent_by_viewer

            if is_reply:
                original = by_id.get(msg.reply_id)

                if original is None:
                    quote = "[replying to a message]"
                elif original.item_type == "text":
                    who = "Me" if original.is_sent_by_viewer else "Them"
                    quote = f'[replying to "{original.text}" ({who})]: '
                else:
                    quote = f"[replying to a {original.media_type or 'media file'}]"

                lines.append(f"  {quote} {msg.text or ''}")

            elif msg.item_type == "text":
                lines.append(f"   {msg.text}")
            else:
                lines.append(f"  [sent a {msg.media_type or 'media file'}]")

        return "".join(lines).strip()


def get_pending_sessions(thread_id):
    with Session(engine) as db:
        done = set(db.exec(select(SessionStatus.session).where(SessionStatus.done == True,
                                                                                        SessionStatus.thread_id == thread_id)).all())

        all_sessions = set(db.exec(
            select(Messages.session).where(Messages.session != None,
                                                                         Messages.thread_id == thread_id).distinct()).all())

        return all_sessions - done


def extract_memories(thread_id):
    for session in get_pending_sessions(thread_id):
        print(session)
        transcript = build_session_transcript(thread_id, session)
        if session == 31: print(transcript)

