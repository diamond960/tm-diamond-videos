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
  "clicks": [t, ...],                                   # ripple + click sound at the cursor
  "keys":  [[t, ["Win", "R"], dur], ...],               # keycap overlay + key sounds
  "typing": [[t0, t1, n], ...],                         # n key sounds spread over t0..t1
  "circles": [[t, [x, y, w, h], dur], ...],             # red marker ellipse around a screen rect
  "arrows": [[t, [x, y], dur, "from_left"|"from_right"|"from_top"], ...],
  "highlight": ["words", ...],                          # caption words shown in yellow
  "sfx": [[t, "pop"|"ding"|"whoosh"|"click"|"key"], ...],
  "follow": t,                                           # follow card from t to the end
  "handle": "TM_Diamond"
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
        drift = 1.0 - min(0.06, 0.012 * max(0.0, t - last_t))
        h *= drift
        return self.clamp(cx, cy, h)

    def clamp(self, cx, cy, h):
        h = min(h, self.sh)
        w = h * W / H
        if w > self.sw:
            w = self.sw
            h = w * H / W
        cx = min(max(cx, w / 2), self.sw - w / 2)
        cy = min(max(cy, h / 2), self.sh - h / 2)
        return cx, cy, h

    @staticmethod
    def to_frame(cam, x, y):
        cx, cy, h = cam
        s = H / h
        return (x - cx) * s + W / 2, (y - cy) * s + H / 2, s


def render_screen(img, cam):
    cx, cy, h = cam
    w = h * W / H
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return img.resize((W, H), Image.LANCZOS, box=box)


# ------------------------------------------------------------------ overlays
def draw_text_stroke(d, xy, text, f, fill, stroke=7, sfill=(0, 0, 0), anchor="la"):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)


def caption_layer(words, t, highlight):
    """Word-by-word captions in groups of up to 3 words: white, black stroke, current word yellow."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not words:
        return layer
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        end_sent = w["w"].rstrip().endswith((".", "?", "!", ","))
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
    f = font(F_BLACK, 92)
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
    y = int(H * 0.17)
    for ln in lines:
        total = sum(wd for _, wd in ln) + space * (len(ln) - 1)
        x = (W - total) / 2
        for (txt, col, shown, ws), wd in ln:
            if shown:
                pop = ease_out_back((t - ws + 0.04) / 0.16)
                size = int(92 * (0.82 + 0.18 * pop))
                ff = font(F_BLACK, size)
                draw_text_stroke(d, (x + wd / 2, y + 50), txt, ff, col, stroke=9, anchor="mm")
            x += wd + space
        y += 112
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


ARROW = [(0, 0), (0, 34), (8, 26), (14, 40), (19, 38), (13, 24), (24, 24)]


def cursor_layer(spec, t, cam):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    path = spec.get("cursor")
    if not path:
        return layer
    if t < path[0][0]:
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
    y0 = H * 0.64 + (1 - a) * 120
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
        first = next(iter(self.images.values()))
        self.sw, self.sh = first.size
        self.cam = Camera(spec["cam"], self.sw, self.sh)
        self.words = json.load(open(os.path.join(base, spec["words"])))["words"] if spec.get("words") else []
        self.hl = set(w.lower() for w in spec.get("highlight", []))
        self.handle_l = handle_layer(spec.get("handle", "TM_Diamond"))

    def shot_at(self, t):
        cur = self.spec["shots"][0][1]
        for st, f in self.spec["shots"]:
            if t >= st:
                cur = f
        return self.images[cur]

    def frame(self, t):
        cam = self.cam.at(t)
        # motion blur while the camera moves fast
        c2 = self.cam.at(t + 1 / FPS)
        speed = abs(c2[0] - cam[0]) + abs(c2[1] - cam[1]) + abs(c2[2] - cam[2])
        img = self.shot_at(t)
        if speed > 18:
            fr = [np.asarray(render_screen(img, self.cam.at(t + k / (3 * FPS))), dtype=np.float32) for k in range(3)]
            base = Image.fromarray(np.clip(sum(fr) / 3, 0, 255).astype(np.uint8))
        else:
            base = render_screen(img, cam)
        base = base.convert("RGBA")
        # soft top/bottom shading so captions read on any screen (whole frame stays the real screen)
        base.alpha_composite(self.shade)
        base.alpha_composite(callouts_layer(self.spec, t, cam))
        base.alpha_composite(cursor_layer(self.spec, t, cam))
        base.alpha_composite(keycaps_layer(self.spec.get("keys", []), t))
        base.alpha_composite(caption_layer(self.words, t, self.hl))
        base.alpha_composite(follow_layer(t, self.spec.get("follow"), self.spec.get("handle", "TM_Diamond")))
        base.alpha_composite(self.handle_l)
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
    "click": (["click_002", "mouseclick1", "click_001"], 0.55),
    "key": (["switch1", "switch2", "switch3", "switch5", "switch7", "click1", "click2"], 0.22),
    "pop": (["drop_002", "pluck_001", "drop_001"], 0.35),
    "ding": (["confirmation_002", "confirmation_001"], 0.45),
    "open": (["maximize_006", "maximize_008", "open_002"], 0.30),
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
            events.append([kt + 0.25 + 0.12 * i, "key"])
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
    base = os.getcwd()
    cut = Cut(spec, base)
    dur = spec["duration"]
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        thumbs = []
        for t in ts:
            fr = cut.frame(t).resize((270, 480))
            ImageDraw.Draw(fr).text((8, 6), f"{t:.2f}s", fill=(255, 255, 0), font=font(F_BOLD, 26), stroke_width=3, stroke_fill=(0, 0, 0))
            thumbs.append(fr)
        cols = min(6, len(thumbs))
        rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (cols * 274, rows * 484), (0, 0, 0))
        for i, th in enumerate(thumbs):
            sheet.paste(th, ((i % cols) * 274, (i // cols) * 484))
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
