import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = (
    "flat colorful cartoon, thick black outlines, small round robot reporter, "
    "cream face, grey metal frame, red ear pieces, yellow hat, green chest panel, "
    "holding a tiny spiral notepad, simple background, no text"
)

models = ["gemini-3.1-flash-lite-image", "gemini-2.5-flash-image"]

for m in models:
    print("Trying:", m)
    try:
        response = client.models.generate_content(model=m, contents=[prompt])
        saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                filename = f"panel_{m}.png"
                with open(filename, "wb") as f:
                    f.write(part.inline_data.data)
                print("  Saved", filename)
                saved = True
        if not saved:
            print("  No image came back")
    except Exception as e:
        print("  Error:", str(e)[:300])