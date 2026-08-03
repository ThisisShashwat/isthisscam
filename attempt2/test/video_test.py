from openai import OpenAI
import base64, os

from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://ai.hackclub.com/proxy/v1", )


video = base64.b64encode(open("reel2.mp4", "rb").read()).decode()

r = client.chat.completions.create(
    model="google/gemini-3.5-flash-lite",   # change if your proxy uses another name
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Summarize this reel in detail. Mention every scene, on-screen text, spoken dialogue, transitions, and end with a one-line TL;DR."
                },
                {
                    "type": "video_url",
                    "video_url": {
                        "url": f"data:video/mp4;base64,{video}"
                    }
                }
            ]
        }
    ]
)

print(r.choices[0].message.content)