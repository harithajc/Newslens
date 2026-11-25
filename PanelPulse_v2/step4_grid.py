from PIL import Image, ImageDraw, ImageFont

DARK = "#263238"

# ---- Layout numbers (all in pixels) ----
W, H = 1200, 1200
HEADER = 60                              # dark bar at the top
MARGIN = 20                              # gap between panels and edges
PANEL_W = (W - 3 * MARGIN) // 2          # 2 panels across, 3 gaps
PANEL_H = (H - HEADER - 3 * MARGIN) // 2 # 2 panels down, 3 gaps
ART_H = 340                              # height of the picture part

img = Image.new("RGB", (W, H), "#EDE6D6")
draw = ImageDraw.Draw(img)

# ---- Helpers from steps 2 and 3 ----
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
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_caption(text, box, start_size=28, min_size=14):
    left, top, right, bottom = box
    width, height = right - left, bottom - top
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size)
        lines = wrap_text(text, font, width)
        line_height = int(size * 1.25)
        if len(lines) * line_height <= height:
            break
    max_lines = max(1, height // line_height)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,") + "..."
    y = top
    for line in lines:
        draw.text((left, y), line, font=font, fill=DARK)
        y += line_height

def circle(cx, cy, r, fill, outline=DARK, width=5):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 fill=fill, outline=outline, width=width)

# ---- The robot, now a function: any position, any size ----
def draw_robot(cx, cy, r):
    k = r / 110                      # scale factor (1.0 = the size from step 2)
    w = max(2, int(4 * k))           # line thickness scales too
    circle(cx, cy, r, "#B8C2CA", width=w + 1)                      # head
    draw.polygon([(cx - 60 * k, cy - 180 * k), (cx + 60 * k, cy - 180 * k),
                  (cx + 120 * k, cy - 110 * k), (cx - 120 * k, cy - 110 * k)],
                 fill="#F2C94C", outline=DARK)                     # hat
    draw.line((cx, cy - 180 * k, cx, cy - 220 * k), fill=DARK, width=w + 1)
    circle(cx, cy - 225 * k, 10 * k, "#E57373", width=w)           # antenna ball
    for ex in (cx - 50 * k, cx + 50 * k):                          # eyes
        circle(ex, cy - 30 * k, 26 * k, "#FFFBEF", width=w)
        circle(ex, cy - 30 * k, 10 * k, DARK, width=1)
    draw.rectangle((cx - 60 * k, cy + 50 * k, cx + 60 * k, cy + 100 * k),
                   fill="#6FBF73", outline=DARK, width=w)          # mouth
    draw.arc((cx - 40 * k, cy + 45 * k, cx + 40 * k, cy + 85 * k),
             start=20, end=160, fill=DARK, width=w)                # smile

# ---- One panel: frame, robot, title, caption ----
def draw_panel(x0, y0, number, title, caption, bg):
    draw.rectangle((x0, y0, x0 + PANEL_W, y0 + PANEL_H),
                   fill=bg, outline=DARK, width=6)
    draw_robot(x0 + PANEL_W // 2, y0 + 215, 80)

    cap_top = y0 + ART_H                       # where the text area starts
    draw.rectangle((x0 + 3, cap_top, x0 + PANEL_W - 3, y0 + PANEL_H - 3),
                   fill="#FFFBEF")
    draw.line((x0, cap_top, x0 + PANEL_W, cap_top), fill=DARK, width=4)
    draw.text((x0 + 24, cap_top + 14), f"{number}. {title}",
              font=load_font(30), fill=DARK)
    draw_caption(caption, (x0 + 24, cap_top + 60,
                           x0 + PANEL_W - 24, y0 + PANEL_H - 20))

# ---- Header bar ----
draw.rectangle((0, 0, W, HEADER), fill=DARK)
draw.text((20, 16), "PANELPULSE | AI-ASSISTED", font=load_font(26), fill="#FFFFFF")

# ---- The four panels (sample story text for now) ----
panels = [
    ("The headline", "$135 billion in debt, still getting loans: Who is keeping Pakistan afloat, and why"),
    ("The key fact", "As of last year, Pakistan grapples with an external debt surpassing $135.1 billion."),
    ("Why it matters", "Despite ongoing financial assistance from global lenders and allies, the nation faces economic hardships marked by high unemployment and escalating poverty rates."),
    ("The takeaway", "Open the source link for the full story."),
]
colors = ["#F7E8C8", "#E3F0E8", "#E4ECF7", "#F7E3E3"]

# ---- The loop: work out each panel's position ----
for i, (title, caption) in enumerate(panels):
    col = i % 2          # 0, 1, 0, 1  -> left or right
    row = i // 2         # 0, 0, 1, 1  -> top or bottom
    x0 = MARGIN + col * (PANEL_W + MARGIN)
    y0 = HEADER + MARGIN + row * (PANEL_H + MARGIN)
    draw_panel(x0, y0, i + 1, title, caption, colors[i])

img.save("step4.png")
print("Saved step4.png")