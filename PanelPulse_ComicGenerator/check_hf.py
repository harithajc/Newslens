import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")

print("Starts with hf_ :", token.startswith("hf_"))
print("Length          :", len(token))
print("Has spaces      :", token != token.strip())
print("Has quote marks :", '"' in token or "'" in token)

r = requests.get(
    "https://huggingface.co/api/whoami-v2",
    headers={"Authorization": f"Bearer {token.strip()}"},
    timeout=30,
)
print("Status:", r.status_code)