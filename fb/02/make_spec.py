"""fb02: clipboard history (Win + V) - paper background, Windows UI, viral sounds."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from shorts import aligned_words  # noqa: E402

d = json.load(open(os.path.join(HERE, "voice.words.json")))
d["text"] = open(os.path.join(HERE, "script.txt")).read()
words = aligned_words(d)
sents, cur = [], []
for w in words:
    cur.append(w)
    if w["w"].rstrip().endswith((".", "?", "!", "…")):
        sents.append(cur); cur = []
if cur:
    sents.append(cur)
S = [x[0]["s"] for x in sents]
DUR = round(d["duration"] + 0.4, 2)


def at(i, word=None, off=0.0):
    if word:
        for w in sents[i]:
            if w["w"].lower().strip(".,!?…\"'").startswith(word.lower()):
                return round(w["s"] + off, 2)
    return round(S[i] + off, 2)


def nxt(i):
    return S[i + 1] if i + 1 < len(S) else DUR - 0.5


V = []


def add(i, v, t1=None):
    v["t0"] = 0.0 if not V else round(at(i), 2)
    v["t1"] = round(t1 if t1 is not None else nxt(i), 2)
    V.append(v)


hook = {"type": "emoji", "items": [{"e": "📋", "t": 0.0, "size": 400}], "cross": {"t": at(0, "losing"), "kind": "x", "size": 440}}
add(0, dict(hook))
add(1, {"type": "bigtext", "text": "OFF", "c": "red", "size": 300, "sub": "UNTIL YOU TURN IT ON", "sub_t": at(1, "turn")})
add(2, {"type": "keys", "keys": ["Win", "V"], "press_t": [at(2, "windows"), at(2, "v")]})
add(3, {"type": "winui", "w": 900, "h": 560, "title": "Clipboard", "icon": "📋", "header": "Clipboard",
        "sub": "Clipboard history is turned off.", "buttons": [{"text": "Turn on", "y": 250}],
        "steps": [{"t": at(3, "turn"), "target": "btn:0", "action": "circle", "arrow": True},
                  {"t": at(4, "click"), "target": "btn:0", "action": "click"}],
        "zoom": [{"t": at(3, "see"), "target": "btn:0", "k": 1.35, "dur": 1.6}]}, t1=nxt(4))
add(5, {"type": "keys", "keys": ["Ctrl", "C"], "press_t": [at(5, "copy"), at(5, "copy", 0.15)]}, t1=at(5, "link"))
V.append({"type": "emoji", "t0": at(5, "link"), "t1": nxt(5), "items": [{"e": "🔗", "t": at(5, "link"), "size": 230, "x": -300},
                                    {"e": "🖼️", "t": at(5, "photo"), "size": 230, "x": 0},
                                    {"e": "📝", "t": at(5, "text"), "size": 230, "x": 300}]})
add(6, {"type": "keys", "keys": ["Win", "V"], "press_t": [at(6, "windows"), at(6, "v")]})
rows = [{"e": "📝", "cells": ["Meeting moved to 5 PM"], "pin": False},
        {"e": "🖼️", "cells": ["photo.png"], "pin": False},
        {"e": "🔗", "cells": ["youtube.com/@TM_Diamond"], "pin": False}]
add(7, {"type": "winui", "w": 900, "h": 640, "title": "Clipboard", "icon": "📋", "header": "Clipboard history",
        "rows": rows, "col_x": [0.0],
        "steps": [{"t": at(7, "everything"), "target": "row:0", "action": "circle"},
                  {"t": at(8, "pin"), "target": "pin:0", "action": "click", "arrow": True, "set": {"pin:0": True}},
                  {"t": at(8, "restart"), "target": "pin:0", "action": "circle"}],
        "zoom": [{"t": at(8, "pin", -0.3), "target": "row:0", "k": 1.3, "dur": 2.4}]}, t1=nxt(8))
add(9, {"type": "follow", "name": "TM_Diamond", "label": "Follow", "done_label": "Following", "tap_t": at(9, "follow", 0.3)})
add(10, {"type": "emoji", "items": [{"e": "📋", "t": at(10), "size": 360}, {"e": "✅", "t": at(10, "never"), "size": 190, "x": 170, "y": 120}]}, t1=DUR - 0.5)
last = dict(hook)
last.update({"t0": round(DUR - 0.5, 2), "t1": DUR, "items": [{"e": "📋", "t": DUR - 0.5, "size": 400}], "cross": {"t": DUR - 0.4, "kind": "x", "size": 440}})
V.append(last)

sfx = [
    {"t": 0.0, "type": "boom"},
    {"t": at(0, "losing"), "type": "buzzer", "vol": 0.8},
    {"t": at(1), "type": "scratch", "vol": 0.8},
    {"t": at(1, "turn"), "type": "pop"},
    {"t": at(2, "windows"), "type": "click"}, {"t": at(2, "v"), "type": "click"},
    {"t": at(3, "turn"), "type": "dun", "vol": 0.7},
    {"t": at(4, "click"), "type": "correct"},
    {"t": at(5, "link"), "type": "shutter"}, {"t": at(5, "photo"), "type": "shutter"}, {"t": at(5, "text"), "type": "shutter"},
    {"t": at(6, "windows"), "type": "click"}, {"t": at(6, "v"), "type": "click"},
    {"t": at(7, "boom"), "type": "boom"},
    {"t": at(8, "pin"), "type": "pop"},
    {"t": at(8, "restart"), "type": "tada", "vol": 0.8},
    {"t": at(9, "follow", 0.3), "type": "click"},
    {"t": at(10, "never"), "type": "correct", "vol": 0.7},
]
spec = {"title": "Stop losing the things you copy", "bg": "paper", "duration": DUR, "narration": "voice.mp3",
        "captions": {"auto": True, "words": "voice.words.json",
                     "highlight": ["losing", "history", "windows", "turn", "boom", "pin", "restart", "never"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, [(v["type"], v["t0"], v["t1"]) for v in V])
