from sqlmodel import Session, select

from utils.db_utils import engine, init_db
from utils.models import Messages

init_db()

with Session(engine) as session:

    messages = session.exec(
        select(Messages)
        .where(Messages.session != None)
        .order_by(Messages.thread_id, Messages.timestamp)
    ).all()

    current = None

    text_count = 0
    non_text_count = 0

    session_messages = []

    for msg in messages:
        key = (msg.thread_id, msg.session)

        if current != key:
            if session_messages:
                start = session_messages[0].timestamp
                end = session_messages[-1].timestamp

                print(f"Session {current[1]} | {start} - {end} ({end - start}) | "
                      f"Total: {len(session_messages)} (text:{text_count}, non-text: {non_text_count})")

            current = key
            session_messages = []
            text_count = 0
            non_text_count = 0

        session_messages.append(msg)
        if msg.item_type == "text": text_count += 1
        else: non_text_count += 1

    if session_messages:
        start = session_messages[0].timestamp
        end = session_messages[-1].timestamp

        print(f"Session {current[1]} | {start} - {end} ({end - start}) | "
              f"Total: {len(session_messages)} (text:{text_count}, non-text: {non_text_count})")


