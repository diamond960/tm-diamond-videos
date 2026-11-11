"""long02 YouTube thumbnail: the real Task Manager (HeavyApp at 45.8% CPU) + bold title, Team Diamond red/black + logo."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1280, 720
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
f = lambda s: ImageFont.truetype(BLACK, s)
# background: Team Diamond red grid
top = Image.open(os.path.join(R, "templates/tmd/top.png")).convert("RGB")
bg = top.crop((0, 0, 860, 312)).resize((W, H), Image.LANCZOS)
img = bg.copy()
# the real screen: Task Manager sorted by CPU, the busy app on top
ss = Image.open(os.path.join(R, "captures/short03/003_sorted_cpu.png")).convert("RGB")
crop = ss.crop((218, 214, 760, 420)).resize((760, 289), Image.LANCZOS)
panel = Image.new("RGB", (crop.width + 16, crop.height + 16), (255, 255, 255))
panel.paste(crop, (8, 8))
px, py = W - panel.width - 30, 300
img.paste(panel, (px, py))
d = ImageDraw.Draw(img)
# red ring on the busy app row (HeavyApp, 45.8% CPU)
k = 760 / 542
ry0, ry1 = py + 8 + int((263 - 214) * k) - 4, py + 8 + int((291 - 214) * k) + 4
d.rounded_rectangle((px + 4, ry0, px + panel.width - 4, ry1), radius=10, outline=(255, 45, 45), width=8)
# title
d.text((48, 40), "PC RUNNING", font=f(96), fill=(255, 255, 255))
d.text((44, 128), "SLOW?", font=f(190), fill=(255, 52, 52), stroke_width=4, stroke_fill=(0, 0, 0))
d.rounded_rectangle((48, 350, 470, 440), radius=16, fill=(255, 255, 255))
d.text((70, 356), "10 FIXES", font=f(76), fill=(10, 10, 10))
d.text((50, 470), "FREE  /  STEP BY STEP", font=f(40), fill=(230, 230, 230))
# Team Diamond logo
logo = top.crop((870, 40, 1070, 165))
lg = logo.convert("L").point(lambda v: 255 if v > 150 else 0)
img.paste(logo, (W - 230, 24), lg)
img.save(os.path.join(R, "long/02/thumbnail.jpg"), quality=92)
print("ok")
