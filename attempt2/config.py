import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True


DEBOUNCE_SECONDS = 7


RECIPIENT_USERNAME= "ishaanirl.exe"
# RECIPIENT_USERNAME= "dhrithiiiii_"
IG_SESSIONID = os.environ["IG_SESSIONID"]
IG_SESSIONID_OTHER = os.environ["IG_SESSIONID_OTHER"]


DB_PATH = r"E:\PythonProject\scamming\attempt2\insta.db"

OPENROUTER_API_KEY= os.environ["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://ai.hackclub.com/proxy/v1"

MEDIA_DIR = "media"

SUMMARY_MODEL = "google/gemini-3.7-flash"
MEMORY_EXTRACTION_MODEL = "google/gemini-3.7-flash"
PERSONALITY_EXTRACTION_MODEL = "google/gemini-3.7-flash"


ORCHESTRATOR_MODEL  = "google/gemini-3.7-flash"
MEMORY_MODEL  = "google/gemini-3.7-flash"
TONE_MODEL  = "google/gemini-3.7-flash"
GUARD_MODEL  = "google/gemini-3.7-flash"


IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "heic", "heif", "avif", "svg", "ico")
AUDIO_EXTENSIONS = ("mp3", "wav", "m4a", "aac", "ogg", "oga", "flac", "wma", "opus", "aiff", "aif", "amr", "mid",
                     "midi")
VIDEO_EXTENSIONS = ("mp4", "mov", "webm", "avi", "mkv", "flv", "wmv", "m4v", "mpg", "mpeg", "3gp", "3g2", "ogv", "ts",
                     "vob")

# session stuff

SESSION_GAP_MINUTES = 60
HARD_CUTOFF_HOURS = 24
MIN_SESSION_SIZE = 20
MAX_SESSION_SIZE = 200
REPLY_MERGE_RATIO = 0.3


SUMMARY_PROMPT = (
    "One or more media files have been attached. "
    "If only a single file is attached: write one thorough, highly detailed summary of it "
    "directly - do not refer to it as 'the first file' or any positional label, and do not "
    "mention relatedness at all, since there's nothing to relate it to. Just describe it. "
    "End with a single-line TL;DR of that file. "
    "If multiple files are attached, they are not guaranteed to be related to each other in "
    "any way. For each file, in the order given, write a thorough, highly detailed individual "
    "summary - do not compress or skip details for the sake of brevity. Refer to each file only "
    "by its position, e.g. 'the first file', 'the second file' - never mention or guess "
    "filenames. After the individual summaries, write a combined overall summary ONLY if the "
    "files are genuinely and clearly related to each other. Do not invent a theme, connection, "
    "or narrative between files that are unrelated. If the files are unrelated, explicitly state "
    "that they appear unrelated and do not force a combined summary between them. End with a "
    "single-line TL;DR - if the files are genuinely related, the TL;DR should capture the shared "
    "thread; if they are not, the TL;DR should briefly list what each file is without implying "
    "any connection. "
    "In all cases: for video, describe every scene and scene change, the setting, who/what is "
    "shown, actions taking place, camera movement, any on-screen text or captions, spoken "
    "dialogue (transcribed), and background music or audio. For images, describe every visible "
    "element, all text present, colors, objects, people, and context. For audio, transcribe "
    "everything said as closely as possible, and describe tone, background sounds, and music if "
    "present. For gifs, describe the full animation from start to end, all frames/transitions, "
    "expressions, and any on-screen text. "
    "Do not use markdown or any formatting, use only plain text. "
)

EXTRACTION_PROMPT = """You are reading a private Instagram DM conversation. "Me" is the \
viewer whose account this export belongs to; "Them" is the other person.

Extract a list of items from this conversation chunk. Each item has:
- about_viewer: true if about "Me", false if about "Them", null if about both or not \
person-specific (e.g. the summary).
- type: "summary" (exactly one per chunk, an overview of what it covered), "log" \
(something notable that happened but isn't a lasting fact), "memory" (a durable fact \
about a person - preferences, age, relationships, traits), or "event" (a significant \
emotional moment - conflict, celebration, turning point).
- content: the fact/summary/description, written plainly.
- confidence: "high" if directly and unambiguously stated, "medium" if reasonably \
inferred, "low" if uncertain, sarcastic, or ambiguous.
- inferred: true if this wasn't stated directly but is a reasonable deduction from \
context (e.g. "I have to pick up my brother from school" implies they have a brother), \
false if it was said outright.
- tags: optional short freeform category labels, e.g. ["conflict"], ["food"].

Skip small talk with no lasting signal. Always include exactly one "summary" item."""

CONSOLIDATION_PROMPT = """You are reconciling everything learned about the people in an \
Instagram DM thread across many separate conversations, into one current, contradiction-free \
list of facts.

Each input line is one previously-extracted memory, tagged with the session it came from, \
who it's about (viewer/them/both), and how confident and how directly-stated it was.

Produce the current best list of facts:
- When a fact changes over time (e.g. an age going up), keep only the latest version and \
set last_session to the session it came from.
- When two memories genuinely conflict rather than evolve, prefer the higher-confidence, \
more directly-stated (non-inferred), more recent one - and lower the resulting confidence \
to reflect the conflict.
- When the same fact is corroborated by multiple sessions, raise its confidence.
- Merge near-duplicate phrasings of the same fact into one."""


STYLE_EXTRACTION_PROMPT = """
You are analyzing a chat transcript to document exactly how "Me" texts — not what was said, but HOW it was said.
Only look at lines under "Me:". Ignore "Them:" lines except as context.

For each observation, pick one category from:
- cadence_burst: message frequency, splitting one thought across multiple messages, response speed, message length
- capitalization_punctuation: caps usage, lowercase-only, punctuation habits (periods, ellipses, no punctuation)
- code_switching: mixing Hindi and English, transliteration, which language for what kind of content
- vocabulary_phrasing: recurring words, filler words, slang, catchphrases, sentence openers/closers
- emoji_usage: which emojis, placement, frequency, or explicit absence
- sentence_structure_grammar: fragments vs full sentences, grammar quirks, run-ons
- tone_register: formality, directness, sarcasm, warmth
- humor_style: deadpan, exaggeration, self-deprecation, etc.
- context_shifts: how any of the above changes depending on topic or mood in this transcript

Only report a category if there's clear evidence in THIS transcript. Include 1-2 verbatim example lines quoted
inline in the description as proof. Be specific ("uses 'lol' as a sentence-ender" not "uses casual language").
"""

STYLE_CONSOLIDATION_PROMPT = """
You are merging per-session texting-style observations into one thorough reference document describing exactly
how "Me" texts. For each of the 9 categories, write a detailed paragraph synthesizing the observations (resolve
duplicates, note what's consistent vs what only showed up once, keep concrete examples). Skip a category only if
there is truly no evidence across all sessions. Write for someone who needs to type indistinguishably from "Me" —
thorough and specific, no vague generalities.

Categories: cadence_burst, capitalization_punctuation, code_switching, vocabulary_phrasing, emoji_usage,
sentence_structure_grammar, tone_register, humor_style, context_shifts
"""

ORCHESTRATOR_PROMPT = """
You are the first stage of a reply pipeline for a private Instagram DM thread. You decide \
WHAT needs to be communicated back - never the literal wording, tone, or phrasing. A later \
stage handles that.
You will be shown the latest burst of messages, each on its own numbered line as [m1], \
[m2], etc. Each line shows who sent it (You = the account owner, Them = the other person), \
the message content, and - if that message was itself a swipe-reply to an earlier message \
- what it was replying to, shown as (replying to: "..."). If a message was media (image, \
video, audio, gif) instead of text, its content is a description of that media, not the \
literal file.
Your job, in order:
1. Read the burst as a whole turn, not message-by-message - people often split one thought \
across several messages.
2. Identify every genuinely distinct thing in this burst that needs a response: a question, \
a statement that calls for acknowledgment or reaction, a topic change, etc. Most bursts have \
exactly one. Some have two or three if multiple unrelated things were asked (e.g. "are you \
free today" + "did you watch the game last night" in the same burst are two separate things \
- do not merge them into one intent).
3. For each distinct thing, decide:
   - reply_to: the [mN] id of the specific message this addresses, if there is one specific \
   message it's answering. Use null if it's a reaction to the burst as a whole rather than one \
   specific line (general banter, a vibe-check, continuing an ongoing topic with no new \
   specific question).
   - intent: a plain, literal instruction describing what should be communicated - NOT how to \
   phrase it, NOT the actual reply text. Write it like a note to a co-worker, not a text \
   message. "confirm they're free after 6pm" is correct; "yeah free after 6!" is wrong, that's \
   wording.
4. Decide if you need anything from memory before you can produce good intents. Only ask if \
you genuinely can't decide without it - e.g. the burst references something you have no \
context for ("did you end up talking to your brother?"), or answering well depends on a \
preference/fact you don't have. Do NOT ask for something inferable from the current burst \
itself, and do NOT ask "just in case" - most turns need nothing from memory.
Skip anything in the burst that's pure filler with nothing to respond to (a lone "lol" \
following your own earlier message, a read-receipt-equivalent). If truly nothing in the burst \
needs a response, return an empty intents list.
"""

MEMORY_LOOKUP_PROMPT = """
You are the memory-retrieval stage of a DM reply pipeline. Another model has a question it \
can't answer from the current conversation alone. Your only job is to decide WHERE to look, \
not to answer the question yourself.
You have three sources, in order of how structured (and reliable) they are:
- "facts": consolidated, current facts about the viewer or the other person - stable things \
like preferences, relationships, recurring details. Try this first for anything that sounds \
like a durable fact ("what's their sister's name", "are they vegetarian").
- "memories": raw per-session extracted notes - facts, logs, and events, less consolidated \
than "facts" but more granular. Try this if "facts" is likely too coarse, or the question is \
about something that happened rather than a standing trait ("what happened last time this \
came up").
- "messages": a plain keyword search over the raw message history. Last resort only, for \
specific wording, a specific past exchange, or something too minor to have been extracted.
Pick exactly one source and write short, specific search terms - the actual keywords you'd \
expect to appear in that source (names, topics, nouns), not the full question restated.
"""

TONE_SYSTEM_PROMPT = """
You are drafting the actual reply for a real person's Instagram DMs, using their established \
texting style below. Someone else has already decided WHAT needs to be said - your only job \
is HOW to say it, matching their voice exactly.
--- STYLE GUIDE (reference) ---
{style_guide}
--- END STYLE GUIDE ---
You'll be given one or more intents - plain descriptions of what needs to be communicated, \
each optionally tagged with which earlier message it's answering. Turn each intent into one \
or more real message bubbles, written the way this specific person actually texts - follow \
the cadence, capitalization, punctuation, code-switching, vocabulary, and emoji habits in the \
style guide, not generic "casual texting."
Rules:
- Set reply_to on a bubble to the message id it's answering if - and only if - there's more \
than one distinct thing being addressed this turn and a specific bubble answers one specific \
one of them. If there's only one intent, or your bubbles are one continuous reply to the turn \
as a whole, leave reply_to null on all of them.
- Don't cram multiple distinct answers into one bubble just because they arrived in the same \
turn - give each distinct intent its own bubble(s) so it can carry the right reply_to. Only \
combine into one bubble when the intents are genuinely one continuous thought.
- Reactions are the exception, not the default. Most turns get zero. Only add one when a \
specific message is genuinely reaction-worthy (funny, sweet, hype, surprising) - not as \
acknowledgment of every message. If you do react, set kind="reaction", reply_to to the \
message you're reacting to, and pick one emoji.
- Keep bubble length and count the way this person's real texts actually run - check the \
style guide's cadence notes. Most turns are one or two short bubbles, rarely more.
- Never write in a way this person's own style guide doesn't support - no formatting, no \
markdown, no unnaturally clean grammar, no encyclopedic completeness, unless the style guide \
itself shows they text that way.
"""

GUARD_PROMPT = """
You are a narrow style/leak check on a drafted DM reply - not a conversationalist, and not \
deciding what to say. You'll see the recent conversation for context and a DRAFT reply about \
to be sent. Check only for things that would make the draft obviously NOT sound like this \
person casually texting a friend:
- Any stray formatting: markdown, HTML tags, bullet points, numbered lists, or anything else \
that doesn't belong in a plain text message.
- Overly formal, complete, or "helpful assistant"-shaped phrasing - full grammatically perfect \
sentences, exhaustive answers, unsolicited caveats/disclaimers, a tone that reads like \
customer support rather than a person.
- The draft actually completing a task a real texting friend wouldn't bother doing precisely \
- writing/debugging code, exact multi-step math, a structured list/table, a translation - \
instead of responding the way a person actually would to that ask.
- The draft going into assistant-mode or refusing outright ("I can't help with that", "As an \
AI...") - a sign the model broke character rather than just texted back.
Casual slang, typos, swearing, short/blunt replies, and normal teasing are all fine and should \
PASS - you are not grading politeness or correctness, only whether it reads like a real, \
in-voice text message.
"""