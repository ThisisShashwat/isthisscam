from sqlmodel import Session

from utils.db_utils import engine, init_db
from utils.extraction import extract_message
from utils.insta_utils import get_client, get_thread_id

cl = get_client()

# THREAD_ID = get_thread_id(cl)
THREAD_ID = 340282366841710301281153262129164814061

messages = cl.direct_messages(THREAD_ID, amount=0)

init_db()

with Session(engine) as session:
    for msg in messages:
        extracted_message = extract_message(msg)
        session.add(extracted_message)
    session.commit()
