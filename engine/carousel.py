"""TikTok / Instagram photo carousel (1080x1920 JPEG slides) in the TM_Diamond style.

Usage: python3 engine/carousel.py spec.json out_dir/
spec: {
  "handle": "TM_Diamond",
  "accent": "lime",                       # lime | orange | cyan | pink | yellow | red | blue
  "cover": {"title": "5 Windows shortcuts nobody uses", "sub": "Number 5 saves hours", "e": "⌨️"},
  "slides": [{"kicker": "1", "title": "Win + V", "body": "Clipboard history: paste anything you copied today.", "e": "📋"}, ...],
  "end": {"title": "Save this for later", "sub": "Follow for daily AI + tech tips", "e": "🔖"}
}
Writes out_dir/01.jpg, 02.jpg, ... (cover first, end slide last). Keep titles to ~6 words and bodies to ~20 words.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
ACC = {"lime": (200, 255, 46), "orange": (217, 119, 87), "red": (255, 77, 77), "cyan": (63, 224, 208),
       "yellow": (255, 214, 10), "pink": (255, 122, 200), "blue": (124, 140, 255)}


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb)
    k = size / max(im.size)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def background(acc, seed):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        c = (int(9 + 6 * t), int(12 + 8 * t), int(24 + 20 * t))
        for x in range(W):
            px[x, y] = c
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gx = 260 + (seed * 370) % 560
    ImageDraw.Draw(glow).ellipse((gx - 420, 420, gx + 420, 1260), fill=acc + (70,))
    return Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(140)))


def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, path, size, maxw, max_lines):
    while size > 48:
        f = ImageFont.truetype(path, size)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= maxw for l in lines):
            return f, lines
        size -= 6
    f = ImageFont.truetype(path, size)
    return f, wrap(d, text, f, maxw)


def shadow_text(d, xy, txt, fnt, fill, anchor="mm"):
    x, y = xy
    for o in (7, 4):
        d.text((x + o, y + o), txt, font=fnt, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), txt, font=fnt, fill=fill, anchor=anchor)


def frame(img, n, total, handle, acc):
    d = ImageDraw.Draw(img)
    fh = ImageFont.truetype(XB, 38)
    d.text((W / 2, 150), "@" + handle.lstrip("@"), font=fh, fill=(255, 255, 255, 200), anchor="mm")
    # progress dots
    gap = 34
    x0 = W / 2 - gap * (total - 1) / 2
    for i in range(total):
        r = 9 if i == n else 6
        c = acc if i == n else (90, 98, 120)
        d.ellipse((x0 + i * gap - r, 1800 - r, x0 + i * gap + r, 1800 + r), fill=c)


def slide_cover(c, acc, seed):
    img = background(acc, seed)
    d = ImageDraw.Draw(img)
    e = emoji(c.get("e", "⚡"), 380) if c.get("e") else None
    if e:
        img.alpha_composite(e, (W // 2 - e.width // 2, 300))
    f, lines = fit(d, c["title"].upper(), BLACK, 150, 940, 4)
    lh = f.size * 1.05
    y = 1080 - lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        shadow_text(d, (W / 2, y + i * lh), ln, f, (255, 255, 255) if i % 2 == 0 else acc)
    if c.get("sub"):
        fs = ImageFont.truetype(XB, 54)
        tw = d.textlength(c["sub"], font=fs)
        y2 = y + lh * len(lines) + 40
        d.rounded_rectangle((W / 2 - tw / 2 - 36, y2 - 48, W / 2 + tw / 2 + 36, y2 + 48), radius=26, fill=(217, 119, 87))
        d.text((W / 2, y2), c["sub"], font=fs, fill="white", anchor="mm")
    if not c.get("end"):
        fsw = ImageFont.truetype(XB, 46)
        d.text((W / 2, 1690), "SWIPE  →", font=fsw, fill=acc, anchor="mm")
    return img


def slide_tip(s, acc, seed):
    img = background(acc, seed)
    d = ImageDraw.Draw(img)
    if s.get("kicker"):
        fk = ImageFont.truetype(BLACK, 230)
        shadow_text(d, (W / 2, 420), str(s["kicker"]), fk, acc)
    e = emoji(s["e"], 230) if s.get("e") else None
    if e:
        img.alpha_composite(e, (W // 2 - e.width // 2, 590))
    f, lines = fit(d, s["title"], BLACK, 120, 960, 3)
    lh = f.size * 1.08
    y = 980
    for i, ln in enumerate(lines):
        shadow_text(d, (W / 2, y + i * lh), ln, f, (255, 255, 255))
    if s.get("body"):
        fb, bl = fit(d, s["body"], SEMI, 60, 900, 6)
        y2 = y + lh * len(lines) + 70
        box_h = len(bl) * fb.size * 1.3 + 70
        d.rounded_rectangle((70, y2 - 35, W - 70, y2 + box_h - 35), radius=36, fill=(22, 27, 44, 235),
                            outline=acc, width=4)
        for i, ln in enumerate(bl):
            d.text((W / 2, y2 + 20 + i * fb.size * 1.3), ln, font=fb, fill=(235, 238, 245), anchor="mm")
    return img


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    acc = ACC.get(spec.get("accent", "lime"), ACC["lime"])
    handle = spec.get("handle", "TM_Diamond")
    pages = [("cover", spec["cover"])] + [("tip", s) for s in spec["slides"]]
    if spec.get("end"):
        pages.append(("cover", dict(spec["end"], end=True)))
    paths = []
    for i, (kind, s) in enumerate(pages):
        img = slide_cover(s, acc, i) if kind == "cover" else slide_tip(s, acc, i)
        frame(img, i, len(pages), handle, acc)
        p = os.path.join(out, f"{i + 1:02d}.jpg")
        img.convert("RGB").save(p, quality=90, optimize=True)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    main()
