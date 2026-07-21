import json

with open("thread_export.json", encoding="utf-8") as f:
    messages = json.load(f)

clean = []
for m in messages:
    entry = {"timestamp": m["timestamp"], "sender": "you" if m["is_sent_by_viewer"] else "them", "text": m["text"], }
    if m.get("reactions"):
        entry["reactions"] = [r["emoji"] for r in m["reactions"].get("emojis", [])]
    if m.get("reply"):
        entry["reply_to"] = m["reply"]["text"]
    clean.append(entry)

with open("thread_clean.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, indent=2, ensure_ascii=False)
