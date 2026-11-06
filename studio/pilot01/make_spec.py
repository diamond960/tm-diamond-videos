"""Studio-style pilot: clipboard history (Win + V). Same narration as fb/02, new house style."""
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
    if w["w"].rstrip().endswith((".", "?", "!")):
        sents.append(cur); cur = []
if cur:
    sents.append(cur)
S = [x[0]["s"] for x in sents]
DUR = round(d["duration"] + 0.5, 2)


def at(i, word=None, off=0.0):
    if word:
        for w in sents[i]:
            if w["w"].lower().strip(".,!?\"'").startswith(word.lower()):
                return round(w["s"] + off, 2)
    return round(S[i] + off, 2)


def nxt(i):
    return S[i + 1] if i + 1 < len(S) else DUR


V = []


def add(i, v, t1=None):
    v["t0"] = 0.0 if not V else round(at(i), 2)
    v["t1"] = round(t1 if t1 is not None else nxt(i), 2)
    V.append(v)


add(0, {"type": "note", "label": "windows 11", "title": "You copy something new...", "tag": "the old one is gone",
        "tag_t": at(0, "losing"), "rows": [{"e": "🔗", "text": "a link", "t": at(0, "things")},
                                           {"e": "❌", "text": "overwritten", "t": at(0, "copy")}]})
add(1, {"type": "note", "label": "settings · clipboard", "title": "Windows can keep a history", "tag": "but it's off",
        "tag_t": at(1, "turn")})
add(2, {"type": "keys", "keys": ["Win", "V"], "press_t": [at(2, "windows"), at(2, "v")]})
add(3, {"type": "winui", "w": 900, "h": 560, "title": "Clipboard", "icon": "📋", "header": "Clipboard",
        "sub": "Clipboard history is turned off.", "buttons": [{"text": "Turn on", "y": 250}],
        "steps": [{"t": at(3, "turn"), "target": "btn:0", "action": "circle", "arrow": True},
                  {"t": at(4, "click"), "target": "btn:0", "action": "click"}],
        "zoom": [{"t": at(3, "see"), "target": "btn:0", "k": 1.35, "dur": 1.6}]}, t1=nxt(4))
add(5, {"type": "note", "label": "copy (ctrl + c)", "title": "Copy a few things",
        "rows": [{"e": "🔗", "text": "a link", "t": at(5, "link")}, {"e": "🖼️", "text": "a photo", "t": at(5, "photo")},
                 {"e": "📝", "text": "some text", "t": at(5, "text")}]})
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
add(9, {"type": "follow", "name": "TM_Diamond", "label": "Follow", "done_label": "Following", "tap_t": at(9, "follow", 0.3)}, t1=DUR)

poses = [[0.0, "shocked"], [at(1), "idea"], [at(2), "point"], [at(4), "thumbs"], [at(5), "phone"],
         [at(6), "point"], [at(7), "shocked"], [at(8), "idea"], [at(9), "thumbs"], [at(10), "talk"]]
sfx = [
    {"t": at(0, "losing"), "type": "pop", "vol": 0.6},
    {"t": at(1, "turn"), "type": "pop", "vol": 0.6},
    {"t": at(2, "windows"), "type": "click"}, {"t": at(2, "v"), "type": "click"},
    {"t": at(3, "turn"), "type": "pop", "vol": 0.5},
    {"t": at(4, "click"), "type": "click"}, {"t": at(4, "click", 0.15), "type": "correct", "vol": 0.6},
    {"t": at(5, "link"), "type": "pop", "vol": 0.5}, {"t": at(5, "photo"), "type": "pop", "vol": 0.5},
    {"t": at(5, "text"), "type": "pop", "vol": 0.5},
    {"t": at(6, "windows"), "type": "click"}, {"t": at(6, "v"), "type": "click"},
    {"t": at(8, "pin"), "type": "click"},
    {"t": at(9, "follow", 0.3), "type": "click"},
]
spec = {"title": "Stop losing the things you copy", "style": "studio", "presenter_preview": True, "series": "windows fix", "duration": DUR,
        "narration": "voice.mp3", "presenter": {"side": "right", "poses": poses},
        "captions": {"words": "voice.words.json",
                     "highlight": ["losing", "history", "turn", "boom,", "boom", "pin", "restart", "never"],
                     "underline": ["history", "never"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, len(sents), "sentences", [(v["type"], v["t0"], v["t1"]) for v in V])
