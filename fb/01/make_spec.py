"""Builds fb/01/spec.json from the voice timings (startup apps fix)."""
import json
import os
import sys

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
        sents.append(cur)
        cur = []
if cur:
    sents.append(cur)
S = [s[0]["s"] for s in sents]
DUR = round(d["duration"] + 0.4, 2)


def at(i, word=None, off=0.0):
    """Start time of sentence i (0-based), or of a word inside it."""
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


# 0 hook
add(0, {"type": "clock", "label": "LOADING...", "land_t": at(0, "forever"), "viewers_t": []})
# 1 every app wants to launch
add(1, {"type": "pills", "items": [
    {"text": "SPOTIFY", "c": "lime", "t": at(1, "every", 0.2)},
    {"text": "TEAMS", "c": "blue", "t": at(1, "install")},
    {"text": "STEAM", "c": "pink", "t": at(1, "launch")},
    {"text": "UPDATERS", "c": "orange", "t": at(1, "windows")}]})
# 2 slows startup
add(2, {"type": "emoji", "items": [{"e": "🐢", "t": at(2), "size": 420}]})
# 3 here's the fix
add(3, {"type": "bigtext", "text": "FIX", "c": "lime", "size": 300, "sub": "30 SECONDS", "sub_t": at(3, "fix")})
# 4 ctrl shift esc
add(4, {"type": "pills", "items": [
    {"text": "CTRL", "c": "cyan", "t": at(4, "control")},
    {"text": "SHIFT", "c": "cyan", "t": at(4, "shift")},
    {"text": "ESC", "c": "cyan", "t": at(4, "escape")},
    {"text": "TASK MANAGER", "c": "lime", "t": at(4, "task")}]})
# 5 startup apps
add(5, {"type": "search", "query": "Startup apps", "type_t": at(5, "click", 0.05), "type_dur": 0.8,
        "rows": [{"text": "Task Manager > Startup apps", "t": at(5, "apps")}], "arrow_t": at(5, "apps", 0.2)})
# 6 startup impact column
add(6, {"type": "list", "items": [
    {"text": "Startup impact: High", "t": at(6, "startup"), "e": "🔴", "c": "red"},
    {"text": "Medium", "t": at(6, "impact"), "e": "🟠", "c": "orange"},
    {"text": "Low", "t": at(6, "column"), "e": "🟢", "c": "lime"}]})
# 7 high you don't need
add(7, {"type": "emoji", "items": [{"e": "🤔", "t": at(7), "size": 380}]})
# 8 right-click disable
add(8, {"type": "progress", "fill_t": at(8, "right"), "fill_dur": 1.2, "checks": [
    {"text": "RIGHT-CLICK", "show": at(8, "right"), "tick": at(8, "right", 0.4)},
    {"text": "DISABLE", "show": at(8, "disable", -0.2), "tick": at(8, "disable", 0.3)}]})
# 9 restart
add(9, {"type": "emoji", "items": [{"e": "🚀", "t": at(9), "size": 420}]})
# 10 follow
add(10, {"type": "follow", "name": "TM_Diamond", "label": "Follow", "done_label": "Following", "tap_t": at(10, "follow", 0.3)})
# 11 loop line -> back to the hook visual
add(11, {"type": "emoji", "items": [{"e": "⏳", "t": at(11), "size": 400}]}, t1=DUR - 0.5)
V.append({"type": "clock", "label": "LOADING...", "land_t": DUR - 0.5, "viewers_t": [], "t0": round(DUR - 0.5, 2), "t1": DUR})

sfx = [
    {"t": 0.0, "type": "bass"},
    {"t": at(0, "forever"), "type": "tick"},
    {"t": at(2), "type": "error", "vol": 0.7},
    {"t": at(3), "type": "bass", "vol": 0.9},
    {"t": at(4, "control"), "type": "click"}, {"t": at(4, "shift"), "type": "click"}, {"t": at(4, "escape"), "type": "click"},
    {"t": at(5, "click", 0.05), "type": "typing", "vol": 0.6},
    {"t": at(6, "startup"), "type": "pop"}, {"t": at(6, "impact"), "type": "pop"}, {"t": at(6, "column"), "type": "pop"},
    {"t": at(8, "right", 0.4), "type": "tick"}, {"t": at(8, "disable", 0.3), "type": "tick"},
    {"t": at(9, "restart", -0.8), "type": "riser", "vol": 0.6},
    {"t": at(9), "type": "ding"},
    {"t": at(10, "follow", 0.3), "type": "click"},
]
for v in V:
    for it in v.get("items", []):
        if v["type"] == "pills":
            sfx.append({"t": it["t"], "type": "pop", "vol": 0.6})

spec = {
    "title": "Your PC takes forever to start",
    "duration": DUR,
    "narration": "voice.mp3",
    "captions": {"auto": True, "words": "voice.words.json",
                 "highlight": ["forever", "slows", "fix", "task", "startup", "impact", "high", "disable", "restart"]},
    "visuals": V,
    "sfx": sorted(sfx, key=lambda e: e["t"]),
}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, "visuals", len(V))
print([(v["type"], v["t0"], v["t1"]) for v in V])
