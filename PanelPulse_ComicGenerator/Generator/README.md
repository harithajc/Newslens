# Comic Generator

This is a working four-panel generator. It accepts a headline and short summary,
creates a fact-bounded script, generates panel art through Hugging Face when
`HF_TOKEN` is configured, and otherwise creates a local robot-reporter fallback.
The fallback means the pipeline can be tested without a paid image API.

## Run it

From `PanelPulse_ComicGenerator`:

```powershell
python -m pip install -r requirements.txt
python -m Generator.comic_generator `
  --headline "A new public health program launches" `
  --summary "The program will expand access to local clinics. Officials said the first phase begins this month." `
  --source-url "https://example.com/article"
```

The finished comic is written to `output/panelpulse-comic.png`. Set `HF_TOKEN`
in `.env` to request generated art from `black-forest-labs/FLUX.1-schnell`.
Provider availability and quotas can change; failures are reported and fall
back to local art.

## Safety and editorial rules

- Supply only a headline and short summary; the generator does not invent article facts.
- Text is rendered in code for readability, not embedded in generated images.
- Every output is labeled AI-assisted and can credit the source URL.
- Review sensitive stories before publishing; do not turn deaths or tragedies into entertainment.
- The output is an explainer, not a replacement for the original Times of India article.
