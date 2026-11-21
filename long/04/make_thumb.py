"""long04 YouTube thumbnail: the real Settings app before/after dark mode (Personalization > Colors) + bold title,
Team Diamond red/black + logo."""
from PIL import Image, ImageDraw, ImageFont
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1280, 720
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
f = lambda s: ImageFont.truetype(BLACK, s)
top = Image.open(os.path.join(R, "templates/tmd/top.png")).convert("RGB")
img = top.crop((0, 0, 860, 312)).resize((W, H), Image.LANCZOS)
# real screens: Settings > Personalization > Colors in light mode and after picking Dark
box = (168, 110, 1712, 760)
light = Image.open(os.path.join(R, "captures/long04_04/006_colors.png")).convert("RGB").crop(box)
dark = Image.open(os.path.join(R, "captures/long04_04/010_dark.png")).convert("RGB").crop(box)
pw, ph = 760, int(760 * (box[3] - box[1]) / (box[2] - box[0]))
light, dark = light.resize((pw, ph), Image.LANCZOS), dark.resize((pw, ph), Image.LANCZOS)
mask = Image.new("L", (pw, ph), 0)
ImageDraw.Draw(mask).polygon([(pw * 0.55, 0), (pw, 0), (pw, ph), (pw * 0.35, ph)], fill=255)
panel = light.copy(); panel.paste(dark, (0, 0), mask)
frame = Image.new("RGB", (pw + 16, ph + 16), (255, 255, 255)); frame.paste(panel, (8, 8))
px, py = W - frame.width - 24, H - frame.height - 40
img.paste(frame, (px, py))
d = ImageDraw.Draw(img)
d.line([(px + 8 + pw * 0.55, py + 8), (px + 8 + pw * 0.35, py + 8 + ph)], fill=(255, 52, 52), width=8)
d.text((44, 36), "9 SETTINGS", font=f(132), fill=(255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0))
tw = d.textlength("CHANGE NOW", font=f(74))
d.rounded_rectangle((44, 200, 44 + tw + 44, 300), radius=16, fill=(255, 52, 52))
d.text((66, 206), "CHANGE NOW", font=f(74), fill=(255, 255, 255))
d.text((48, 330), "WINDOWS 11", font=f(64), fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
logo = top.crop((870, 40, 1070, 165))
lg = logo.convert("L").point(lambda v: 255 if v > 150 else 0)
img.paste(logo, (W - 230, 24), lg)
img.save(os.path.join(R, "long/04/thumbnail.jpg"), quality=92)
print("ok")
