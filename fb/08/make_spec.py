"""fb08: Free up space without deleting your files - Settings > System > Storage > Temporary files > Remove files.
Team Diamond template (layout "tmd"), real screens: captures/fb08 (Settings on a real Windows PC, dark mode).
Every event is placed on the spoken words from tight.json (engine/tighten.py)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]


def word(text, after=0.0):
    for w in W:
        if w["w"].strip(".,?!").lower() == text.lower() and w["s"] >= after - 0.01:
            return w
    raise KeyError(text)


dur = round(T["duration"] + 0.35, 2)
junk = word("junk")
system = word("system", S[1]["s"])
storage = word("storage", S[1]["s"])
temp = word("files", S[2]["s"])
tick = word("tick", S[3]["s"])
remove = word("remove", S[4]["s"])
cont = word("continue", S[4]["s"])
yours = word("yours", S[5]["s"])

SYSTEM = (250, 252)          # left nav "System" (Find-Rect 184,234,280,36)
TEMP = (700, 330)            # "Temporary files" row on the Storage page
REMOVE = (642, 292)          # "Remove files" button (591,276,102,32)
CONT = (845, 597)            # "Continue" in the Remove files dialog (753,581,184,32)
system_click = system["s"] + 0.05
temp_click = temp["s"]
remove_click = remove["s"] + 0.15
cont_click = cont["s"] + 0.1

shots = [
    [0.0, "001_storage.png"],
    [temp_click + 0.12, "003_temp_page.png"],
    [remove_click + 0.15, "006_confirm.png"],
    [cont_click + 0.3, "008_done2.png"],
]

checks = [384, 460, 546, 670, 784]   # the five ticked boxes (x 594, 21 px)

spec = {
    "layout": "tmd",
    "captures": "captures/fb08",
    "narration": "fb/08/tight.wav",
    "words": "fb/08/tight.json",
    "script": "fb/08/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": shots,
    "cam": [
        [0.0, 880, 360, 520, 0],                          # Storage page: C: drive bar + Temporary files 1.45 GB
        [S[1]["s"] + 0.6, 460, 360, 520, 0.45],           # left nav: System
        [storage["s"] - 0.3, 880, 330, 460, 0.45],        # System > Storage, Temporary files row
        [temp_click + 0.15, 810, 560, 500, 0.45],         # the ticked list
        [S[4]["s"] - 0.1, 810, 400, 420, 0.4],            # Remove files button + Total selected
        [remove_click + 0.25, 940, 520, 420, 0.4],        # the real Remove files dialog
        [cont_click + 0.2, 814, 302, 420, 0.35],          # Finished cleanup, Total selected: 0 bytes
        [S[6]["s"], 880, 420, 520, 0.5],
    ],
    "cursor": [
        [S[1]["s"] + 0.3, 600, 520],
        [system_click - 0.08, SYSTEM[0], SYSTEM[1]],
        [temp_click - 0.5, 900, 450],
        [temp_click - 0.08, TEMP[0], TEMP[1]],
        [tick["s"], 760, 620],
        [remove_click - 0.1, REMOVE[0], REMOVE[1]],
        [cont_click - 0.1, CONT[0], CONT[1]],
        [cont_click + 0.6, 960, 420],
    ],
    "clicks": [system_click, temp_click, remove_click, cont_click],
    "keys": [[S[1]["s"] + 0.05, ["Win", "I"], 1.0, 0.58]],
    "boxes": [
        [junk["s"], [645, 317, 103, 24], 0.9, [255, 70, 70]],      # Temporary files (the junk)
        [system["s"] - 0.3, [184, 234, 280, 36], 0.75],            # System
        [storage["s"] - 0.1, [725, 145, 99, 38], 0.9],             # Storage
        [temp["s"] - 0.45, [640, 314, 112, 28], 0.7],              # Temporary files
    ] + [
        [tick["s"] + 0.12 * k, [592, y, 25, 21], 1.25] for k, y in enumerate(checks)   # ticked boxes
    ] + [
        [remove["s"] - 0.3, [591, 276, 102, 32], 0.75],            # Remove files
        [remove["s"] - 0.1, [899, 283, 143, 20], 0.9, [255, 70, 70]],  # Total selected: 417 MB
        [cont["s"] - 0.35, [753, 581, 184, 32], 0.6],              # Continue
        [yours["s"] - 0.4, [894, 283, 143, 22], 1.9, [255, 70, 70]],   # Total selected: 0 bytes
        [S[5]["s"], [588, 258, 205, 21], 1.6],                     # Finished temporary files cleanup.
    ],
    "card": {"t0": 0.0, "t1": round(S[0]["e"] + 0.3, 2), "y": 313 + 520,
             "title": "Your PC is full of junk", "sub": "Windows finds it for you",
             "count": [0, 417], "suffix": "MB of junk", "count_dur": 1.3},
    "highlight": [],
    "sfx": [[junk["s"], "pop"], [cont_click + 0.25, "ding"]],
    "follow": S[6]["s"],
    "follow_y": 0.55,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "system", system_click, "temp", temp_click, "remove", remove_click, "continue", cont_click)
