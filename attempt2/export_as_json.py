import json

from attempt2.utils.insta_utils import get_client, get_thread_id

OUTPUT_FILE = "test/thread_export.json"

cl = get_client()
# THREAD_ID = get_thread_id(cl)
THREAD_ID = 340282366841710301281153262129164814061

messages = cl.direct_messages(THREAD_ID, amount=0)

data = [msg.dict() for msg in messages]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
