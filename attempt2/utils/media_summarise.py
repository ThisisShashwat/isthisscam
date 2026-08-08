import base64
import os

from openai import OpenAI

from config import OPENROUTER_API_KEY, SUMMARY_MODEL

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://ai.hackclub.com/proxy/v1", )

audio_path = r"E:\PythonProject\scamming\attempt2\media\32946349913594990503845414400163840_0_voice_message.mp4"

import json
import subprocess


def has_video_stream(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "json",
         file_path], capture_output=True, text=True, )
    info = json.loads(result.stdout or "{}")
    return bool(info.get("streams"))


def summarise_file(file_path):
    extension = os.path.splitext(file_path)[1].lower().lstrip(".")

    with open(file_path, "rb") as f:
        media_data = base64.b64encode(f.read()).decode("utf-8")

    if extension == "mp4" and not has_video_stream(file_path):
        extension = "m4a"

    if extension in ("jpg", "jpeg", "png", "webp"):

        content = [{"type": "text", "text": ("Describe this image in detail. "
                                             "Mention all important visual elements, "
                                             "people, objects, actions, visible text, "
                                             "and relevant context. "
                                             "End with a one-line TL;DR."
                                             "Do not use markdown or any formatting, use only plain text. "), },
                   {"type": "image_url", "image_url": {"url": f"data:image/{extension};base64,{media_data}"}, }, ]


    elif extension == "gif":

        content = [{"type": "text", "text": ("Describe this GIF in detail. "
                                             "Explain what happens throughout the animation, "
                                             "including important actions, visible text, "
                                             "changes between frames, and context. "
                                             "End with a one-line TL;DR."
                                             "Do not use markdown or any formatting, use only plain text. "), },
                   {"type": "image_url", "image_url": {"url": f"data:image/gif;base64,{media_data}"}, }, ]


    elif extension in ("mp3", "wav", "m4a", "aac", "ogg", "flac",):

        content = [{"type": "text", "text": ("First, Transcribe the audio properly "
                                             "Include everything important that is said if any. "
                                             "then summarise the audio in the end in a single line. "
                                             "Do not use markdown or any formatting, use only plain text. "), },
                   {"type": "input_audio", "input_audio": {"data": media_data, "format": extension, }, }, ]

    elif extension in ("mp4", "mov", "webm", "avi", "mkv",):

        content = [{"type": "text", "text": ("Summarize this video in detail. "
                                             "Mention every scene, on-screen text, "
                                             "spoken dialogue, transitions, and important "
                                             "visual details. "
                                             "End with a one-line TL;DR."
                                             "Do not use markdown or any formatting, use only plain text. "), },
                   {"type": "video_url", "video_url": {"url": f"data:video/{extension};base64,{media_data}"}, }, ]

    else:
        raise ValueError(f"Unsupported media extension: .{extension}")

    response = client.chat.completions.create(model=SUMMARY_MODEL, messages=[{"role": "user", "content": content, }], )

    return response.choices[0].message.content

