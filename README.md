# Newslens
# currently working on :PanelPulse

**News, drawn as comics.** PanelPulse turns the day's news into short, shareable 4-panel comics, so anyone can understand a story in under 30 seconds.

## The Problem

News articles are long and dense, and many people skip them. They never find out what happened or why it matters.

## Our Solution

Each news story becomes a 4-panel comic starring a friendly robot reporter:

1. **Hook:** grabs attention
2. **What happened:** the key facts
3. **Why it matters:** the context
4. **Takeaway:** a closing line and a question that invites discussion

## Example

Our first test comic, "Tech in 4 Panels: Apple Goes Foldable", was made from a real tech news story.

![Sample comic](images/sample-image.png)

## How It Works

1. **News ingestion:** stories are fetched from RSS feeds or a news API
2. **Script generation:** an LLM writes a 4-panel script using only facts from the article
3. **Panel art:** an image model draws each panel with the same mascot and style
4. **Lettering:** speech bubbles and captions are added in code, so text is always sharp and correct
5. **Human review:** an editor approves each comic before publishing
6. **Publish:** the comic appears in the app with share buttons

## Current Status

- [x] Concept validated with a manual test (script, 4 panels, lettering, layout)
- [x] Mascot and art style defined
- [ ] Automated script generation
- [ ] Automated panel generation
- [ ] Automated lettering
- [ ] Automatic news fetching
- [ ] App interface and share buttons
- [ ] User testing

## Design Principles

- **Accuracy first:** scripts use only facts from the source article, and a human reviews every comic
- **Clear labeling:** every comic is marked "AI-assisted" and credits its source
- **Careful topics:** sensitive stories (deaths, wars, tragedies) are not turned into comics
- **No real faces:** a mascot is used instead of drawing real people
- **Original art:** we do not train on other artists' copyrighted work

## Planned Tech

- Python
- LLM API for script generation
- Image generation API for panels
- Pillow for speech bubbles and text
- Cloud storage for finished comics

## Roadmap

- **Phase 1:** working comic generator (script, images, lettering)
- **Phase 2:** reliability and consistent character art
- **Phase 3:** automatic news fetching, app and sharing
- **Phase 4:** user testing and polish

**Target launch:** December 30, 2026

## License

MIT License
