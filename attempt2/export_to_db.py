from sqlmodel import Session

from utils.db_utils import engine, init_db
from utils.extraction import extract_message
from utils.insta_utils import get_client, get_thread_id, fetch_new_messages

cl = get_client()

# THREAD_ID = get_thread_id(cl)
THREAD_ID = 340282366841710301281153262129164814061

init_db()

with Session(engine) as session:
    new_messages = fetch_new_messages(THREAD_ID, cl, session)

    for msg in new_messages:
        print(msg.id)
        extracted_message = extract_message(msg, cl, media_download=True, media_summary=True)
        session.add(extracted_message)
    session.commit()
