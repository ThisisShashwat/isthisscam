import json
from datetime import datetime, timedelta

GAP_THRESHOLD = timedelta(hours=0.5)
MIN_TURNS = 3

with open("thread_turns.json", encoding="utf-8") as f:
    turns = json.load(f)

def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

sessions = []
for t in turns:
    if sessions and parse(t["start"]) - parse(sessions[-1]["end"]) <= GAP_THRESHOLD:
        sessions[-1]["turns"].append(t)
        sessions[-1]["end"] = t["end"]
    else:
        sessions.append({"start": t["start"], "end": t["end"], "turns": [t]})

merged = []
for s in sessions:
    if merged and len(s["turns"]) < MIN_TURNS:
        merged[-1]["turns"].extend(s["turns"])
        merged[-1]["end"] = s["end"]
    else:
        merged.append(s)
sessions = merged

with open("thread_sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, indent=2, ensure_ascii=False)

print(f"{len(turns)} turns into {len(sessions)} sessions ")