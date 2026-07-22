import json
from collections import Counter

with open("thread_export.json", encoding="utf-8") as f:
    messages = json.load(f)

ids = [m["id"] for m in messages]
counts = Counter(ids)
dupes = {k: v for k, v in counts.items() if v > 1}

print(f"Total messages: {len(ids)}")
print(f"Unique ids: {len(counts)}")
print(f"Duplicate ids: {len(dupes)}")
if dupes:
    example = next(iter(dupes))
    print(f"\nExample duplicate id ({example}) appears {dupes[example]} times")


import json

with open("thread_sessions.json", encoding="utf-8") as f:
    sessions = json.load(f)

SESSION_INDEX = 1  # 1-based, change to whichever session looks wrong

s = sessions[SESSION_INDEX - 1]
print(f"Session {SESSION_INDEX}: {s['start']} to {s['end']}  ({len(s['turns'])} turns)\n")
for t in s["turns"]:
    print(f"[{t['start']} -> {t['end']}] {t['sender']}: {t['messages']}")