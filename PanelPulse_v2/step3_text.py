from PIL import Image, ImageDraw, ImageFont

DARK = "#263238"

img = Image.new("RGB", (800, 500), "#F7E8C8")
draw = ImageDraw.Draw(img)

# 1. Load a font at a given size (Arial on Windows, with a safe fallback)
def load_font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

# 2. Break text into lines that are not wider than max_width pixels
def wrap_text(text, font, max_width):
    lines = []
    line = ""
    for word in text.split():
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            line = test              # the word still fits on this line
        else:
            if line:
                lines.append(line)   # finish this line
            line = word              # start a new line with the word
    if line:
        lines.append(line)
    return lines

# 3. Fit text in a box: try big letters first, shrink until it fits
def draw_caption(text, box, start_size=32, min_size=14):
    left, top, right, bottom = box
    width = right - left
    height = bottom - top

    for size in range(start_size, min_size - 1, -2):
        font = load_font(size)
        lines = wrap_text(text, font, width)
        line_height = int(size * 1.25)
        if len(lines) * line_height <= height:
            break                    # it fits, stop shrinking

    # still too tall at the smallest size: cut lines and add "..."
    max_lines = max(1, height // line_height)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,") + "..."

    y = top
    for line in lines:
        draw.text((left, y), line, font=font, fill=DARK)
        y += line_height

# Draw a caption box and put text inside it
draw.rectangle((40, 60, 760, 200), fill="#FFFBEF", outline=DARK, width=4)
draw_caption(
    "$135 billion in debt, still getting loans: Who is keeping Pakistan afloat, and why",
    (60, 75, 740, 190),
)

# A second box with a very long text, to test shrinking and cutting
draw.rectangle((40, 260, 760, 400), fill="#FFFBEF", outline=DARK, width=4)
draw_caption(
    "Despite ongoing financial assistance from global lenders and allies, the nation faces "
    "economic hardships marked by high unemployment and escalating poverty rates, and "
    "analysts say the situation may continue for several more years unless reforms arrive.",
    (60, 275, 740, 390),
)

img.save("step3.png")
print("Saved step3.png")