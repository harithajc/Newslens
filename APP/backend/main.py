"""NewsLens API for generating PanelPulse comics."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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
generator = ComicGenerator(output_dir=OUTPUT_DIR)
app = FastAPI(title="NewsLens API", version="0.1.0")
app.mount("/comics", StaticFiles(directory=OUTPUT_DIR), name="comics")


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


@app.post("/api/comics", response_model=ComicResponse, status_code=201)
def create_comic(request: ComicRequest) -> ComicResponse:
    try:
        result = generator.generate(
            ComicInput(request.headline, request.summary, request.source_url),
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
