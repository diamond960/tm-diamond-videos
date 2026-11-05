"""fb01 v2: startup apps fix - paper background, Task Manager mockup, viral sounds."""
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


add(0, {"type": "clock", "label": "LOADING...", "land_t": at(0, "forever"), "viewers_t": []}, t1=nxt(1))
add(2, {"type": "pills", "items": [
    {"text": "SPOTIFY", "c": "lime", "t": at(2, "every", 0.2)}, {"text": "TEAMS", "c": "blue", "t": at(2, "install")},
    {"text": "STEAM", "c": "pink", "t": at(2, "launch")}, {"text": "UPDATERS", "c": "orange", "t": at(2, "windows")}]})
add(3, {"type": "emoji", "items": [{"e": "🐢", "t": at(3), "size": 420}]})
add(4, {"type": "bigtext", "text": "FIX", "c": "lime", "size": 300, "sub": "NO APP NEEDED", "sub_t": at(4, "fix")})
add(5, {"type": "keys", "keys": ["Ctrl", "Shift", "Esc"], "press_t": [at(5, "control"), at(5, "shift"), at(5, "escape")]})
side = [{"text": t, "e": e} for t, e in [("Processes", "🧩"), ("Performance", "📈"), ("App history", "🕘"),
                                           ("Startup apps", "🚀"), ("Users", "👥"), ("Details", "📋"), ("Services", "⚙️")]]
rows = [{"e": "🎵", "cells": ["Spotify", "Enabled", "High"]}, {"e": "💬", "cells": ["Teams", "Enabled", "High"]},
        {"e": "🎮", "cells": ["Steam", "Enabled", "Medium"]}, {"e": "☁️", "cells": ["OneDrive", "Enabled", "Low"]},
        {"e": "🔊", "cells": ["Audio helper", "Enabled", "Low"]}]
add(6, {"type": "winui", "title": "Task Manager", "icon": "📊", "sidebar": side, "active": 0,
        "headers": {"0": "Processes", "3": "Startup apps"}, "rows_on": 3,
        "columns": ["Name", "Status", "Startup impact"], "col_x": [0.0, 0.45, 0.70], "rows": rows,
        "steps": [
            {"t": at(6, "startup"), "target": "sidebar:3", "action": "click"},
            {"t": at(7, "impact"), "target": "cell:0:2", "action": "circle", "arrow": True},
            {"t": at(8, "high"), "target": "cell:1:2", "action": "circle", "arrow": True},
            {"t": at(9, "right"), "target": "row:0", "action": "rightclick",
             "menu": ["Disable", "Open file location", "Search online", "Properties"]},
            {"t": at(10, "disable"), "target": "menu:0", "action": "click", "set": {"cell:0:1": "Disabled"}}],
        "zoom": [{"t": at(7, "startup"), "target": "cell:0:2", "k": 1.45, "dur": 2.2}]}, t1=nxt(10))
add(11, {"type": "emoji", "items": [{"e": "🚀", "t": at(11), "size": 420}]})
add(12, {"type": "follow", "name": "TM_Diamond", "label": "Follow", "done_label": "Following", "tap_t": at(12, "follow", 0.3)})
add(13, {"type": "emoji", "items": [{"e": "⏳", "t": at(13), "size": 400}]}, t1=DUR - 0.5)
V.append({"type": "clock", "label": "LOADING...", "land_t": DUR - 0.5, "viewers_t": [], "t0": round(DUR - 0.5, 2), "t1": DUR})

sfx = [
    {"t": 0.0, "type": "boom"},
    {"t": at(1), "type": "dun", "vol": 0.8},
    {"t": at(3, "slows"), "type": "buzzer", "vol": 0.8},
    {"t": at(4), "type": "scratch", "vol": 0.8},
    {"t": at(5, "control"), "type": "click"}, {"t": at(5, "shift"), "type": "click"}, {"t": at(5, "escape"), "type": "click"},
    {"t": at(6, "startup"), "type": "click"},
    {"t": at(7, "impact"), "type": "pop"}, {"t": at(8, "high"), "type": "boom", "vol": 0.7},
    {"t": at(9, "right"), "type": "click"},
    {"t": at(10, "disable"), "type": "correct"},
    {"t": at(11), "type": "tada"},
    {"t": at(12, "follow", 0.3), "type": "click"},
]
for v in V:
    if v["type"] == "pills":
        sfx += [{"t": it["t"], "type": "pop", "vol": 0.6} for it in v["items"]]
spec = {"title": "Your PC takes forever to start", "bg": "paper", "duration": DUR, "narration": "voice.mp3",
        "captions": {"auto": True, "words": "voice.words.json",
                     "highlight": ["forever", "slows", "fix", "task", "startup", "impact", "high", "disable", "restart"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, [(v["type"], v["t0"], v["t1"]) for v in V])
