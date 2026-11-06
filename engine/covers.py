"""Four platform thumbnails/covers for one video, in the TM Diamond studio look.

Usage: python3 engine/covers.py covers.json out_dir/ [--presenter]
covers.json: {
  "label": "windows fix",                      # small mono label
  "youtube":   {"title": ["STOP LOSING", "what you *copy*"], "pose": "shocked", "card": "Win + V"},
  "facebook":  {"title": ["Windows keeps", "a *history*", "of everything"], "pose": "point"},
  "instagram": {"title": ["The Win + V", "*trick*"], "pose": "idea", "kicker": "save this"},
  "tiktok":    {"title": ["Your clipboard", "has a *secret*"], "pose": "phone"}
}
Words wrapped in *stars* are set in red serif italic. Writes youtube.jpg (1280x720), facebook.jpg,
instagram.jpg and tiktok.jpg (1080x1920 each) with every platform's safe area respected:
  YouTube 16:9: nothing important in the bottom-right corner (time stamp).
  Facebook Reel: text between 14% from the top and 35% from the bottom, 6% side margins.
  Instagram Reel: title inside the centred 1080x1440 box the profile grid shows (3:4).
  TikTok: clear of the top 160 px, bottom 480 px and right 120 px (app buttons).
The presenter is drawn only when engine/brand.json has presenter_approved true (or with --presenter for a preview).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import studio  # noqa: E402

BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INK, RED = studio.INK, studio.RED


def paper(w, h):
    p = studio.StudioPaper().paper
    k = max(w / p.width, h / p.height)
    p = p.resize((int(p.width * k) + 1, int(p.height * k) + 1))
    return p.crop((0, 0, w, h)).convert("RGBA")


def title_block(lines, size, maxw, align="left"):
    """Render title lines; *word* = red serif italic. Returns an RGBA sprite."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    while size > 40:
        f_s = ImageFont.truetype(BLACK, size)
        f_r = ImageFont.truetype(studio.SERIF_IT, int(size * 1.22))
        rows = []
        for ln in lines:
            parts = []
            for i, chunk in enumerate(ln.split("*")):
                if chunk:
                    parts.append((chunk, i % 2 == 1))
            wsum = sum(tmp.textlength(c, font=f_r if red else f_s) for c, red in parts)
            rows.append((parts, wsum))
        if max(r[1] for r in rows) <= maxw:
            break
        size -= 4
    lh = int(size * 1.08)
    img = Image.new("RGBA", (int(maxw) + 20, lh * len(rows) + int(size * 0.5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (parts, wsum) in enumerate(rows):
        x = 0 if align == "left" else (maxw - wsum) / 2
        y = i * lh + size
        for chunk, red in parts:
            f = f_r if red else f_s
            d.text((x, y), chunk, font=f, fill=(RED if red else INK) + (255,), anchor="ls")
            if red:
                x0, x1 = x + 4, x + tmp.textlength(chunk, font=f) - 4
                d.line([(x0 + (x1 - x0) * k / 16, y + 16 + 4 * ((k % 2) - 0.5)) for k in range(17)],
                       fill=RED + (230,), width=max(5, size // 14), joint="curve")
            x += tmp.textlength(chunk, font=f)
    return img.crop(img.getbbox())


def mono(d, xy, text, size=30, anchor="ls"):
    d.text(xy, text, font=ImageFont.truetype(studio.MONO, size), fill=(128, 118, 104, 255), anchor=anchor)


def chip(text, size=56):
    f = ImageFont.truetype(studio.SERIF_IT, size)
    tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(text, font=f)
    im = Image.new("RGBA", (int(tw) + 60, int(size * 1.5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=RED + (255,))
    d.text((30, im.height * 0.74), text, font=f, fill=(255, 255, 255, 255), anchor="ls")
    return im.rotate(4, expand=True, resample=Image.BICUBIC)


def key_card(text, size=64):
    f = ImageFont.truetype(studio.sh.FONT_BOLD, size)
    tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(text, font=f)
    im = Image.new("RGBA", (int(tw) + 110, int(size * 2.1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 14, im.width - 8, im.height - 4), 28, fill=(70, 50, 20, 60))
    d.rounded_rectangle((0, 0, im.width - 12, im.height - 14), 28, fill=(255, 255, 255, 255), outline=(222, 214, 200, 255), width=3)
    d.text((48, im.height * 0.62), text, font=f, fill=INK + (255,), anchor="ls")
    return im.rotate(-3, expand=True, resample=Image.BICUBIC)


def presenter(pose, height, mirror=False):
    p = os.path.join(studio.POSE_DIR, pose + ".png")
    im = Image.open(p if os.path.exists(p) else os.path.join(studio.POSE_DIR, "talk.png")).convert("RGBA")
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im


def youtube(c, label, show_pres):
    W, H = 1280, 720
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    mono(d, (56, 70), "// tm_diamond · " + label, 26)
    tw = 720 if show_pres else 1140
    t = title_block(c["title"], 120, tw)
    img.alpha_composite(t, (56, 120))
    if c.get("card"):
        k = key_card(c["card"], 60)
        img.alpha_composite(k, (60, min(H - k.height - 40, 140 + t.height + 30)))
    if show_pres:
        pr = presenter(c.get("pose", "point"), 640, mirror=False)
        img.alpha_composite(pr, (W - pr.width + 40, H - pr.height + 40))
    return img


def vertical(c, label, show_pres, box, platform):
    """box = (x0, y0, x1, y1) where the title must sit."""
    W, H = 1080, 1920
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    mono(d, (x0, y0 + 30), "// tm_diamond · " + label, 30)
    t = title_block(c["title"], 210, x1 - x0)
    ty = y0 + 70
    img.alpha_composite(t, (x0, ty))
    yy = ty + t.height + 40
    if c.get("kicker"):
        ch = chip(c["kicker"], 80)
        img.alpha_composite(ch, (x0, yy))
        yy += ch.height + 20
    if c.get("card"):
        k = key_card(c["card"], 96)
        img.alpha_composite(k, (x0, yy))
    if show_pres:
        pr = presenter(c.get("pose", "talk"), 1000)
        img.alpha_composite(pr, (W - pr.width + 60, H - pr.height + 40))
    return img


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    show = studio.PRESENTER_OK or "--presenter" in sys.argv
    label = spec.get("label", "tech tip")
    files = []
    if "youtube" in spec:
        youtube(spec["youtube"], label, show).convert("RGB").save(os.path.join(out, "youtube.jpg"), quality=90)
        files.append("youtube.jpg")
    boxes = {"facebook": (65, int(1920 * 0.14), 1015, int(1920 * 0.65)),
             "instagram": (70, 240, 960, 1680),
             "tiktok": (70, 170, 960, 1440)}
    for plat, box in boxes.items():
        if plat in spec:
            vertical(spec[plat], label, show, box, plat).convert("RGB").save(os.path.join(out, plat + ".jpg"), quality=90)
            files.append(plat + ".jpg")
    print("\n".join(os.path.join(out, f) for f in files))


if __name__ == "__main__":
    main()
