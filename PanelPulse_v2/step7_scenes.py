from PIL import Image, ImageDraw

DARK = "#263238"

img = Image.new("RGB", (1200, 600), "#EDE6D6")
draw = ImageDraw.Draw(img)

def circle(cx, cy, r, fill, outline=DARK, width=4):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 fill=fill, outline=outline, width=width)

# ---- Robot with a mood (the face changes, the head stays) ----
def draw_robot(cx, cy, r, mood="neutral"):
    k = r / 110
    w = max(2, int(4 * k))
    circle(cx, cy, r, "#B8C2CA", width=w + 1)
    draw.polygon([(cx - 60 * k, cy - 180 * k), (cx + 60 * k, cy - 180 * k),
                  (cx + 120 * k, cy - 110 * k), (cx - 120 * k, cy - 110 * k)],
                 fill="#F2C94C", outline=DARK)
    # eyes: pupil size depends on mood
    pupil = 15 * k if mood == "surprised" else 10 * k
    for ex in (cx - 50 * k, cx + 50 * k):
        circle(ex, cy - 30 * k, 26 * k, "#FFFBEF", width=w)
        circle(ex, cy - 30 * k, pupil, DARK, width=1)
    # mouth: shape depends on mood
    if mood == "happy":
        draw.arc((cx - 45 * k, cy + 30 * k, cx + 45 * k, cy + 90 * k),
                 start=20, end=160, fill=DARK, width=w + 1)
    elif mood == "surprised":
        circle(cx, cy + 65 * k, 18 * k, DARK, width=1)
    elif mood == "thinking":
        draw.line((cx - 35 * k, cy + 65 * k, cx + 35 * k, cy + 55 * k),
                  fill=DARK, width=w + 1)
        # eyebrow raised on one side
        draw.line((cx + 25 * k, cy - 75 * k, cx + 75 * k, cy - 85 * k),
                  fill=DARK, width=w)
    else:  # neutral: a flat line
        draw.line((cx - 35 * k, cy + 65 * k, cx + 35 * k, cy + 65 * k),
                  fill=DARK, width=w + 1)

# ---- Scenes: each one is drawn around a point (cx, cy) ----
def scene_money(cx, cy):
    circle(cx, cy, 55, "#F2C94C", width=5)
    circle(cx, cy, 38, "#F7DC7A", width=2)
    draw.line((cx, cy - 22, cx, cy + 22), fill=DARK, width=6)
    draw.line((cx - 14, cy - 8, cx + 14, cy - 8), fill=DARK, width=5)
    draw.line((cx - 14, cy + 8, cx + 14, cy + 8), fill=DARK, width=5)

def scene_health(cx, cy):
    draw.rectangle((cx - 15, cy - 55, cx + 15, cy + 55),
                   fill="#E57373", outline=DARK, width=4)
    draw.rectangle((cx - 55, cy - 15, cx + 55, cy + 15),
                   fill="#E57373", outline=DARK, width=4)
    draw.rectangle((cx - 13, cy - 13, cx + 13, cy + 13), fill="#E57373")

def scene_law(cx, cy):
    draw.line((cx, cy - 55, cx, cy + 55), fill=DARK, width=6)       # pole
    draw.line((cx - 60, cy - 35, cx + 60, cy - 35), fill=DARK, width=6)  # beam
    for sx in (cx - 60, cx + 60):                                   # two pans
        draw.line((sx, cy - 35, sx, cy + 5), fill=DARK, width=3)
        draw.pieslice((sx - 28, cy - 15, sx + 28, cy + 30),
                      start=0, end=180, fill="#B8C2CA", outline=DARK, width=3)
    draw.rectangle((cx - 30, cy + 50, cx + 30, cy + 62), fill=DARK)  # base

def scene_school(cx, cy):
    draw.rectangle((cx - 60, cy - 40, cx + 60, cy + 40),
                   fill="#64B5F6", outline=DARK, width=4)           # cover
    draw.rectangle((cx - 60, cy - 40, cx - 45, cy + 40), fill=DARK) # spine
    for ly in (cy - 15, cy + 5, cy + 25):                           # title lines
        draw.line((cx - 30, ly, cx + 40, ly), fill="#FFFBEF", width=4)

def scene_weather(cx, cy):
    for (ox, oy, r) in ((-35, 5, 32), (0, -15, 42), (38, 8, 30)):
        circle(cx + ox, cy + oy, r, "#DCE6EE", outline=DARK, width=4)
    draw.rectangle((cx - 60, cy + 10, cx + 65, cy + 36), fill="#DCE6EE")
    for dx in (-35, 0, 35):                                         # raindrops
        draw.line((cx + dx, cy + 50, cx + dx - 6, cy + 70), fill="#1976D2", width=5)

def scene_sports(cx, cy):
    circle(cx, cy, 55, "#FFFBEF", width=5)
    draw.polygon([(cx, cy - 22), (cx + 21, cy - 7), (cx + 13, cy + 18),
                  (cx - 13, cy + 18), (cx - 21, cy - 7)], fill=DARK)
    for ang_x, ang_y in ((0, -55), (52, -17), (32, 45), (-32, 45), (-52, -17)):
        draw.line((cx + ang_x * 0.4, cy + ang_y * 0.4, cx + ang_x, cy + ang_y),
                  fill=DARK, width=3)

def scene_warning(cx, cy):
    draw.polygon([(cx, cy - 60), (cx + 62, cy + 50), (cx - 62, cy + 50)],
                 fill="#F2C94C", outline=DARK)
    draw.line((cx, cy - 25, cx, cy + 15), fill=DARK, width=8)       # the "!"
    circle(cx, cy + 33, 5, DARK, width=1)

def scene_transport(cx, cy):
    draw.rectangle((cx - 70, cy - 15, cx + 50, cy + 25),            # body
                   fill="#90CAF9", outline=DARK, width=4)
    draw.polygon([(cx + 50, cy - 15), (cx + 80, cy + 5), (cx + 50, cy + 25)],
                 fill="#90CAF9", outline=DARK)                      # nose
    draw.polygon([(cx - 30, cy + 25), (cx + 10, cy + 25), (cx - 20, cy + 60)],
                 fill="#B8C2CA", outline=DARK)                      # wing
    draw.polygon([(cx - 70, cy - 15), (cx - 50, cy - 15), (cx - 70, cy - 45)],
                 fill="#B8C2CA", outline=DARK)                      # tail

def scene_newspaper(cx, cy):
    draw.rectangle((cx - 60, cy - 45, cx + 60, cy + 45),
                   fill="#FFFBEF", outline=DARK, width=4)
    draw.rectangle((cx - 50, cy - 35, cx + 50, cy - 15), fill=DARK)  # headline bar
    for ly in (cy + 0, cy + 15, cy + 30):
        draw.line((cx - 50, ly, cx + 50, ly), fill="#90A4AE", width=4)

def scene_magnifier(cx, cy):
    circle(cx - 10, cy - 10, 38, "#E3F2FD", width=6)
    draw.line((cx + 17, cy + 17, cx + 55, cy + 55), fill=DARK, width=10)

def scene_checkmark(cx, cy):
    circle(cx, cy, 55, "#6FBF73", width=5)
    draw.line((cx - 25, cy, cx - 8, cy + 20), fill="#FFFFFF", width=10)
    draw.line((cx - 8, cy + 20, cx + 28, cy - 22), fill="#FFFFFF", width=10)

# ---- A dictionary: scene name -> function ----
SCENES = {
    "money": scene_money, "health": scene_health, "law": scene_law,
    "school": scene_school, "weather": scene_weather, "sports": scene_sports,
    "warning": scene_warning, "transport": scene_transport,
    "newspaper": scene_newspaper, "magnifier": scene_magnifier,
    "checkmark": scene_checkmark,
}

# ---- Gallery 1: all 11 scenes in a row-of-6 grid ----
names = list(SCENES)
for i, name in enumerate(names):
    cx = 100 + (i % 6) * 200
    cy = 90 + (i // 6) * 170
    SCENES[name](cx, cy)
    draw.text((cx - 40, cy + 75), name, fill=DARK)

# ---- Gallery 2: the 4 robot moods along the bottom ----
for i, mood in enumerate(["neutral", "surprised", "thinking", "happy"]):
    cx = 150 + i * 300
    draw_robot(cx, 470, 55, mood)
    draw.text((cx - 25, 560), mood, fill=DARK)

img.save("step7.png")
print("Saved step7.png")