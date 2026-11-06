"""fb05: ipconfig /flushdns - website won't load (~39 s). Studio style."""
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

add(0, {"type": "note", "label": "windows", "title": "Website won't load?", "tag": "but the rest works",
        "tag_t": at(0, "everything"), "rows": [{"e": "🚫", "text": "one site keeps failing", "t": at(0, "load")}]})
add(1, {"type": "note", "label": "command prompt", "title": "Try this one command", "tag": "1 line", "tag_t": at(1, "command")})
add(2, {"type": "note", "label": "dns cache", "title": "Your PC saves website addresses",
        "rows": [{"e": "🌐", "text": "website name → address", "t": at(2, "website")},
                 {"e": "🗂️", "text": "called the DNS cache", "t": at(2, "dns")}]})
add(3, {"type": "note", "label": "dns cache", "title": "One bad entry", "tag": "can't load", "tag_t": at(3, "fail"),
        "rows": [{"e": "❌", "text": "a saved address goes bad", "t": at(3, "bad")},
                 {"e": "🚫", "text": "that site can fail to load", "t": at(3, "site")}]})
add(4, {"type": "winui", "w": 900, "h": 620, "title": "Search", "icon": "🔎", "header": "Best match", "sub": "Searched for: cmd",
        "rows": [{"e": "⬛", "cells": ["Command Prompt"], "sub": "App"}], "col_x": [0.0],
        "steps": [{"t": at(4, "cmd"), "target": "row:0", "action": "circle"},
                  {"t": at(5, "click"), "target": "row:0", "action": "rightclick",
                   "menu": ["Run as administrator", "Open file location", "Pin to Start", "Pin to taskbar"]},
                  {"t": at(5, "run"), "target": "menu:0", "action": "click", "arrow": True}],
        "zoom": [{"t": at(5, "choose"), "target": "row:0", "k": 1.2, "dur": 1.2}]}, t1=nxt(5))
add(6, {"type": "note", "label": "administrator: command prompt", "title": "ipconfig /flushdns", "tag": "type this",
        "tag_t": at(6, "ipconfig")},
    t1=at(6, "then"))
V.append({"type": "keys", "t0": at(6, "then"), "t1": nxt(6), "keys": ["Enter"], "press_t": [at(6, "enter")]})
add(7, {"type": "note", "label": "administrator: command prompt", "title": "Successfully flushed the DNS Resolver Cache.",
        "tag": "done", "tag_t": at(7, "successfully")})
add(8, {"type": "note", "label": "browser", "title": "Now reload the website", "rows": [{"e": "🔄", "text": "reload the page", "t": at(8, "reload")}]})
add(9, {"type": "note", "label": "is it safe?", "title": "It only clears that saved list", "tag": "safe", "tag_t": at(9, "safe"),
        "rows": [{"e": "🧹", "text": "clears the DNS cache", "t": at(9, "clears")},
                 {"e": "🔁", "text": "Windows rebuilds it as you browse", "t": at(9, "rebuilds")}]})
add(10, {"type": "follow", "name": "TMDiamond", "label": "Follow", "done_label": "Following", "tap_t": at(10, "follow", 0.3)})
add(11, {"type": "note", "label": "windows", "title": "Website won't load?", "tag": "try this", "tag_t": at(11, "try")}, t1=DUR)

poses = [[0.0, "shocked"], [at(1), "idea"], [at(2), "talk"], [at(3), "shrug"], [at(4), "point"], [at(5), "point"],
         [at(6), "phone"], [at(7), "thumbs"], [at(8), "point"], [at(9), "talk"], [at(10), "thumbs"], [at(11), "talk"]]
sfx = [
    {"t": at(0, "load"), "type": "pop", "vol": 0.5}, {"t": at(0, "everything"), "type": "pop", "vol": 0.5},
    {"t": at(1, "command"), "type": "pop", "vol": 0.5},
    {"t": at(2, "website"), "type": "pop", "vol": 0.45}, {"t": at(2, "dns"), "type": "pop", "vol": 0.45},
    {"t": at(3, "bad"), "type": "pop", "vol": 0.45},
    {"t": at(4, "start"), "type": "click"}, {"t": at(4, "cmd"), "type": "typing", "vol": 0.5},
    {"t": at(5, "click"), "type": "click"}, {"t": at(5, "run"), "type": "click"},
    {"t": at(6, "ipconfig"), "type": "typing", "vol": 0.5}, {"t": at(6, "enter"), "type": "click"},
    {"t": at(7, "successfully"), "type": "correct", "vol": 0.55},
    {"t": at(8, "reload"), "type": "click"},
    {"t": at(9, "safe"), "type": "pop", "vol": 0.45}, {"t": at(9, "rebuilds"), "type": "pop", "vol": 0.45},
    {"t": at(10, "follow", 0.3), "type": "click"},
    {"t": at(11, "try"), "type": "pop", "vol": 0.5},
]
spec = {"title": "Website won't load? Try this one command", "style": "studio", "series": "cmd", "duration": DUR,
        "narration": "voice.mp3", "presenter": {"side": "right", "poses": poses},
        "captions": {"words": "voice.words.json",
                     "highlight": ["load", "command", "dns", "administrator", "flushdns", "successfully", "safe"],
                     "underline": ["flushdns", "safe"]},
        "visuals": V, "sfx": sorted(sfx, key=lambda e: e["t"])}
json.dump(spec, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
print("duration", DUR, len(sents), "sentences", [(v["type"], v["t0"], v["t1"]) for v in V])
