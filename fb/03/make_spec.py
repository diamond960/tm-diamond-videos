"""fb03: Snap layouts with Windows + Z (quick fix, ~19 s). Studio style."""
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

add(0, {"type": "note", "label": "windows 11", "title": "Still dragging windows around?", "tag": "stop",
        "tag_t": at(0, "stop", 0.1), "rows": [{"e": "🖱️", "text": "drag, resize, repeat", "t": at(0, "windows")},
                                             {"e": "😩", "text": "every single time", "t": at(0, "around")}]})
add(1, {"type": "keys", "keys": ["Win", "Z"], "press_t": [at(1, "windows"), at(1, "z")]})
add(2, {"type": "note", "label": "snap layouts", "title": "Pick a layout, then a spot",
        "rows": [{"e": "▫️", "text": "1. choose a layout", "t": at(2, "layout")},
                 {"e": "👉", "text": "2. click where this window goes", "t": at(2, "spot")}]})
add(3, {"type": "note", "label": "snap assist", "title": "Click another app to fill the gap",
        "rows": [{"e": "🌐", "text": "your browser", "t": at(3, "another")},
                 {"e": "📁", "text": "File Explorer", "t": at(3, "fill")}], "tag": "done", "tag_t": at(3, "gap")})
add(4, {"type": "note", "label": "not working?", "title": "Check one setting", "tag": "fix", "tag_t": at(4, "working", 0.1)})
side = [{"text": "System", "e": "🖥️"}, {"text": "Bluetooth & devices", "e": "🔵"}, {"text": "Network & internet", "e": "🌐"},
        {"text": "Personalization", "e": "🎨"}, {"text": "Apps", "e": "🧩"}]
add(5, {"type": "winui", "w": 900, "h": 600, "title": "Settings", "icon": "⚙️",
        "header": "System", "rows": [{"e": "🖥️", "cells": ["Display"]}, {"e": "🔊", "cells": ["Sound"]},
                                     {"e": "🔔", "cells": ["Notifications"]}, {"e": "🗂️", "cells": ["Multitasking"]}],
        "col_x": [0.0],
        "steps": [{"t": at(5, "multitasking"), "target": "row:3", "action": "click", "arrow": True}],
        "zoom": [{"t": at(5, "multitasking", -0.3), "target": "row:3", "k": 1.3, "dur": 0.9}]}, t1=at(5, "and"))
V.append({"type": "winui", "t0": at(5, "and"), "t1": nxt(5), "w": 900, "h": 460, "title": "Settings", "icon": "⚙️",
          "header": "System  ›  Multitasking",
          "rows": [{"e": "🪟", "cells": ["Snap windows"], "toggle": False}, {"e": "🖥️", "cells": ["Desktops"]}],
          "col_x": [0.0],
          "steps": [{"t": at(5, "turn"), "target": "toggle:0", "action": "click", "arrow": True, "set": {"toggle:0": True}},
                    {"t": at(5, "snap", 0.2), "target": "toggle:0", "action": "circle"}],
          "zoom": [{"t": at(5, "turn", -0.2), "target": "toggle:0", "k": 1.25, "dur": 1.0}]})
add(6, {"type": "follow", "name": "TMDiamond", "label": "Follow", "done_label": "Following", "tap_t": at(6, "follow", 0.3)})
add(7, {"type": "note", "label": "windows 11", "title": "Still dragging windows around?", "tag": "stop",
        "tag_t": at(7, "stop", 0.1)}, t1=DUR)

poses = [[0.0, "shocked"], [at(1), "point"], [at(2), "idea"], [at(3), "thumbs"], [at(4), "think"],
         [at(5), "point"], [at(6), "thumbs"], [at(7), "talk"]]
sfx = [
    {"t": at(0, "stop", 0.1), "type": "pop", "vol": 0.6},
    {"t": at(1, "windows"), "type": "click"}, {"t": at(1, "z"), "type": "click"},
    {"t": at(2, "layout"), "type": "pop", "vol": 0.5}, {"t": at(2, "spot"), "type": "click"},
    {"t": at(3, "another"), "type": "click"}, {"t": at(3, "gap"), "type": "correct", "vol": 0.55},
    {"t": at(4, "working", 0.1), "type": "pop", "vol": 0.5},
    {"t": at(5, "multitasking"), "type": "click"},
    {"t": at(5, "turn"), "type": "click"}, {"t": at(5, "turn", 0.2), "type": "correct", "vol": 0.55},
    {"t": at(6, "follow", 0.3), "type": "click"},
    {"t": at(7, "stop", 0.1), "type": "pop", "vol": 0.5},
]
spec = {"title": "Stop dragging windows around on Windows 11", "style": "studio", "series": "windows fix", "duration": DUR,
        "narration": "voice.mp3", "presenter": {"side": "right", "poses": poses},
        "captions": {"words": "voice.words.json",
                     "highlight": ["dragging", "z", "layout", "spot", "multitasking", "snap"],
                     "underline": ["dragging", "snap"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, len(sents), "sentences", [(v["type"], v["t0"], v["t1"]) for v in V])
