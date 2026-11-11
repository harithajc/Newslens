"""Generate fact-bounded four-panel news comics.

The pipeline is intentionally provider-neutral:
* script generation is local and only uses the supplied headline and summary;
* Hugging Face image generation is optional;
* Pillow creates a readable local fallback when no image provider is configured.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from PIL import Image, ImageDraw, ImageFont


PANEL_SIZE = (768, 768)
CANVAS_SIZE = (1536, 1536)
HF_MODEL = "black-forest-labs/FLUX.1-schnell"
MASCOT_PROMPT = (
    "flat colorful editorial cartoon, thick black outlines, a small round robot "
    "reporter with a yellow hat, grey metal frame, red ear pieces and a green "
    "chest panel, simple background, no text, no speech bubbles"
)


@dataclass(frozen=True)
class ComicInput:
    headline: str
    summary: str
    source_url: str = ""

    def validate(self) -> None:
        if not self.headline.strip():
            raise ValueError("headline must not be empty")
        if not self.summary.strip():
            raise ValueError("summary must not be empty")


@dataclass(frozen=True)
class PanelScript:
    title: str
    caption: str
    dialogue: str
    art_prompt: str


@dataclass(frozen=True)
class ComicResult:
    output_path: Path
    used_image_provider: bool
    panels: tuple[PanelScript, ...]


class ComicGenerator:
    """Create a four-panel comic without requiring a paid API."""

    def __init__(
        self,
        output_dir: str | Path = "output",
        hf_token: str | None = None,
        image_model: str = HF_MODEL,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.image_model = image_model

    def generate(self, story: ComicInput, filename: str = "panelpulse-comic.png") -> ComicResult:
        story.validate()
        panels = self.build_script(story)
        images: list[Image.Image] = []
        used_provider = False

        for panel in panels:
            image = self._generate_image(panel.art_prompt)
            used_provider = used_provider or image is not None
            images.append(image or self._fallback_panel(panel))

        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._compose(images, panels, story, output_path)
        return ComicResult(output_path, used_provider, tuple(panels))

    @staticmethod
    def build_script(story: ComicInput) -> list[PanelScript]:
        """Create a short script using no facts beyond the supplied story."""
        headline = _clean(story.headline)
        summary = _clean(story.summary)
        sentences = _sentences(summary)
        what_happened = sentences[0] if sentences else summary
        context = sentences[1] if len(sentences) > 1 else (
            "The briefing explains why this development matters."
        )
        return [
            PanelScript(
                "The headline",
                headline,
                "What happened?",
                f"{MASCOT_PROMPT}, curious reporter reacting to: {headline}",
            ),
            PanelScript(
                "The key fact",
                what_happened,
                "Here is the key fact.",
                f"{MASCOT_PROMPT}, reporter presenting a clear news card about: {what_happened}",
            ),
            PanelScript(
                "Why it matters",
                context,
                "Why should we care?",
                f"{MASCOT_PROMPT}, reporter pointing at a simple cause-and-effect diagram about: {context}",
            ),
            PanelScript(
                "The takeaway",
                "Read the source for the full context and latest updates.",
                "That is the briefing.",
                f"{MASCOT_PROMPT}, reporter closing a calm news briefing, hopeful mood",
            ),
        ]

    def _generate_image(self, prompt: str) -> Image.Image | None:
        if not self.hf_token:
            return None
        url = f"https://router.huggingface.co/hf-inference/models/{self.image_model}"
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.hf_token}"},
                json={"inputs": prompt},
                timeout=120,
            )
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            return image.resize(PANEL_SIZE)
        except (requests.RequestException, OSError) as exc:
            print(f"Image provider unavailable; using local art fallback: {exc}")
            return None

    @staticmethod
    def _fallback_panel(panel: PanelScript) -> Image.Image:
        image = Image.new("RGB", PANEL_SIZE, "#f7e7c6")
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 738, 738), outline="#263238", width=8)
        draw.ellipse((220, 180, 548, 508), fill="#b9c3c7", outline="#263238", width=8)
        draw.ellipse((290, 260, 350, 320), fill="#fff8e7", outline="#263238", width=5)
        draw.ellipse((418, 260, 478, 320), fill="#fff8e7", outline="#263238", width=5)
        draw.ellipse((312, 282, 334, 304), fill="#263238")
        draw.ellipse((440, 282, 462, 304), fill="#263238")
        draw.rectangle((296, 370, 472, 440), fill="#6fbf73", outline="#263238", width=5)
        draw.arc((330, 320, 438, 410), 20, 160, fill="#263238", width=5)
        draw.polygon(((250, 190), (310, 110), (458, 110), (520, 190)), fill="#f3c84b", outline="#263238")
        draw.text((40, 570), "LOCAL ART FALLBACK", fill="#263238", font=_font(28))
        return image

    @staticmethod
    def _compose(
        images: Iterable[Image.Image],
        panels: list[PanelScript],
        story: ComicInput,
        output_path: Path,
    ) -> None:
        canvas = Image.new("RGB", CANVAS_SIZE, "#fffaf0")
        draw = ImageDraw.Draw(canvas)
        for index, (image, panel) in enumerate(zip(images, panels)):
            x = (index % 2) * PANEL_SIZE[0]
            y = (index // 2) * PANEL_SIZE[1]
            canvas.paste(image.resize(PANEL_SIZE), (x, y))
            draw.rectangle((x + 16, y + 16, x + 752, y + 752), outline="#263238", width=6)
            draw.rectangle((x + 28, y + 570, x + 740, y + 744), fill="#fffaf0")
            draw.text((x + 48, y + 590), f"{index + 1}. {panel.title}", fill="#263238", font=_font(30))
            draw.multiline_text(
                (x + 48, y + 635),
                "\n".join(textwrap.wrap(panel.caption, width=39)),
                fill="#263238",
                font=_font(24),
                spacing=4,
            )
        draw.rectangle((0, 0, CANVAS_SIZE[0], 54), fill="#263238")
        draw.text((28, 12), "PANELPULSE | AI-ASSISTED | SOURCE-BASED BRIEFING", fill="white", font=_font(24))
        if story.source_url:
            draw.text((28, 1480), f"Source: {story.source_url}", fill="#263238", font=_font(18))
        canvas.save(output_path)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _sentences(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", value) if part.strip()]


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a four-panel PanelPulse comic.")
    parser.add_argument("--headline", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--output", default="output/panelpulse-comic.png")
    args = parser.parse_args()
    result = ComicGenerator(Path(args.output).parent).generate(
        ComicInput(args.headline, args.summary, args.source_url),
        Path(args.output).name,
    )
    print(f"Saved {result.output_path}")
    print("Image provider:", "Hugging Face" if result.used_image_provider else "local fallback")


if __name__ == "__main__":
    main()
