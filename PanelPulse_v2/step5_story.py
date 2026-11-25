import html
import re

# 1. Clean a summary: remove HTML tags and extra spaces
def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())

# 2. Split text into sentences (after . ! or ?)
def split_sentences(text):
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

# 3. Are two texts "the same"? Ignore capitals, spaces and punctuation
def same_text(a, b):
    def simple(t):
        return re.sub(r"[^a-z0-9]", "", t.lower())
    return simple(a) == simple(b)

# 4. The main function: story in, 4 panels out
def make_panels(headline, summary):
    headline = clean_text(headline)
    sentences = split_sentences(clean_text(summary))

    # throw away sentences that just repeat the headline
    sentences = [s for s in sentences if not same_text(s, headline)]

    key_fact = sentences[0] if len(sentences) > 0 else "The source has more details."
    why = (sentences[1] if len(sentences) > 1
           else "The feed gave only a short summary, so the details are in the full article.")

    return [
        {"title": "The headline",   "caption": headline},
        {"title": "The key fact",   "caption": key_fact},
        {"title": "Why it matters", "caption": why},
        {"title": "The takeaway",   "caption": "Open the source link to read the full story."},
    ]

# ---- Test it with 4 different kinds of stories ----
tests = [
    ("Normal story with a long summary",
     "$135 billion in debt, still getting loans: Who is keeping Pakistan afloat, and why",
     "As of last year, Pakistan grapples with an external debt surpassing $135.1 billion. "
     "Despite ongoing financial assistance, the nation faces economic hardships."),
    ("Summary is the same as the headline",
     "Customs seize 11 air rifles from passengers at Kochi airport",
     "Customs seize 11 air rifles from passengers at Kochi airport"),
    ("Empty summary",
     "IndiGo joins Air India, Akasa in suspending Saudi flights until November 30",
     ""),
    ("Summary with HTML",
     "Fuel prices unchanged for the third week",
     "<p>Petrol and diesel prices stayed the same today.</p><p>Experts expect no change soon.</p>"),
]

for name, headline, summary in tests:
    print("=== " + name)
    for p in make_panels(headline, summary):
        print("  " + p["title"] + ": " + p["caption"])
    print()