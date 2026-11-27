import html
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps

DARK = "#263238"

# ---- Layout numbers ----
W, H = 2000, 2000
HEADER = 120
MARGIN = 30
PANEL_W = (W - 3 * MARGIN) // 2
PANEL_H = (H - HEADER - 3 * MARGIN) // 2
ART_H = 600

ART_DIR = Path(__file__).parent / "scene_art"
ART_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

# `draw` and `canvas` are set at the start of make_comic.
draw = None
canvas = None   # the whole image, needed for pasting pictures

# a tiny invisible image, only used to MEASURE text width
_measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))


# =====================  PART 1: TEXT (steps 3 and 5)  =====================
def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())

def split_sentences(text):
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

def same_text(a, b):
    def simple(t):
        return re.sub(r"[^a-z0-9]", "", t.lower())
    return simple(a) == simple(b)

def make_panels(headline, summary):
    headline = clean_text(headline)
    sentences = split_sentences(clean_text(summary))
    sentences = [s for s in sentences if not same_text(s, headline)]
    key_fact = sentences[0] if len(sentences) > 0 else "Full details are in the article."
    why = (sentences[1] if len(sentences) > 1
           else "Read the full article for more details.")
    return [
        {"title": "The headline",   "caption": headline},
        {"title": "The key fact",   "caption": key_fact},
        {"title": "Why it matters", "caption": why},
        {"title": "The takeaway",   "caption": "Open the source link to read the full story."},
    ]

def load_font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def wrap_text(text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        test = (line + " " + word).strip()
        if _measure.textlength(test, font=font) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = ""
            for character in word:
                test = line + character
                if line and _measure.textlength(test, font=font) > max_width:
                    lines.append(line)
                    line = character
                else:
                    line = test
    if line:
        lines.append(line)
    return lines


def _ellipsize(text, font, max_width):
    suffix = "..."
    while text and _measure.textlength(text + suffix, font=font) > max_width:
        text = text[:-1]
    return text.rstrip() + suffix


def find_caption_font_size(captions, width, height, start_size=72, min_size=28):
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size)
        line_height = max(1, int(size * 1.2))
        if all(
            len(wrap_text(caption, font, width)) * line_height <= height
            for caption in captions
        ):
            return size
    return min_size


def draw_caption(text, box, font_size):
    left, top, right, bottom = box
    width, height = right - left, bottom - top
    font = load_font(font_size)
    line_height = max(1, int(font_size * 1.2))
    lines = wrap_text(text, font, width)

    max_lines = max(1, height // line_height)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = _ellipsize(lines[-1], font, width)

    for index, line in enumerate(lines):
        draw.text((left, top + index * line_height), line, font=font, fill=DARK)


def draw_panel_title(title, x, y, max_width):
    for size in range(56, 27, -2):
        font = load_font(size)
        if _measure.textlength(title, font=font) <= max_width:
            break
    draw.text((x, y), title, font=font, fill=DARK)


# =====================  PART 2: TOPIC (step 6)  =====================
TOPIC_WORDS = {
    "health":  ["health", "hospital", "doctor", "disease", "vaccine", "virus",
                "cancer", "dengue", "flu", "medicine", "patient", "surgery"],
    "weather": ["rain", "flood", "cyclone", "storm", "heatwave", "weather",
                "monsoon", "fog", "temperature"],
    "school":  ["school", "college", "exam", "student", "university",
                "education", "teacher", "neet", "jee"],
    "law":     ["court", "high court", "supreme court", "judge", "bail",
                "jail", "verdict", "ruling", "petition", "tribunal", "law"],
    "sports":  ["cricket", "match", "tournament", "league", "goal", "century",
                "wicket", "batter", "bowler", "ipl", "olympic", "medal"],
    "money":   ["price", "rupee", "inflation", "economy", "economic", "gdp",
                "tax", "bank", "loan", "debt", "budget", "stock", "sensex",
                "nifty", "fuel", "petrol", "diesel", "gold", "market", "jobs"],
    "warning": ["accident", "crash", "fire", "blast", "killed", "kills",
                "death", "rams", "earthquake", "alert", "outbreak"],
    "transport": ["flight", "train", "metro", "airport", "railway", "traffic"],
}

TRAGIC_WORDS = [
    "killed", "dead", "death", "dies", "died", "murder", "blast",
    "fire", "crash", "accident", "flood", "injured", "collapse",
]
SERIOUS_TOPICS = {"warning", "weather", "law", "health"}
CHECKMARK_TOPICS = {"money", "school", "sports", "newspaper"}


def pick_topic(headline, summary=""):
    text = ((headline + " ") * 2 + summary).lower()
    best_topic, best_score = "newspaper", 0
    for topic, words in TOPIC_WORDS.items():
        score = 0
        for word in words:
            score += len(re.findall(r"\b" + re.escape(word) + r"s?\b", text))
        if score > best_score:
            best_topic, best_score = topic, score
    return best_topic


def is_serious_story(headline, summary="", topic=None):
    if topic is None:
        topic = pick_topic(clean_text(headline), clean_text(summary))
    if topic in SERIOUS_TOPICS:
        return True
    story_text = f"{clean_text(headline)} {clean_text(summary)}"
    tragic_pattern = r"\b(?:" + "|".join(map(re.escape, TRAGIC_WORDS)) + r")\b"
    return re.search(tragic_pattern, story_text, flags=re.IGNORECASE) is not None


def panel_plan(topic, sensitive=False):
    serious = sensitive or topic in SERIOUS_TOPICS
    has_topic = topic != "newspaper"
    scene = topic if has_topic else "magnifier"
    if topic == "warning":
        moods = ["neutral", "thinking", "thinking", "neutral"]
    else:
        moods = ["neutral", "surprised", "thinking", "happy"]

    calm_newspaper_exists = scene_art_path("newspaper_calm") is not None
    calm_closing_exists = scene_art_path("closing_calm") is not None
    if serious:
        opening = "newspaper_calm" if calm_newspaper_exists else "magnifier"
        panel_three = (
            "magnifier" if has_topic else
            "newspaper_calm" if calm_newspaper_exists else
            "newspaper"
        )
        closing = (
            "closing_calm" if calm_closing_exists else
            "newspaper_calm" if calm_newspaper_exists else
            "magnifier"
        )
    else:
        opening = "newspaper"
        panel_three = (
            "magnifier" if has_topic else
            "newspaper_calm" if calm_newspaper_exists else
            "newspaper"
        )
        if calm_closing_exists:
            closing = "closing_calm"
        elif topic in CHECKMARK_TOPICS:
            closing = "checkmark"
        else:
            closing = "magnifier"

    scenes = [opening, scene, panel_three, closing]
    return [{"scene": s, "mood": m} for s, m in zip(scenes, moods)]


# =====================  PART 3: PICTURES  =====================
# ---- Fallback drawings (steps 2 and 7), used only if an art file is missing ----
def circle(cx, cy, r, fill, outline=DARK, width=4):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 fill=fill, outline=outline, width=width)

def draw_robot(cx, cy, r, mood="neutral"):
    k = r / 110
    w = max(2, int(4 * k))
    circle(cx, cy, r, "#B8C2CA", width=w + 1)
    draw.polygon([(cx - 60 * k, cy - 180 * k), (cx + 60 * k, cy - 180 * k),
                  (cx + 120 * k, cy - 110 * k), (cx - 120 * k, cy - 110 * k)],
                 fill="#F2C94C", outline=DARK)
    draw.line((cx, cy - 180 * k, cx, cy - 220 * k), fill=DARK, width=w + 1)
    circle(cx, cy - 225 * k, 10 * k, "#E57373", width=w)
    pupil = 15 * k if mood == "surprised" else 10 * k
    for ex in (cx - 50 * k, cx + 50 * k):
        circle(ex, cy - 30 * k, 26 * k, "#FFFBEF", width=w)
        circle(ex, cy - 30 * k, pupil, DARK, width=1)
    if mood == "happy":
        draw.arc((cx - 45 * k, cy + 30 * k, cx + 45 * k, cy + 90 * k),
                 start=20, end=160, fill=DARK, width=w + 2)
    elif mood == "surprised":
        circle(cx, cy + 65 * k, 18 * k, DARK, width=1)
    elif mood == "thinking":
        draw.line((cx - 35 * k, cy + 65 * k, cx + 35 * k, cy + 55 * k),
                  fill=DARK, width=w + 2)
        draw.line((cx + 25 * k, cy - 75 * k, cx + 75 * k, cy - 85 * k),
                  fill=DARK, width=w + 2)
    else:
        draw.line((cx - 35 * k, cy + 65 * k, cx + 35 * k, cy + 65 * k),
                  fill=DARK, width=w + 2)

def scene_money(cx, cy):
    circle(cx, cy, 55, "#F2C94C", width=5)
    circle(cx, cy, 38, "#F7DC7A", width=2)
    draw.line((cx, cy - 22, cx, cy + 22), fill=DARK, width=6)
    draw.line((cx - 14, cy - 8, cx + 14, cy - 8), fill=DARK, width=5)
    draw.line((cx - 14, cy + 8, cx + 14, cy + 8), fill=DARK, width=5)

def scene_health(cx, cy):
    draw.rectangle((cx - 15, cy - 55, cx + 15, cy + 55), fill="#E57373", outline=DARK, width=4)
    draw.rectangle((cx - 55, cy - 15, cx + 55, cy + 15), fill="#E57373", outline=DARK, width=4)
    draw.rectangle((cx - 13, cy - 13, cx + 13, cy + 13), fill="#E57373")

def scene_law(cx, cy):
    draw.line((cx, cy - 55, cx, cy + 55), fill=DARK, width=6)
    draw.line((cx - 60, cy - 35, cx + 60, cy - 35), fill=DARK, width=6)
    for sx in (cx - 60, cx + 60):
        draw.line((sx, cy - 35, sx, cy + 5), fill=DARK, width=3)
        draw.pieslice((sx - 28, cy - 15, sx + 28, cy + 30),
                      start=0, end=180, fill="#B8C2CA", outline=DARK, width=3)
    draw.rectangle((cx - 30, cy + 50, cx + 30, cy + 62), fill=DARK)

def scene_school(cx, cy):
    draw.rectangle((cx - 60, cy - 40, cx + 60, cy + 40), fill="#64B5F6", outline=DARK, width=4)
    draw.rectangle((cx - 60, cy - 40, cx - 45, cy + 40), fill=DARK)
    for ly in (cy - 15, cy + 5, cy + 25):
        draw.line((cx - 30, ly, cx + 40, ly), fill="#FFFBEF", width=4)

def scene_weather(cx, cy):
    for (ox, oy, r) in ((-35, 5, 32), (0, -15, 42), (38, 8, 30)):
        circle(cx + ox, cy + oy, r, "#DCE6EE", outline=DARK, width=4)
    draw.rectangle((cx - 60, cy + 10, cx + 65, cy + 36), fill="#DCE6EE")
    draw.line((cx - 60, cy + 36, cx + 65, cy + 36), fill=DARK, width=4)
    for dx in (-35, 0, 35):
        draw.line((cx + dx, cy + 50, cx + dx - 6, cy + 70), fill="#1976D2", width=5)

def scene_sports(cx, cy):
    circle(cx, cy, 55, "#FFFBEF", width=5)
    draw.polygon([(cx, cy - 22), (cx + 21, cy - 7), (cx + 13, cy + 18),
                  (cx - 13, cy + 18), (cx - 21, cy - 7)], fill=DARK)
    for ax, ay in ((0, -55), (52, -17), (32, 45), (-32, 45), (-52, -17)):
        draw.line((cx + ax * 0.4, cy + ay * 0.4, cx + ax, cy + ay), fill=DARK, width=3)

def scene_warning(cx, cy):
    draw.polygon([(cx, cy - 60), (cx + 62, cy + 50), (cx - 62, cy + 50)],
                 fill="#F2C94C", outline=DARK)
    draw.line((cx, cy - 25, cx, cy + 15), fill=DARK, width=8)
    circle(cx, cy + 33, 5, DARK, width=1)

def scene_transport(cx, cy):          # a simple train
    draw.rectangle((cx - 65, cy - 35, cx + 65, cy + 30), fill="#90CAF9", outline=DARK, width=4)
    for wx in (cx - 50, cx - 10, cx + 30):
        draw.rectangle((wx, cy - 22, wx + 22, cy - 2), fill="#FFFBEF", outline=DARK, width=3)
    for wx in (cx - 38, cx + 38):
        circle(wx, cy + 40, 14, DARK, width=2)

def scene_newspaper(cx, cy):
    draw.rectangle((cx - 60, cy - 45, cx + 60, cy + 45), fill="#FFFBEF", outline=DARK, width=4)
    draw.rectangle((cx - 50, cy - 35, cx + 50, cy - 15), fill=DARK)
    for ly in (cy, cy + 15, cy + 30):
        draw.line((cx - 50, ly, cx + 50, ly), fill="#90A4AE", width=4)

def scene_magnifier(cx, cy):
    circle(cx - 10, cy - 10, 38, "#E3F2FD", width=6)
    draw.line((cx + 17, cy + 17, cx + 55, cy + 55), fill=DARK, width=10)

def scene_checkmark(cx, cy):
    circle(cx, cy, 55, "#6FBF73", width=5)
    draw.line((cx - 25, cy, cx - 8, cy + 20), fill="#FFFFFF", width=10)
    draw.line((cx - 8, cy + 20, cx + 28, cy - 22), fill="#FFFFFF", width=10)

SCENES = {
    "money": scene_money, "health": scene_health, "law": scene_law,
    "school": scene_school, "weather": scene_weather, "sports": scene_sports,
    "warning": scene_warning, "transport": scene_transport,
    "newspaper": scene_newspaper, "newspaper_calm": scene_newspaper,
    "magnifier": scene_magnifier, "closing_calm": scene_magnifier,
    "checkmark": scene_checkmark,
}

# ---- The art pack: AI-made pictures in scene_art/ (png, jpg, jpeg or webp) ----
def scene_art_path(scene):
    for ext in ART_EXTENSIONS:
        path = ART_DIR / f"{scene}{ext}"
        if path.exists():
            return path
    return None


@lru_cache(maxsize=None)
def load_scene_art(scene, size):
    path = scene_art_path(scene)
    if path is None:
        return None
    try:
        with Image.open(path) as source:
            art = source.convert("RGB")
        return ImageOps.fit(art, size, method=Image.LANCZOS)  # crop to fill, no stretching
    except OSError as exc:
        print(f"Could not load scene art {path}: {exc}; using the drawn fallback.")
        return None


def draw_panel(
    x0, y0, number, title, caption, bg, scene, mood, caption_font_size,
    mirror_art=False, force_fallback=False,
):
    draw.rectangle((x0, y0, x0 + PANEL_W, y0 + PANEL_H), fill=bg, outline=DARK, width=6)

    art = None if force_fallback else load_scene_art(scene, (PANEL_W - 12, ART_H - 12))
    if art:
        if mirror_art:
            art = ImageOps.mirror(art)
        canvas.paste(art, (x0 + 6, y0 + 6))
    else:                                   # fallback: shapes from steps 2 and 7
        draw_robot(x0 + 280, y0 + 350, 130, mood)
        SCENES[scene](x0 + PANEL_W - 250, y0 + 350)

    cap_top = y0 + ART_H
    draw.rectangle((x0 + 3, cap_top, x0 + PANEL_W - 3, y0 + PANEL_H - 3), fill="#FFFBEF")
    draw.line((x0, cap_top, x0 + PANEL_W, cap_top), fill=DARK, width=5)
    draw_panel_title(f"{number}. {title}", x0 + 36, cap_top + 12, PANEL_W - 72)
    draw_caption(
        caption,
        (x0 + 36, cap_top + 88, x0 + PANEL_W - 36, y0 + PANEL_H - 18),
        caption_font_size,
    )


def draw_header(source_url):
    left_label = "PANELPULSE | AI-ASSISTED"
    source_url = (source_url or "").strip()
    parsed_url = urlparse(
        source_url
        if "://" in source_url or source_url.startswith("//")
        else f"//{source_url}"
    )
    domain = parsed_url.netloc or "SOURCE UNAVAILABLE"
    right_label = f"SOURCE: {domain}"
    for size in range(54, 27, -2):
        left_font = load_font(size)
        if _measure.textlength(left_label, font=left_font) <= 900:
            break
    for size in range(54, 29, -2):
        right_font = load_font(size)
        if _measure.textlength(right_label, font=right_font) <= 900:
            break
    right_width = _measure.textlength(right_label, font=right_font)
    if right_width > 900:
        right_label = _ellipsize(right_label, right_font, 900)
        right_width = _measure.textlength(right_label, font=right_font)

    draw.rectangle((0, 0, W, HEADER), fill=DARK)
    draw.text((MARGIN, 27), left_label, font=left_font, fill="#FFFFFF")
    draw.text((W - MARGIN - right_width, 31), right_label, font=right_font, fill="#FFFFFF")


# =====================  PART 4: THE ONE FUNCTION  =====================
def make_comic(headline, summary="", source_url=""):
    global draw, canvas
    img = Image.new("RGB", (W, H), "#EDE6D6")
    draw = ImageDraw.Draw(img)
    canvas = img

    panels = make_panels(headline, summary)                       # step 5
    topic = pick_topic(clean_text(headline), clean_text(summary)) # step 6
    sensitive = is_serious_story(headline, summary, topic)
    plan = panel_plan(topic, sensitive)                           # step 6
    colors = ["#F7E8C8", "#E3F0E8", "#E4ECF7", "#F7E3E3"]
    caption_width = PANEL_W - 72
    caption_height = PANEL_H - ART_H - 106
    caption_size = find_caption_font_size(
        [panel["caption"] for panel in panels],
        caption_width,
        caption_height,
    )

    draw_header(source_url)

    seen_art_files = set()
    for i, p in enumerate(panels):                                # step 4
        x0 = MARGIN + (i % 2) * (PANEL_W + MARGIN)
        y0 = HEADER + MARGIN + (i // 2) * (PANEL_H + MARGIN)
        art_path = scene_art_path(plan[i]["scene"])
        duplicate_art = art_path is not None and art_path in seen_art_files
        mirror_art = (
            duplicate_art
            and sensitive
            and i == 3
            and plan[i]["scene"] == "magnifier"
            and scene_art_path("closing_calm") is None
            and scene_art_path("newspaper_calm") is None
        )
        force_fallback = duplicate_art and not mirror_art
        if art_path is not None:
            seen_art_files.add(art_path)
        draw_panel(x0, y0, i + 1, p["title"], p["caption"], colors[i],
                   plan[i]["scene"], plan[i]["mood"], caption_size,
                   mirror_art, force_fallback)
    return img


# ---- Test: make 3 different comics ----
if __name__ == "__main__":
    stories = [
        ("$135 billion in debt, still getting loans: Who is keeping Pakistan afloat, and why",
         "As of last year, Pakistan grapples with an external debt surpassing $135.1 billion. "
         "Despite ongoing financial assistance, the nation faces economic hardships."),
        ("Telangana former CM KCR's long-time attendant, another youth killed as truck rams bike", ""),
        ("Heavy rain floods streets, schools shut for two days",
         "<p>Authorities closed schools in the city on Monday.</p><p>More rain is expected.</p>"),
    ]
    for n, (headline, summary) in enumerate(stories, start=1):
        make_comic(headline, summary).save(f"comic_{n}.png")
        print(f"Saved comic_{n}.png  (topic: {pick_topic(headline, summary)})")