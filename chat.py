import os, threading
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv
load_dotenv()

SESSION_FILE = "ig_session.json"
cl = Client()

if Path(SESSION_FILE).exists():
    cl.load_settings(SESSION_FILE)
else:
    cl.login_by_sessionid(os.environ["IG_SESSIONID"])
    cl.dump_settings(SESSION_FILE)

target_id = cl.user_id_from_username("iampihooo")
thread = cl.direct_thread_by_participants([int(target_id)])
THREAD_ID = thread["thread"]["thread_id"]
last_msg_id = None

def handle_direct_message(payload):
    global last_msg_id
    try:
        msg = payload["message"]
        last_msg_id = msg.get("item_id") or msg.get("id")
        if msg["user_id"] == int(target_id): print(f"\n{msg['text']}\n> ", end="", flush=True)
    except Exception:
        pass

cl.realtime_on("message", handle_direct_message)
rt = cl.realtime_connect()
rt.direct_subscribe()
rt.ping()

def listen():
    while True:
        try:
            rt.read_once()
        except TimeoutError:
            pass

threading.Thread(target=listen, daemon=True).start()
try:
    while True:
        text = input("> ")
        if text.startswith("/react"):
            emoji = text.split(maxsplit=1)[1] if " " in text else "❤"
            if last_msg_id:
                cl.direct_send_reaction(THREAD_ID, last_msg_id, emoji=emoji)
        elif text.strip():
            cl.direct_send(text, thread_ids=[THREAD_ID])
finally:
    cl.realtime_disconnect()