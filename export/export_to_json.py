import json

from instagrapi import Client

SESSION_FILE = "../ig_session.json"
THREAD_ID = 340282366841710301244259135983410713362
OUTPUT_FILE = "thread_export.json"

cl = Client()
cl.load_settings(SESSION_FILE)

messages = cl.direct_messages(THREAD_ID, amount=0)

data = [msg.dict() for msg in messages]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
