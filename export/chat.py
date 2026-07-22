import os
from openrouter import OpenRouter
from dotenv import load_dotenv
load_dotenv()

MODEL = "google/gemini-3.5-flash-lite"

client = OpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    server_url="https://ai.hackclub.com/proxy/v1",
)

with open("persona_prompt.txt", encoding="utf-8") as f:
    persona = f.read()

with open("style_guide.md", encoding="utf-8") as f:
    style_guide = f.read()

system_prompt = persona + "\n\n--- STYLE GUIDE (reference) ---\n\n" + style_guide

history = [{"role": "system", "content": system_prompt}]

print("Persona loaded. Type as 'them'. Ctrl+C or 'quit' to exit.\n")

while True:
    user_input = input("them: ")
    if user_input.strip().lower() in ("quit", "exit"):
        break

    history.append({"role": "user", "content": user_input})

    response = client.chat.send(
        model=MODEL,
        messages=history,
        max_tokens=500,
    )
    reply = response.choices[0].message.content
    print(f"you: {reply}\n")

    history.append({"role": "assistant", "content": reply})