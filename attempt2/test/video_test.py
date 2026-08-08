from openai import OpenAI
import base64, os

from dotenv import load_dotenv

from config import OPENROUTER_API_KEY

load_dotenv()


client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://ai.hackclub.com/proxy/v1", )


# video = base64.b64encode(open("E:\\PythonProject\\scamming\\attempt2\\media\\32946349913594990503845414400163840_0_voice_message.m4a", "rb").read()).decode()



audio_path = r"E:\PythonProject\scamming\attempt2\media\32946349913594990503845414400163840_0_voice_message.m4a"

with open(audio_path, "rb") as f:
    audio = base64.b64encode(f.read()).decode()



# r = client.chat.completions.create(
#     model="google/gemini-3.5-flash-lite",
#     messages=[ # type: ignore
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Summarize this reel in detail. Mention every scene, on-screen text, spoken dialogue, transitions, and end with a one-line TL;DR."
#                 },
#                 {
#                     "type": "video_url",
#                     "video_url": {
#                         "url": f"data:video/mp4;base64,{video}"
#                     }
#                 }
#             ]
#         }
#     ]
# )

r = client.chat.completions.create(
    model="google/gemini-3.5-flash-lite",
    messages=[ # type: ignore
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Transcribe this voice message exactly, then summarize what is being said properly"
                    )
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio,
                        "format": "m4a"
                    }
                }
            ]
        }
    ]
)

print(r.choices[0].message.content)