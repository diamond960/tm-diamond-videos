"""1280x720 YouTube thumbnail in the TM_Diamond style.

Usage: python3 engine/thumbnail.py spec.json out.jpg
spec: {"line1": "9 APPS", "line2": "1 CHAT", "badge": "AI VIDEO STUDIO",
       "emoji": ["🤖", "🎬"], "accent": "lime"|"orange"|"red"|"cyan", "arrow": true}
Keep line1/line2 to 1-3 short words each (big text wins clicks on phones).
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
ACC = {"lime": (200, 255, 46), "orange": (217, 119, 87), "red": (255, 77, 77), "cyan": (63, 224, 208), "yellow": (255, 214, 10)}


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    k = size / max(im.size)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def fit_font(d, txt, path, size, maxw):
    while size > 40:
        f = ImageFont.truetype(path, size)
        if d.textlength(txt, font=f) <= maxw:
            return f
        size -= 6
    return ImageFont.truetype(path, size)


def main():
    spec = json.load(open(sys.argv[1]))
    acc = ACC.get(spec.get("accent", "lime"), ACC["lime"])
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        c = (int(9 + 7 * t), int(13 + 9 * t), int(24 + 22 * t))
        for x in range(W):
            px[x, y] = c
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((760, 90, 1260, 630), fill=acc + (85,))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(100)))
    ems = spec.get("emoji", [])
    if ems:
        big = emoji(ems[0], 400)
        img.alpha_composite(big, (1010 - big.width // 2, 360 - big.height // 2))
    if len(ems) > 1:
        sm = emoji(ems[1], 190)
        img.alpha_composite(sm, (1180 - sm.width // 2, 150 - sm.height // 2))
    d = ImageDraw.Draw(img)

    def shadow(xy, txt, font, fill):
        x, y = xy
        for o in (9, 6):
            d.text((x + o, y + o), txt, font=font, fill=(0, 0, 0))
        d.text((x, y), txt, font=font, fill=fill)

    f1 = fit_font(d, spec["line1"], BLACK, 190, 720)
    shadow((48, 90), spec["line1"], f1, (255, 255, 255))
    if spec.get("line2"):
        f2 = fit_font(d, spec["line2"], BLACK, 190, 720)
        shadow((48, 300), spec["line2"], f2, acc)
    if spec.get("badge"):
        fb = ImageFont.truetype(XB, 36)
        tw = d.textlength(spec["badge"], font=fb)
        d.rounded_rectangle((52, 560, 52 + tw + 48, 628), radius=16, fill=(217, 119, 87))
        d.text((52 + 24 + tw / 2, 594), spec["badge"], font=fb, fill="white", anchor="mm")
    if spec.get("arrow"):
        d.line([(700, 560), (820, 470)], fill=(255, 77, 77), width=22)
        d.polygon([(845, 448), (780, 455), (835, 510)], fill=(255, 77, 77))
    img.convert("RGB").save(sys.argv[2], quality=88, optimize=True)


if __name__ == "__main__":
    main()
