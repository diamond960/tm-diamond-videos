"""TM_Diamond free Shorts renderer.

Renders a 1080x1920 vertical Short from a JSON spec: animated visuals,
kinetic captions, camera punch-ins, shake, flashes, synthesized sound
effects and music, mixed under a narration track. Output is an H.264 MP4
kept small enough for Make's free plan (5 MB).

Usage: python3 engine/shorts.py spec.json out.mp4 [--preview t1,t2,...]
"""
import json
import math
import os
import random
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SR = 48000
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

COL = {
    "w": (255, 255, 255), "white": (255, 255, 255),
    "lime": (200, 255, 46), "orange": (217, 119, 87), "red": (255, 77, 77),
    "blue": (124, 140, 255), "pink": (255, 122, 200), "cyan": (63, 224, 208),
    "yellow": (255, 214, 10), "navy": (11, 16, 32), "card": (21, 28, 54),
    "card2": (32, 44, 84), "grey": (120, 132, 160), "dark": (6, 9, 20),
    "ytred": (255, 0, 51), "green": (46, 204, 113),
}
VIS_CY = 720      # centre of the visual area
CAP_CY = 1300     # centre of the caption block
CAP_MAXW = 820    # keeps captions clear of the Shorts buttons on the right
CAP_CX = 520


def C(name, a=255):
    c = COL.get(name, name) if isinstance(name, str) else name
    return (c[0], c[1], c[2], a)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.9):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_in_out(t):
    t = clamp(t)
    return 3 * t * t - 2 * t * t * t


@lru_cache(maxsize=256)
def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- sprites
SS = 2  # supersampling for smooth shapes


def canvas(w, h):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def done(img):
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def s(v):
    return int(round(v * SS))


def rrect(d, box, r, fill=None, outline=None, width=0):
    d.rounded_rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])], radius=s(r),
                        fill=fill, outline=outline, width=s(width) if width else 0)


def text_sprite(txt, size, color="w", path=FONT_BLACK, stroke=0, stroke_col="dark"):
    f = font(path, size * SS)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = tmp.textbbox((0, 0), txt, font=f, stroke_width=s(stroke))
    w, h = bb[2] - bb[0] + s(8), bb[3] - bb[1] + s(8)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((-bb[0] + s(4), -bb[1] + s(4)), txt, font=f, fill=C(color),
           stroke_width=s(stroke), stroke_fill=C(stroke_col))
    return done(img)


@lru_cache(maxsize=128)
def emoji_sprite(ch, size):
    f = font(EMOJI_FONT, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((10, 10), ch, font=f, embedded_color=True)
    bb = img.getbbox() or (0, 0, 160, 160)
    img = img.crop(bb)
    k = size / max(img.size)
    return img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)


def scaled(img, k):
    if abs(k - 1) < 0.01:
        return img
    w, h = max(1, int(img.width * k)), max(1, int(img.height * k))
    return img.resize((w, h), Image.BILINEAR)


def with_alpha(img, a):
    if a >= 0.999:
        return img
    img = img.copy()
    al = img.getchannel("A").point(lambda v: int(v * a))
    img.putalpha(al)
    return img


def paste(cv, img, cx, cy, k=1.0, a=1.0):
    if a <= 0.01 or k <= 0.01:
        return
    img = with_alpha(scaled(img, k), a)
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cv.width, x + img.width), min(cv.height, y + img.height)
    if x1 <= x0 or y1 <= y0:
        return
    cv.alpha_composite(img.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def pop(t, t0, dur=0.22):
    """scale, alpha for a pop-in starting at t0"""
    if t < t0:
        return 0.0, 0.0
    p = (t - t0) / dur
    return 0.35 + 0.65 * ease_out_back(p), clamp(p * 2.5)


# ---------------------------------------------------------------- visuals
class Visual:
    def __init__(self, p, t0, t1):
        self.p, self.t0, self.t1 = p, t0, t1

    def draw(self, cv, t):
        pass


def studio_card():
    w, h = 760, 440
    img, d = canvas(w, h)
    rrect(d, (0, 0, w, h), 36, fill=C("card"), outline=C("card2"), width=3)
    rrect(d, (34, 32, 74, 60), 8, fill=C("ytred"))
    d.polygon([(s(49), s(39)), (s(49), s(53)), (s(61), s(46))], fill=C("w"))
    d.text((s(86), s(30)), "STUDIO", font=font(FONT_XB, s(26)), fill=C("w"))
    rrect(d, (34, 84, w - 34, 300), 22, fill=C("card2"))
    cx, cy = w / 2, 192
    d.ellipse([s(cx - 46), s(cy - 46), s(cx + 46), s(cy + 46)], fill=C("lime"))
    d.polygon([(s(cx - 14), s(cy - 22)), (s(cx - 14), s(cy + 22)), (s(cx + 24), s(cy))], fill=C("navy"))
    rrect(d, (34, 322, 520, 338), 8, fill=C("card2"))
    rrect(d, (34, 350, 380, 364), 7, fill=C("card2"))
    rrect(d, (34, 382, 250, 422), 20, fill=C("green"))
    d.text((s(58), s(390)), "SCHEDULED", font=font(FONT_XB, s(22)), fill=C("navy"))
    d.ellipse([s(w - 90), s(380), s(w - 46), s(424)], outline=C("w"), width=s(4))
    d.line([s(w - 68), s(390), s(w - 68), s(402), s(w - 58), s(408)], fill=C("w"), width=s(4))
    return done(img)


class Card(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.img = studio_card()

    def draw(self, cv, t):
        dt = t - self.t0
        k = 1.0 + 0.6 * (1 - ease_out_cubic(dt / 0.35)) if self.p.get("crash", True) else 1.0
        paste(cv, self.img, W / 2, VIS_CY - 40 + 8 * math.sin(t * 2.2), k, clamp(dt / 0.12))


class Emoji(Visual):
    """One or more emoji popping in; optional red X / ban over them."""

    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        items = p["items"]  # [{"e": "🤖", "t": 1.2, "x": 0, "y": 0, "size": 360}]
        self.items = [(emoji_sprite(i["e"], i.get("size", 380)), i) for i in items]

    def draw(self, cv, t):
        for img, i in self.items:
            ti = i.get("t", self.t0)
            k, a = pop(t, ti, 0.28)
            bob = 10 * math.sin((t - ti) * 3 + i.get("x", 0))
            paste(cv, img, W / 2 + i.get("x", 0), VIS_CY + i.get("y", 0) + bob, k, a)
        cross = self.p.get("cross")
        if cross:
            draw_cross(cv, t, cross.get("t", self.t0 + 0.3), cross.get("kind", "x"),
                       cross.get("size", 420), cross.get("x", 0), cross.get("y", 0))


def draw_cross(cv, t, tc, kind, size, ox=0, oy=0):
    if t < tc:
        return
    p = ease_out_cubic((t - tc) / 0.18)
    layer, d = canvas(size + 40, size + 40)
    c = (size + 40) / 2
    r = size / 2
    red = C("red")
    if kind == "ban":
        d.ellipse([s(c - r), s(c - r), s(c + r), s(c + r)], outline=red, width=s(26))
        a = math.radians(225)
        x0, y0 = c + r * math.cos(a) * 0.98, c + r * math.sin(a) * 0.98
        x1, y1 = c - r * math.cos(a) * 0.98, c - r * math.sin(a) * 0.98
        d.line([s(x0), s(y0), s(x0 + (x1 - x0) * p), s(y0 + (y1 - y0) * p)], fill=red, width=s(26))
    else:
        q = r * 0.8
        p1, p2 = clamp(p * 2), clamp(p * 2 - 1)
        d.line([s(c - q), s(c - q), s(c - q + 2 * q * p1), s(c - q + 2 * q * p1)], fill=red, width=s(30))
        if p2 > 0:
            d.line([s(c + q), s(c - q), s(c + q - 2 * q * p2), s(c - q + 2 * q * p2)], fill=red, width=s(30))
    paste(cv, done(layer), W / 2 + ox, VIS_CY + oy, 1.0 + 0.25 * (1 - p))


def timeline_sprite():
    w, h = 640, 330
    img, d = canvas(w, h)
    rrect(d, (0, 0, w, h), 30, fill=C("card"), outline=C("card2"), width=3)
    rows = [[("blue", 40, 250), ("lime", 262, 470)], [("pink", 40, 180), ("cyan", 192, 420), ("yellow", 432, 600)],
            [("orange", 40, 330), ("blue", 342, 560)]]
    for ri, row in enumerate(rows):
        y = 60 + ri * 80
        for col, x0, x1 in row:
            rrect(d, (x0, y, x1, y + 52), 12, fill=C(col))
    d.line([s(300), s(30), s(300), s(h - 24)], fill=C("w"), width=s(5))
    return done(img)


def upload_sprite():
    w, h = 420, 300
    img, d = canvas(w, h)
    rrect(d, (0, 0, w, h), 60, fill=C("lime"))
    cx = w / 2
    d.polygon([(s(cx), s(60)), (s(cx - 70), s(140)), (s(cx + 70), s(140))], fill=C("navy"))
    d.rectangle([s(cx - 22), s(130), s(cx + 22), s(215)], fill=C("navy"))
    rrect(d, (cx - 100, 228, cx + 100, 250), 10, fill=C("navy"))
    return done(img)


class IconX(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.img = {"timeline": timeline_sprite, "upload": upload_sprite}[p["icon"]]()

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.img, W / 2, VIS_CY, k, a)
        draw_cross(cv, t, self.p.get("cross_t", self.t0 + 0.35), "x", 360)


class Chat(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        w, h = 760, 300
        img, d = canvas(w, h)
        rrect(d, (0, 0, w, h), 36, fill=C("card"), outline=C("card2"), width=3)
        d.ellipse([s(34), s(34), s(104), s(104)], fill=C("orange"))
        d.text((s(124), s(44)), p.get("name", "Claude"), font=font(FONT_XB, s(40)), fill=C("orange"))
        rrect(d, (34, 136, 640, 158), 11, fill=C("card2"))
        rrect(d, (34, 176, 520, 198), 11, fill=C("card2"))
        self.card = done(img)
        self.user = None
        if p.get("user"):
            ut = text_sprite(p["user"], 40, "navy", FONT_XB)
            bw, bh = ut.width + 70, ut.height + 44
            img, d = canvas(bw, bh)
            rrect(d, (0, 0, bw, bh), bh / 2, fill=C("lime"))
            ub = done(img)
            ub.alpha_composite(ut, (35, 22))
            self.user = ub

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.card, W / 2, VIS_CY - 70, k, a)
        if a > 0.5 and t < self.p.get("user_t", 1e9):
            for i in range(3):
                ph = (t * 3 - i * 0.3) % 1.0
                yy = VIS_CY + 40 - 12 * max(0, math.sin(ph * math.pi))
                dot, dd = canvas(26, 26)
                dd.ellipse([0, 0, s(26), s(26)], fill=C("grey"))
                paste(cv, done(dot), W / 2 - 330 + i * 40, yy + 30)
        if self.user is not None:
            k2, a2 = pop(t, self.p.get("user_t", 1e9), 0.25)
            paste(cv, self.user, W / 2 + 380 - self.user.width / 2, VIS_CY + 150, k2, a2)


class Search(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        w, h = 820, 110
        img, d = canvas(w, h)
        rrect(d, (0, 0, w, h), 55, fill=C("w"))
        d.ellipse([s(36), s(30), s(80), s(74)], outline=C("navy"), width=s(7))
        d.line([s(74), s(68), s(96), s(90)], fill=C("navy"), width=s(8))
        self.bar = done(img)
        self.rows = []
        for r in p.get("rows", []):
            ts = text_sprite(r["text"], 34, "w", FONT_BOLD)
            img, d = canvas(780, 78)
            rrect(d, (0, 0, 780, 78), 18, fill=C("card2"))
            rs = done(img)
            rs.alpha_composite(ts, (28, (78 - ts.height) // 2))
            self.rows.append((rs, r["t"]))

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.22)
        y = VIS_CY - 260
        paste(cv, self.bar, W / 2, y, k, a)
        q = self.p["query"]
        tt0, dur = self.p.get("type_t", self.t0 + 0.3), self.p.get("type_dur", 1.6)
        n = int(len(q) * clamp((t - tt0) / dur)) if t >= tt0 else 0
        caret = "|" if (n < len(q) or int(t * 2) % 2 == 0) and a > 0.9 else ""
        if n or caret:
            ts = text_sprite(q[:n] + caret, 40, "navy", FONT_SEMI)
            paste(cv, ts, W / 2 - 300 + ts.width / 2, y)
        for i, (rs, rt) in enumerate(self.rows):
            k2, a2 = pop(t, rt, 0.2)
            paste(cv, rs, W / 2, y + 130 + i * 96, k2, a2)
        at = self.p.get("arrow_t")
        if at is not None and t >= at:
            pr = ease_out_cubic((t - at) / 0.6)
            pts = [(120, 330), (330, 210), (450, 280), (720, 80)]
            layer, d = canvas(840, 380)
            seg = pr * (len(pts) - 1)
            path = [pts[0]]
            for j in range(1, len(pts)):
                if seg >= j:
                    path.append(pts[j])
                else:
                    f = seg - (j - 1)
                    if f > 0:
                        a0, b0 = pts[j - 1], pts[j]
                        path.append((a0[0] + (b0[0] - a0[0]) * f, a0[1] + (b0[1] - a0[1]) * f))
                    break
            d.line([(s(x), s(y2)) for x, y2 in path], fill=C("lime"), width=s(18), joint="curve")
            if pr > 0.97:
                d.polygon([(s(760), s(55)), (s(690), s(70)), (s(745), s(125))], fill=C("lime"))
            paste(cv, done(layer), W / 2, y + 470)


class Page(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        w, h = 470, 600
        img, d = canvas(w, h)
        rrect(d, (0, 0, w, h), 26, fill=C("w"))
        rrect(d, (40, 44, 300, 70), 13, fill=C("navy"))
        self.page = done(img)
        self.hl = text_sprite(p.get("label", "THE HOOK"), 28, "navy", FONT_XB)

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        pg = self.page.copy()
        d = ImageDraw.Draw(pg)
        lt = self.p.get("lines_t", self.t0 + 0.5)
        n = int(clamp((t - lt) / 2.4) * 8) if t >= lt else 0
        for i in range(n):
            y = 110 + i * 56
            if i == 0:
                d.rounded_rectangle([40, y, 430, y + 40], 12, fill=C("lime"))
                pg.alpha_composite(self.hl, (56, y + 6))
            else:
                d.rounded_rectangle([40, y + 8, 400 - (i * 37) % 140, y + 28], 10, fill=(200, 205, 220, 255))
        paste(cv, pg, W / 2, VIS_CY - 20, k, a)


class Pills(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.pills = []
        for it in p["items"]:
            ts = text_sprite(it["text"], 44, "navy", FONT_BLACK)
            bw, bh = max(360, ts.width + 90), 104
            img, d = canvas(bw, bh)
            rrect(d, (0, 0, bw, bh), bh / 2, fill=C(it.get("c", "lime")))
            pl = done(img)
            pl.alpha_composite(ts, ((bw - ts.width) // 2, (bh - ts.height) // 2))
            self.pills.append((pl, it["t"]))

    def draw(self, cv, t):
        n = len(self.pills)
        for i, (pl, pt) in enumerate(self.pills):
            k, a = pop(t, pt, 0.22)
            paste(cv, pl, W / 2, VIS_CY - (n - 1) * 62 + i * 124, k, a)


class Waveform(Visual):
    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        layer, d = canvas(800, 360)
        nb = 34
        for i in range(nb):
            x = 20 + i * 22.6
            env = math.sin(math.pi * (i + 0.5) / nb) ** 0.6
            v = 0.25 + 0.75 * abs(math.sin(t * 9.1 + i * 0.83) * math.sin(t * 5.3 + i * 1.7))
            hgt = 30 + 290 * env * v
            d.rounded_rectangle([s(x), s(180 - hgt / 2), s(x + 12), s(180 + hgt / 2)], s(6), fill=C("lime"))
        paste(cv, done(layer), W / 2, VIS_CY, k, a)


class Progress(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.rows = []
        for it in p["checks"]:
            ts = text_sprite(it["text"], 40, "w", FONT_XB)
            self.rows.append((ts, it["show"], it["tick"]))

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.2)
        y = VIS_CY - 230
        pr = ease_in_out((t - self.p["fill_t"]) / self.p.get("fill_dur", 2.2)) if t >= self.p["fill_t"] else 0
        layer, d = canvas(760, 160)
        rrect(d, (20, 100, 740, 140), 20, fill=C("card2"))
        if pr > 0.01:
            rrect(d, (20, 100, 20 + 720 * pr, 140), 20, fill=C("lime"))
        lay = done(layer)
        pct = text_sprite(f"{int(round(pr * 100))}%", 64, "w", FONT_BLACK)
        lay.alpha_composite(pct, ((760 - pct.width) // 2, 8))
        paste(cv, lay, W / 2, y, k, a)
        for i, (ts, show, tick) in enumerate(self.rows):
            k2, a2 = pop(t, show, 0.2)
            if a2 <= 0:
                continue
            img, d = canvas(620, 96)
            rrect(d, (0, 0, 620, 96), 22, fill=C("card"), outline=C("card2"), width=3)
            ok = t >= tick
            if ok:
                d.ellipse([s(26), s(22), s(78), s(74)], fill=C("lime"))
                d.line([s(38), s(48), s(49), s(60), s(68), s(36)], fill=C("navy"), width=s(7))
            else:
                d.ellipse([s(26), s(22), s(78), s(74)], outline=C("grey"), width=s(5))
            row = done(img)
            row.alpha_composite(ts, (104, (96 - ts.height) // 2))
            bump = 1 + 0.12 * (1 - ease_out_cubic((t - tick) / 0.2)) if ok else 1
            paste(cv, row, W / 2, y + 160 + i * 116, k2 * bump, a2)


class Clock(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.digital = text_sprite(p.get("label", "6:00 PM"), 76, "lime", FONT_BLACK)

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        r = 200
        layer, d = canvas(2 * r + 20, 2 * r + 20)
        c = r + 10
        d.ellipse([s(10), s(10), s(c + r), s(c + r)], fill=C("card"), outline=C("w"), width=s(12))
        for i in range(12):
            an = i * math.pi / 6
            r0 = r - 44 if i % 3 == 0 else r - 32
            d.line([s(c + r0 * math.sin(an)), s(c - r0 * math.cos(an)), s(c + (r - 18) * math.sin(an)),
                    s(c - (r - 18) * math.cos(an))], fill=C("w"), width=s(8 if i % 3 == 0 else 4))
        target = self.p.get("land_t", self.t0 + 1.2)
        pr = ease_out_cubic((t - self.t0) / max(0.2, target - self.t0))
        hours = 6 * pr + (1 - pr) * 1.5
        mins = 12 * 60 * pr * 0 + (1 - pr) * 40
        ha = (hours % 12) / 12 * 2 * math.pi
        ma = (mins % 60) / 60 * 2 * math.pi + pr * 6 * 2 * math.pi
        d.line([s(c), s(c), s(c + (r - 110) * math.sin(ha)), s(c - (r - 110) * math.cos(ha))], fill=C("lime"), width=s(16))
        d.line([s(c), s(c), s(c + (r - 50) * math.sin(ma)), s(c - (r - 50) * math.cos(ma))], fill=C("w"), width=s(10))
        d.ellipse([s(c - 14), s(c - 14), s(c + 14), s(c + 14)], fill=C("lime"))
        paste(cv, done(layer), W / 2, VIS_CY - 80, k, a)
        k2, a2 = pop(t, target, 0.25)
        paste(cv, self.digital, W / 2, VIS_CY + 200, k2, a2)
        for i, vt in enumerate(self.p.get("viewers_t", [])):
            k3, a3 = pop(t, vt, 0.2)
            col = ["blue", "pink", "cyan", "yellow", "orange"][i % 5]
            dot, dd = canvas(70, 70)
            dd.ellipse([0, 0, s(66), s(66)], fill=C(col))
            dd.ellipse([s(46), s(46), s(68), s(68)], fill=C("green"), outline=C("navy"), width=s(4))
            n = len(self.p["viewers_t"])
            paste(cv, done(dot), W / 2 - (n - 1) * 44 + i * 88, VIS_CY + 300, k3, a3)


class Calendar(Visual):
    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        pages = self.p["pages"]  # [{"t":..., "head":"NOV", "num":"6"}]
        cur = pages[0]
        last_t = pages[0]["t"]
        for pg in pages:
            if t >= pg["t"]:
                cur, last_t = pg, pg["t"]
        w, h = 400, 430
        img, d = canvas(w, h)
        rrect(d, (0, 0, w, h), 34, fill=C("w"))
        rrect(d, (0, 0, w, 110), 34, fill=C("red"))
        d.rectangle([0, s(70), s(w), s(110)], fill=C("red"))
        for x in (110, 290):
            d.ellipse([s(x - 14), s(-10), s(x + 14), s(18)], fill=C("navy"))
        card = done(img)
        hd = text_sprite(cur["head"], 52, "w", FONT_BLACK)
        card.alpha_composite(hd, ((w - hd.width) // 2, (110 - hd.height) // 2 + 4))
        nm = text_sprite(cur["num"], 230, "navy", FONT_BLACK)
        fl = ease_out_cubic((t - last_t) / 0.16) if t >= last_t else 1
        nm = nm.resize((nm.width, max(1, int(nm.height * (0.15 + 0.85 * fl)))), Image.BILINEAR)
        card.alpha_composite(nm, ((w - nm.width) // 2, 110 + (320 - nm.height) // 2))
        paste(cv, card, W / 2, VIS_CY - 30, k, a)


class Follow(Visual):
    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        w, h = 800, 200
        img, d = canvas(w, h)
        rrect(d, (0, 0, w, h), 40, fill=C("card"), outline=C("card2"), width=3)
        d.ellipse([s(30), s(40), s(150), s(160)], fill=C("lime"))
        self.base = done(img)
        tm = text_sprite("TM", 50, "navy", FONT_BLACK)
        self.base.alpha_composite(tm, (90 - tm.width // 2, 100 - tm.height // 2))
        nm = text_sprite(p.get("name", "TM_Diamond"), 46, "w", FONT_XB)
        self.base.alpha_composite(nm, (176, 100 - nm.height // 2))
        self.btn1 = self._btn(p.get("label", "Subscribe"), "ytred", "w")
        self.btn2 = self._btn(p.get("done_label", "Subscribed"), "card2", "w")
        self.plus = text_sprite("+1", 70, "lime", FONT_BLACK)

    @staticmethod
    def _btn(txt, bg, fg):
        ts = text_sprite(txt, 34, fg, FONT_XB)
        bw, bh = ts.width + 60, 76
        img, d = canvas(bw, bh)
        rrect(d, (0, 0, bw, bh), 38, fill=C(bg))
        b = done(img)
        b.alpha_composite(ts, ((bw - ts.width) // 2, (bh - ts.height) // 2))
        return b

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        y = VIS_CY - 20
        paste(cv, self.base, W / 2, y, k, a)
        tap = self.p["tap_t"]
        btn = self.btn2 if t >= tap else self.btn1
        press = 1 - 0.12 * clamp(1 - abs(t - tap) / 0.08)
        bx = W / 2 + 400 - 30 - btn.width / 2
        paste(cv, btn, bx, y, k * press, a)
        if t >= tap:
            pr = ease_out_cubic((t - tap) / 0.6)
            paste(cv, self.plus, bx, y - 100 - 60 * pr, 1, clamp(1.6 - pr * 1.2))
            rp = ease_out_cubic((t - tap) / 0.4)
            ring, d = canvas(200, 200)
            rr_ = 20 + 75 * rp
            d.ellipse([s(100 - rr_), s(100 - rr_), s(100 + rr_), s(100 + rr_)], outline=C("w"), width=s(6))
            paste(cv, done(ring), bx, y, 1, clamp(1 - rp))
        # cursor
        cp = ease_in_out((t - self.t0 - 0.1) / max(0.2, tap - self.t0 - 0.15))
        cx = W / 2 + 380 + (bx - (W / 2 + 380)) * cp
        cy = y + 330 + (y + 10 - (y + 330)) * cp
        cur, d = canvas(70, 90)
        d.polygon([(s(4), s(4)), (s(4), s(76)), (s(24), s(58)), (s(38), s(86)), (s(50), s(80)), (s(36), s(52)), (s(62), s(50))],
                  fill=C("w"), outline=C("navy"))
        paste(cv, done(cur), cx + 20, cy + 30, 1, a)


class BigText(Visual):
    """A giant word/number (e.g. "3", "FREE", "10X") with optional small label under it."""

    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.big = text_sprite(p["text"], p.get("size", 300), p.get("c", "lime"), FONT_BLACK, stroke=6)
        if self.big.width > 900:
            k = 900 / self.big.width
            self.big = self.big.resize((900, int(self.big.height * k)), Image.LANCZOS)
        self.sub = text_sprite(p["sub"], 54, "w", FONT_XB) if p.get("sub") else None

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.3)
        paste(cv, self.big, W / 2, VIS_CY - 30 + 6 * math.sin(t * 3), k, a)
        if self.sub is not None:
            k2, a2 = pop(t, self.p.get("sub_t", self.t0 + 0.25), 0.22)
            paste(cv, self.sub, W / 2, VIS_CY + self.big.height / 2 + 30, k2, a2)


class ListItems(Visual):
    """Numbered rows appearing one by one: items [{"text": "...", "t": 1.2, "e": "🎬"}]."""

    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.rows = []
        for i, it in enumerate(p["items"]):
            w, h = 820, 120
            img, d = canvas(w, h)
            rrect(d, (0, 0, w, h), 30, fill=C("card"), outline=C(it.get("c", "card2")), width=3)
            d.ellipse([s(22), s(22), s(98), s(98)], fill=C(it.get("c", "lime")))
            row = done(img)
            num = text_sprite(str(it.get("n", i + 1)), 46, "navy", FONT_BLACK)
            row.alpha_composite(num, (60 - num.width // 2, 60 - num.height // 2))
            x = 124
            if it.get("e"):
                em = emoji_sprite(it["e"], 70)
                row.alpha_composite(em, (x, 60 - em.height // 2))
                x += 90
            ts = text_sprite(it["text"], 46, "w", FONT_XB)
            if ts.width > w - x - 30:
                kk = (w - x - 30) / ts.width
                ts = ts.resize((int(ts.width * kk), int(ts.height * kk)), Image.LANCZOS)
            row.alpha_composite(ts, (x, 60 - ts.height // 2))
            self.rows.append((row, it["t"]))

    def draw(self, cv, t):
        n = len(self.rows)
        for i, (row, rt) in enumerate(self.rows):
            k, a = pop(t, rt, 0.22)
            paste(cv, row, W / 2, VIS_CY - (n - 1) * 72 + i * 144, k, a)


class Versus(Visual):
    """2-3 columns: cols [{"title": "ChatGPT", "e": "💬", "c": "green", "t": 0.5, "line": "Best for...", "line_t": 1.0}]."""

    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.cols = []
        n = len(p["cols"])
        cw = 300 if n == 3 else 420
        for cdef in p["cols"]:
            img, d = canvas(cw, 470)
            rrect(d, (0, 0, cw, 470), 34, fill=C("card"), outline=C(cdef.get("c", "lime")), width=5)
            col = done(img)
            if cdef.get("e"):
                em = emoji_sprite(cdef["e"], 130)
                col.alpha_composite(em, ((cw - em.width) // 2, 40))
            ts = text_sprite(cdef["title"], 44, cdef.get("c", "lime"), FONT_BLACK)
            if ts.width > cw - 30:
                kk = (cw - 30) / ts.width
                ts = ts.resize((int(ts.width * kk), int(ts.height * kk)), Image.LANCZOS)
            col.alpha_composite(ts, ((cw - ts.width) // 2, 200))
            line = None
            if cdef.get("line"):
                line = text_sprite(cdef["line"], 34, "w", FONT_BOLD)
                if line.width > cw - 30:
                    kk = (cw - 30) / line.width
                    line = line.resize((int(line.width * kk), int(line.height * kk)), Image.LANCZOS)
            self.cols.append((col, cdef, line))
        self.cw = cw

    def draw(self, cv, t):
        n = len(self.cols)
        gap = 24
        total = n * self.cw + (n - 1) * gap
        for i, (col, cdef, line) in enumerate(self.cols):
            k, a = pop(t, cdef.get("t", self.t0), 0.25)
            x = W / 2 - total / 2 + self.cw / 2 + i * (self.cw + gap) - 20
            win = 1.08 if cdef.get("win_t") is not None and t >= cdef["win_t"] else 1.0
            paste(cv, col, x, VIS_CY, k * win, a)
            if line is not None and t >= cdef.get("line_t", 1e9):
                k2, a2 = pop(t, cdef["line_t"], 0.2)
                paste(cv, line, x, VIS_CY + 150, k2, a2)


VISUALS = {"card": Card, "emoji": Emoji, "iconx": IconX, "chat": Chat, "search": Search, "page": Page,
           "pills": Pills, "waveform": Waveform, "progress": Progress, "clock": Clock, "calendar": Calendar,
           "follow": Follow, "bigtext": BigText, "list": ListItems, "versus": Versus}


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def aligned_words(data):
    """Word timings using the script's own words and punctuation when the job stored the script
    ("text"); whisper's words keep their timings, script words are matched to them in order."""
    ws = data["words"]
    text = data.get("text")
    if not text:
        return ws
    import difflib
    toks = text.replace("\n", " ").split()
    a = [_norm(t) for t in toks]
    b = [_norm(w["w"]) for w in ws]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    times = [None] * len(toks)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = ws[blk.b + k]
            times[blk.a + k] = (w["s"], w["e"])
    known = [i for i, tm in enumerate(times) if tm]
    if not known:
        return ws
    for i in range(len(toks)):
        if times[i] is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            if prev is None:
                s0 = 0.0
            else:
                s0 = times[prev][1]
            e0 = times[nxt][0] if nxt is not None else s0 + 0.35
            span = [j for j in range(prev + 1 if prev is not None else 0, nxt if nxt is not None else len(toks))]
            k = span.index(i)
            step = (e0 - s0) / max(1, len(span))
            times[i] = (s0 + k * step, s0 + (k + 1) * step)
    return [{"w": t, "s": round(tm[0], 3), "e": round(tm[1], 3)} for t, tm in zip(toks, times)]


def auto_captions(cfg, base):
    """Build caption groups from word timings: 1-3 words per line, 2 lines per group,
    a new group at every sentence start. Highlight words go lime, 'claude' orange, negatives red."""
    data = json.load(open(os.path.join(base, cfg["words"])))
    if cfg.get("text") and not data.get("text"):
        data["text"] = cfg["text"]
    data = dict(data, words=aligned_words(data))
    hl = {w.lower() for w in cfg.get("highlight", [])}
    neg = {w.lower() for w in cfg.get("negative", ["no", "never", "not", "don't", "stop"])}
    groups, cur_lines, line = [], [], []
    def color(word):
        k = word.lower().strip(".,!?…\"'")
        if k == "claude":
            return "orange"
        if k in hl:
            return "lime"
        if k in neg:
            return "red"
        return "w"
    def flush_line():
        nonlocal line
        if line:
            txt = " ".join(w["w"].strip(",") for w in line).upper().replace("...", "").replace("…", "")
            cols = [color(w["w"]) for w in line]
            c = next((x for x in cols if x != "w"), "w")
            cur_lines.append({"text": txt.strip(), "t": line[0]["s"], "c": c})
            line = []
    def flush_group():
        nonlocal cur_lines
        flush_line()
        if cur_lines:
            groups.append({"t": cur_lines[0]["t"], "lines": cur_lines})
            cur_lines = []
    for wd in data["words"]:
        line.append(wd)
        txt = " ".join(x["w"] for x in line)
        end_sentence = wd["w"].rstrip().endswith((".", "?", "!", "…"))
        if len(line) >= 3 or len(txt) >= 13 or end_sentence or wd["w"].endswith(","):
            flush_line()
            if len(cur_lines) >= 2 or end_sentence:
                flush_group()
    flush_group()
    return groups


# ---------------------------------------------------------------- captions
@lru_cache(maxsize=512)
def cap_sprite(txt, color, size):
    while size > 50:
        sp = text_sprite(txt, size, color, FONT_BLACK, stroke=7, stroke_col="dark")
        if sp.width <= CAP_MAXW:
            return sp
        size -= 6
    return text_sprite(txt, size, color, FONT_BLACK, stroke=6, stroke_col="dark")


def draw_captions(cv, t, groups):
    g = None
    for gr in groups:
        if t >= gr["t"]:
            g = gr
    if not g or t >= g.get("end", 1e9):
        return
    lines = g["lines"]
    size = g.get("size", 118 if len(lines) <= 2 else 104)
    sprites = [cap_sprite(ln["text"], ln.get("c", "w"), size) for ln in lines]
    gap = 6
    total = sum(sp.height for sp in sprites) + gap * (len(sprites) - 1)
    y = CAP_CY - total / 2
    for ln, sp in zip(lines, sprites):
        lt = ln.get("t", g["t"])
        if t >= lt:
            p = (t - lt) / 0.16
            k = 0.55 + 0.45 * ease_out_back(p, 2.4)
            paste(cv, sp, CAP_CX, y + sp.height / 2, k, clamp(p * 3))
        y += sp.height + gap


# ---------------------------------------------------------------- background
def make_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = COL["navy"]
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - VIS_CY) * 0.85) ** 2)
    glow = np.clip(1 - d / 760, 0, 1) ** 2
    vign = np.clip(1 - np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / 1500, 0.55, 1)
    return base, glow[..., None], vign[..., None]


class Background:
    def __init__(self, seed=7):
        self.base, self.glow, self.vign = make_background()
        rnd = random.Random(seed)
        self.parts = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 5), rnd.uniform(18, 60), rnd.uniform(0.15, 0.5))
                      for _ in range(46)]
        self.cache = {}

    def frame(self, t, tint=(200, 255, 46)):
        pulse = 0.13 + 0.035 * math.sin(t * 2.4)
        key = (round(pulse, 3), tint)
        arr = self.cache.get(key)
        if arr is None:
            arr = self.base + self.glow * np.array(tint, np.float32) * pulse
            arr = np.clip(arr * self.vign, 0, 255).astype(np.uint8)
            if len(self.cache) > 80:
                self.cache.clear()
            self.cache[key] = arr
        img = Image.fromarray(arr, "RGB").convert("RGBA")
        d = ImageDraw.Draw(img)
        for x, y, r, sp, al in self.parts:
            py = (y - t * sp) % H
            px = x + 12 * math.sin(t * 0.7 + y)
            d.ellipse([px - r, py - r, px + r, py + r], fill=(200, 255, 46, int(255 * al * 0.33)))
        return img


# ---------------------------------------------------------------- audio
def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def lowpass(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    # vectorised one-pole via lfilter-like loop in chunks
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp_fast(x, fc):
    # FFT-domain gentle low-pass (no per-sample loop)
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, n)


def hp_fast(x, fc):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X, n)


def sine_glide(f0, f1, dur, curve=3.0):
    n = int(dur * SR)
    tt = np.arange(n) / n
    f = f1 + (f0 - f1) * np.exp(-curve * tt * 3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def sfx(kind, rng):
    if kind == "whoosh":
        n = int(0.42 * SR)
        x = rng.standard_normal(n)
        lo = lp_fast(x, 900)
        hi = hp_fast(x, 2500)
        tt = np.arange(n) / n
        mix = lo * (1 - tt) + hi * tt * 0.6
        env = np.sin(np.pi * np.clip(tt * 1.2, 0, 1)) ** 2
        return mix * env * 0.9
    if kind == "pop":
        y = sine_glide(1100, 320, 0.12, 2.5) * env_exp(int(0.12 * SR), 0.035)
        y[:200] += rng.standard_normal(200) * np.linspace(0.4, 0, 200)
        return y * 0.8
    if kind == "click":
        n = int(0.03 * SR)
        y = hp_fast(rng.standard_normal(n), 3000) * env_exp(n, 0.004)
        y += np.sin(2 * np.pi * 2400 * np.arange(n) / SR) * env_exp(n, 0.006) * 0.5
        return y
    if kind == "bass":
        n = int(0.7 * SR)
        y = np.tanh(2.2 * sine_glide(160, 42, 0.7, 1.4) * env_exp(n, 0.22))
        y[:600] += rng.standard_normal(600) * np.linspace(0.5, 0, 600)
        return y * 0.95
    if kind == "tick":
        n = int(0.09 * SR)
        return np.sin(2 * np.pi * 1760 * np.arange(n) / SR) * env_exp(n, 0.02) * 0.7
    if kind == "ding":
        n = int(1.3 * SR)
        tt = np.arange(n) / SR
        y = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d)
                for f, a, d in [(988, 0.6, 0.6), (1976, 0.3, 0.35), (2730, 0.18, 0.2)])
        return y * 0.8
    if kind == "error":
        n = int(0.22 * SR)
        tt = np.arange(n) / SR
        y = np.sign(np.sin(2 * np.pi * 150 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * tt))
        return lp_fast(y, 1800) * env_exp(n, 0.09) * 0.6
    if kind == "ping":
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * 1318 * tt) * np.exp(-tt / 0.08)
        y2 = np.zeros(n)
        k = int(0.08 * SR)
        y2[k:] = np.sin(2 * np.pi * 1760 * tt[: n - k]) * np.exp(-tt[: n - k] / 0.15)
        return (y + y2) * 0.5
    if kind == "glitch":
        out = []
        for _ in range(8):
            m = int(rng.uniform(0.015, 0.035) * SR)
            if rng.random() < 0.5:
                f = rng.uniform(200, 2000)
                seg = np.sign(np.sin(2 * np.pi * f * np.arange(m) / SR)) * 0.5
            else:
                seg = rng.standard_normal(m) * 0.5
            out.append(seg)
        return np.concatenate(out) * 0.8
    if kind == "flip":
        n = int(0.07 * SR)
        return lp_fast(hp_fast(rng.standard_normal(n), 900), 5000) * env_exp(n, 0.015) * 0.9
    if kind == "typing":
        n = int(1.4 * SR)
        y = np.zeros(n)
        pos = 0
        while pos < n - 2000:
            c = sfx("click", rng) * rng.uniform(0.35, 0.7)
            y[pos:pos + len(c)] += c
            pos += int(rng.uniform(0.06, 0.13) * SR)
        return y
    if kind == "zoom":
        n = int(0.26 * SR)
        tt = np.arange(n) / n
        sw = hp_fast(rng.standard_normal(n), 1800) * tt ** 2.2 * 0.55
        k = int(0.2 * SR)
        th = np.tanh(1.8 * sine_glide(140, 55, 0.2, 1.6) * env_exp(k, 0.07)) * 0.75
        y = np.zeros(int(0.46 * SR))
        y[:n] += sw
        y[n - int(0.02 * SR):n - int(0.02 * SR) + k] += th
        return y
    if kind == "riser":
        n = int(1.0 * SR)
        tt = np.arange(n) / n
        y = hp_fast(rng.standard_normal(n), 1500) * tt ** 2 * 0.5 + sine_glide(200, 900, 1.0, 0.2) * tt * 0.2
        return y
    raise ValueError(kind)


def note_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(dur, bpm=118, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR
    out = np.zeros(n)
    beat = 60 / bpm
    prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G
    kick = sfx("bass", rng)[: int(0.35 * SR)] * 0.9
    hat_n = int(0.05 * SR)
    t = 0.0
    bar = 0
    while t < dur + beat:
        root, chord = prog[bar % 4]
        # pad
        pd = int(4 * beat * SR)
        tt = np.arange(pd) / SR
        pad = sum(np.sin(2 * np.pi * note_freq(m + 12) * tt) + 0.5 * np.sin(2 * np.pi * note_freq(m + 12) * 1.003 * tt) for m in chord)
        pad *= np.minimum(1, tt / 0.25) * np.minimum(1, (tt[-1] - tt) / 0.3 + 0.05)
        i0 = int(t * SR)
        seg = out[i0:i0 + pd]
        seg += pad[: len(seg)] * 0.045
        for b in range(8):  # eighths
            tb = t + b * beat / 2
            j = int(tb * SR)
            if j >= n:
                break
            if b in (0, 3, 4):
                k = kick[: n - j]
                out[j:j + len(k)] += k * 0.55
            if b in (2, 6):
                cn = int(0.18 * SR)
                clap = hp_fast(rng.standard_normal(cn), 1200) * env_exp(cn, 0.045) * 0.35
                out[j:j + cn] += clap[: n - j]
            hat = hp_fast(rng.standard_normal(hat_n), 7000) * env_exp(hat_n, 0.012) * (0.22 if b % 2 else 0.12)
            out[j:j + hat_n] += hat[: max(0, min(hat_n, n - j))]
            bn = int(beat / 2 * SR * 0.9)
            tt2 = np.arange(bn) / SR
            f = note_freq(root - 12)
            saw = 2 * ((tt2 * f) % 1) - 1
            bassn = lp_fast(saw, 380) * env_exp(bn, 0.12) * 0.28
            out[j:j + bn] += bassn[: max(0, min(bn, n - j))]
            arp_m = chord[(b * 2) % 3] + 24
            an = int(beat / 2 * SR)
            tt3 = np.arange(an) / SR
            tri = 2 * np.abs(2 * ((tt3 * note_freq(arp_m)) % 1) - 1) - 1
            out[j:j + an] += (tri * env_exp(an, 0.07) * 0.06)[: max(0, min(an, n - j))]
        t += 4 * beat
        bar += 1
    out = out[: int(dur * SR)]
    return out / (np.max(np.abs(out)) + 1e-9)


def read_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def build_audio(spec, dur, out_wav):
    rng = np.random.default_rng(11)
    n = int(dur * SR)
    narr = np.zeros(n)
    if spec.get("narration"):
        v = read_audio(spec["narration"])
        v = v / (np.max(np.abs(v)) + 1e-9) * 0.92
        narr[: min(n, len(v))] = v[:n]
    use_music = spec.get("music", True)
    mus = music(dur, spec.get("bpm", 118)) if use_music else np.zeros(n)
    if np.any(narr):
        rms_v = np.sqrt(np.mean(narr[np.abs(narr) > 0.02] ** 2))
    else:
        rms_v = 0.25
    if use_music:
        mus *= rms_v * 10 ** (-spec.get("music_db", 19) / 20) / (np.sqrt(np.mean(mus ** 2)) + 1e-9)
    env = np.abs(narr)
    k = int(0.08 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = env / (env.max() + 1e-9)
    mus *= 1 - 0.35 * np.clip(env * 3, 0, 1)
    fx = np.zeros(n)
    for ev in spec.get("sfx", []):
        y = sfx(ev["type"], rng) * ev.get("vol", 1.0)
        j = int(ev["t"] * SR)
        if j < n:
            fx[j:j + len(y)] += y[: n - j]
    fx *= rms_v * (1.1 if use_music else 1.3)  # no beat: effects carry the energy
    mix = narr + mus + fx
    fade = int(0.04 * SR)
    mix[-fade:] *= np.linspace(1, 0.6, fade)
    mix = np.tanh(mix * 1.15) / np.tanh(1.15) * 0.82
    pcm = (np.clip(mix, -1, 1) * 32000).astype(np.int16)
    st = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(st.tobytes())


# ---------------------------------------------------------------- frames
class Renderer:
    def __init__(self, spec):
        self.spec = spec
        self.bg = Background()
        self.vis = []
        for v in spec["visuals"]:
            cls = VISUALS[v["type"]]
            self.vis.append(cls(v, v["t0"], v["t1"]))
        self.cuts = sorted(v["t0"] for v in spec["visuals"])
        self.bass = [e["t"] for e in spec.get("sfx", []) if e["type"] in ("bass",)]
        self.glitch = [e["t"] for e in spec.get("sfx", []) if e["type"] == "glitch"]
        self.zooms = sorted(e["t"] for e in spec.get("sfx", []) if e["type"] == "zoom")
        self.rng = random.Random(5)

    def frame(self, t):
        cv = self.bg.frame(t)
        for v in self.vis:
            if v.t0 <= t < v.t1:
                v.draw(cv, t)
        draw_captions(cv, t, self.spec["captions"])
        # camera: punch-in at cuts, slow drift, shake on bass hits
        last_cut = max([c for c in self.cuts if c <= t] or [0])
        dt = t - last_cut
        z = 1.0 + 0.11 * (1 - ease_out_cubic(dt / 0.32)) + 0.025 * clamp(dt / 4)
        # emphasis zoom: snap in on the keyword, hold, ease back out (the "zoom" sfx plays with it)
        for zt in self.zooms:
            dz = t - zt
            if 0 <= dz < 0.9 and zt >= last_cut:
                k = ease_out_cubic(clamp(dz / 0.12)) * (1 - ease_out_cubic(clamp((dz - 0.45) / 0.45)))
                z = max(z, 1.0 + 0.15 * k + 0.025 * clamp(dt / 4))
        sx = sy = 0.0
        for b in self.bass:
            if 0 <= t - b < 0.3:
                amp = 16 * (1 - (t - b) / 0.3)
                sx += amp * math.sin(t * 90)
                sy += amp * math.cos(t * 77)
        img = cv.convert("RGB")
        if sx or sy:
            z = max(z, 1.04)
        if z > 1.001:
            cw, ch = W / z, H / z
            x0 = clamp((W - cw) / 2 - sx, 0, W - cw)
            y0 = clamp((H - ch) / 2 - sy, 0, H - ch)
            img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        fl = clamp(1 - dt / 0.1) * 0.16
        for g in self.glitch:
            if 0 <= t - g < 0.25:
                arr = np.asarray(img).copy()
                off = int(18 * (1 - (t - g) / 0.25))
                arr[..., 0] = np.roll(arr[..., 0], off, axis=1)
                arr[..., 2] = np.roll(arr[..., 2], -off, axis=1)
                img = Image.fromarray(arr)
                fl = max(fl, 0.22 * (1 - (t - g) / 0.25))
        if fl > 0.005:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), fl)
        return img


def render(spec_path, out_path, preview=None, no_music=False):
    spec = json.load(open(spec_path))
    base = os.path.dirname(os.path.abspath(spec_path))
    if spec.get("narration") and not os.path.isabs(spec["narration"]):
        spec["narration"] = os.path.join(base, spec["narration"])
    if isinstance(spec.get("captions"), dict) and spec["captions"].get("auto"):
        spec["captions"] = auto_captions(spec["captions"], base)
    if no_music:
        spec["music"] = False
    if spec.get("auto_zoom", True) and isinstance(spec.get("captions"), list):
        cuts = [v["t0"] for v in spec["visuals"]]
        busy = cuts + [e["t"] for e in spec.get("sfx", []) if e["type"] in ("zoom", "bass", "glitch")]
        for g in spec["captions"]:
            for ln in g["lines"]:
                t = ln.get("t", g["t"])
                if ln.get("c", "w") != "w" and all(abs(t - b) > 0.7 for b in busy) and t < spec["duration"] - 0.8:
                    spec.setdefault("sfx", []).append({"t": round(t, 3), "type": "zoom", "vol": 0.8})
                    busy.append(t)
    if spec.get("auto_sfx", True):
        have = {(round(e["t"], 2), e["type"]) for e in spec.get("sfx", [])}
        extra = [{"t": v["t0"], "type": "whoosh", "vol": 0.7} for v in spec["visuals"]
                 if (round(v["t0"], 2), "whoosh") not in have and v["t0"] > 0.05]
        spec["sfx"] = spec.get("sfx", []) + extra
    dur = spec["duration"]
    r = Renderer(spec)
    if preview:
        frames = [r.frame(t) for t in preview]
        cols = min(6, len(frames))
        rows = math.ceil(len(frames) / cols)
        tw = 270
        th = int(tw * H / W)
        sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), (0, 0, 0))
        dd = ImageDraw.Draw(sheet)
        for i, (fr, tt) in enumerate(zip(frames, preview)):
            x, y = (i % cols) * tw, (i // cols) * (th + 30)
            sheet.paste(fr.resize((tw, th), Image.LANCZOS), (x, y + 30))
            dd.text((x + 6, y + 4), f"{tt:.2f}s", fill=(255, 255, 255), font=font(FONT_BOLD, 20))
        sheet.save(out_path)
        return
    wav = out_path + ".wav"
    build_audio(spec, dur, wav)
    nfr = int(round(dur * FPS))
    # Uploads go through a YouTube resumable session (no Make file limit), so Shorts can be sharp.
    # 3000 kbps peak also stays under Instagram's 5 Mbps Reel limit.
    vb = spec.get("max_video_kbps", 3000)
    crf = str(spec.get("crf", 21))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", crf,
           "-maxrate", f"{vb}k", "-bufsize", f"{vb * 2}k", "-pix_fmt", "yuv420p", "-g", "60",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nfr):
        p.stdin.write(r.frame(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{nfr}", flush=True)
    p.stdin.close()
    p.wait()
    os.remove(wav)
    print("size_bytes", os.path.getsize(out_path))


if __name__ == "__main__":
    pv = None
    args = sys.argv[3:]
    if "--preview" in args:
        pv = [float(x) for x in args[args.index("--preview") + 1].split(",")]
    render(sys.argv[1], sys.argv[2], pv, no_music="--no-music" in args)
