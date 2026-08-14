from sqlmodel import Session

from utils.db_utils import init_db, engine
from utils.extract_memories import extract_memories
from utils.extraction import extract_message
from utils.general_utils import get_field
from utils.ingest_messages import ingest_new_messages
from utils.insta_utils import get_client, get_thread_id
from utils.sessionizer import recalculate_session

print("before getclient")
cl = get_client()
print("after getclient")

THREAD_ID = get_thread_id(cl, test=False)


def handle_direct_message(payload):
    try:
        msg = cl.direct_message(get_field(payload, "message", "thread_id"), get_field(payload, "message", "item_id"),
                                amount=20)
        extracted_msg = extract_message(msg, cl, media_download=True, media_summary=True, include_reels=True)
        print(extracted_msg)

        if extracted_msg.item_type == "action_log": return
        with Session(engine) as session:
            with session.begin():
                session.merge(extracted_msg)
    except Exception as e:
        print(e)


print("Initialing db")
init_db()
print("Done")

print("Stating ingest_new_messages")
ingest_new_messages(cl, THREAD_ID)
print("Done")

print("Stating recalculate_sessions")
recalculate_session(THREAD_ID)
print("Done")

print("Stating extract_memories")
extract_memories(THREAD_ID)
print("Done")

exit()

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
