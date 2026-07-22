import json, os, re
from openrouter import OpenRouter
from dotenv import load_dotenv
load_dotenv()

MODEL = "google/gemini-3.6-flash"

client = OpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    server_url="https://ai.hackclub.com/proxy/v1",
)

with open("sessions_flat.json", encoding="utf-8") as f:
    sessions = json.load(f)

PROMPT = """You are extracting memory from a private chat transcript between two people,
labeled "you" and "them", exported from Instagram DMs. Your job is to capture
everything worth remembering from this session — not just tidy biographical
facts, but the full picture: who they are, what's going on in their lives,
how they relate to each other, and what actually happened in this
conversation.

INPUT FORMAT
You will receive one session as flattened text: a header with the session
number and time range, followed by turns like:
[start -> end] sender: message1 / message2 / ...  (replying to: "...")  [reacted emoji]
- "[non-text message]" = a non-text attachment — no extractable content alone.
- "[shared a reel]" = a shared post — note as a chat_event if it sparked
  discussion; otherwise skip.
- (replying to: "...") is context only — don't attribute the quoted text to
  the replier as their own statement.
- [reacted emoji] is context only, but a strong/repeated reaction pattern can
  itself be worth noting as a chat_event.

METHOD — READ SEQUENTIALLY, DON'T SUMMARIZE
Go through the transcript turn by turn, in order, for BOTH senders. A detail
mentioned once between ten unrelated turns counts as much as one repeated
five times.

ATTRIBUTION CHECK
Before writing "who", re-check which sender's turn a line actually appeared
in. Never attribute a quoted or paraphrased line to the other person by
default.

CATEGORIES
- identity: stable info — name, age, school, hometown, family background
- situation: time-bound state — injuries, current events, moods. If it
  evolves during the session, collapse into ONE fact reflecting the latest
  state, not one entry per update.
- preference: likes/dislikes, habits, recurring opinions
- relationship_dynamic: inside jokes, banter style, stated boundaries
- plan: concrete future actions, logistics
- chat_event: things that happened IN this conversation — a game they
  played (describe the game + outcome, don't log wrong guesses as facts), a
  disagreement, a joke, a shared link/reel and the reaction to it
- inference: pattern-based, not stated outright — restrict to communication
  style (slang, joking style, response speed). Do NOT infer the emotional
  nature of the relationship ("flirtatious", "close") unless directly and
  repeatedly stated — banter alone isn't enough.

CONFIDENCE
"explicit" = directly stated. "inferred" = pattern-based or derived (e.g.
age from "turning 18 next year" is inferred, not explicit).

ACCURACY RULES
- Rejected guesses in a guessing game aren't facts about the answer — but
  "they played a guessing game about X" is a valid chat_event.
- Sarcasm/hyperbole/bits aren't literal facts, even hedged as "joking
  reference to..." — those go in chat_event or relationship_dynamic, never
  identity or situation.
- Never invent specifics not present in the text.

OUTPUT FORMAT
First think turn-by-turn in a <scratchpad> block. Then output ONLY a JSON
array inside <memories></memories> tags:
[
  {{"who": "you" | "them" | "both",
   "category": "identity" | "situation" | "preference" | "relationship_dynamic" | "plan" | "chat_event" | "inference",
   "fact": "concise statement",
   "confidence": "explicit" | "inferred",
   "session": <int>}}
]
If nothing qualifies, output an empty array.

--- SESSION TO ANALYZE ---
{session_text}
"""

all_memories = []
for i, session_text in enumerate(sessions, start=1):
    print(f"[{i}/{len(sessions)}] running...")
    try:
        from openrouter.utils import RetryConfig, BackoffStrategy

        response = client.chat.send(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT.format(session_text=session_text)}],
            max_tokens=7000,
            timeout_ms=120_000,  # generous read timeout — Gemini can take 15-20s+
            retries=RetryConfig(
                strategy="backoff",
                backoff=BackoffStrategy(
                    initial_interval=1000,
                    max_interval=10_000,
                    max_elapsed_time=30_000,  # cap total retry budget, don't let it silently multiply cost
                    exponent=1.5,
                ),
                retry_connection_errors=True,
            ),
        )

        raw = response.choices[0].message.content
        memories = json.loads(re.search(r"<memories>(.*?)</memories>", raw, re.DOTALL).group(1))
    except Exception as e:
        print(f"[{i}/{len(sessions)}] FAILED: {e}")
        continue

    for m in memories:
        m["session"] = i
    all_memories.extend(memories)

    with open("memories.json", "w", encoding="utf-8") as f:
        json.dump(all_memories, f, indent=2, ensure_ascii=False)

    print(f"[{i}/{len(sessions)}] ok -> {len(memories)} memories (total {len(all_memories)})")

print(f"done: {len(sessions)} sessions -> {len(all_memories)} memories")