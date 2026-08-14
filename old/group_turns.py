import json
from datetime import datetime, timedelta

TURN_GAP = timedelta(minutes=10)

def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

with open("thread_clean.json", encoding="utf-8") as f:
    messages = json.load(f)

messages.sort(key=lambda m: m["timestamp"])

def item(m):
    return {"is_share": True, "shared_url": m["shared_url"]} if m.get("is_share") else m["text"]

turns = []
for m in messages:
    same_sender = turns and turns[-1]["sender"] == m["sender"]
    close_enough = turns and parse(m["timestamp"]) - parse(turns[-1]["end"]) <= TURN_GAP
    if same_sender and close_enough:
        turns[-1]["messages"].append(item(m))
        turns[-1]["end"] = m["timestamp"]
        if m.get("reactions"):
            turns[-1].setdefault("reactions", []).extend(m["reactions"])
        if m.get("reply_to"):
            turns[-1].setdefault("reply_to", []).append(m["reply_to"])
    else:
        turn = {"sender": m["sender"], "start": m["timestamp"], "end": m["timestamp"], "messages": [item(m)]}
        if m.get("reactions"):
            turn["reactions"] = list(m["reactions"])
        if m.get("reply_to"):
            turn["reply_to"] = [m["reply_to"]]
        turns.append(turn)

with open("thread_turns.json", "w", encoding="utf-8") as f:
    json.dump(turns, f, indent=2, ensure_ascii=False)