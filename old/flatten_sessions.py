import json

with open("thread_sessions.json", encoding="utf-8") as f:
    sessions = json.load(f)


def render_turn(t):
    parts = []
    for m in t["messages"]:
        if isinstance(m, dict):
            parts.append(f"[shared a reel]")
        elif m is None:
            parts.append("[non-text message]")
        else:
            parts.append(m)
    line = f"{t['sender']}: " + " / ".join(parts)
    if t.get("reply_to"):
        line += f"  (replying to: \"{t['reply_to'][0]}\")"
    if t.get("reactions"):
        line += f"  [reacted {', '.join(t['reactions'])}]"
    return line


transcripts = []
for i, s in enumerate(sessions):
    header = f"--- Session {i + 1}: {s['start']} to {s['end']} ---"
    body = "\n".join(render_turn(t) for t in s["turns"])
    transcripts.append(header + "\n" + body)

with open("sessions_flat.json", "w", encoding="utf-8") as f:
    json.dump(transcripts, f, indent=2, ensure_ascii=False)
