import os
import random
import re
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv
from instagrapi import Client
from openrouter import OpenRouter

load_dotenv()

MODEL = "google/gemini-3.5-flash-lite"
GUARD_MODEL = "google/gemini-3.5-flash-lite"
DEBOUNCE_SECONDS = 10
MAX_BUBBLES = 4
MAX_GUARD_RETRIES = 2

client = OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"], server_url="https://ai.hackclub.com/proxy/v1", )

persona, style_guide = "", ""
if Path("../persona_prompt.txt").exists():
    with open("../persona_prompt.txt", encoding="utf-8") as f:
        persona = f.read()

if Path("../style_guide.md").exists():
    with open("../style_guide.md", encoding="utf-8") as f:
        style_guide = f.read()

system_prompt = persona + "\n\n--- STYLE GUIDE (reference) ---\n\n" + style_guide
history = [{"role": "system", "content": system_prompt}]

OUTPUT_PROTOCOL = """
Reply using exactly this format, nothing outside it. No HTML, no markdown, no code
formatting of any kind - just plain text, like a real text message.

<reaction target="N">EMOJI or NONE</reaction>
<reply_to bubble="B">N</reply_to>
<messages>
first bubble
second bubble
</messages>

- You'll be shown the messages from this burst numbered above the conversation, purely
  so you can target a specific one. Never mention the numbers - they aren't part of the
  chat.
- <reaction target="N"> reacts to message N from that numbered list. Omit target to react
  to the most recent message. Use EMOJI or NONE.
- <reply_to bubble="B">N</reply_to> is OPTIONAL. Use it whenever one specific bubble below is
  answering one particular message from the burst - common whenever the burst had more than
  one distinct question or topic. "B" is which bubble (1st, 2nd, ...) should carry the
  reply, "N" is which burst message it answers. Omit the whole tag if there's only one
  message in the burst, or none of your bubbles map onto one specific message.
- Each line inside <messages> is sent as its own separate text bubble. Keep it to at most
  {max_bubbles} bubbles - real texting is rarely more than that in one turn. One line is
  often enough. <messages> can be empty if a reaction alone is the right move.
""".strip().format(max_bubbles=MAX_BUBBLES)

TAG_PATTERN = re.compile(r"<[^>]+>")
LEAK_PHRASES = [
    "as an ai", "i'm an ai", "i am an ai", "language model", "i'm a bot", "i am a bot",
    "as a language model", "i don't have feelings", "i cannot fulfill", "i'm not able to",
    "large language model", "openai", "anthropic", "system prompt", "i'm just a program",
]


def sanitize(text):
    flags = []
    if TAG_PATTERN.search(text):
        flags.append("html/xml tag")
    clean = TAG_PATTERN.sub("", text).strip()
    lowered = clean.lower()
    for phrase in LEAK_PHRASES:
        if phrase in lowered:
            flags.append(f"phrase: {phrase}")
    return clean, flags


def guard_check(reaction, bubbles, recent_context):
    guard_prompt = f"""
You are a narrow content check, not a conversationalist. You will see the last few messages
of a real DM conversation and a DRAFT reply someone is about to send. Your only job: does
the draft contain anything that would reveal or strongly suggest the sender is an AI, a bot,
or not a real person typing casually? This includes stray HTML/markdown, mentions of being
an AI/model/assistant/bot, unnaturally formal or robotic phrasing, or any leaked
formatting/system artifacts. Casual slang, swearing, typos, and normal teasing are fine and
should PASS.

Recent conversation:
{recent_context}

Draft reaction: {reaction}
Draft messages:
{chr(10).join(bubbles) if bubbles else "(none)"}

Respond in exactly this format:
<verdict>PASS or FAIL</verdict>
<reason>one short sentence, only if FAIL</reason>
""".strip()

    response = client.chat.send(
        model=GUARD_MODEL,
        messages=[{"role": "user", "content": guard_prompt}],
        max_tokens=100,
    )
    raw = response.choices[0].message.content
    verdict_match = re.search(r"<verdict>(.*?)</verdict>", raw, re.DOTALL)
    reason_match = re.search(r"<reason>(.*?)</reason>", raw, re.DOTALL)
    verdict = verdict_match.group(1).strip().upper() if verdict_match else "FAIL"
    reason = reason_match.group(1).strip() if reason_match else "guard response unparseable"
    return verdict == "PASS", reason


SESSION_FILE = "../../ig_session.json"
cl = Client()

if Path(SESSION_FILE).exists():
    cl.load_settings(SESSION_FILE)
else:
    cl.login_by_sessionid(os.environ["IG_SESSIONID"])
    cl.dump_settings(SESSION_FILE)

TARGET_USERNAME = "iampihooo"
target_id = cl.user_id_from_username(TARGET_USERNAME)
thread = cl.direct_thread_by_participants([int(target_id)])
THREAD_ID = thread["thread"]["thread_id"]

pending_lock = threading.Lock()
pending = {"messages": [], "last_id": None}
debounce_timer = None


def format_burst(burst_messages):
    return "\n".join(f"{i + 1}. {m['text']}" for i, m in enumerate(burst_messages))


def generate_draft(burst_messages, extra_instruction=None):
    context_msg = {
        "role": "system",
        "content": (
            "Messages from this burst, numbered for <reaction>/<reply_to> targeting only:\n"
            + format_burst(burst_messages)
        ),
    }
    call_messages = history + [context_msg, {"role": "system", "content": OUTPUT_PROTOCOL}]
    if extra_instruction:
        call_messages.append({"role": "system", "content": extra_instruction})
    response = client.chat.send(model=MODEL, messages=call_messages, max_tokens=500)
    raw = response.choices[0].message.content

    reaction_match = re.search(r'<reaction(?:\s+target="(\d+)")?>(.*?)</reaction>', raw, re.DOTALL)
    reply_to_match = re.search(r'<reply_to(?:\s+bubble="(\d+)")?>\s*(\d+)\s*</reply_to>', raw, re.DOTALL)
    messages_match = re.search(r"<messages>(.*?)</messages>", raw, re.DOTALL)

    reaction_target_idx = int(reaction_match.group(1)) if reaction_match and reaction_match.group(1) else None
    reaction = reaction_match.group(2).strip() if reaction_match else "NONE"
    reply_bubble_idx = int(reply_to_match.group(1)) if reply_to_match and reply_to_match.group(1) else 1
    reply_to_idx = int(reply_to_match.group(2)) if reply_to_match else None

    bubbles = []
    if messages_match:
        bubbles = [line.strip() for line in messages_match.group(1).strip().splitlines() if line.strip()]

    cleaned_bubbles = []
    all_flags = []
    for b in bubbles[:MAX_BUBBLES]:
        clean, flags = sanitize(b)
        if clean:
            cleaned_bubbles.append(clean)
        all_flags.extend(flags)

    clean_reaction, reaction_flags = sanitize(reaction) if reaction.upper() != "NONE" else (reaction, [])
    all_flags.extend(reaction_flags)

    return clean_reaction, reaction_target_idx, reply_to_idx, reply_bubble_idx, cleaned_bubbles, all_flags


def keep_typing_alive(stop_event, thread_id, interval=4.0):
    while not stop_event.wait(interval):
        try:
            rt.direct_indicate_activity(thread_id, is_active=True)
        except Exception as e:
            print(f"[typing heartbeat failed]: {e}")


def process_burst():
    with pending_lock:
        if not pending["messages"]:
            return
        burst_messages = pending["messages"]
        pending["messages"] = []
        pending["last_id"] = None

    typing_stop = threading.Event()
    try:
        rt.direct_indicate_activity(THREAD_ID, is_active=True)
    except Exception as e:
        print(f"[typing indicator on failed]: {e}")
    typing_thread = threading.Thread(target=keep_typing_alive, args=(typing_stop, THREAD_ID), daemon=True)
    typing_thread.start()

    try:
        recent_context = "\n".join(f"{m['role']}: {m['content']}" for m in history[-8:])
        extra_instruction = None

        for attempt in range(MAX_GUARD_RETRIES + 1):
            reaction, reaction_target_idx, reply_to_idx, reply_bubble_idx, bubbles, flags = generate_draft(
                burst_messages, extra_instruction
            )

            if flags:
                print(f"[Guard] deterministic flags on attempt {attempt}: {flags}")
                extra_instruction = (
                    f"Your previous draft was rejected for: {', '.join(flags)}. "
                    "Write it again as plain text only, fully in character, nothing that looks like this."
                )
                continue

            ok, reason = guard_check(reaction, bubbles, recent_context)

            if ok:
                break
            print(f"[Guard] semantic check failed on attempt {attempt}: {reason}")
            extra_instruction = f"Your previous draft was rejected: {reason}. Write it again avoiding that."
        else:
            print("[Guard] all retries failed, skipping this reply entirely")
            return

        print(f"[debug] reply_to_idx={reply_to_idx} reply_bubble_idx={reply_bubble_idx} reaction_target_idx={reaction_target_idx}")

        target_msg = burst_messages[-1]
        if reaction_target_idx and 1 <= reaction_target_idx <= len(burst_messages):
            target_msg = burst_messages[reaction_target_idx - 1]

        if reaction and reaction.upper() != "NONE":
            if target_msg["item_id"]:
                try:
                    cl.direct_send_reaction(THREAD_ID, target_msg["item_id"], emoji=reaction)
                    print(f"[Reacted \"{target_msg['text'][:30]}\"]: {reaction}")
                except Exception as e:
                    print(f"[Reaction failed]: {e}")
            else:
                print(f"[Reaction skipped, no message id captured]: wanted to react {reaction}")

        reply_target = None
        if reply_to_idx and 1 <= reply_to_idx <= len(burst_messages):
            candidate = burst_messages[reply_to_idx - 1]
            if candidate["item_id"]:
                reply_target = SimpleNamespace(id=candidate["item_id"], client_context=candidate["client_context"])
            else:
                print("[reply_to skipped, no message id captured for target]")

        for i, bubble in enumerate(bubbles):
            delay = min(4.0, 0.6 + len(bubble) * 0.03) + random.uniform(0, 1.5)
            time.sleep(delay)

            this_reply = reply_target if reply_target and (i + 1) == reply_bubble_idx else None
            cl.direct_send(bubble, thread_ids=[THREAD_ID], reply_to_message=this_reply)
            print(f"[Bot Reply]: {bubble}" + ("  (as reply)" if this_reply else ""))

        if bubbles:
            history.append({"role": "assistant", "content": "\n".join(bubbles)})

    except Exception as e:
        print(f"\n[Error generating/sending reply]: {e}")
    finally:
        typing_stop.set()
        try:
            rt.direct_indicate_activity(THREAD_ID, is_active=False)
        except Exception as e:
            print(f"[typing indicator off failed]: {e}")


def handle_direct_message(payload):
    global debounce_timer
    try:
        msg = payload.get("message", {})
        sender_id = msg.get("user_id")

        if sender_id != int(target_id):
            return

        payload_thread_id = payload.get("thread_id") or msg.get("thread_id")
        if payload_thread_id is not None and str(payload_thread_id) != str(THREAD_ID):
            print(f"[SAFETY] message claims thread_id={payload_thread_id}, expected {THREAD_ID} - skipping")
            return

        text = msg.get("text")
        if not text:
            return

        msg_id = msg.get("item_id") or msg.get("id")
        client_context = msg.get("client_context")
        if msg_id is None:
            print(f"[warn] no message id found in payload, reactions/replies will be skipped: {msg}")

        print(f"\n[{TARGET_USERNAME}]: {text}")
        history.append({"role": "user", "content": text})

        with pending_lock:
            pending["messages"].append({"text": text, "item_id": msg_id, "client_context": client_context})
            pending["last_id"] = msg_id

            if debounce_timer:
                debounce_timer.cancel()
            debounce_timer = threading.Timer(DEBOUNCE_SECONDS, process_burst)
            debounce_timer.daemon = True
            debounce_timer.start()

    except Exception as e:
        print(f"\n[Error handling message]: {e}")


def handle_typing(payload):
    global debounce_timer
    try:
        payload_thread_id = payload.get("thread_id")
        if payload_thread_id is not None and str(payload_thread_id) != str(THREAD_ID):
            return

        value = payload.get("value")
        status = value.get("activity_status") if isinstance(value, dict) else payload.get("activity_status")
        if str(status) not in ("1", "true", "True"):
            return

        with pending_lock:
            if debounce_timer and pending["messages"]:
                debounce_timer.cancel()
                debounce_timer = threading.Timer(DEBOUNCE_SECONDS, process_burst)
                debounce_timer.daemon = True
                debounce_timer.start()
                print("[typing] friend is still typing, extending debounce")
    except Exception as e:
        print(f"\n[Error handling typing event]: {e}")


cl.realtime_on("message", handle_direct_message)
cl.realtime_on("typing", handle_typing)
rt = cl.realtime_connect()
rt.direct_subscribe()
rt.ping()


def listen():
    while True:
        try:
            rt.read_once()
        except TimeoutError:
            pass
        except Exception:
            time.sleep(5)


threading.Thread(target=listen, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    if debounce_timer:
        debounce_timer.cancel()
    cl.realtime_disconnect()