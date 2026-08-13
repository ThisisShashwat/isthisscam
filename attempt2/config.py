import os

from dotenv import load_dotenv

load_dotenv()


RECIPIENT_USERNAME= "ishaanirl.exe"
# RECIPIENT_USERNAME= "dhrithiiiii_"
IG_SESSIONID = os.environ["IG_SESSIONID"]
IG_SESSIONID_OTHER = os.environ["IG_SESSIONID_OTHER"]


DB_PATH= "insta.db"
OPENROUTER_API_KEY= os.environ["OPENROUTER_API_KEY"]


MEDIA_DIR = "media"

SUMMARY_MODEL = "google/gemini-3.5-flash-lite"

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