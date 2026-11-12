"""realcut.py - vertical videos edited from REAL screen captures (TM Diamond).

The picture is always a real screen (screenshots taken on a real Windows PC by engine/wincap.ps1,
or real phone/Mac screenshots), filling the whole 1080x1920 frame edge to edge: a virtual camera
pans and zooms over the real screen (full -> focus -> full), so there is never a border or margin.
On top: word-by-word captions, a smooth cursor with click ripples, keycap overlays for shortcuts,
red hand-drawn circles/arrows on the exact target, a follow card at the end. Sound = narration +
real recorded CC0 UI sounds (engine/sfx/kenney) synced to each action. No music.

Usage: python3 engine/realcut.py spec.json out.mp4 [--preview t1,t2,...]

spec.json:
{
  "captures": "captures/fb06",            # folder with the PNGs (screen pixels = camera units)
  "narration": "fb/06/voice.mp3", "words": "fb/06/voice.words.json",
  "duration": 15.2,
  "shots": [[t, "002_edge_error.png"], ...],            # which real screen is visible from time t
  "cam":   [[t, cx, cy, h, dur], ...],                  # camera moves: centre + height (screen px), ease over dur s
  "cursor": [[t, x, y], ...],                           # optional cursor path (screen px); omitted = hidden
  "cursor_on": [[t0, t1], ...],                         # optional: cursor visible only in these spans
  "clicks": [t, ...],                                   # ripple + click sound at the cursor
  "keys":  [[t, ["Win", "R"], dur], ...],               # keycap overlay + key sounds
  "typing": [[t0, t1, n], ...],                         # n key sounds spread over t0..t1
  "circles": [[t, [x, y, w, h], dur], ...],             # red marker ellipse around a screen rect
  "arrows": [[t, [x, y], dur, "from_left"|"from_right"|"from_top"], ...],
  "highlight": ["words", ...],                          # caption words shown in yellow
  "sfx": [[t, "pop"|"ding"|"whoosh"|"click"|"key"], ...],
  "follow": t,                                           # follow card from t to the end
  "titles": [[t, "Chapter title", dur], ...],
  "caption_y": [[t, 0.72], [t2, 0.17]],                # optional: caption height (fraction of frame) from time t           # chapter cards (long videos)
  "size": [1920, 1080],                                 # landscape for long YouTube videos (default 1080x1920)
  "handle": "TM_Diamond",
  "layout": "tmd",       # Team Diamond template (the owner's own format): templates/tmd/top.png (red grid + TMD logo),
                         # the real screen in the middle panel (y 313-1292), the owner's presenter clip below
                         # (templates/tmd/bottom.mp4, looped); captions off unless "captions": true
  "card": {"t0": 0, "t1": 2.6, "title": "Where did it go?", "sub": "Sold as a 1 TB SSD", "count": [1000, 953],
           "suffix": "GB in Windows"}   # or "big": "invoice.pdf", "big2": "invoice.pdf.exe", "swap_t": 1.4
  "boxes": [[t, [x, y, w, h], dur], ...]  # green highlight box around a real UI element
}
"""
import json
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
# the real screen is shown inside this viewport (whole frame by default; the TMD template uses a middle panel)
PX, PY, PW, PH = 0, 0, 1080, 1920
TMD_PANEL = (0, 313, 1080, 979)   # Team Diamond template: logo strip above, presenter strip below
# "framing": "full" (owner, 2026-11-11: show the whole laptop screen, don't zoom in): the full 16:9 screen sits
# right under the logo strip, and an info band (hook card, step labels, titles, follow card) fills the rest of the panel.
TMD_FULL = (0, 313, 1080, 608)
TMD_BAND = (0, 921, 1080, 371)
TITLES_Y = None   # centre line of the titles band (None = middle of the frame)
GREEN = (52, 211, 104)
FOLLOW_Y = 0.64
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
YELLOW = (255, 214, 10)
RED = (232, 33, 39)
SR = 48000


def font(path, size):
    return ImageFont.truetype(path, size)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


def ease_out_back(x):
    x = min(1.0, max(0.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)


# ------------------------------------------------------------------ camera
class Camera:
    def __init__(self, keys, screen_w, screen_h):
        self.keys = sorted(keys, key=lambda k: k[0])
        self.sw, self.sh = screen_w, screen_h

    def at(self, t):
        ks = self.keys
        cx, cy, h = ks[0][1], ks[0][2], ks[0][3]
        last_t = ks[0][0]
        for k in ks[1:]:
            kt, kx, ky, kh = k[0], k[1], k[2], k[3]
            dur = k[4] if len(k) > 4 else 0.45
            if t < kt:
                break
            p = ease((t - kt) / dur) if dur > 0 else 1.0
            cx, cy, h = cx + (kx - cx) * p, cy + (ky - cy) * p, h + (kh - h) * p
            last_t = kt
        # slow push-in between moves: the whole frame (edges included) keeps moving
        # (spec "drift": max push-in, default 0.06; terminal text at the screen edge needs ~0.01 so nothing is cut)
        drift = 1.0 - min(getattr(self, "max_drift", 0.06), 0.012 * max(0.0, t - last_t))
        h *= drift
        return self.clamp(cx, cy, h)

    def clamp(self, cx, cy, h):
        h = min(h, self.sh)
        w = h * PW / PH
        if w > self.sw:
            w = self.sw
            h = w * PH / PW
        cx = min(max(cx, w / 2), self.sw - w / 2)
        cy = min(max(cy, h / 2), self.sh - h / 2)
        return cx, cy, h

    @staticmethod
    def to_frame(cam, x, y):
        cx, cy, h = cam
        s = PH / h
        return (x - cx) * s + PX + PW / 2, (y - cy) * s + PY + PH / 2, s


def render_screen(img, cam):
    cx, cy, h = cam
    w = h * PW / PH
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return img.resize((PW, PH), Image.LANCZOS, box=box)


# ------------------------------------------------------------------ overlays
def draw_text_stroke(d, xy, text, f, fill, stroke=7, sfill=(0, 0, 0), anchor="la"):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)


def sentence_ends(script_text, n_words):
    """Indices of the last word of each sentence, by matching the script to the timed words.
    Spelled-out letters ("C M D", "I P") count as one word, as the timing tool writes them."""
    import re
    ends, count = set(), 0
    for line in script_text.splitlines():
        for sent in re.split(r"(?<=[.?!])\s+", line.strip()):
            toks = [x for x in re.split(r"\s+", sent) if re.search(r"\w", x)]
            merged, run = [], False
            for tk in toks:
                single = len(re.sub(r"\W", "", tk)) == 1 and tk.strip(",.?!").isupper()
                if single and run:
                    continue
                merged.append(tk)
                run = single
            count += len(merged)
            if merged:
                ends.add(count - 1)
    return ends if count == n_words else None


def caption_layer(words, t, highlight, ends=None, cy=None):
    """Word-by-word captions in groups of up to 3 words: white, black stroke, current word yellow."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not words:
        return layer
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        end_sent = (i in ends) if ends else w["w"].rstrip().endswith((".", "?", "!", ","))
        gap = (words[i + 1]["s"] - w["e"]) if i + 1 < len(words) else 9
        if len(cur) == 3 or end_sent or gap > 0.28:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    g = None
    for grp in groups:
        s = words[grp[0]]["s"] - 0.05
        e = words[grp[-1]]["e"] + 0.25
        if s <= t < e:
            g = grp
            break
    if g is None:
        return layer
    CS = int(max(64, 92 * H / 1920))
    f = font(F_BLACK, CS)
    d = ImageDraw.Draw(layer)
    toks = []
    for i in g:
        raw = words[i]["w"].strip()
        clean = raw.strip(".,?!").lower()
        col = YELLOW if (clean in highlight or t >= words[i]["s"] and t < words[i]["e"] + 0.05 and False) else (255, 255, 255)
        shown = t >= words[i]["s"] - 0.04
        toks.append((raw.upper(), col if clean in highlight else (255, 255, 255), shown, words[i]["s"]))
    # layout on up to 2 lines
    space = 26
    widths = [d.textlength(tk[0], font=f) for tk in toks]
    lines, line, lw = [], [], 0
    for tk, wd in zip(toks, widths):
        if line and lw + space + wd > W - 140:
            lines.append(line)
            line, lw = [], 0
        line.append((tk, wd))
        lw += wd + (space if len(line) > 1 else 0)
    if line:
        lines.append(line)
    y = int(H * (cy if cy is not None else (0.17 if H > W else 0.80)))
    for ln in lines:
        total = sum(wd for _, wd in ln) + space * (len(ln) - 1)
        x = (W - total) / 2
        for (txt, col, shown, ws), wd in ln:
            if shown:
                pop = ease_out_back((t - ws + 0.04) / 0.16)
                size = int(CS * (0.82 + 0.18 * pop))
                ff = font(F_BLACK, size)
                draw_text_stroke(d, (x + wd / 2, y + 50), txt, ff, col, stroke=9, anchor="mm")
            x += wd + space
        y += int(CS * 1.22)
    return layer


def keycaps_layer(keys, t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for k in keys:
        kt, names, dur = k[0], k[1], k[2]
        yfrac = k[3] if len(k) > 3 else 0.70
        if not (kt <= t < kt + dur):
            continue
        a = ease_out_back((t - kt) / 0.22)
        out = min(1.0, (kt + dur - t) / 0.18)
        f = font(F_BOLD, 64)
        d = ImageDraw.Draw(layer)
        caps = []
        for n in names:
            tw = d.textlength(n, font=f)
            caps.append((n, max(150, tw + 80)))
        gap = 70
        total = sum(c[1] for c in caps) + gap * (len(caps) - 1)
        x = (W - total) / 2
        y = int(H * yfrac + (1 - a) * 60)
        for i, (n, cw) in enumerate(caps):
            pressed = (t - kt) > 0.25 + 0.12 * i
            dy = 10 if pressed else 0
            # shadow + key
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle((x, y + 22, x + cw, y + 150 + 22), 28, fill=(0, 0, 0, int(150 * out)))
            layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
            d.rounded_rectangle((x, y + 14, x + cw, y + 150 + 14), 28, fill=(150, 150, 158, int(255 * out)))
            d.rounded_rectangle((x, y + dy, x + cw, y + 140 + dy), 28, fill=(250, 250, 252, int(255 * out)), outline=(205, 205, 212, int(255 * out)), width=3)
            d.text((x + cw / 2, y + 70 + dy), n, font=f, fill=(25, 25, 30, int(255 * out)), anchor="mm")
            if i < len(caps) - 1:
                draw_text_stroke(d, (x + cw + gap / 2, y + 70), "+", font(F_BLACK, 70), (255, 255, 255, int(255 * out)), stroke=6, anchor="mm")
            x += cw + gap
    return layer


def marker_ellipse(d, box, prog, width=10, color=RED):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    n = 90
    end = int(n * 1.12 * prog)
    pts = []
    for i in range(min(end, int(n * 1.12)) + 1):
        a = -2.4 + 2 * math.pi * i / n
        wob = 1 + 0.035 * math.sin(i * 0.35)
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    if len(pts) > 1:
        d.line(pts, fill=color, width=width, joint="curve")


def callouts_layer(spec, t, cam):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for ct, rect, dur in spec.get("circles", []):
        if ct <= t < ct + dur:
            x, y, w, h = rect
            fx0, fy0, s = Camera.to_frame(cam, x, y)
            fx1, fy1, _ = Camera.to_frame(cam, x + w, y + h)
            pad = 26
            marker_ellipse(d, (fx0 - pad, fy0 - pad, fx1 + pad, fy1 + pad), ease((t - ct) / 0.35))
    for at, pt, dur, side in spec.get("arrows", []):
        if at <= t < at + dur:
            fx, fy, s = Camera.to_frame(cam, pt[0], pt[1])
            p = ease((t - at) / 0.3)
            L = 190
            if side == "from_left":
                sx, sy = fx - L - 30, fy + L * 0.55
            elif side == "from_top":
                sx, sy = fx - 40, fy - L - 40
            else:
                sx, sy = fx + L + 30, fy + L * 0.55
            ex, ey = sx + (fx - sx) * p, sy + (fy - sy) * p
            d.line((sx, sy, ex, ey), fill=RED, width=14)
            if p > 0.95:
                ang = math.atan2(fy - sy, fx - sx)
                for da in (2.6, -2.6):
                    d.line((fx, fy, fx + 52 * math.cos(ang + da), fy + 52 * math.sin(ang + da)), fill=RED, width=14)
    return layer


def boxes_layer(spec, t, cam):
    """Rounded highlight boxes drawn around a real UI element (TMD style: thin green outline)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for b in spec.get("boxes", []):
        bt, rect, dur = b[0], b[1], b[2]
        col = tuple(b[3]) if len(b) > 3 else GREEN
        if not (bt <= t < bt + dur):
            continue
        x, y, w, h = rect
        fx0, fy0, s = Camera.to_frame(cam, x, y)
        fx1, fy1, _ = Camera.to_frame(cam, x + w, y + h)
        pad = 6
        p = ease((t - bt) / 0.3)
        out = min(1.0, (bt + dur - t) / 0.2)
        x0, y0, x1, y1 = fx0 - pad, fy0 - pad, fx1 + pad, fy1 + pad
        # grow from the centre line outwards
        cx = (x0 + x1) / 2
        x0p, x1p = cx - (cx - x0) * p, cx + (x1 - cx) * p
        d.rounded_rectangle((x0p, y0, x1p, y1), radius=10, outline=col + (int(255 * out),), width=6)
    return layer


def card_layer(card, t):
    """Hook card (TMD style): dark glass panel with a teal glow, icon + title, grey subtitle, a big number
    that counts (count: [from, to]) or a big text that changes (big -> big2 at swap_t, the new part in red)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not card or not (card["t0"] <= t < card["t1"]):
        return layer
    a = min(ease((t - card["t0"]) / 0.3), ease((card["t1"] - t) / 0.25))
    x0, x1 = 22, W - 22
    y0 = card.get("y", PY + PH * 0.30)
    hgt = 300
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, y0 + hgt + 6), 26, fill=(40, 190, 170, int(150 * a)))
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x1, y0 + hgt), 22, fill=(22, 26, 30, int(235 * a)), outline=(70, 200, 185, int(160 * a)), width=2)
    # icon: a small drive / file glyph
    ix, iy = x0 + 40, y0 + 52
    d.rounded_rectangle((ix, iy - 12, ix + 46, iy + 12), 6, outline=(120, 200, 255, int(255 * a)), width=4)
    d.line((ix + 10, iy, ix + 22, iy), fill=(120, 200, 255, int(255 * a)), width=4)
    d.text((ix + 66, iy), card.get("title", ""), font=font(F_BOLD, 50), fill=(255, 255, 255, int(255 * a)), anchor="lm")
    d.text((x0 + 40, y0 + 108), card.get("sub", ""), font=font(F_SEMI, 34), fill=(150, 156, 165, int(255 * a)), anchor="lm")
    by = y0 + 210
    if "count" in card:
        c0, c1 = card["count"]
        ct0 = card.get("count_t", card["t0"] + 0.4)
        p = ease((t - ct0) / card.get("count_dur", 1.6))
        num = str(int(round(c0 + (c1 - c0) * p)))
        fbig = font(F_BLACK, 150)
        d.text((x0 + 36, by), num, font=fbig, fill=(255, 255, 255, int(255 * a)), anchor="lm")
        nw = d.textlength(num, font=fbig)
        d.text((x0 + 60 + nw, by + 22), card.get("suffix", ""), font=font(F_BOLD, 54), fill=(225, 228, 232, int(255 * a)), anchor="lm")
    else:
        big, big2 = card.get("big", ""), card.get("big2")
        swapped = big2 is not None and t >= card.get("swap_t", 1e9)
        size = 120
        dd = ImageDraw.Draw(Image.new("L", (1, 1)))
        while size > 50 and dd.textlength(big2 or big, font=font(F_BLACK, size)) > (x1 - x0 - 80):
            size -= 4
        fbig = font(F_BLACK, size)
        if swapped:
            d.text((x0 + 36, by), big, font=fbig, fill=(255, 255, 255, int(255 * a)), anchor="lm")
            extra = big2[len(big):] if big2.startswith(big) else big2
            ex = x0 + 36 + d.textlength(big, font=fbig)
            p = ease_out_back((t - card["swap_t"]) / 0.3)
            fe = font(F_BLACK, int(fbig.size * (0.6 + 0.4 * p)))
            d.text((ex, by), extra, font=fe, fill=(255, 70, 70, int(255 * a)), anchor="lm")
        else:
            d.text((x0 + 36, by), big, font=fbig, fill=(255, 255, 255, int(255 * a)), anchor="lm")
    return layer


ARROW = [(0, 0), (0, 34), (8, 26), (14, 40), (19, 38), (13, 24), (24, 24)]


def cursor_layer(spec, t, cam):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    path = spec.get("cursor")
    if not path:
        return layer
    if t < path[0][0]:
        return layer
    on = spec.get("cursor_on")  # optional [[t0, t1], ...]: show the cursor only inside these spans (long videos)
    if on and not any(a <= t < b for a, b in on):
        return layer
    x, y = path[0][1], path[0][2]
    for i in range(1, len(path)):
        t0, x0, y0 = path[i - 1]
        t1, x1, y1 = path[i]
        if t >= t1:
            x, y = x1, y1
        elif t >= t0:
            p = ease((t - t0) / max(0.01, t1 - t0))
            x, y = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
            break
    fx, fy, s = Camera.to_frame(cam, x, y)
    d = ImageDraw.Draw(layer)
    for ct in spec.get("clicks", []):
        if ct <= t < ct + 0.5:
            p = (t - ct) / 0.5
            r = 24 + 70 * p
            d.ellipse((fx - r, fy - r, fx + r, fy + r), outline=(255, 214, 10, int(230 * (1 - p))), width=8)
    k = max(2.2, s * 1.1)
    pts = [(fx + px * k, fy + py * k) for px, py in ARROW]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(px + 5, py + 7) for px, py in pts], fill=(0, 0, 0, 110))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    d.polygon(pts, fill=(255, 255, 255), outline=(0, 0, 0))
    d.line(pts + [pts[0]], fill=(0, 0, 0), width=3)
    return layer


def follow_layer(t, t0, handle):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t0 is None or t < t0:
        return layer
    a = ease_out_back((t - t0) / 0.35)
    d = ImageDraw.Draw(layer)
    cw, ch = 760, 170
    x0 = (W - cw) / 2
    y0 = H * FOLLOW_Y + (1 - a) * 120
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 16, x0 + cw, y0 + ch + 16), 85, fill=(0, 0, 0, 120))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 85, fill=(24, 26, 34))
    d.ellipse((x0 + 25, y0 + 25, x0 + 145, y0 + 145), fill=(122, 201, 67))
    d.text((x0 + 85, y0 + 86), "TM", font=font(F_BLACK, 52), fill=(20, 20, 20), anchor="mm")
    d.text((x0 + 170, y0 + 86), handle, font=font(F_BOLD, 52), fill=(255, 255, 255), anchor="lm")
    clicked = t > t0 + 0.9
    bx0, bx1 = x0 + cw - 250, x0 + cw - 30
    d.rounded_rectangle((bx0, y0 + 45, bx1, y0 + 125), 40, fill=(70, 74, 88) if clicked else (24, 119, 242))
    d.text(((bx0 + bx1) / 2, y0 + 86), "Following" if clicked else "Follow", font=font(F_BOLD, 40), fill=(255, 255, 255), anchor="mm")
    return layer


def titles_layer(titles, t):
    """Chapter titles: a dark glass band across the middle with big white text (the real screen stays visible)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for tt in titles or []:
        t0, text, dur = tt[0], tt[1], tt[2]
        if not (t0 <= t < t0 + dur):
            continue
        a = min(ease((t - t0) / 0.25), ease((t0 + dur - t) / 0.25))
        d = ImageDraw.Draw(layer)
        size = int(max(70, 110 * H / 1920))
        f = font(F_BLACK, size)
        while size > 40 and d.textlength(text.upper(), font=f) > W * 0.9:
            size -= 4
            f = font(F_BLACK, size)
        bh = int(size * 2.1)
        y0 = int((TITLES_Y if TITLES_Y else H * 0.5) - bh / 2)
        d.rectangle((0, y0, W, y0 + bh), fill=(10, 12, 18, int(200 * a)))
        d.rectangle((0, y0, int(W * 0.012), y0 + bh), fill=(232, 33, 39, int(255 * a)))
        draw_text_stroke(d, (W / 2, y0 + bh / 2), text.upper(), f, (255, 255, 255, int(255 * a)), stroke=0, anchor="mm")
    return layer


def band_image():
    """Info band under the full screen: the template's dark-red grid, darker at the top."""
    bx, by, bw, bh = TMD_BAND
    a = np.zeros((bh, bw, 3), dtype=np.float32)
    for y in range(bh):
        f = y / bh
        a[y, :] = (14 + 34 * f, 1 + 2 * f, 2 + 5 * f)
    img = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(img)
    for x in range(48, bw, 140):
        d.line((x, 0, x, bh), fill=(58, 58, 60), width=3)
    for y in range(45, bh, 140):
        d.line((0, y, bw, y), fill=(58, 58, 60), width=3)
    return img


def steps_layer(steps, t, card):
    """Step labels in the info band (full framing): a green kicker ("STEP 2") and the step in big white text."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if card and card["t0"] <= t < card["t1"]:
        return layer
    bx, by, bw, bh = TMD_BAND
    for st in steps or []:
        t0, t1, kicker, text = st[0], st[1], st[2], st[3]
        if not (t0 <= t < t1):
            continue
        a = min(ease((t - t0) / 0.25), ease((t1 - t) / 0.2))
        d = ImageDraw.Draw(layer)
        x0, x1, y0, y1 = 30, W - 30, by + 40, by + bh - 40
        d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(14, 16, 22, int(225 * a)), outline=(122, 201, 67, int(255 * a)), width=4)
        kf = font(F_BLACK, 46)
        d.text((x0 + 40, y0 + 34), kicker.upper(), font=kf, fill=(122, 201, 67, int(255 * a)), anchor="lt")
        size = 74
        f = font(F_BLACK, size)
        words, lines = text.split(), []
        while True:
            lines, cur = [], ""
            for w_ in words:
                nxt = (cur + " " + w_).strip()
                if d.textlength(nxt, font=f) > (x1 - x0 - 80) and cur:
                    lines.append(cur); cur = w_
                else:
                    cur = nxt
            lines.append(cur)
            if len(lines) <= 2 or size <= 48:
                break
            size -= 6
            f = font(F_BLACK, size)
        ty = y0 + 100
        for ln in lines[:2]:
            d.text((x0 + 40, ty), ln, font=f, fill=(255, 255, 255, int(255 * a)), anchor="lt")
            ty += int(size * 1.12)
    return layer


def handle_layer(handle):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(F_SEMI, 34)
    txt = "@" + handle
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle((40, 60, 40 + tw + 40, 120), 30, fill=(0, 0, 0, 110))
    d.text((60, 90), txt, font=f, fill=(255, 255, 255, 230), anchor="lm")
    return layer


# ------------------------------------------------------------------ frames
class Cut:
    def __init__(self, spec, base):
        self.spec = spec
        self.base = base
        cap = os.path.join(base, spec["captures"])
        self.images = {}
        for _, f in spec["shots"]:
            if f not in self.images:
                self.images[f] = Image.open(os.path.join(cap, f)).convert("RGB")
        # "hide": [[x, y, w, h], ...] smears things that are not part of the tutorial (the capture PC's
        # "Test Mode / Windows Server" desktop watermark, a stranger's name) on every screenshot
        for f, im in self.images.items():
            for x, y, w, h in spec.get("hide", []):
                pad = 40
                box = (max(0, x - pad), max(0, y - pad), min(im.width, x + w + pad), min(im.height, y + h + pad))
                region = im.crop(box).filter(ImageFilter.GaussianBlur(22))
                im.paste(region.crop((x - box[0], y - box[1], x - box[0] + w, y - box[1] + h)), (x, y))
        first = next(iter(self.images.values()))
        self.sw, self.sh = first.size
        self.cam = Camera(spec["cam"], self.sw, self.sh)
        self.cam.max_drift = spec.get("drift", 0.06)
        self.words = json.load(open(os.path.join(base, spec["words"])))["words"] if spec.get("words") else []
        self.hl = set(w.lower() for w in spec.get("highlight", []))
        self.ends = None
        if spec.get("script") and self.words:
            self.ends = sentence_ends(open(os.path.join(base, spec["script"])).read(), len(self.words))
            print("sentence breaks:", "matched" if self.ends else "script/word mismatch, using pauses")
        self.handle_l = handle_layer(spec.get("handle", "TM_Diamond"))
        self.tmd = spec.get("layout") == "tmd"
        if self.tmd:
            tdir = os.path.join(HERE, "..", "templates", "tmd")
            self.top = Image.open(os.path.join(tdir, "top.png")).convert("RGB")
            self.strip_path = os.path.join(tdir, "bottom.mp4")
            self.strip_w, self.strip_h = 1080, 628
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", self.strip_path],
                                       capture_output=True, text=True).stdout.strip())
            self.strip_n = int(dur * FPS) - 2
            self.strip_proc, self.strip_idx, self.strip_img = None, -1, None
            self.full = spec.get("framing") == "full"
            self.band = band_image() if self.full else None

    def caption_y(self, t):
        # optional "caption_y": [[t, frac], ...] moves the captions (e.g. down while the camera is on an address bar)
        y = None
        for ct, frac in self.spec.get("caption_y", []):
            if t >= ct:
                y = frac
        return y

    def shot_at(self, t):
        cur = self.spec["shots"][0][1]
        for st, f in self.spec["shots"]:
            if t >= st:
                cur = f
        return self.images[cur]

    def strip_at(self, t):
        """The owner's presenter strip (templates/tmd/bottom.mp4), looped."""
        idx = int(round(t * FPS)) % self.strip_n
        if self.strip_proc is None or idx < self.strip_idx:
            if self.strip_proc:
                self.strip_proc.kill()
            ss = idx / FPS
            self.strip_proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", self.strip_path, "-f", "rawvideo",
                                                "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            self.strip_idx = idx - 1
            self.strip_img = None
        while self.strip_idx < idx:
            raw = self.strip_proc.stdout.read(self.strip_w * self.strip_h * 3)
            if len(raw) < self.strip_w * self.strip_h * 3:
                self.strip_proc.kill()
                self.strip_proc = None
                return self.strip_at(0) if idx else self.strip_img
            self.strip_img = Image.frombytes("RGB", (self.strip_w, self.strip_h), raw)
            self.strip_idx += 1
        return self.strip_img

    def frame(self, t):
        if self.tmd:
            return self.frame_tmd(t)
        cam = self.cam.at(t)
        # motion blur while the camera moves fast
        c2 = self.cam.at(t + 1 / FPS)
        speed = abs(c2[0] - cam[0]) + abs(c2[1] - cam[1]) + abs(c2[2] - cam[2])
        img = self.shot_at(t)
        if speed > 30:
            fr = [np.asarray(render_screen(img, self.cam.at(t + k / (8 * FPS))), dtype=np.float32) for k in range(3)]
            base = Image.fromarray(np.clip(sum(fr) / 3, 0, 255).astype(np.uint8))
        else:
            base = render_screen(img, cam)
        base = base.convert("RGBA")
        # soft top/bottom shading so captions read on any screen (whole frame stays the real screen)
        base.alpha_composite(self.shade)
        base.alpha_composite(boxes_layer(self.spec, t, cam))
        base.alpha_composite(callouts_layer(self.spec, t, cam))
        base.alpha_composite(cursor_layer(self.spec, t, cam))
        base.alpha_composite(keycaps_layer(self.spec.get("keys", []), t))
        base.alpha_composite(caption_layer(self.words, t, self.hl, self.ends, self.caption_y(t)))
        base.alpha_composite(titles_layer(self.spec.get("titles"), t))
        base.alpha_composite(follow_layer(t, self.spec.get("follow"), self.spec.get("handle", "TM_Diamond")))
        base.alpha_composite(self.handle_l)
        return base.convert("RGB")

    def frame_tmd(self, t):
        cam = self.cam.at(t)
        c2 = self.cam.at(t + 1 / FPS)
        speed = abs(c2[0] - cam[0]) + abs(c2[1] - cam[1]) + abs(c2[2] - cam[2])
        img = self.shot_at(t)
        if speed > 30:
            fr = [np.asarray(render_screen(img, self.cam.at(t + k / (8 * FPS))), dtype=np.float32) for k in range(3)]
            panel = Image.fromarray(np.clip(sum(fr) / 3, 0, 255).astype(np.uint8))
        else:
            panel = render_screen(img, cam)
        base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        base.paste(self.top, (0, 0))
        if self.full:
            base.paste(self.band, TMD_BAND[:2])
            base.paste(self.strip_at(t), (0, TMD_PANEL[1] + TMD_PANEL[3]))
        else:
            base.paste(self.strip_at(t), (0, PY + PH))
        base.paste(panel, (PX, PY))
        base.alpha_composite(boxes_layer(self.spec, t, cam))
        base.alpha_composite(callouts_layer(self.spec, t, cam))
        base.alpha_composite(cursor_layer(self.spec, t, cam))
        base.alpha_composite(keycaps_layer(self.spec.get("keys", []), t))
        if self.full:
            base.alpha_composite(steps_layer(self.spec.get("steps"), t, self.spec.get("card")))
        base.alpha_composite(card_layer(self.spec.get("card"), t))
        base.alpha_composite(titles_layer(self.spec.get("titles"), t))
        if self.spec.get("captions", False):
            base.alpha_composite(caption_layer(self.words, t, self.hl, self.ends, self.caption_y(t)))
        base.alpha_composite(follow_layer(t, self.spec.get("follow"), self.spec.get("handle", "TM_Diamond")))
        return base.convert("RGB")

    @property
    def shade(self):
        if not hasattr(self, "_shade"):
            a = np.zeros((H, 1), dtype=np.float32)
            for y in range(H):
                top = max(0.0, 1 - y / (H * 0.36)) * 0.42
                bot = max(0.0, (y - H * 0.80) / (H * 0.20)) * 0.30
                a[y] = max(top, bot)
            alpha = (np.repeat(a, W, axis=1) * 255).astype(np.uint8)
            self._shade = Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(alpha)])
        return self._shade


# ------------------------------------------------------------------ audio
def load_wav(path):
    with wave.open(path) as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
        sr = w.getframerate()
    if sr != SR:
        idx = np.arange(0, len(data), sr / SR)
        data = np.interp(idx, np.arange(len(data)), data)
    return data


def kenney(name):
    for pack in ("interface-sounds", "ui-audio", "digital-audio"):
        p = os.path.join(HERE, "sfx", "kenney", pack, name + ".wav")
        if os.path.exists(p):
            return p
    return None


SOUNDS = {
    # Kenney "Interface Sounds" (CC0), engine/sfx/kenney/interface-sounds
    "click": (["click_004", "select_001", "select_002"], 0.42),
    "key": (["tick_001", "tick_004", "toggle_004", "click_001"], 0.17),
    "shortcut": (["toggle_001", "toggle_002", "click_001"], 0.30),
    "pop": (["drop_002", "pluck_002", "drop_001"], 0.26),
    "ding": (["confirmation_001", "confirmation_003"], 0.38),
    "open": (["open_002", "maximize_003", "open_004"], 0.24),
}


def synth_whoosh(dur=0.32):
    n = int(SR * dur)
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    # band sweep via moving average of varying length
    out = np.zeros(n, dtype=np.float32)
    k = 1
    acc = 0.0
    for i in range(n):
        acc += noise[i]
        if i >= k:
            acc -= noise[i - k]
        out[i] = acc / k
        k = max(1, int(28 - 24 * i / n))
    return out * env * 0.5


def synth(kind, rng):
    """Fallback UI sounds made from filtered noise and short tones (used only if the CC0 packs are absent)."""
    t = lambda d: np.arange(int(SR * d)) / SR
    g = np.random.default_rng(rng.randint(0, 9999))
    if kind in ("click", "key"):
        d = 0.045 if kind == "key" else 0.06
        x = t(d)
        n = g.standard_normal(len(x)).astype(np.float32)
        hp = np.diff(n, prepend=0)  # bright click
        env = np.exp(-x * (160 if kind == "key" else 110))
        body = np.sin(2 * np.pi * (1900 if kind == "key" else 1400) * x) * np.exp(-x * 220)
        return ((hp * 0.5 + body * 0.6) * env).astype(np.float32)
    if kind == "pop":
        x = t(0.12)
        f = 520 + 900 * np.exp(-x * 40)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30) * 0.8).astype(np.float32)
    if kind in ("ding", "open"):
        x = t(0.7 if kind == "ding" else 0.25)
        base = 1318.5 if kind == "ding" else 880.0
        y = np.sin(2 * np.pi * base * x) + 0.5 * np.sin(2 * np.pi * base * 1.5 * x)
        return (y * np.exp(-x * (6 if kind == "ding" else 18)) * 0.45).astype(np.float32)
    return synth_whoosh()


def build_sfx(spec, duration):
    total = np.zeros(int(SR * (duration + 1)), dtype=np.float32)
    rng = random.Random(7)
    cache = {}

    def get(kind):
        names, vol = SOUNDS.get(kind, ([], 0.3))
        avail = [n for n in names if kenney(n)]
        if not avail:
            return synth(kind, rng), vol
        n = rng.choice(avail)
        if n not in cache:
            cache[n] = load_wav(kenney(n))
        return cache[n], vol

    events = list(spec.get("sfx", []))
    events += [[c, "click"] for c in spec.get("clicks", [])]
    for k in spec.get("keys", []):
        kt, names = k[0], k[1]
        for i in range(len(names)):
            events.append([kt + 0.25 + 0.12 * i, "shortcut"])
        events.append([kt, "pop"])
    for t0, t1, n in spec.get("typing", []):
        for i in range(int(n)):
            events.append([t0 + (t1 - t0) * i / max(1, n - 1) + rng.uniform(-0.015, 0.015), "key"])
    if spec.get("follow") is not None:
        events.append([spec["follow"], "pop"])
        events.append([spec["follow"] + 0.9, "click"])
    for t, kind in events:
        if kind == "whoosh":
            s, vol = synth_whoosh(), 0.35
        else:
            s, vol = get(kind)
            if s is None:
                continue
            vol *= rng.uniform(0.85, 1.1)
        i = int(t * SR)
        if i < 0 or i >= len(total):
            continue
        seg = s[: len(total) - i] * vol
        total[i: i + len(seg)] += seg
    return total


def write_wav(path, data):
    d = np.clip(data, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((d * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------ main
def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path))
    global W, H, PX, PY, PW, PH, FOLLOW_Y, TITLES_Y
    if spec.get("size"):
        W, H = int(spec["size"][0]), int(spec["size"][1])
    PX, PY, PW, PH = 0, 0, W, H
    # the owner's Team Diamond template is the default for every vertical video ("layout": "full" opts out)
    spec.setdefault("layout", "tmd" if H > W else "full")
    if spec.get("layout") == "tmd":
        PX, PY, PW, PH = TMD_PANEL
        FOLLOW_Y = spec.get("follow_y", 0.55)
        if spec.get("framing") == "full":
            PX, PY, PW, PH = TMD_FULL
            bx, by, bw, bh = TMD_BAND
            FOLLOW_Y = spec.get("follow_y", (by + (bh - 170) / 2) / H)
            TITLES_Y = by + bh / 2
            if spec.get("card"):
                spec["card"].setdefault("y", by + (bh - 300) / 2)
    base = os.getcwd()
    cut = Cut(spec, base)
    dur = spec["duration"]
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        thumbs = []
        for t in ts:
            tw, th = (270, 480) if H > W else (480, 270)
            fr = cut.frame(t).resize((tw, th))
            ImageDraw.Draw(fr).text((8, 6), f"{t:.2f}s", fill=(255, 255, 0), font=font(F_BOLD, 26), stroke_width=3, stroke_fill=(0, 0, 0))
            thumbs.append(fr)
        cols = min(6, len(thumbs))
        rows = math.ceil(len(thumbs) / cols)
        tw, th = thumbs[0].size
        sheet = Image.new("RGB", (cols * (tw + 4), rows * (th + 4)), (0, 0, 0))
        for i, im in enumerate(thumbs):
            sheet.paste(im, ((i % cols) * (tw + 4), (i // cols) * (th + 4)))
        sheet.save(out)
        print(out)
        return
    tmp = out + ".parts"
    os.makedirs(tmp, exist_ok=True)
    sfx = build_sfx(spec, dur)
    write_wav(os.path.join(tmp, "sfx.wav"), sfx)
    n = int(dur * FPS)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", os.path.join(base, spec["narration"]), "-i", os.path.join(tmp, "sfx.wav"),
                            "-filter_complex", "[1:a]aresample=48000,volume=1.0[v];[2:a]volume=1.0[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "4000k", "-bufsize", "8000k",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{dur:.2f}", "-movflags", "+faststart", out],
                           stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(cut.frame(i / FPS).tobytes())
    enc.stdin.close()
    enc.wait()
    print(out, os.path.getsize(out))


if __name__ == "__main__":
    main()
