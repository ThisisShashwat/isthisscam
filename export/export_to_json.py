import json,os

from instagrapi import Client
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

SESSION_FILE = "../ig_session.json"
cl = Client()

if Path(SESSION_FILE).exists():
    cl.load_settings(SESSION_FILE)
else:
    cl.login_by_sessionid(os.environ["IG_SESSIONID"])
    cl.dump_settings(SESSION_FILE)

OUTPUT_FILE = "thread_export.json"

target_id = cl.user_id_from_username("ishaanirl.exe")
thread = cl.direct_thread_by_participants([int(target_id)])
THREAD_ID = thread["thread"]["thread_id"]

messages = cl.direct_messages(THREAD_ID, amount=0)

data = [msg.dict() for msg in messages]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
