import json

from sqlmodel import Session

from export_to_db import ingest_new_messages
from utils.db_utils import init_db, engine
from utils.extraction import extract_message
from utils.insta_utils import get_client

print("before getclient")
cl = get_client()
print("after getclient")
THREAD_ID = 340282366841710301281153262129164814061

def handle_direct_message(payload):
    msg = cl.direct_message(payload["message"]["thread_id"], payload["message"]["item_id"], amount=20)
    extracted_msg = extract_message(msg, cl, media_download=True, media_summary=True)
    print(extracted_msg)
    with Session(engine) as session:
        with session.begin():
            session.add(extracted_msg)



print("init_db")
init_db()
print("after init_db")

print("before ingest_new_messages")
ingest_new_messages(cl, THREAD_ID)
print("after ingest_new_messages")

cl.realtime_on("message", handle_direct_message)

print("before realtime_connect")
rt = cl.realtime_connect()
rt.direct_subscribe()
print("after realtime_connect")

try:
    rt.ping()
    rt.direct_send_text(THREAD_ID, "Hello from MQTT")
    while True:
        rt.read_once()
finally:
    cl.realtime_disconnect()
