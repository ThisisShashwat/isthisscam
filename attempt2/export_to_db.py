from sqlalchemy import insert
from sqlmodel import Session

from utils.db_utils import engine
from utils.extraction import extract_message
from utils.insta_utils import fetch_new_messages
from utils.models import Messages


def ingest_new_messages(cl, thread_id):
    with Session(engine) as session:
        new_messages = fetch_new_messages(thread_id, cl, session)

    print(len(new_messages))
    extract_messages = []
    for msg in new_messages:
        extract_messages.append(extract_message(msg, cl, media_download=False, media_summary=False))

    with Session(engine) as session:
        with session.begin():
            session.add_all(extract_messages)

