from PIL import Image, ImageDraw

# 1. Make a blank image: 800 pixels wide, 500 tall, light cream color
img = Image.new("RGB", (800, 500), "#F7E8C8")

# 2. Make a "pen" that can draw on that image
draw = ImageDraw.Draw(img)

# 3. Draw a dark border rectangle: (left, top, right, bottom)
draw.ellipse((300, 150, 500, 350), fill="#B8C2CA", outline="#263238", width=5)

# 4. Save the picture
img.save("step1.png")
print("Saved step1.png")