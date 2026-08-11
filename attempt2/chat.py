from sqlmodel import Session

from export_to_db import ingest_new_messages
from utils.db_utils import init_db, engine
from utils.extraction import extract_message
from utils.insta_utils import get_client, get_thread_id

print("before getclient")
cl = get_client()
print("after getclient")

THREAD_ID = get_thread_id(cl, test=True)

def handle_direct_message(payload):
    msg = cl.direct_message(payload["message"]["thread_id"], payload["message"]["item_id"], amount=20)
    extracted_msg = extract_message(msg, cl, media_download=True, media_summary=True)
    print(extracted_msg)
    with Session(engine) as session:
        with session.begin():
            session.merge(extracted_msg)



print("Initialing db")
init_db()
print("Done")

print("Stating ingest_new_messages")
ingest_new_messages(cl, THREAD_ID)
print("Done")

cl.realtime_on("message", handle_direct_message)

print("Subscribing to realtime_connect")
rt = cl.realtime_connect()
rt.direct_subscribe()
print("Ready...")

try:
    rt.ping()
    # rt.direct_send_text(THREAD_ID, "Hello from MQTT")
    while True:
        try:
            rt.read_once()
        except TimeoutError:
            continue
finally:
    cl.realtime_disconnect()
