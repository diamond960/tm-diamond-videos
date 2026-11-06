"""TM Diamond "studio" look for vertical videos (the permanent house style from 2026-11-06).

Beige graph paper, a progressive caption at the top (dark sans words, keywords in red serif italic),
the content (UI recreations, cards, keys...) in the middle band, and the cartoon presenter at the
bottom (lower-right by default). Paper-cut wipes between scenes, red marker circles/arrows,
gentle camera punch-ins. NO music: narration + synced sound effects only.

Used by engine/shorts.py when the spec has "style": "studio". Spec additions:
  "style": "studio",
  "series": "windows fix",                  # small label top-right (optional)
  "presenter": {"side": "right",            # right | left (mirrored) | none
                "poses": [[0.0, "talk"], [3.2, "idea"], ...]},   # optional; auto when missing
  "captions": {"words": "voice.words.json", "highlight": [...], "underline": [...]}
Visuals keep their usual types; they are drawn into the content band (scaled by "content_scale",
default 0.72, or per visual "scale").
Poses: talk, idea, point, think, thumbs, shrug, shocked, phone (presenter/poses/*.png).
"""
import json
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import shorts as sh

W, H = sh.W, sh.H
HERE = os.path.dirname(os.path.abspath(__file__))
POSE_DIR = os.path.join(HERE, "..", "presenter", "poses")
SERIF_IT = os.path.join(HERE, "fonts", "InstrumentSerif-Italic.ttf")
MONO = os.path.join(HERE, "fonts", "JetBrainsMono.ttf")
INK = (28, 27, 30)
RED = (214, 36, 36)
PAPER = (239, 234, 224)
CAP_X, CAP_Y, CAP_W = 72, 196, 936
CONTENT_CY = 842          # centre of the content band (y 500-1180)
PRES_H = 770              # presenter height on screen
TYPE_SCALE = {"winui": 0.92, "note": 0.9, "keys": 1.25, "follow": 1.15, "emoji": 0.8, "bigtext": 0.8}
POSES = ["talk", "idea", "point", "think", "thumbs", "shrug", "shocked", "phone"]

sh.WIN["arrow"] = RED     # studio arrows are red marker, like the circles
try:
    BRAND = json.load(open(os.path.join(HERE, "brand.json")))
except Exception:
    BRAND = {}
PRESENTER_OK = bool(BRAND.get("presenter_approved"))


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- paper
class StudioPaper:
    """Clean beige paper with a faint graph grid and soft grain; drifts slowly (parallax base layer)."""

    def __init__(self, seed=5):
        rnd = np.random.default_rng(seed)
        PW, PH = W + 96, H + 96
        base = np.empty((PH, PW, 3), np.float32)
        base[:] = PAPER
        yy, xx = np.mgrid[0:PH, 0:PW]
        minor = ((yy % 36) == 0) | ((xx % 36) == 0)
        major = ((yy % 180) == 0) | ((xx % 180) == 0)
        ink = np.array([120, 104, 80], np.float32)
        for m, a in ((minor, 0.07), (major, 0.08)):
            base[m] = base[m] * (1 - a) + ink * a
        noise = Image.fromarray((rnd.random((PH // 3, PW // 3)) * 255).astype(np.uint8), "L")
        noise = np.asarray(noise.resize((PW, PH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(18)), np.float32)
        base *= (1 + (noise - noise.mean()) / 255 * 0.10)[..., None]
        base += rnd.normal(0, 1.7, (PH, PW, 1)).astype(np.float32)
        vign = np.clip(1.05 - np.sqrt(((xx - PW / 2) / PW) ** 2 + ((yy - PH / 2) / PH) ** 2) * 0.32, 0.86, 1.0)
        base *= vign[..., None]
        self.paper = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    def frame(self, t):
        ox = 48 + 30 * math.sin(t * 0.11)
        oy = 48 + 34 * math.sin(t * 0.08 + 1.3)
        return self.paper.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))


@lru_cache(maxsize=4)
def torn_panel(seed=1):
    """A sheet of paper with torn left/right edges, used for the paper-cut wipe (content band height)."""
    ph, pw = 760, 1300
    r = random.Random(seed)
    img = Image.new("RGBA", (pw + 80, ph + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    left = [(40 + r.uniform(0, 26), 40 + y) for y in range(0, ph + 1, 22)]
    right = [(40 + pw - r.uniform(0, 26), 40 + y) for y in range(ph, -1, -22)]
    poly = left + right
    sh_ = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh_).polygon([(x + 10, y + 14) for x, y in poly], fill=(60, 45, 20, 70))
    img.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(12)))
    d.polygon(poly, fill=(247, 243, 235, 255))
    for x in range(40, pw + 40, 36):
        d.line([(x, 46), (x, ph + 34)], fill=(232, 226, 214, 255), width=1)
    for y in range(40, ph + 40, 36):
        d.line([(66, y), (pw + 14, y)], fill=(232, 226, 214, 255), width=1)
    return img


# ---------------------------------------------------------------- captions
@lru_cache(maxsize=1024)
def word_sprite(word, key):
    if key:
        f = font(SERIF_IT, 84)
        col = RED
    else:
        f = font(sh.FONT_BOLD, 62)
        col = INK
    bb = f.getbbox(word)
    im = Image.new("RGBA", (bb[2] + 6, 120), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 92), word, font=f, fill=col + (255,), anchor="ls")
    return im


def build_caption_groups(cfg, base):
    data = json.load(open(os.path.join(base, cfg["words"])))
    if cfg.get("text") and not data.get("text"):
        data["text"] = cfg["text"]
    words = sh.aligned_words(data)
    hl = {w.lower() for w in cfg.get("highlight", [])}
    ul = {w.lower() for w in cfg.get("underline", [])}
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        raw = w["w"].rstrip()
        end = raw.endswith((".", "?", "!", "…"))
        soft = raw.endswith((",", ":", ";")) and len(cur) >= 6
        if end or soft or len(cur) >= 11:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        laid, x, y = [], CAP_X, CAP_Y
        for w in g:
            txt = w["w"].replace("...", "").replace("…", "")
            k = txt.lower().strip(".,!?\"':;")
            key = k in hl
            sp = word_sprite(txt, key)
            space = 15
            if x + sp.width > CAP_X + CAP_W and x > CAP_X:
                x, y = CAP_X, y + 84
            laid.append({"sp": sp, "x": x, "y": y, "s": w["s"], "key": key, "ul": k in ul})
            x += sp.width + space
        out.append({"t": g[0]["s"], "words": laid, "end_word": g[-1]["e"]})
    for i, g in enumerate(out):
        g["t1"] = out[i + 1]["t"] if i + 1 < len(out) else 1e9
    return out, words


def draw_studio_captions(cv, t, groups):
    g = None
    for gr in groups:
        if gr["t"] - 0.05 <= t < gr["t1"]:
            g = gr
    if g is None:
        return
    layer = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for w in g["words"]:
        dt = t - w["s"]
        if dt < -0.02:
            continue
        p = sh.clamp(dt / 0.16)
        e = sh.ease_out_cubic(p)
        sp = w["sp"]
        if w["key"]:
            k = 0.82 + 0.18 * sh.ease_out_back(p, 2.2)
            im = sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.BICUBIC) if k != 1 else sp
            ox, oy = (sp.width - im.width) / 2, (sp.height - im.height) * 0.7
        else:
            im, ox, oy = sp, 0, 12 * (1 - e)
        if p < 1:
            im = sh.with_alpha(im, e)
        layer.alpha_composite(im, (int(w["x"] + ox), int(w["y"] - 20 + oy)))
        if w["ul"] and dt > 0.2:
            q = sh.clamp((dt - 0.2) / 0.3)
            x0, x1 = w["x"] + 2, w["x"] + 2 + (sp.width - 8) * sh.ease_out_cubic(q)
            yb = w["y"] + 86
            pts = [(x0 + (x1 - x0) * i / 20, yb + 4 * math.sin(i * 0.9)) for i in range(21)]
            d.line(pts, fill=RED + (235,), width=7, joint="curve")
    # exit: blur + fade in the last 0.18 s before the next sentence
    rem = g["t1"] - t
    if rem < 0.18:
        q = 1 - rem / 0.18
        layer = layer.filter(ImageFilter.GaussianBlur(10 * q))
        layer = sh.with_alpha(layer, 1 - q)
    cv.alpha_composite(layer, (0, 0))


def draw_header(cv, series):
    d = ImageDraw.Draw(cv)
    f = font(MONO, 28)
    d.text((CAP_X, 112), "// tm_diamond", font=f, fill=(128, 118, 104, 255), anchor="ls")
    if series:
        d.text((W - CAP_X, 112), series.lower(), font=f, fill=(128, 118, 104, 255), anchor="rs")


# ---------------------------------------------------------------- presenter
@lru_cache(maxsize=32)
def pose_sprite(name, mirror):
    p = os.path.join(POSE_DIR, name + ".png")
    if not os.path.exists(p):
        p = os.path.join(POSE_DIR, "talk.png")
    im = Image.open(p).convert("RGBA")
    k = PRES_H / im.height
    im = im.resize((int(im.width * k), PRES_H), Image.LANCZOS)
    a = np.asarray(im)[..., 3]
    rows = a[int(im.height * 0.86):]
    cols = np.where(rows.max(axis=0) > 40)[0]
    torso_cx = (cols.min() + cols.max()) / 2 if len(cols) else im.width / 2
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        torso_cx = im.width - torso_cx
    return im, torso_cx


class Presenter:
    def __init__(self, cfg, words, sentences, narr, dur):
        self.side = cfg.get("side", "right")
        self.mirror = self.side == "left"
        self.anchor_x = 286 if self.mirror else W - 286
        poses = cfg.get("poses")
        if not poses:
            poses = auto_poses(sentences, dur)
        self.poses = sorted((float(t), p) for t, p in poses)
        # speech envelope (per video frame) for a subtle talking bob
        self.env = None
        if narr is not None and len(narr):
            hop = sh.SR // sh.FPS
            nfr = len(narr) // hop
            e = np.sqrt(np.convolve(narr[: nfr * hop] ** 2, np.ones(hop) / hop, mode="same")[::hop])
            e = np.convolve(e, np.ones(4) / 4, mode="same")
            self.env = e / (e.max() + 1e-9)
        self.changes = [t for t, _ in self.poses[1:]]

    def pose_at(self, t):
        cur, ts = self.poses[0][1], self.poses[0][0]
        for tt, p in self.poses:
            if t >= tt:
                cur, ts = p, tt
        return cur, ts

    def draw(self, cv, t):
        pose, ts = self.pose_at(t)
        im, tcx = pose_sprite(pose, self.mirror)
        dt = t - ts
        k = 0.94 + 0.06 * sh.ease_out_back(sh.clamp(dt / 0.26), 2.0) if ts > 0 else 1.0
        breathe = 1 + 0.007 * math.sin(t * 2 * math.pi / 3.4)
        bob = 0.0
        if self.env is not None:
            i = min(len(self.env) - 1, int(t * sh.FPS))
            bob = 9 * self.env[i]
        enter = sh.ease_out_cubic(sh.clamp(t / 0.45))
        sx = 4 * math.sin(t * 0.9)
        kk = k
        w2, h2 = int(im.width * kk), int(im.height * kk * breathe)
        img = im.resize((w2, h2), Image.BILINEAR) if (w2, h2) != im.size else im
        x = self.anchor_x - tcx * kk + sx
        y = H + 34 - h2 - bob + (1 - enter) * 420
        cv.alpha_composite(img, (int(x), int(y)))


def auto_poses(sentences, dur):
    """One pose per sentence: questions think/shrug, hype words shocked, last sentence thumbs."""
    out, cyc = [], ["talk", "idea", "point", "talk", "phone", "idea"]
    j = 0
    for i, (t, txt) in enumerate(sentences):
        low = txt.lower()
        if i == 0:
            p = "talk"
        elif i == len(sentences) - 1:
            p = "thumbs"
        elif any(w in low for w in ("insane", "crazy", "secret", "wow", "nobody", "hidden", "boom")):
            p = "shocked"
        elif low.rstrip().endswith("?"):
            p = "think" if i % 2 else "shrug"
        else:
            p = cyc[j % len(cyc)]
            j += 1
        if out and out[-1][1] == p:
            p = "talk" if p != "talk" else "idea"
        out.append((t, p))
    return out or [(0.0, "talk")]


# ---------------------------------------------------------------- renderer
class StudioRenderer:
    def __init__(self, spec):
        self.spec = spec
        self.bg = StudioPaper()
        base = spec.get("_base", ".")
        cap = spec.get("_studio_captions")
        self.groups, words = cap if cap else ([], [])
        sents_txt = spec.get("_sentences") or [(0.0, "")]
        self.vis = []
        for v in spec["visuals"]:
            cls = sh.VISUALS[v["type"]]
            self.vis.append(cls(v, v["t0"], v["t1"]))
        self.cuts = sorted(v["t0"] for v in spec["visuals"] if v["t0"] > 0.05)
        self.bass = [e["t"] for e in spec.get("sfx", []) if e["type"] in ("bass", "boom", "dun")]
        self.zooms = sorted(e["t"] for e in spec.get("sfx", []) if e["type"] == "zoom")
        self.scale = spec.get("content_scale", 0.72)
        pcfg = spec.get("presenter", {"side": "right"})
        if not PRESENTER_OK and not spec.get("presenter_preview"):
            pcfg = {"side": "none"}   # owner hasn't approved the cartoon presenter yet
        global CONTENT_CY
        if pcfg.get("side") == "none":
            CONTENT_CY = 1000          # no presenter: content sits lower and larger
            self.scale = spec.get("content_scale", 0.85)
        narr = None
        if spec.get("narration"):
            try:
                narr = sh.read_audio(spec["narration"])
            except Exception:
                narr = None
        self.pres = None if pcfg.get("side") == "none" else Presenter(pcfg, words, sents_txt, narr, spec["duration"])
        self.wipe = spec.get("wipes", True)

    def content(self, t):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        any_ = False
        for v in self.vis:
            if v.t0 <= t < v.t1:
                v.draw(layer, t)
                any_ = True
        if not any_:
            return None
        k = self.scale
        cur = [v for v in self.vis if v.t0 <= t < v.t1]
        if cur:
            k = cur[-1].p.get("scale", TYPE_SCALE.get(cur[-1].p.get("type"), self.scale) * (1.0 if self.pres else 1.12))
        bb = layer.getbbox()
        if not bb:
            return None
        part = layer.crop(bb)
        part = part.resize((max(1, int(part.width * k)), max(1, int(part.height * k))), Image.BICUBIC)
        # keep the visual's own centre (VIS_CY) mapped onto the content band centre
        cx = W / 2 + (bb[0] + (bb[2] - bb[0]) / 2 - W / 2) * k
        cy = CONTENT_CY + (bb[1] + (bb[3] - bb[1]) / 2 - sh.VIS_CY) * k
        return part, int(cx - part.width / 2), int(cy - part.height / 2)

    def frame(self, t):
        cv = self.bg.frame(t)
        draw_header(cv, self.spec.get("series"))
        c = self.content(t)
        if c:
            part, x, y = c
            # soft contact shadow so floating UI sits on the paper
            shadow = Image.new("RGBA", part.size, (0, 0, 0, 0))
            shadow.putalpha(part.getchannel("A").point(lambda a: int(a * 0.20)))
            shadow = shadow.filter(ImageFilter.GaussianBlur(16))
            sc = Image.new("RGBA", part.size, (70, 50, 20, 255))
            sc.putalpha(shadow.getchannel("A"))
            cv.alpha_composite(sc, (x + 8, y + 18))
            cv.alpha_composite(part, (x, y))
        # paper-cut wipe across the content band around every cut
        if self.wipe:
            for ct in self.cuts:
                u = (t - ct + 0.2) / 0.42
                if 0 <= u <= 1:
                    panel = torn_panel(int(ct * 10) % 3 + 1)
                    px = int(W + 60 - (W + panel.width + 120) * sh.ease_in_out(u))
                    cv.alpha_composite(panel, (px, CONTENT_CY - panel.height // 2))
        if self.pres:
            self.pres.draw(cv, t)
        draw_studio_captions(cv, t, self.groups)
        # camera: gentle punch-in at cuts and on keyword zooms, small shake on bass hits
        last_cut = max([cc for cc in self.cuts if cc <= t] or [0])
        dt = t - last_cut
        z = 1.0 + 0.05 * (1 - sh.ease_out_cubic(dt / 0.4)) + 0.018 * sh.clamp(dt / 5)
        for zt in self.zooms:
            dz = t - zt
            if 0 <= dz < 0.9 and zt >= last_cut:
                kz = sh.ease_out_cubic(sh.clamp(dz / 0.14)) * (1 - sh.ease_out_cubic(sh.clamp((dz - 0.45) / 0.45)))
                z = max(z, 1.0 + 0.07 * kz + 0.018 * sh.clamp(dt / 5))
        sx = sy = 0.0
        for b in self.bass:
            if 0 <= t - b < 0.25:
                amp = 7 * (1 - (t - b) / 0.25)
                sx += amp * math.sin(t * 90)
                sy += amp * math.cos(t * 77)
        img = cv.convert("RGB")
        if z > 1.001 or sx or sy:
            z = max(z, 1.012)
            cw, ch = W / z, H / z
            x0 = sh.clamp((W - cw) / 2 - sx, 0, W - cw)
            y0 = sh.clamp((H - ch) * 0.42 - sy, 0, H - ch)
            img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        return img


def prepare(spec, base):
    """Called by shorts.render before rendering a studio spec."""
    spec["_base"] = base
    cfg = spec["captions"]
    groups, words = build_caption_groups(cfg, base)
    spec["_studio_captions"] = (groups, words)
    sents = []
    for g in groups:
        txt = []
        for w in words:
            if g["t"] <= w["s"] < g["t1"]:
                txt.append(w["w"])
        sents.append((g["t"], " ".join(txt)))
    spec["_sentences"] = sents
    # a soft pop on every presenter pose change, a click under every caption keyword
    pcfg = spec.get("presenter", {"side": "right"})
    if pcfg.get("side") != "none" and (PRESENTER_OK or spec.get("presenter_preview")):
        poses = pcfg.get("poses") or auto_poses(sents, spec["duration"])
        spec.setdefault("presenter", {})["poses"] = poses
        for t_, _ in poses[1:]:
            spec.setdefault("sfx", []).append({"t": round(float(t_), 3), "type": "pop", "vol": 0.3})
    # keyword punch-ins (soft), never within 0.8 s of a scene cut or another hit
    busy = [v["t0"] for v in spec["visuals"]] + [e["t"] for e in spec.get("sfx", []) if e["type"] in ("zoom", "boom", "bass", "dun")]
    for g in groups:
        for w in g["words"]:
            if w["key"] and all(abs(w["s"] - b) > 0.8 for b in busy) and w["s"] < spec["duration"] - 0.8:
                spec.setdefault("sfx", []).append({"t": round(w["s"], 3), "type": "zoom", "vol": 0.45})
                busy.append(w["s"])
    return spec


# ---------------------------------------------------------------- studio visuals
def _wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if d.textlength(tt, font=f) <= maxw or not cur:
            cur = tt
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class NoteCard(sh.Visual):
    """White instructional card: mono label, big title, optional rows (emoji + text) and a red serif sticker.
    p: {"label": "windows 11", "title": "Clipboard history", "rows": [{"e": "🔗", "text": "a link", "t": 3.1}],
        "tag": "turned off", "tag_t": 2.0, "w": 920}"""

    def __init__(self, p, t0, t1):
        super().__init__(p, t0, t1)
        self.w = p.get("w", 920)
        f_title = font(sh.FONT_BOLD, p.get("title_size", 84))
        tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        self.lines = _wrap(tmp, p.get("title", ""), f_title, self.w - 110)
        self.f_title = f_title

    def height(self, nrows):
        return 128 + len(self.lines) * 92 + (24 + nrows * 104 if nrows else 0) + 26

    def base(self, upto_rows):
        w, h = self.w, self.height(upto_rows)
        img = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((20, 20, 20 + w, 20 + h), 34, fill=(255, 255, 255, 255), outline=(222, 214, 200, 255), width=3)
        d.text((70, 92), self.p.get("label", "").lower(), font=font(MONO, 30), fill=(140, 130, 116, 255), anchor="ls")
        y = 120
        for ln in self.lines:
            d.text((70, y + 72), ln, font=self.f_title, fill=INK + (255,), anchor="ls")
            y += 92
        y += 24
        for i, r in enumerate(self.p.get("rows", [])[:upto_rows]):
            d.rounded_rectangle((60, y, 20 + w - 40, y + 86), 22, fill=(246, 242, 234, 255))
            em = sh.emoji_sprite(r["e"], 56) if r.get("e") else None
            if em:
                img.alpha_composite(em, (84, int(y + 43 - em.height / 2)))
            d.text((170, y + 58), r["text"], font=font(sh.FONT_SEMI, 44), fill=(60, 58, 62, 255), anchor="ls")
            y += 104
        return img

    def draw(self, cv, t):
        rows = self.p.get("rows", [])
        n = sum(1 for r in rows if t >= r.get("t", self.t0))
        img = self.base(n)
        self.h = img.height - 40
        k, a = sh.pop(t, self.t0, 0.3)
        sh.paste(cv, img, W / 2, sh.VIS_CY, k, a)
        tag = self.p.get("tag")
        if tag:
            tt = self.p.get("tag_t", self.t0 + 0.4)
            if t >= tt:
                kt, at_ = sh.pop(t, tt, 0.25)
                sp = tag_sprite(tag)
                sh.paste(cv, sp, W / 2 + self.w / 2 - sp.width / 2 + 20, sh.VIS_CY - self.h / 2 - 6, kt, at_)


@lru_cache(maxsize=64)
def tag_sprite(text):
    f = font(SERIF_IT, 70)
    tw = int(ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(text, font=f))
    im = Image.new("RGBA", (tw + 70, 116), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 10, tw + 62, 104), 46, fill=RED + (255,))
    d.text((34, 84), text, font=f, fill=(255, 255, 255, 255), anchor="ls")
    return im.rotate(5, resample=Image.BICUBIC, expand=True)


sh.VISUALS["note"] = NoteCard
