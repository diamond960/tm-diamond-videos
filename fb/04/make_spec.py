"""fb04: Screenshot to table with ChatGPT (~27 s). Studio style."""
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

add(0, {"type": "note", "label": "screenshot → table", "title": "Still retyping tables by hand?", "tag": "never again",
        "tag_t": at(0, "again"), "rows": [{"e": "🖼️", "text": "a table in a screenshot", "t": at(0, "table")},
                                         {"e": "⌨️", "text": "typing it all out", "t": at(0, "screenshot")}]})
add(1, {"type": "note", "label": "chatgpt", "title": "Click the + button", "tag": "step 1", "tag_t": at(1, "plus"),
        "rows": [{"e": "💬", "text": "open ChatGPT", "t": at(1, "chatgpt")},
                 {"e": "➕", "text": "the + next to the message box", "t": at(1, "plus")}]})
add(2, {"type": "note", "label": "chatgpt", "title": "Upload your screenshot",
        "rows": [{"e": "🖼️", "text": "screenshot.png", "t": at(2, "screenshot")}]})
add(3, {"type": "note", "label": "type this", "title": "“Turn this into a table”", "tag": "step 2", "tag_t": at(3, "turn"),
        "rows": [{"e": "🖼️", "text": "screenshot.png", "t": at(3)}, {"e": "💬", "text": "turn this into a table", "t": at(3, "turn")}]})
rows = [{"e": "☕", "cells": ["Coffee", "2", "$7.00"]}, {"e": "🥐", "cells": ["Croissant", "1", "$4.50"]},
        {"e": "🧃", "cells": ["Juice", "3", "$9.00"]}]
add(4, {"type": "winui", "w": 900, "h": 560, "title": "ChatGPT", "icon": "💬", "header": "Your table",
        "columns": ["Item", "Qty", "Price"], "col_x": [0.0, 0.55, 0.75], "rows": rows,
        "steps": [{"t": at(4, "row"), "target": "row:0", "action": "circle"},
                  {"t": at(4, "column"), "target": "cell:1:2", "action": "circle", "arrow": True}],
        "zoom": [{"t": at(4, "typed"), "target": "row:1", "k": 1.25, "dur": 0.9}]})
add(5, {"type": "note", "label": "excel", "title": "Want it in Excel?", "rows": [{"e": "📊", "text": "open it in Excel", "t": at(5, "excel")}]})
add(6, {"type": "note", "label": "ask chatgpt", "title": "Ask for a CSV file", "tag": "download", "tag_t": at(6, "download"),
        "rows": [{"e": "💬", "text": "give me this as a CSV file", "t": at(6, "csv")},
                 {"e": "📄", "text": "table.csv", "t": at(6, "download")}]})
add(7, {"type": "note", "label": "important", "title": "Check the numbers first", "tag": "always", "tag_t": at(7, "always", 0.1),
        "rows": [{"e": "🔍", "text": "compare with the screenshot", "t": at(7, "numbers")}]})
add(8, {"type": "note", "label": "claude", "title": "Works in Claude too",
        "rows": [{"e": "📎", "text": "attach it, same prompt", "t": at(8, "claude")}]})
add(9, {"type": "follow", "name": "TMDiamond", "label": "Follow", "done_label": "Following", "tap_t": at(9, "follow", 0.3)})
add(10, {"type": "note", "label": "screenshot → table", "title": "Still retyping tables by hand?", "tag": "never again",
         "tag_t": at(10, "retype")}, t1=DUR)

poses = [[0.0, "shocked"], [at(1), "point"], [at(2), "phone"], [at(3), "talk"], [at(4), "shocked"], [at(5), "think"],
         [at(6), "idea"], [at(7), "point"], [at(8), "thumbs"], [at(9), "thumbs"], [at(10), "talk"]]
sfx = [
    {"t": at(0, "again"), "type": "pop", "vol": 0.6},
    {"t": at(1, "chatgpt"), "type": "pop", "vol": 0.5}, {"t": at(1, "plus"), "type": "click"},
    {"t": at(2, "screenshot"), "type": "pop", "vol": 0.5},
    {"t": at(3, "turn"), "type": "typing", "vol": 0.5},
    {"t": at(4, "seconds"), "type": "correct", "vol": 0.55},
    {"t": at(5, "excel"), "type": "pop", "vol": 0.5},
    {"t": at(6, "csv"), "type": "pop", "vol": 0.5}, {"t": at(6, "download"), "type": "click"},
    {"t": at(7, "always", 0.1), "type": "pop", "vol": 0.5},
    {"t": at(8, "claude"), "type": "pop", "vol": 0.5},
    {"t": at(9, "follow", 0.3), "type": "click"},
    {"t": at(10, "retype"), "type": "pop", "vol": 0.5},
]
spec = {"title": "Never retype a table from a screenshot again", "style": "studio", "series": "ai tools", "duration": DUR,
        "narration": "voice.mp3", "presenter": {"side": "right", "poses": poses},
        "captions": {"words": "voice.words.json",
                     "highlight": ["retype", "plus", "table", "seconds", "csv", "check", "claude"],
                     "underline": ["retype", "csv"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, len(sents), "sentences", [(v["type"], v["t0"], v["t1"]) for v in V])
