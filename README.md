# NewsLens

**A short daily news briefing ranked by importance, not clicks.**

NewsLens gives a short daily list of the most important stories from Times of India, picked by machine learning. When a story is hard to understand, a button shows it as a simple 4-panel comic.

## The Problem

- Fewer people read newspapers now.
- News apps rank stories by clicks, so gossip can appear above a health alert.
- Endless feeds mean nobody feels "done" with the news.
- Feeds only show what you already like (filter bubble).

People spend hours on news but still miss what matters.

## Our Solution

- **Must Know Today:** the 5 to 10 most important stories
- **Sections:** India, Business, World, Sports
- **Short summaries** with a link to the full Times of India article
- **"You're all caught up"** screen at the end
- **Comic version (PanelPulse):** tap a button to see a hard story as 3 to 4 simple comic panels
- No ads, no click tracking, the same list for everyone

## How It Works

1. **Collect:** headlines come from Times of India RSS feeds
2. **Label:** the team marks headlines as important (policy, health, money, safety, education) or not important (gossip, clickbait, trivia)
3. **Train:** TF-IDF with Logistic Regression learns from the labels and ranks new stories
4. **Check:** accuracy and F1-score
5. **Show:** the backend sends ranked stories to the app
6. **Comic (optional):** the comic generator uses the headline and summary to create a 4-panel comic

## PanelPulse (Comic Feature)

PanelPulse uses the story's headline and summary for the comic text. The first panel uses the headline and the second uses the first summary sentence; panels 3 and 4 use fixed template text. When a second summary sentence is available, panel 3 can use it as context. A Hugging Face provider can generate panel art, with a local Pillow fallback when it is unavailable.

![Sample comic](PanelPulse_ComicGenerator/Images/sample-image.png)

Rules for comics: use only the headline and short summary, add text in code (not inside generated images), avoid real people's faces, label every comic "AI-assisted", and credit the source.

## Tech Stack

| Part | Tool |
|---|---|
| News source | Times of India RSS feeds |
| Fetching | Python, feedparser |
| Machine learning | scikit-learn (planned), sentence-transformers (planned) |
| Backend | FastAPI |
| Database | SQLite |
| Updates | APScheduler (every 30 minutes) |
| Frontend | React with Tailwind CSS (planned) |
| Hosting | Render or Railway, Vercel or Netlify |

## Repository Structure

- `APP/`: the NewsLens app
  - `backend/`: FastAPI backend, feed fetching, SQLite storage, and scheduled refresh
  - `ml/` (planned): labeled data and the importance model
  - `frontend/` (planned): the screens users see
- `PanelPulse_ComicGenerator/`: the comic feature
  - `Images/`: sample comics

## Status

- [x] Idea and plan
- [x] Feed fetching
- [x] SQLite storage
- [x] Scheduled refresh every 30 minutes
- [x] Backend API (`/api/stories`, `/api/refresh`, and comic endpoints)
- [x] Automated comic generation from stored stories
- [ ] Labeled dataset
- [ ] Importance model
- [ ] Frontend app
- [ ] Pilot survey and user testing

## How to run

From the repository root, install the backend dependencies:

```bash
pip install -r APP/backend/requirements.txt
```

Then start the API:

```bash
py -m uvicorn APP.backend.main:app --reload
```

After starting, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Call `POST /api/refresh` once to load stories.

Put any Hugging Face key in a `.env` file that is never committed. On Mac or Linux, use `python3` instead of `py`.

## AI Use

GitHub Copilot helped write code. All code was run, tested and reviewed by the team, and comics are labeled AI-assisted.

## Limitations

- "Important" is partly an opinion.
- Only one newspaper for now.
- Feeds give only headlines and short summaries, so comics are simple explanations, not the full story.
- Small data, so some stories may be sorted wrongly.

## Future Scope

More newspapers, Kannada and Hindi, better AI comic art, an email digest, and a mobile app.

## Sustainable Development Goals

SDG 9, SDG 11, SDG 17

## Credits

News headlines, short summaries and links belong to Times of India. NewsLens shows only short summaries with credit and a link to the original article.

NewsLens uses only RSS headlines, short summaries and links. The feed terms of use are to be confirmed.
