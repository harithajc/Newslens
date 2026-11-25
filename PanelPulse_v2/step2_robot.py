from PIL import Image, ImageDraw

DARK = "#263238"

img = Image.new("RGB", (800, 500), "#F7E8C8")
draw = ImageDraw.Draw(img)

# Helper: Pillow wants a box (left, top, right, bottom),
# but it is easier to think "center and radius".
def circle(cx, cy, r, fill, outline=DARK, width=5):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 fill=fill, outline=outline, width=width)

# Border
draw.rectangle((20, 20, 780, 480), outline=DARK, width=6)

# Head (big grey circle)
circle(400, 270, 110, "#B8C2CA")

# Hat (yellow trapezoid): four corner points, drawn after the head so it sits on top
draw.polygon([(340, 70), (460, 70), (520, 140), (280, 140)],
             fill="#F2C94C", outline=DARK)
draw.line((400, 130, 400, 70), fill=DARK, width=5)
(circle(400, 65, 10, "#E57373"))

# Eyes: white circle, then a smaller dark circle (pupil) on top
for eye_x in (350, 450):
    circle(eye_x, 240, 26, "#FFFBEF", width=4)
    circle(eye_x, 240, 10, DARK, width=1)

# Mouth: green rectangle with a smile curve
draw.rectangle((340, 320, 460, 370), fill="#6FBF73", outline=DARK, width=4)
draw.arc((360, 315, 440, 355), start=20, end=160, fill=DARK, width=4)


img.save("step2.png")
print("Saved step2.png")