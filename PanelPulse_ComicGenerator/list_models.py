import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for m in client.models.list():
    if "image" in m.name or "flash" in m.name:
        print(m.name)