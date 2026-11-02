import os
import json
import urllib.request
from dotenv import load_dotenv

# Load your HF_TOKEN from the .env file
load_dotenv()
token = os.getenv("HF_TOKEN")

print("Requesting image from Hugging Face...")

# The direct URL to the FLUX model
url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

# Package your prompt and secure token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# The prompt is updated for the 2D comic style
data = {
    "inputs": "2D vector art, flat colors, thick black outlines, comic book panel. A small round robot reporter with a yellow hat and a tiny notepad looks surprised, holding a phone. Simple city street background. No text."
}

# Send the request and save the image
try:
    req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode("utf-8"))
    # Added a 30-second timeout to prevent infinite hanging
    with urllib.request.urlopen(req, timeout=30) as response:
        with open("panel_hf.png", "wb") as f:
            f.write(response.read())
    print("Success! Saved panel_hf.png")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")