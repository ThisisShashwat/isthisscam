from sqlmodel import Session

from utils.db_utils import engine, init_db
from utils.extraction import extract_message
from utils.insta_utils import get_client, get_thread_id, fetch_new_messages

# THREAD_ID = get_thread_id(cl)
THREAD_ID = 340282366841710301281153262129164814061


def ingest_new_messages(cl, thread_id):
    with Session(engine) as session:
        new_messages = fetch_new_messages(thread_id, cl, session)

    extract_messages = []
    for msg in new_messages:
        extract_messages.append(extract_message(msg, cl, media_download=True, media_summary=True))

    with Session(engine) as session:
        with session.begin():
            session.add_all(extract_messages)


cl = get_client()
init_db()
ingest_new_messages(cl, THREAD_ID)