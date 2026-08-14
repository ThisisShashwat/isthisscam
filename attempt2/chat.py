import threading

from sqlmodel import Session

from ai.llm_pipeline import run_turn
from config import DEBOUNCE_SECONDS, DEBUG
from utils.db_utils import init_db, engine
from sessions.extract_memories import extract_memories
from sessions.extract_personality import extract_personality
from utils.extraction import extract_message
from utils.general_utils import get_field
from utils.ingest_messages import ingest_new_messages
from utils.insta_utils import get_client, get_thread_id
from sessions.sessionizer import recalculate_session

print("before getclient")
cl = get_client()
print("after getclient")

THREAD_ID = get_thread_id(cl, test=False)

pending_messages = {}
pending_timers = {}

def flush(thread_id):

    messages = pending_messages.pop(thread_id, [])
    pending_timers.pop(thread_id, None)

    if not messages:
        return

    print("flushed")

    draft = run_turn(thread_id, messages, personality)
    print(draft.model_dump() if draft else None)


def handle_direct_message(payload):
    try:
        msg = cl.direct_message(get_field(payload, "message", "thread_id"), get_field(payload, "message", "item_id"),
                                amount=20)
        extracted_msg = extract_message(msg, cl, media_download=True, media_summary=True, include_reels=True)

        if extracted_msg.item_type == "action_log": return
        with Session(engine) as session:
            with session.begin():
                session.merge(extracted_msg)

        thread_id = str(extracted_msg.thread_id)
        if DEBUG: thread_id = get_thread_id(cl, test=True)

        if extracted_msg.is_sent_by_viewer:
            old_timer = pending_timers.pop(thread_id, None)
            if old_timer:
                old_timer.cancel()

            pending_messages.pop(thread_id, None)
            return

        pending_messages.setdefault(thread_id, []).append(extracted_msg)

        old_timer = pending_timers.get(thread_id)
        if old_timer:
            old_timer.cancel()

        timer = threading.Timer(DEBOUNCE_SECONDS, flush, [thread_id])
        timer.daemon = True
        pending_timers[thread_id] = timer
        timer.start()

    except Exception as e:
        print(e)


print("Initialing db")
init_db()
print("Done")

print("Stating ingest_new_messages")
# ingest_new_messages(cl, THREAD_ID)
print("Done")

print("Stating recalculate_sessions")
# recalculate_session(THREAD_ID)
print("Done")

print("Stating extract_memories")
# extract_memories(THREAD_ID)
print("Done")

print("Stating extract_personality")
personality = extract_personality(THREAD_ID)
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
