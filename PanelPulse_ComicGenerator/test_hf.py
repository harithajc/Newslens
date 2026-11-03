import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")
print("Token found:", token is not None)   # prints True/False only, never the key

url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {token}"}
prompt = (
    "flat colorful cartoon, thick black outlines, small round robot reporter, "
    "cream face, grey metal frame, red ear pieces, yellow hat, green chest panel, "
    "holding a tiny spiral notepad, simple background, no text"
)

response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=120)
print("Status:", response.status_code)

if response.status_code == 200:
    with open("panel_hf.png", "wb") as f:
        f.write(response.content)
    print("Saved panel_hf.png")
else:
    print(response.text[:500])