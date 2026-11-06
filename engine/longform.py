"""TM_Diamond long-form (16:9) renderer.

A video is built from a Python "build" file that returns a spec dict:
  {"script": "long/01/script.txt", "words": "long/01/voice.words.json", "narration": "long/01/voice.mp3",
   "scenes": [ {"type": ..., "at": L(line, word=None), ...}, ... ], "sfx": [...]}
Times are anchored to narration lines (and optionally a word in the line), so the same build file
re-times itself automatically when the voiceover is regenerated.

Usage: python3 engine/longform.py long/01/build.py out.mp4 [--preview 1.0,5.0,...] [--start S --end E]
"""
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shorts as sh  # noqa: E402
from shorts import (C, FONT_BLACK, FONT_BOLD, FONT_SEMI, FONT_XB, canvas, clamp, done, ease_in_out,  # noqa: E402
                    ease_out_back, ease_out_cubic, emoji_sprite, font, pop, rrect, s, text_sprite)

W, H, FPS = 1920, 1080, 30
SR = sh.SR
CAP_Y = 985
CAP_MAXW = 1560
STAGE_CY = 470


def paste(cv, img, cx, cy, k=1.0, a=1.0):
    sh.paste(cv, img, cx, cy, k, a)


# ------------------------------------------------------------ timeline
class Timeline:
    def __init__(self, script_path, words_path):
        raw = open(script_path).read().splitlines()
        self.lines, self.sections = [], []
        for ln in raw:
            if ln.startswith("##"):
                self.sections.append((ln[2:].strip(), len(self.lines)))
            elif ln.strip():
                self.lines.append(ln.strip())
        data = json.load(open(words_path))
        data["text"] = "\n".join(self.lines)
        self.words = sh.aligned_words(data)
        self.duration = data["duration"]
        self.line_tok = []
        i = 0
        for ln in self.lines:
            n = len(ln.split())
            self.line_tok.append((i, i + n))
            i += n

    def line_start(self, li):
        a, _ = self.line_tok[li]
        return self.words[a]["s"]

    def line_end(self, li):
        _, b = self.line_tok[li]
        return self.words[b - 1]["e"]

    def t(self, anchor):
        """anchor: int line (0-based) or (line, word) or float seconds offset tuple ('+', base, sec)."""
        if isinstance(anchor, (int, float)) and not isinstance(anchor, bool):
            return self.line_start(int(anchor))
        li, w = anchor[0], anchor[1]
        if isinstance(w, (int, float)) and not isinstance(w, bool):
            return self.line_start(li) + float(w)
        a, b = self.line_tok[li]
        key = sh._norm(w.split()[0])
        for k in range(a, b):
            if sh._norm(self.words[k]["w"]) == key:
                return self.words[k]["s"]
        return self.line_start(li)

    def find(self, text, start_line=0):
        """index of the first line at/after start_line that contains text"""
        for i in range(start_line, len(self.lines)):
            if text.lower() in self.lines[i].lower():
                return i
        raise KeyError(text)


# ------------------------------------------------------------ chrome
def window(w, h, title="", accent="lime", title_icon=None):
    img, d = canvas(w, h)
    rrect(d, (0, 0, w, h), 26, fill=(17, 23, 44, 255), outline=(44, 56, 98, 255), width=2)
    rrect(d, (0, 0, w, 64), 26, fill=(26, 34, 64, 255))
    d.rectangle([0, s(40), s(w), s(64)], fill=(26, 34, 64, 255))
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([s(24 + i * 30), s(22), s(42 + i * 30), s(40)], fill=col + (255,))
    win = done(img)
    if title:
        x = 130
        if title_icon:
            em = emoji_sprite(title_icon, 34)
            win.alpha_composite(em, (x, 32 - em.height // 2))
            x += 46
        ts = text_sprite(title, 28, "w", FONT_XB)
        win.alpha_composite(ts, (x, 32 - ts.height // 2))
    return win


def chip(txt, bg, fg="navy", size=34, pad=34, h=70, path=FONT_XB):
    ts = text_sprite(txt, size, fg, path)
    bw = ts.width + 2 * pad
    img, d = canvas(bw, h)
    rrect(d, (0, 0, bw, h), h / 2, fill=C(bg))
    out = done(img)
    out.alpha_composite(ts, ((bw - ts.width) // 2, (h - ts.height) // 2))
    return out


def fit(img, maxw):
    if img.width <= maxw:
        return img
    k = maxw / img.width
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)


# ------------------------------------------------------------ scenes
class Scene:
    def __init__(self, p, tl):
        self.p, self.tl = p, tl
        self.t0 = tl.t(p["at"])
        self.t1 = None

    def T(self, a):
        return self.tl.t(a)

    def draw(self, cv, t):
        pass


class HookText(Scene):
    """Big kinetic statements: lines [{"text", "at", "c", "size"}], optional emoji [{"e","at","x","y","size"}]."""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.items = []
        for ln in p["lines"]:
            sp = fit(text_sprite(ln["text"], ln.get("size", 120), ln.get("c", "w"), FONT_BLACK, stroke=6), 1700)
            self.items.append((sp, self.T(ln["at"]), ln))
        self.emojis = [(emoji_sprite(e["e"], e.get("size", 220)), self.T(e["at"]), e) for e in p.get("emoji", [])]

    def draw(self, cv, t):
        total = sum(sp.height for sp, _, _ in self.items) + 38 * (len(self.items) - 1)
        y = STAGE_CY + 40 - total / 2
        for sp, ta, ln in self.items:
            k, a = pop(t, ta, 0.2)
            if ln.get("strike_at") is not None and t >= self.T(ln["strike_at"]):
                pass
            paste(cv, sp, W / 2, y + sp.height / 2, k, a)
            if ln.get("strike_at") is not None:
                ts = self.T(ln["strike_at"])
                if t >= ts:
                    pr = ease_out_cubic((t - ts) / 0.25)
                    bar, d = canvas(sp.width + 40, 26)
                    rrect(d, (0, 0, (sp.width + 40) * pr, 26), 13, fill=C("red"))
                    paste(cv, done(bar), W / 2, y + sp.height / 2)
            y += sp.height + 38
        for em, ta, e in self.emojis:
            k, a = pop(t, ta, 0.28)
            paste(cv, em, W / 2 + e.get("x", 0), STAGE_CY + e.get("y", -260) + 8 * math.sin(t * 2.5), k, a)


class Chapter(Scene):
    """Full-screen chapter card: {"num": "APP 1", "title": "DESCRIPT", "e": "📝", "c": "lime"}"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.num = text_sprite(p["num"], 64, p.get("c", "lime"), FONT_BLACK)
        self.title = fit(text_sprite(p["title"], 150, "w", FONT_BLACK, stroke=6), 1650)
        self.em = emoji_sprite(p["e"], 230) if p.get("e") else None

    def draw(self, cv, t):
        dt = t - self.t0
        k, a = pop(t, self.t0, 0.25)
        slide = 120 * (1 - ease_out_cubic(dt / 0.35))
        paste(cv, self.num, W / 2 - slide, STAGE_CY - 120, 1, a)
        paste(cv, self.title, W / 2 + slide, STAGE_CY + 20, k, a)
        if self.em is not None:
            k2, a2 = pop(t, self.t0 + 0.12, 0.3)
            paste(cv, self.em, W / 2, STAGE_CY - 330 + 6 * math.sin(t * 3), k2, a2)


class Chat(Scene):
    """A chat window. {"title": "Claude", "user": "...", "user_at", "reply": "...", "reply_at",
    "apps": [{"name","e","at","done_at"}]}"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.win = window(1500, 760, p.get("title", "Claude"), title_icon=p.get("icon", "✳️"))
        self.apps = []
        for i, ap in enumerate(p.get("apps", [])):
            row, d = canvas(680, 74)
            rrect(d, (0, 0, 680, 74), 18, fill=(29, 39, 74, 255))
            r = done(row)
            em = emoji_sprite(ap.get("e", "🔌"), 44)
            r.alpha_composite(em, (18, 37 - em.height // 2))
            nm = fit(text_sprite(ap["name"], 30, "w", FONT_XB), 400)
            r.alpha_composite(nm, (80, 37 - nm.height // 2))
            self.apps.append((r, ap))
        self.b1 = chip("Connect", "lime", "navy", 24, 22, 46)
        self.b2 = chip("Connected ✓", "green", "navy", 24, 18, 46)

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.win, W / 2, STAGE_CY, k, a)
        if a < 0.9:
            return
        x0, y0 = W / 2 - 750, STAGE_CY - 380
        ut = self.T(self.p["user_at"]) if self.p.get("user") else None
        if ut is not None and t >= ut - 0.05:
            q = self.p["user"]
            n = int(len(q) * clamp((t - ut) / max(0.6, len(q) / 38)))
            txt = q[:n]
            lines = wrap(txt, 52)
            bub_h = 40 + 46 * max(1, len(lines))
            img, d = canvas(980, bub_h)
            rrect(d, (0, 0, 980, bub_h), 26, fill=(44, 56, 98, 255))
            bub = done(img)
            for i, ln in enumerate(lines):
                ts = text_sprite(ln, 30, "w", FONT_SEMI)
                bub.alpha_composite(ts, (30, 20 + i * 46))
            paste(cv, bub, x0 + 1500 - 40 - 490, y0 + 110 + bub_h / 2)
        rt = self.T(self.p["reply_at"]) if self.p.get("reply") else None
        if rt is not None and t >= rt:
            lines = wrap(self.p["reply"], 60)
            n = int(len(lines) * clamp((t - rt) / 1.0)) + 1
            for i, ln in enumerate(lines[:n]):
                ts = text_sprite(ln, 30, "w", FONT_SEMI)
                paste(cv, ts, x0 + 60 + ts.width / 2, y0 + 300 + i * 46)
            av, d = canvas(44, 44)
            d.ellipse([0, 0, s(44), s(44)], fill=C("orange"))
            paste(cv, done(av), x0 + 36, y0 + 300)
        for i, (row, ap) in enumerate(self.apps):
            at = self.T(ap["at"])
            k2, a2 = pop(t, at, 0.2)
            col, rr = i % 2, i // 2
            cx = x0 + 60 + 340 + col * 700
            cy = y0 + 420 + rr * 86
            paste(cv, row, cx, cy, k2, a2)
            if a2 > 0:
                b = self.b2 if ap.get("done_at") is not None and t >= self.T(ap["done_at"]) else self.b1
                paste(cv, b, cx + 340 - 20 - b.width / 2, cy, k2, a2)


def wrap(txt, n):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


class AppScene(Scene):
    """App window with feature rows: {"name","e","c","rows":[{"text","e","at"}], "demo": optional}"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.win = window(1500, 760, p["name"], title_icon=p.get("e"))
        self.big = {}
        self.rows = []
        for r in p["rows"]:
            img, d = canvas(800, 96)
            rrect(d, (0, 0, 800, 96), 22, fill=(29, 39, 74, 255))
            row = done(img)
            em = emoji_sprite(r.get("e", "✅"), 52)
            row.alpha_composite(em, (24, 48 - em.height // 2))
            ts = fit(text_sprite(r["text"], 36, "w", FONT_XB), 660)
            row.alpha_composite(ts, (100, 48 - ts.height // 2))
            self.rows.append((row, self.T(r["at"]), r))
        self.title = fit(text_sprite(p.get("headline", p["name"]), 58, p.get("c", "lime"), FONT_BLACK), 560)

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.win, W / 2, STAGE_CY, k, a)
        if a < 0.9:
            return
        x0, y0 = W / 2 - 750, STAGE_CY - 380
        cur = None
        for row, ta, r in self.rows:
            if t >= ta:
                cur = r
        em = cur.get("e") if cur else self.p.get("e", "✨")
        big = self.big.get(em)
        if big is None:
            big = self.big[em] = emoji_sprite(em, 300)
        last_t = max([ta for _, ta, _ in self.rows if ta <= t] or [self.t0])
        k3 = 0.6 + 0.4 * ease_out_back((t - last_t) / 0.3)
        paste(cv, big, x0 + 330, y0 + 360 + 10 * math.sin(t * 2.2), k3)
        paste(cv, self.title, x0 + 330, y0 + 620)
        n = len(self.rows)
        for i, (row, ta, r) in enumerate(self.rows):
            k2, a2 = pop(t, ta, 0.22)
            hl = 1.0 if (cur is r) else 0.92
            paste(cv, row, x0 + 1060, y0 + 400 - (n - 1) * 56 + i * 112, k2 * hl, a2 * (1 if cur is r else 0.75))


class Transcript(Scene):
    """Descript-style demo: paragraphs; one line gets struck and removed at strike_at."""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.win = window(1500, 760, "Descript", title_icon="📝")
        self.lines = p["lines"]

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.win, W / 2, STAGE_CY, k, a)
        if a < 0.9:
            return
        x0, y0 = W / 2 - 750, STAGE_CY - 380
        st = self.T(self.p["strike_at"])
        y = y0 + 120
        for i, ln in enumerate(self.lines):
            target = i == self.p["strike_line"]
            ts = text_sprite(ln, 40, "w" if not target else "yellow", FONT_SEMI)
            hgt = ts.height + 26
            if target and t >= st:
                pr = clamp((t - st) / 0.5)
                if pr < 1:
                    paste(cv, ts, x0 + 80 + ts.width / 2, y + hgt / 2, 1, 1 - max(0, pr - 0.5) * 2)
                    bar, d = canvas(ts.width + 10, 10)
                    rrect(d, (0, 0, (ts.width + 10) * min(1, pr * 2), 10), 5, fill=C("red"))
                    paste(cv, done(bar), x0 + 80 + ts.width / 2, y + hgt / 2)
                y += hgt * (1 - ease_in_out(clamp((t - st - 0.5) / 0.4)))
                continue
            paste(cv, ts, x0 + 80 + ts.width / 2, y + hgt / 2)
            y += hgt
        # waveform strip
        layer, d = canvas(1340, 120)
        for i in range(120):
            hh = 10 + 90 * abs(math.sin(i * 0.7) * math.sin(i * 0.23 + 1))
            col = C("lime") if (i < 120 * clamp((t - self.t0) / 6)) else (70, 84, 130, 255)
            d.rounded_rectangle([s(i * 11.1), s(60 - hh / 2), s(i * 11.1 + 6), s(60 + hh / 2)], s(3), fill=col)
        paste(cv, done(layer), W / 2, y0 + 660)


class Stats(Scene):
    """Keyword stats rows: [{"kw","num","label","comp","at"}]"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.win = window(1500, 760, "vidIQ keyword research", title_icon="📈")
        self.rows = p["rows"]
        self.kws = [fit(text_sprite(r["kw"], 38, "w", FONT_XB), 620) for r in self.rows]

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        paste(cv, self.win, W / 2, STAGE_CY, k, a)
        if a < 0.9:
            return
        x0, y0 = W / 2 - 750, STAGE_CY - 380
        hdr = [("KEYWORD", 80), ("SEARCHES / MONTH", 760), ("COMPETITION", 1140)]
        for txt, x in hdr:
            ts = text_sprite(txt, 24, "grey", FONT_XB)
            paste(cv, ts, x0 + x + ts.width / 2, y0 + 110)
        for i, r in enumerate(self.rows):
            ta = self.T(r["at"])
            k2, a2 = pop(t, ta, 0.22)
            if a2 <= 0:
                continue
            y = y0 + 190 + i * 150
            img, d = canvas(1400, 120)
            rrect(d, (0, 0, 1400, 120), 24, fill=(29, 39, 74, 255))
            paste(cv, done(img), W / 2, y + 20, k2, a2)
            paste(cv, self.kws[i], x0 + 80 + self.kws[i].width / 2, y + 20, k2, a2)
            pr = ease_out_cubic((t - ta) / 1.2)
            val = r["num"] * pr
            label = f"{val / 1000:,.0f}K" if r["num"] >= 1000 else f"{val:.0f}"
            ns = text_sprite(label, 52, "lime", FONT_BLACK)
            paste(cv, ns, x0 + 760 + ns.width / 2, y + 20, k2, a2)
            if r.get("comp") is not None:
                cb, d = canvas(260, 26)
                rrect(d, (0, 0, 260, 26), 13, fill=(50, 62, 104, 255))
                rrect(d, (0, 0, 260 * r["comp"] / 100 * pr, 26), 13, fill=C("green"))
                paste(cv, done(cb), x0 + 1140 + 130, y + 20, k2, a2)
                cs = text_sprite(f"{int(r['comp'] * pr)}/100", 30, "w", FONT_XB)
                paste(cv, cs, x0 + 1140 + 300 + cs.width / 2 - 30, y + 20, k2, a2)
            if r.get("tag") and t >= self.T(r.get("tag_at", r["at"])):
                tg = chip(r["tag"], "orange", "navy", 26, 20, 48)
                k3, a3 = pop(t, self.T(r.get("tag_at", r["at"])), 0.2)
                paste(cv, tg, x0 + 760 + 330, y + 20, k3, a3)


class BigStat(Scene):
    """{"big": "2.3M", "label": "VIEWS", "sub": "...", "e": "🔥", "c": "lime", "items": optional [{"text","at"}]}"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.big = fit(text_sprite(p["big"], 260, p.get("c", "lime"), FONT_BLACK, stroke=6), 1500)
        self.label = text_sprite(p.get("label", ""), 64, "w", FONT_BLACK) if p.get("label") else None
        self.sub = fit(text_sprite(p["sub"], 40, "grey", FONT_XB), 1500) if p.get("sub") else None
        self.em = emoji_sprite(p["e"], 170) if p.get("e") else None

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.3)
        paste(cv, self.big, W / 2, STAGE_CY - 20, k, a)
        if self.label is not None:
            k2, a2 = pop(t, self.t0 + 0.2, 0.2)
            paste(cv, self.label, W / 2, STAGE_CY + self.big.height / 2 + 30, k2, a2)
        if self.sub is not None:
            k3, a3 = pop(t, self.T(self.p.get("sub_at", self.p["at"])) + 0.3, 0.2)
            paste(cv, self.sub, W / 2, STAGE_CY + self.big.height / 2 + 110, k3, a3)
        if self.em is not None:
            k4, a4 = pop(t, self.t0 + 0.1, 0.3)
            paste(cv, self.em, W / 2 + self.big.width / 2 + 110, STAGE_CY - 120 + 8 * math.sin(t * 3), k4, a4)


class Flow(Scene):
    """Pipeline of steps lighting up: steps [{"text","e","at"}] (up to 8, two rows)."""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.steps = []
        for i, st in enumerate(p["steps"]):
            img, d = canvas(380, 230)
            rrect(d, (0, 0, 380, 230), 30, fill=(24, 32, 62, 255), outline=(60, 74, 120, 255), width=3)
            card = done(img)
            em = emoji_sprite(st["e"], 80)
            card.alpha_composite(em, ((380 - em.width) // 2, 26))
            ts = fit(text_sprite(st["text"], 30, "w", FONT_XB), 340)
            card.alpha_composite(ts, ((380 - ts.width) // 2, 140))
            num = chip(str(i + 1), "lime", "navy", 28, 18, 52)
            card.alpha_composite(num, (16, 16))
            img, d = canvas(380, 230)
            rrect(d, (0, 0, 380, 230), 30, outline=C("lime"), width=6)
            self.steps.append((card, done(img), st))

    def draw(self, cv, t):
        n = len(self.steps)
        per = math.ceil(n / 2)
        for i, (card, ring, st) in enumerate(self.steps):
            ta = self.T(st["at"])
            row, col = i // per, i % per
            cnt = per if row == 0 else n - per
            x = W / 2 - (cnt - 1) * 210 + col * 420
            y = STAGE_CY - 150 + row * 290
            k, a = pop(t, ta, 0.25)
            if a <= 0:
                a = 0.25
                k = 1
            paste(cv, card, x, y, k, a)
            nxt = self.T(self.steps[i + 1][2]["at"]) if i + 1 < n else 1e9
            if ta <= t < nxt:
                paste(cv, ring, x, y, k)


class Cards(Scene):
    """Numbered cards popping in: cards [{"title","text","e","at","c"}]"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        self.cards = []
        for i, cd in enumerate(p["cards"]):
            img, d = canvas(520, 470)
            rrect(d, (0, 0, 520, 470), 34, fill=(24, 32, 62, 255), outline=C(cd.get("c", "orange")), width=4)
            card = done(img)
            em = emoji_sprite(cd["e"], 120)
            card.alpha_composite(em, ((520 - em.width) // 2, 40))
            ts = fit(text_sprite(cd["title"], 44, cd.get("c", "orange"), FONT_BLACK), 470)
            card.alpha_composite(ts, ((520 - ts.width) // 2, 200))
            for j, ln in enumerate(wrap(cd.get("text", ""), 24)[:4]):
                tx = text_sprite(ln, 30, "w", FONT_SEMI)
                card.alpha_composite(tx, ((520 - tx.width) // 2, 280 + j * 42))
            self.cards.append((card, cd))

    def draw(self, cv, t):
        n = len(self.cards)
        for i, (card, cd) in enumerate(self.cards):
            k, a = pop(t, self.T(cd["at"]), 0.25)
            paste(cv, card, W / 2 - (n - 1) * 290 + i * 580, STAGE_CY, k, a)


class Resize(Scene):
    """Aspect ratio morph demo: {"steps": [{"ratio": [16,9], "label": "YouTube", "at"}]}"""

    def draw(self, cv, t):
        steps = self.p["steps"]
        cur, prev, ta = steps[0], steps[0], self.T(steps[0]["at"])
        for i, st in enumerate(steps):
            if t >= self.T(st["at"]):
                prev, cur, ta = (steps[i - 1] if i else st), st, self.T(st["at"])
        pr = ease_in_out((t - ta) / 0.5)
        def box(r):
            w, h = r
            kk = min(900 / w, 680 / h)
            return w * kk, h * kk
        w0, h0 = box(prev["ratio"])
        w1, h1 = box(cur["ratio"])
        bw, bh = w0 + (w1 - w0) * pr, h0 + (h1 - h0) * pr
        img, d = canvas(int(bw) + 10, int(bh) + 10)
        rrect(d, (5, 5, bw + 5, bh + 5), 24, fill=(30, 42, 80, 255), outline=C("lime"), width=6)
        paste(cv, done(img), W / 2, STAGE_CY)
        lb = text_sprite(f"{cur['ratio'][0]}:{cur['ratio'][1]}  {cur['label']}", 56, "w", FONT_BLACK)
        paste(cv, lb, W / 2, STAGE_CY)
        em = emoji_sprite("🎬", 120)
        paste(cv, em, W / 2, STAGE_CY - 110)


class Subscribe(Scene):
    """CTA: {"name": "TM_Diamond", "tap_at", "next": "optional next video title", "next_at"}"""

    def __init__(self, p, tl):
        super().__init__(p, tl)
        img, d = canvas(980, 210)
        rrect(d, (0, 0, 980, 210), 44, fill=(24, 32, 62, 255), outline=(60, 74, 120, 255), width=3)
        d.ellipse([s(36), s(40), s(166), s(170)], fill=C("lime"))
        self.card = done(img)
        tm = text_sprite("TM", 54, "navy", FONT_BLACK)
        self.card.alpha_composite(tm, (101 - tm.width // 2, 105 - tm.height // 2))
        nm = text_sprite(p.get("name", "TM_Diamond"), 52, "w", FONT_XB)
        self.card.alpha_composite(nm, (196, 105 - nm.height // 2))
        self.b1 = chip("SUBSCRIBE", "ytred", "w", 34, 34, 80)
        self.b2 = chip("SUBSCRIBED", "card2", "w", 34, 30, 80)
        self.bell = emoji_sprite("🔔", 90)
        self.next = None
        if p.get("next"):
            img, d = canvas(1100, 150)
            rrect(d, (0, 0, 1100, 150), 30, fill=(24, 32, 62, 255), outline=C("lime"), width=4)
            nc = done(img)
            lab = text_sprite("NEXT VIDEO", 26, "lime", FONT_BLACK)
            nc.alpha_composite(lab, (40, 26))
            tt = fit(text_sprite(p["next"], 40, "w", FONT_XB), 1020)
            nc.alpha_composite(tt, (40, 70))
            self.next = nc

    def draw(self, cv, t):
        k, a = pop(t, self.t0, 0.25)
        y = STAGE_CY - 120
        paste(cv, self.card, W / 2, y, k, a)
        tap = self.T(self.p["tap_at"])
        b = self.b2 if t >= tap else self.b1
        press = 1 - 0.1 * clamp(1 - abs(t - tap) / 0.08)
        bx = W / 2 + 490 - 40 - b.width / 2
        paste(cv, b, bx, y, k * press, a)
        if t >= tap:
            kb, ab = pop(t, tap + 0.25, 0.25)
            wob = math.sin((t - tap) * 18) * 12 * clamp(1 - (t - tap) / 1.2)
            paste(cv, self.bell.rotate(wob, resample=Image.BICUBIC), bx + 220, y, kb, ab)
        if self.next is not None:
            k2, a2 = pop(t, self.T(self.p["next_at"]), 0.25)
            paste(cv, self.next, W / 2, y + 270, k2, a2)


SCENES = {"hook": HookText, "chapter": Chapter, "chat": Chat, "app": AppScene, "transcript": Transcript,
          "stats": Stats, "bigstat": BigStat, "flow": Flow, "cards": Cards, "resize": Resize, "subscribe": Subscribe}


# ------------------------------------------------------------ background, progress, captions
class Background:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        base = np.zeros((H, W, 3), np.float32)
        base[:] = (9, 13, 28)
        d = np.sqrt((xx - W / 2) ** 2 + ((yy - STAGE_CY) * 1.6) ** 2)
        self.glow = (np.clip(1 - d / 1100, 0, 1) ** 2)[..., None]
        vign = np.clip(1 - np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 0.9, 0.5, 1)[..., None]
        grid = np.zeros((H, W), np.float32)
        grid[::60, :] = 1
        grid[:, ::60] = 1
        self.base = base + grid[..., None] * np.array([18, 24, 44], np.float32) * 0.5
        self.vign = vign
        self.cache = {}

    def frame(self, t):
        pulse = round(0.10 + 0.03 * math.sin(t * 1.6), 3)
        arr = self.cache.get(pulse)
        if arr is None:
            arr = np.clip((self.base + self.glow * np.array((200, 255, 46), np.float32) * pulse) * self.vign, 0, 255).astype(np.uint8)
            if len(self.cache) > 70:
                self.cache.clear()
            self.cache[pulse] = arr
        return Image.fromarray(arr, "RGB").convert("RGBA")


def caption_groups(tl, hl, max_words=7, max_chars=40):
    hl = {h.lower() for h in hl}
    groups = []
    for li, (a, b) in enumerate(tl.line_tok):
        ws = tl.words[a:b]
        cur = []
        for w in ws:
            cur.append(w)
            txt = " ".join(x["w"] for x in cur)
            if len(cur) >= max_words or len(txt) >= max_chars or w["w"].endswith((".", "?", "!", ",")):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
    out = []
    for g in groups:
        out.append({"t": g[0]["s"], "end": g[-1]["e"] + 0.25, "words": [(w["w"], w["s"], _hl(w["w"], hl)) for w in g]})
    for i in range(len(out) - 1):
        out[i]["end"] = min(out[i]["end"], out[i + 1]["t"])
    return out


def _hl(w, hl):
    k = sh._norm(w)
    if k == "claude":
        return "orange"
    if k in hl:
        return "lime"
    return "w"


_capcache = {}


def draw_caption(cv, t, groups, idx):
    while idx[0] + 1 < len(groups) and groups[idx[0] + 1]["t"] <= t:
        idx[0] += 1
    g = groups[idx[0]]
    if not (g["t"] <= t < g["end"]):
        return
    key = id(g)
    sprites = _capcache.get(key)
    if sprites is None:
        sprites = [text_sprite(w, 54, c if c != "w" else "w", FONT_BLACK, stroke=5) for w, _, c in g["words"]]
        dim = [text_sprite(w, 54, (200, 205, 220), FONT_BLACK, stroke=5) for w, _, c in g["words"]]
        if len(_capcache) > 400:
            _capcache.clear()
        _capcache[key] = sprites = (sprites, dim)
    sp, dim = sprites
    gap = 16
    total = sum(x.width for x in sp) + gap * (len(sp) - 1)
    kk = min(1.0, CAP_MAXW / max(1, total))
    x = W / 2 - total * kk / 2
    for (w, ws, c), a_sp, d_sp in zip(g["words"], sp, dim):
        img = a_sp if (t >= ws and c != "w") else (a_sp if t >= ws else d_sp)
        k = 1.0
        if 0 <= t - ws < 0.12 and c != "w":
            k = 1.0 + 0.12 * (1 - (t - ws) / 0.12)
        paste(cv, img, x + img.width * kk / 2, CAP_Y, kk * k)
        x += (img.width + gap) * kk


class Progress:
    """9-app tracker along the top during the app sections."""

    def __init__(self, cfg, tl):
        self.cfg = cfg
        self.t0 = tl.t(cfg["show_at"])
        self.t1 = tl.t(cfg["hide_at"])
        self.marks = [tl.t(a) for a in cfg["apps_at"]]
        self.tease = cfg.get("tease", 8)

    def draw(self, cv, t):
        if not (self.t0 <= t < self.t1):
            return
        n = len(self.marks)
        cur = sum(1 for m in self.marks if t >= m)
        a = clamp((t - self.t0) / 0.4) * clamp((self.t1 - t) / 0.4)
        for i in range(n):
            x = W / 2 - (n - 1) * 46 + i * 92
            done_ = i < cur
            img, d = canvas(64, 64)
            if done_:
                d.ellipse([0, 0, s(64), s(64)], fill=C("lime") if i == cur - 1 else (90, 110, 60, 255))
            else:
                d.ellipse([s(3), s(3), s(61), s(61)], outline=(80, 94, 140, 255), width=s(4))
            sp = done(img)
            num = text_sprite(str(i + 1), 28, "navy" if done_ else "grey", FONT_BLACK)
            sp.alpha_composite(num, (32 - num.width // 2, 32 - num.height // 2))
            k = 1.0
            if i + 1 == self.tease and not done_:
                k = 1.0 + 0.12 * (0.5 + 0.5 * math.sin(t * 5))
                star = emoji_sprite("⭐", 30)
                paste(cv, star, x + 26, 34, 1, a)
            paste(cv, sp, x, 58, k, a)


# ------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, spec, tl):
        self.spec, self.tl = spec, tl
        self.bg = Background()
        self.scenes = [SCENES[p["type"]](p, tl) for p in spec["scenes"]]
        self.scenes.sort(key=lambda sc: sc.t0)
        for i, sc in enumerate(self.scenes):
            sc.t1 = self.scenes[i + 1].t0 if i + 1 < len(self.scenes) else spec["duration"]
        self.cuts = [sc.t0 for sc in self.scenes]
        self.caps = caption_groups(tl, spec.get("highlight", []))
        self.cap_idx = [0]
        self.progress = Progress(spec["progress"], tl) if spec.get("progress") else None
        self.bass = [e["t"] for e in spec["sfx_resolved"] if e["type"] == "bass"]
        self.si = 0

    def frame(self, t):
        cv = self.bg.frame(t)
        while self.si + 1 < len(self.scenes) and self.scenes[self.si + 1].t0 <= t:
            self.si += 1
        sc = self.scenes[self.si]
        if sc.t0 <= t:
            sc.draw(cv, t)
        if self.progress:
            self.progress.draw(cv, t)
        if t < self.caps[self.cap_idx[0]]["t"]:
            self.cap_idx[0] = 0
        draw_caption(cv, t, self.caps, self.cap_idx)
        dt = t - sc.t0
        z = 1.0 + 0.045 * (1 - ease_out_cubic(dt / 0.35)) + 0.03 * clamp(dt / max(2, sc.t1 - sc.t0))
        sx = sy = 0.0
        for b in self.bass:
            if 0 <= t - b < 0.3:
                amp = 12 * (1 - (t - b) / 0.3)
                sx += amp * math.sin(t * 90)
                sy += amp * math.cos(t * 77)
        if sx or sy:
            z = max(z, 1.03)
        img = cv.convert("RGB")
        if z > 1.001:
            cw, ch = W / z, H / z
            x0 = clamp((W - cw) / 2 - sx, 0, W - cw)
            y0 = clamp((H - ch) / 2 - sy, 0, H - ch)
            img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        fl = clamp(1 - dt / 0.08) * 0.10
        if fl > 0.005:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), fl)
        return img


def load_build(path):
    spec_mod = importlib.util.spec_from_file_location("build", path)
    mod = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(mod)
    return mod


def build_audio(spec, tl, dur, out_wav):
    rng = np.random.default_rng(11)
    n = int(dur * SR)
    narr = np.zeros(n)
    v = sh.read_audio(spec["narration"])
    v = v / (np.max(np.abs(v)) + 1e-9) * 0.92
    narr[: min(n, len(v))] = v[:n]
    rms_v = np.sqrt(np.mean(narr[np.abs(narr) > 0.02] ** 2))
    # OWNER RULE (permanent, 2026-11-05): no background music, beats, ambience or sound beds - ever.
    mus = np.zeros(n)
    fx = np.zeros(n)
    for ev in spec["sfx_resolved"]:
        y = sh.sfx(ev["type"], rng) * ev.get("vol", 1.0)
        j = int(ev["t"] * SR)
        if 0 <= j < n:
            fx[j:j + len(y)] += y[: n - j]
    fx *= rms_v * spec.get("sfx_gain", 1.0)
    mix = narr + mus + fx
    fade = int(1.5 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1) * 0.8
    pcm = (np.clip(mix, -1, 1) * 32000).astype(np.int16)
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())


def main():
    build_path, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    mod = load_build(build_path)
    spec = mod.SPEC
    tl = Timeline(spec["script"], spec["words"])
    spec = mod.build(tl) if hasattr(mod, "build") else spec
    spec["duration"] = spec.get("duration") or tl.duration + 1.5
    res = []
    for ev in spec.get("sfx", []):
        e = dict(ev)
        e["t"] = tl.t(ev["at"]) + ev.get("dt", 0)
        res.append(e)
    r0 = Renderer(dict(spec, sfx_resolved=res), tl)
    for sc in r0.scenes:  # automatic whoosh at every scene change
        res.append({"t": sc.t0, "type": "whoosh", "vol": 0.55})
    spec["sfx_resolved"] = res
    r = Renderer(spec, tl)
    if "--preview" in args:
        times = [float(x) for x in args[args.index("--preview") + 1].split(",")]
        frames = []
        for tt in times:
            r.si, r.cap_idx = 0, [0]
            frames.append(r.frame(tt))
        cols = min(4, len(frames))
        rows = math.ceil(len(frames) / cols)
        tw, th = 480, 270
        sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), (0, 0, 0))
        dd = ImageDraw.Draw(sheet)
        for i, (fr, tt) in enumerate(zip(frames, times)):
            x, y = (i % cols) * tw, (i // cols) * (th + 26)
            sheet.paste(fr.resize((tw, th), Image.LANCZOS), (x, y + 26))
            dd.text((x + 6, y + 3), f"{tt:.1f}s", fill=(255, 255, 255), font=font(FONT_BOLD, 18))
        sheet.save(out)
        return
    dur = spec["duration"]
    wav = out + ".wav"
    build_audio(spec, tl, dur, wav)
    vb = spec.get("max_video_kbps", 1100)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-maxrate", f"{vb}k",
           "-bufsize", f"{vb * 2}k", "-pix_fmt", "yuv420p", "-g", "90", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nfr = int(round(dur * FPS))
    for i in range(nfr):
        p.stdin.write(r.frame(i / FPS).tobytes())
        if i % 900 == 0:
            print(f"frame {i}/{nfr}", flush=True)
    p.stdin.close()
    p.wait()
    os.remove(wav)
    print("size_bytes", os.path.getsize(out))


if __name__ == "__main__":
    main()
