"""NewsLens API for generating PanelPulse comics."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel, Field

from .database import get_story_by_id, get_stories, save_stories
from .fetch_news import fetch_all_feeds

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMIC_ROOT = PROJECT_ROOT / "PanelPulse_ComicGenerator"
if str(COMIC_ROOT) not in sys.path:
    sys.path.insert(0, str(COMIC_ROOT))

from Generator.comic_generator import ComicGenerator, ComicInput  # noqa: E402


class ComicRequest(BaseModel):
    """Story facts accepted by the comic generator."""

    headline: str = Field(..., min_length=1, max_length=300)
    summary: str = Field(..., min_length=1, max_length=2000)
    source_url: str = Field(default="", max_length=2048)


class PanelResponse(BaseModel):
    title: str
    caption: str
    dialogue: str


class ComicResponse(BaseModel):
    comic_url: str
    used_image_provider: bool
    panels: List[PanelResponse]


OUTPUT_DIR = COMIC_ROOT / "output"
REFRESH_MINUTES = 30
generator = ComicGenerator(output_dir=OUTPUT_DIR)
scheduler = BackgroundScheduler()
app = FastAPI(title="NewsLens API", version="0.1.0")
app.mount("/comics", StaticFiles(directory=OUTPUT_DIR), name="comics")


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
    """Start automatic headline refreshes."""
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


@app.get("/api/stories")
def read_stories(limit: int = 50, section: str = None) -> List[Dict[str, str]]:
    """Return stories saved in the database."""
    return get_stories(limit, section)


@app.post("/api/refresh")
def refresh_stories() -> Dict[str, int]:
    """Fetch Times of India headlines and save new stories."""
    return refresh_news()


def make_comic(headline: str, summary: str, source_url: str) -> ComicResponse:
    """Create a comic using the same logic for stories and manual requests."""
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
