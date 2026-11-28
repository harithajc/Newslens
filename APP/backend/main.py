"""NewsLens API for generating PanelPulse comics."""
from __future__ import annotations

import sys
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import (
    get_story_by_id,
    get_stories,
    migrate_published_dates,
    migrate_story_text,
    save_stories,
)
from .fetch_news import fetch_all_feeds
from .story_text import is_comic_available

# ---- Find the two comic generators (original and v2) ----
PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMIC_ROOT = PROJECT_ROOT / "PanelPulse_ComicGenerator"
if str(COMIC_ROOT) not in sys.path:
    sys.path.insert(0, str(COMIC_ROOT))

from Generator.comic_generator import ComicGenerator, ComicInput  # noqa: E402

V2_ROOT = PROJECT_ROOT / "PanelPulse_v2"
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

import comic as comic_v2  # noqa: E402


# ---- Request and response shapes ----
class ComicRequest(BaseModel):
    """Story facts accepted by the comic generator."""

    headline: str = Field(..., min_length=1, max_length=300)
    summary: str = Field(default="", max_length=2000)  # can be empty
    source_url: str = Field(default="", max_length=2048)


class PanelResponse(BaseModel):
    title: str
    caption: str
    dialogue: str


class ComicResponse(BaseModel):
    comic_url: str
    used_image_provider: bool
    panels: List[PanelResponse]


class V2ComicResponse(ComicResponse):
    sensitive: bool


# ---- App setup ----
OUTPUT_DIR = COMIC_ROOT / "output"
REFRESH_MINUTES = 30
generator = ComicGenerator(output_dir=OUTPUT_DIR)
scheduler = BackgroundScheduler()
v2_lock = Lock()  # comic.py uses one shared pen, so draw one comic at a time

app = FastAPI(title="NewsLens API", version="0.1.0")

# CORS lets the demo page (Live Server, port 5500) and the future React app
# (port 5173) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "http://127.0.0.1:5173", "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/comics", StaticFiles(directory=OUTPUT_DIR), name="comics")


# ---- News refresh (manual and every 30 minutes) ----
def refresh_news() -> Dict[str, int]:
    """Fetch and save headlines, then print the refresh result."""
    stories = fetch_all_feeds()
    saved = save_stories(stories)
    print(
        f"News refresh: fetched={len(stories)}, saved={saved}",
        flush=True,
    )
    return {"fetched": len(stories), "saved": saved}


@app.on_event("startup")
def start_scheduler() -> None:
    """Clean old data, then start automatic headline refreshes."""
    migrate_published_dates()
    migrate_story_text()
    scheduler.add_job(
        refresh_news,
        "interval",
        minutes=REFRESH_MINUTES,
        id="news-refresh",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def stop_scheduler() -> None:
    """Stop automatic headline refreshes."""
    if scheduler.running:
        scheduler.shutdown(wait=False)


# ---- Basic routes ----
@app.get("/")
def root() -> Dict[str, str]:
    return {
        "name": "NewsLens API",
        "health": "/health",
        "docs": "/docs",
        "create_comic": "POST /api/comics",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


# ---- Stories ----
@app.get("/api/stories")
def read_stories(limit: int = 50, section: Optional[str] = None) -> List[Dict[str, object]]:
    """Return stories saved in the database, with comic flags."""
    enriched_stories = []
    for story in get_stories(limit, section):
        headline = story.get("title", "")
        summary = story.get("summary", "")
        enriched_stories.append(
            {
                **story,
                "comic_available": is_comic_available(headline, summary),
                "sensitive": comic_v2.is_sensitive(headline, summary),
            }
        )
    return enriched_stories


@app.post("/api/refresh")
def refresh_stories() -> Dict[str, int]:
    """Fetch Times of India headlines and save new stories."""
    return refresh_news()


# ---- Original comic generator ----
def make_comic(headline: str, summary: str, source_url: str) -> ComicResponse:
    """Create a comic using the same logic for stories and manual requests."""
    headline = headline.strip()
    summary = summary.strip()
    normalized_headline = " ".join(headline.casefold().split())
    normalized_summary = " ".join(summary.casefold().split())
    if not summary or normalized_summary == normalized_headline:
        summary = "Open the source link for the full story."
    try:
        result = generator.generate(
            ComicInput(headline, summary, source_url),
            filename=f"{uuid4().hex}.png",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save comic output") from exc

    return ComicResponse(
        comic_url=f"/comics/{result.output_path.name}",
        used_image_provider=result.used_image_provider,
        panels=[
            PanelResponse(
                title=panel.title,
                caption=panel.caption,
                dialogue=panel.dialogue,
            )
            for panel in result.panels
        ],
    )


@app.post("/api/comics", response_model=ComicResponse, status_code=201)
def create_comic(request: ComicRequest) -> ComicResponse:
    """Create a comic from a manual headline and summary."""
    return make_comic(request.headline, request.summary, request.source_url)


@app.post("/api/stories/{story_id}/comic", response_model=ComicResponse, status_code=201)
def create_story_comic(story_id: str) -> ComicResponse:
    """Create a comic from a saved news story."""
    story = get_story_by_id(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    title = story.get("title", "")
    summary = story.get("summary", "").strip() or title
    return make_comic(title, summary, story.get("link", ""))


# ---- PanelPulse v2 comic generator (rule-based, local art) ----
def make_comic_v2(headline: str, summary: str, source_url: str = "") -> V2ComicResponse:
    """Create a comic with the rule-based PanelPulse v2 generator."""
    with v2_lock:
        image = comic_v2.make_comic(headline, summary, source_url)
    filename = f"{uuid4().hex}.png"
    try:
        image.save(OUTPUT_DIR / filename)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save comic output") from exc

    panels = comic_v2.make_panels(headline, summary)
    return V2ComicResponse(
        comic_url=f"/comics/{filename}",
        used_image_provider=False,
        panels=[
            PanelResponse(title=p["title"], caption=p["caption"], dialogue="")
            for p in panels
        ],
        sensitive=comic_v2.is_sensitive(headline, summary),
    )


@app.post("/api/v2/comics", response_model=V2ComicResponse, status_code=201)
def create_comic_v2(request: ComicRequest) -> V2ComicResponse:
    """Create a v2 comic from a manual headline and summary."""
    return make_comic_v2(request.headline, request.summary, request.source_url)


@app.post("/api/v2/stories/{story_id}/comic", response_model=V2ComicResponse, status_code=201)
def create_story_comic_v2(story_id: str) -> V2ComicResponse:
    """Create a v2 comic from a saved news story."""
    story = get_story_by_id(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return make_comic_v2(
        story.get("title", ""),
        story.get("summary", ""),
        story.get("link", ""),
    )