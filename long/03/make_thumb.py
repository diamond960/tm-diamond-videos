"""long03 YouTube thumbnail: the real Command Prompt (sfc /scannow repaired files) + bold title, Team Diamond red/black + logo."""
from PIL import Image, ImageDraw, ImageFont
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1280, 720
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
f = lambda s: ImageFont.truetype(BLACK, s)
top = Image.open(os.path.join(R, "templates/tmd/top.png")).convert("RGB")
img = top.crop((0, 0, 860, 312)).resize((W, H), Image.LANCZOS)
# the real screen: sfc /scannow result
ss = Image.open(os.path.join(R, "captures/day20261112b/060_b2e4_result.png")).convert("RGB")
crop = ss.crop((0, 50, 700, 320)).resize((700, 270), Image.LANCZOS)
panel = Image.new("RGB", (crop.width + 16, crop.height + 16), (255, 255, 255))
panel.paste(crop, (8, 8))
px, py = W - panel.width - 30, 330
img.paste(panel, (px, py))
d = ImageDraw.Draw(img)
# red ring on "found corrupt files and successfully repaired them"
d.rounded_rectangle((px + 4, py + 8 + 226 - 50 - 8, px + panel.width - 4, py + 8 + 226 - 50 + 26), radius=10, outline=(255, 45, 45), width=7)
d.text((48, 40), "10 CMD", font=f(150), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
d.text((44, 200), "COMMANDS", font=f(118), fill=(255, 52, 52), stroke_width=4, stroke_fill=(0, 0, 0))
d.rounded_rectangle((48, 360, 470, 450), radius=16, fill=(255, 255, 255))
d.text((70, 366), "YOU NEED", font=f(72), fill=(10, 10, 10))
logo = top.crop((870, 40, 1070, 165))
lg = logo.convert("L").point(lambda v: 255 if v > 150 else 0)
img.paste(logo, (W - 230, 24), lg)
img.save(os.path.join(R, "long/03/thumbnail.jpg"), quality=92)
print("ok")
