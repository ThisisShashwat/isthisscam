"""

session seperatuion:

1. get last msg timestamp+session id
2. no last message = session--->1
3. gap since last msg > hard cutoff ---> new sesion
4. gap <= session gap mins ---> same session

5. gap > session gap mins, gap < hard cutoff:
    a. calculate reply ratio of last session msgs replied in this session
    b.. ratio >= 30% ---> same session
    c. ratio < 30% --> new session

6. calculate session size currently chosen & last also,
7. current session size > max size ---> new session
8. last session size < min size ---> last session

"""

from datetime import timedelta

from sqlmodel import Session, select, update

from config import SESSION_GAP_MINUTES, HARD_CUTOFF_HOURS, MAX_SESSION_SIZE, MIN_SESSION_SIZE
from utils.db_utils import engine
from utils.models import Messages, SessionStatus


def recalculate_session(thread_id):

    with Session(engine) as db:
        with db.begin():
            last = db.exec(
                select(Messages)
                .where(Messages.thread_id == thread_id, Messages.session != None)
                .order_by(Messages.timestamp.desc())
            ).first()

            batch = db.exec(
                select(Messages)
                .where(Messages.thread_id == thread_id, Messages.session == None)
                .order_by(Messages.timestamp)
            ).all()

            if not batch:
                return

            if last is None:
                session_id, session_ids, last_time = 1, [], None
            else:
                session_id = last.session

                change_session_status(db, thread_id, session_id, False)

                session_ids = db.exec(
                    select(Messages.id)
                    .where(
                        Messages.thread_id == thread_id,
                        Messages.session == session_id,
                        Messages.item_type == "text",
                    )
                ).all()

                last_time = last.timestamp

            open_msgs: list[Messages] = []

            for msg in batch:

                if msg.item_type != "text":
                    msg.session = session_id
                    continue

                same = last_time is None or is_same_session(msg, last_time, session_ids)

                if same and len(session_ids) >= MAX_SESSION_SIZE:
                    same = False

                if not same:
                    if len(session_ids) < MIN_SESSION_SIZE and session_id > 1:
                        for m in open_msgs:
                            m.session = session_id - 1

                        db.exec(
                            update(Messages)
                            .where(Messages.thread_id == thread_id, Messages.session == session_id)
                            .values(session=session_id - 1)
                        )

                        change_session_status(db, thread_id, session_id - 1, False)

                    else:
                        session_id += 1

                    session_ids, open_msgs = [], []

                msg.session = session_id
                session_ids.append(msg.id)
                open_msgs.append(msg)
                last_time = msg.timestamp

def is_same_session(msg, last_time, session_ids):
    gap = msg.timestamp - last_time

    if gap > timedelta(hours=HARD_CUTOFF_HOURS):
        return False
    if gap <= timedelta(minutes=SESSION_GAP_MINUTES):
        return True

    return msg.reply_id in session_ids



def change_session_status(db, thread_id, session, to_status):
    status = db.get(SessionStatus, (thread_id, session))

    if status:
        status.done = to_status
    else:
        db.add(SessionStatus(thread_id=thread_id, session=session, done=to_status))



