"""Shared builder for Facebook reels / TikToks cut from one day's real capture session (Team Diamond template,
owner's full-screen framing). Generalises fb/make_batch_1111.py: shots can be named by their capture label.

Beat format, one per spoken sentence (index = sentence number):
  shot  - screenshot shown from the start of the sentence: a file name, or a capture label ("b2e2_result" =
          the last frame with that label, "b2e2_type:first" = the first one)
  cam   - (cx, cy, h) in screen pixels; FULL = the whole screen
  boxes - [([x, y, w, h], colour or None), ...] drawn from the start of the sentence to its end
          (or ([x, y, w, h], colour, f0, f1) = from fraction f0 to f1 of the sentence)
  clicks- [(x, y, frac, next_shot), ...] click at frac of the sentence, then show next_shot
  seq   - (label, f0, f1) play every frame with that label between fractions f0..f1 (typing, scrolling)
  typing- True: key sounds during seq
  after - [(frac, shot), ...] switch shots inside the sentence
  keys  - (["Win", "R"], frac) keycaps at frac of the sentence
  step  - (kicker, text) label in the info band
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RED = [255, 70, 70]


class Caps:
    def __init__(self, folder):
        self.folder = folder
        self.files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, folder, "*.png")))

    def frames(self, label):
        out = [f for f in self.files if f[4:-4] == label]
        if not out:
            raise KeyError(f"no frames labelled {label} in {self.folder}")
        return out

    def get(self, name):
        if name.endswith(".png"):
            return name
        if name.endswith(":first"):
            return self.frames(name[:-6])[0]
        return self.frames(name)[-1]


def build(out_dir, beats, card, captures, full, hide=None, titles=None, extra_post=None, end_pad=0.35, drift=None):
    """Writes out_dir/spec.json from out_dir/tight.json and the beats; returns the duration."""
    caps = Caps(captures)
    d = os.path.join(ROOT, out_dir)
    T = json.load(open(os.path.join(d, "tight.json")))
    S = T["sentences"]
    assert len(S) == len(beats), (out_dir, len(S), len(beats))
    dur = round(T["duration"] + end_pad, 2)
    shots, cam, boxes, clicks, cursor, keys, steps, sfx, typing = [], [], [], [], [], [], [], [], []
    last_cam = None
    for i, (s, b) in enumerate(zip(S, beats)):
        t0 = s["s"] - (0.12 if i else 0)
        t1 = S[i + 1]["s"] - 0.12 if i + 1 < len(S) else dur
        span = s["e"] - s["s"]
        at = lambda f: round(s["s"] + span * f, 3)
        if b.get("shot"):
            shots.append([round(max(0, t0), 3), caps.get(b["shot"])])
        cc = b.get("cam", full)
        if cc != last_cam:
            cam.append([round(max(0, t0), 3), *cc, 0 if i == 0 else b.get("ease", 0.5)])
            last_cam = cc
        for bx in b.get("boxes", []):
            rect, col = bx[0], bx[1]
            f0, f1 = (bx[2], bx[3]) if len(bx) > 2 else (None, None)
            b0 = at(f0) if f0 is not None else round(s["s"] + 0.15, 3)
            b1 = at(f1) if f1 is not None else round(t1 - 0.05, 3)
            boxes.append([b0, rect, round(b1 - b0, 2)] + ([col] if col else []))
        if b.get("seq"):
            label, f0, f1 = b["seq"]
            fr = caps.frames(label)
            a, z = at(f0), at(f1)
            for k, f in enumerate(fr):
                shots.append([round(a + (z - a) * k / max(1, len(fr)), 3), f])
            if b.get("typing"):
                typing.append([a, z, len(fr)])
        for x, y, frac, nxt in b.get("clicks", []):
            tc = at(frac)
            cursor.append([round(tc - 0.45, 3), x, y]); cursor.append([round(tc + 0.15, 3), x, y])
            clicks.append(tc); shots.append([round(tc + 0.12, 3), caps.get(nxt)]); sfx.append([tc, "click"])
        for frac, nxt in b.get("after", []):
            shots.append([at(frac), caps.get(nxt)])
        kl = b.get("keys") or []
        if kl and isinstance(kl[1], (int, float)):
            kl = [kl]
        for ks, frac in kl + list(b.get("keys2", [])):
            keys.append([at(frac), ks, 0.9, 0.37])
        if b.get("step"):
            steps.append([round(s["s"], 3), round(t1, 3), *b["step"]])
        for frac, name in b.get("sfx", []):
            sfx.append([at(frac), name])
    shots.sort(key=lambda x: x[0])
    cursor.sort(key=lambda x: x[0])
    on = [[cursor[0][0] - 0.3, cursor[-1][0] + 0.6]] if cursor else []
    spec = {
        "layout": "tmd", "framing": "full",
        "captures": captures, "narration": f"{out_dir}/tight.wav", "words": f"{out_dir}/tight.json",
        "script": f"{out_dir}/script.txt", "duration": dur, "handle": "TM_Diamond", "captions": False,
        "shots": shots, "cam": cam, "cursor": cursor, "cursor_on": on, "clicks": clicks, "keys": keys,
        "typing": typing, "boxes": boxes,
        "card": dict(t0=0.0, t1=round(S[0]["e"] + 0.3, 2), **card),
        "steps": steps, "highlight": [], "sfx": sfx, "follow": round(S[-1]["s"], 2),
    }
    if hide:
        spec["hide"] = hide
    if drift is not None:
        spec["drift"] = drift
    if titles:
        spec["titles"] = titles
    json.dump(spec, open(os.path.join(d, "spec.json"), "w"), indent=1)
    return dur, S
