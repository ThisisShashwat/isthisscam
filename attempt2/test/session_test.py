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

    session_messages = []

    for msg in messages:
        key = (msg.thread_id, msg.session)

        if current != key:
            if session_messages:
                start = session_messages[0].timestamp
                end = session_messages[-1].timestamp

                print(f"Session {current[1]} | {start} - {end} ({end - start}) | Total: {len(session_messages)}")

            current = key
            session_messages = []

        session_messages.append(msg)

    if session_messages:
        start = session_messages[0].timestamp
        end = session_messages[-1].timestamp

        print(f"Session {current[1]} | {start} - {end} ({end - start}) | Total: {len(session_messages)}")


