
# NewsLens app

## Run the API

From the repository root:

```powershell
python -m pip install -r APP/backend/requirements.txt
python -m uvicorn APP.backend.main:app --reload
```

Open `http://127.0.0.1:8000/` for the API links, or check
`http://127.0.0.1:8000/health`, then generate a local comic:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/comics `
  -ContentType "application/json" `
  -Body '{"headline":"A new public health program launches","summary":"The program expands access to local clinics. The first phase begins this month.","source_url":"https://example.com/article"}'
```

The response contains the comic URL and the four-panel script. Generated images
are served from `/comics/{filename}`. The API uses the local art fallback by
default; setting `HF_TOKEN` enables optional Hugging Face image generation.
