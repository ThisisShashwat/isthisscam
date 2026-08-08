import base64
import json
import mimetypes
import os
import subprocess

from openai import OpenAI

from config import OPENROUTER_API_KEY, SUMMARY_MODEL, IMAGE_EXTENSIONS, AUDIO_EXTENSIONS, VIDEO_EXTENSIONS, \
    summary_instruction

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://ai.hackclub.com/proxy/v1", )


def has_video_stream(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "json",
         file_path], capture_output=True, text=True, )
    info = json.loads(result.stdout or "{}")
    return bool(info.get("streams"))


def _build_media_block(file_path):
    extension = os.path.splitext(file_path)[1].lower().lstrip(".")

    with open(file_path, "rb") as f:
        media_data = base64.b64encode(f.read()).decode("utf-8")

    if extension == "mp4" and not has_video_stream(file_path):
        extension = "m4a"

    if extension in IMAGE_EXTENSIONS:
        return {"type": "image_url", "image_url": {"url": f"data:image/{extension};base64,{media_data}"}, }

    elif extension == "gif":
        return {"type": "image_url", "image_url": {"url": f"data:image/gif;base64,{media_data}"}, }

    elif extension in AUDIO_EXTENSIONS:
        return {"type": "input_audio", "input_audio": {"data": media_data, "format": extension}, }

    elif extension in VIDEO_EXTENSIONS:
        return {"type": "video_url", "video_url": {"url": f"data:video/{extension};base64,{media_data}"}, }

    else:
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        return {"type": "file", "file": {"filename": os.path.basename(file_path),
                                         "file_data": f"data:{mime_type};base64,{media_data}"}, }


def summarise_files(file_paths):
    content = [{"type": "text", "text": summary_instruction}]

    for file_path in file_paths:
        try:
            content.append(_build_media_block(file_path))
        except ValueError as e:
            print(f"Skipping {file_path}: {e}")

    if len(content) == 1:
        return None

    response = client.chat.completions.create(model=SUMMARY_MODEL, messages=[{"role": "user", "content": content}], )

    return response.choices[0].message.content
