"""fb09: How to grow on Facebook - 4 tips straight from Facebook's own Professional dashboard.
Team Diamond template (fb/07 look). Real screens: the owner's own Facebook dashboard screenshots (iPhone):
001_summary = a post's Summary (border warning, 20-second view rate, "159% more views under 15 s" tip),
002_match = Content protection match details (the other account's name and photo are blurred)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]


def word(text, after=0.0):
    for w in W:
        if w["w"].strip(".,?!:").lower() == text.lower() and w["s"] >= after - 0.01:
            return w
    raise KeyError(text)


dur = round(T["duration"] + 0.35, 2)
hide = word("hide", S[8]["s"])
RED = [255, 70, 70]
BORDER = [140, 680, 1060, 180]
VIEW20 = [140, 1070, 1060, 190]
TIP = [36, 1444, 1104, 306]
MATCH = [30, 1780, 1230, 180]
HIDE = [30, 2135, 1230, 120]

spec = {
    "layout": "tmd",
    "captures": "captures/fb09",
    "narration": "fb/09/tight.wav",
    "words": "fb/09/tight.json",
    "script": "fb/09/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": [
        [0.0, "001_summary.png"],
        [S[7]["s"] - 0.2, "002_match.png"],
        [S[9]["s"] - 0.2, "001_summary.png"],
    ],
    "cam": [
        [0.0, 645, 1750, 1150, 0],                       # the "159% more views" tip card, above the hook card
        [S[1]["s"] - 0.15, 645, 900, 1150, 0.5],          # the post's Summary
        [S[2]["s"] - 0.15, 660, 820, 980, 0.5],           # tip 1: border warning
        [S[4]["s"] - 0.15, 660, 1170, 980, 0.5],          # tip 2: 20-second view rate
        [S[5]["s"] - 0.15, 590, 1560, 1000, 0.5],          # tip 3: under 15 seconds
        [S[6]["s"] - 0.1, 590, 1600, 980, 0.5],           # "159% more views"
        [S[7]["s"] - 0.2, 645, 700, 1150, 0],             # tip 4: the match (cut)
        [S[8]["s"] - 0.1, 645, 1870, 1150, 0.5],           # the match
        [hide["s"] - 0.3, 645, 2150, 1150, 0.45],          # Hide from everyone
        [S[9]["s"] - 0.2, 645, 1300, 1150, 0],
    ],
    "boxes": [
        [S[2]["s"] + 0.2, BORDER, round(S[3]["e"] - S[2]["s"], 2), RED],
        [S[4]["s"] + 0.3, VIEW20, round(S[4]["e"] - S[4]["s"] - 0.1, 2), RED],
        [S[5]["s"] + 0.3, TIP, round(S[6]["e"] - S[5]["s"], 2)],
        [S[8]["s"] + 0.3, MATCH, round(hide["s"] - S[8]["s"] - 0.4, 2)],
        [hide["s"] - 0.1, HIDE, round(S[8]["e"] - hide["s"] + 0.3, 2)],
    ],
    "card": {"t0": 0.0, "t1": round(S[0]["e"] + 0.3, 2), "y": 313 + 520,
             "title": "Facebook told me this", "sub": "Reels under 15 seconds got",
             "count": [0, 159], "suffix": "% more views", "count_t": 0.3, "count_dur": 1.5},
    "highlight": [],
    "sfx": [[S[2]["s"] + 0.2, "pop"], [S[4]["s"] + 0.3, "pop"], [S[5]["s"] + 0.3, "pop"], [S[8]["s"] + 0.3, "pop"]],
    "follow": S[9]["s"],
    "follow_y": 0.55,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur)
