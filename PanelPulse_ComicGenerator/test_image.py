import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite-image"   # change this name if it fails

prompt = (
    "Flat colorful cartoon, thick black outlines. A small round robot reporter "
    "with a yellow hat and a tiny notepad looks surprised, holding a phone. "
    "Simple city street background. No text."
)

response = client.models.generate_content(model=MODEL, contents=[prompt])

saved = False
for part in response.parts:
    if part.text:
        print("Model said:", part.text)
    elif part.inline_data is not None:
        part.as_image().save("panel_test.png")
        saved = True
        print("Saved panel_test.png")

if not saved:
    print("No image came back. Try another model name.")