import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True

RECIPIENT_USERNAME= "ishaanirl.exe"
# RECIPIENT_USERNAME= "dhrithiiiii_"
IG_SESSIONID = os.environ["IG_SESSIONID"]
IG_SESSIONID_OTHER = os.environ["IG_SESSIONID_OTHER"]


DB_PATH = r"E:\PythonProject\scamming\attempt2\insta.db"

OPENROUTER_API_KEY= os.environ["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://ai.hackclub.com/proxy/v1"

MEDIA_DIR = "media"

SUMMARY_MODEL = "google/gemini-3.5-flash-lite"
MEMORY_EXTRACTION_MODEL = "google/gemini-3.5-flash-lite"

IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "heic", "heif", "avif", "svg", "ico")
AUDIO_EXTENSIONS = ("mp3", "wav", "m4a", "aac", "ogg", "oga", "flac", "wma", "opus", "aiff", "aif", "amr", "mid",
                     "midi")
VIDEO_EXTENSIONS = ("mp4", "mov", "webm", "avi", "mkv", "flv", "wmv", "m4v", "mpg", "mpeg", "3gp", "3g2", "ogv", "ts",
                     "vob")

summary_instruction = (
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

# session stuff

SESSION_GAP_MINUTES = 60
HARD_CUTOFF_HOURS = 24
MIN_SESSION_SIZE = 20
MAX_SESSION_SIZE = 200
REPLY_MERGE_RATIO = 0.3


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