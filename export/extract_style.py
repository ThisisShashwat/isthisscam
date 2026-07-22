import json, os, re
from openrouter import OpenRouter
from openrouter.utils import RetryConfig, BackoffStrategy
from dotenv import load_dotenv
load_dotenv()

MODEL = "google/gemini-3.6-flash"

client = OpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    server_url="https://ai.hackclub.com/proxy/v1",
)

with open("sessions_flat.json", encoding="utf-8") as f:
    sessions = json.load(f)

PROMPT = """You are extracting a texting-style profile for "you" from a private chat
transcript between two people, labeled "you" and "them", exported from
Instagram DMs. The goal is a profile precise enough that another model could
read it and type indistinguishably from "you" - not a personality summary,
a style manual: every habit in how the messages are typed.

INPUT FORMAT
You will receive {n} sessions as flattened text, each with a header giving
the session number and time range, followed by turns like:
[start -> end] sender: message1 / message2 / ...  (replying to: "...")  [reacted emoji]
- "[non-text message]" = a non-text attachment, no extractable style alone.
- "[shared a reel]" = a shared post - only relevant if "you" commented on it.
- (replying to: "...") and [reacted emoji] are context only.

SCOPE
Only catalog "you"'s style. "them"'s messages are context for what "you" is
responding to - never attribute their phrasing or habits to "you".

METHOD - READ SEQUENTIALLY, DON'T SUMMARIZE
Go session by session, in order. In a scratchpad, log concrete style
observations as you find them, each with a verbatim example message from
that session as evidence. A habit seen once between ten unrelated turns
counts as much as one repeated five times - note it either way.

CATEGORIES
- orthography: default capitalization, end-of-message punctuation (period /
  none / "!!!" / "???" / "..."), apostrophe habits, spelling that's actually
  just their normal spelling vs a one-off typo
- segmentation: one long message vs a burst of short ones for one thought,
  typical bubbles per turn, double-texting when unanswered, self-corrections
  in a follow-up bubble
- length_structure: typical message length, fragments vs full sentences vs
  run-ons, how questions get phrased
- vocabulary: filler words/tics, recurring catchphrases, swearing (frequency,
  words, what triggers it), nicknames used for "them" or for themself
- emoji_reactions: which emoji recur and where (end of message / replacing a
  word / standalone), which emoji they react with and to what kind of message
- humor_register: sarcasm markers, teasing style, self-deprecation, how a
  joke is typically built
- conversational_moves: openers, sign-offs, how they change topic, agree or
  disagree, apologize, ask for something, express excitement or annoyance
- context_sensitivity: conditional shifts - e.g. punctuation returning when
  annoyed or serious, tone shifting by topic. Write these as if-then rules,
  not as a separate flat average.

CONFIDENCE
"consistent" = shows up across most sessions. "occasional" = only 2-3
sessions. Tag every rule - do not silently smooth an occasional pattern into
a flat, unconditional rule.

ACCURACY RULES
- Never invent a habit not evidenced by a verbatim example.
- Sarcasm, bits, and hyperbole are humor_register material, not literal
  rules about how "you" always types.
- Before logging a line, re-check it actually appeared in a "you" turn.

OUTPUT FORMAT
First think session-by-session in a <scratchpad> block. Then output:

<style_guide>
A markdown document organized by the categories above. Each rule states the
pattern, its confidence tag, and 1-2 verbatim example messages.
</style_guide>

<persona_prompt>
A second-person system prompt instructing a model to type as "you" - direct
imperative rules (not a description), 8-12 verbatim example messages as
anchors, and an explicit instruction to never break character or mention
being an AI.
</persona_prompt>

--- SESSIONS ---
{sessions_text}
"""

sessions_text = "\n\n".join(sessions)

response = client.chat.send(
    model=MODEL,
    messages=[{"role": "user", "content": PROMPT.format(n=len(sessions), sessions_text=sessions_text)}],
    max_tokens=16000,
    timeout_ms=300_000,  # generous - one big call across all sessions, not a quick lookup
    retries=RetryConfig(
        strategy="backoff",
        backoff=BackoffStrategy(
            initial_interval=1000,
            max_interval=10_000,
            max_elapsed_time=30_000,
            exponent=1.5,
        ),
        retry_connection_errors=True,
    ),
)

raw = response.choices[0].message.content

with open("style_raw.txt", "w", encoding="utf-8") as f:
    f.write(raw)

style_guide = re.search(r"<style_guide>(.*?)</style_guide>", raw, re.DOTALL).group(1).strip()
persona_prompt = re.search(r"<persona_prompt>(.*?)</persona_prompt>", raw, re.DOTALL).group(1).strip()

with open("style_guide.md", "w", encoding="utf-8") as f:
    f.write(style_guide)

with open("persona_prompt.txt", "w", encoding="utf-8") as f:
    f.write(persona_prompt)