"""fb07: That PDF is really a program - turn on File name extensions.
Team Diamond template (layout "tmd"): logo strip on top, the real Windows screen in the middle panel,
the presenter strip below. Real screens: captures/fb07 (File Explorer on a real Windows PC, dark mode).
Narration tightened with engine/tighten.py; every event is placed on the spoken words."""
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
program = word("program", S[1]["s"])
view = word("view", S[2]["s"])
show = word("show", S[3]["s"])
ext = word("extensions", S[3]["s"])
real = word("real", S[4]["s"])
exe = next(w for w in W if w["s"] >= S[5]["s"] and "exe" in w["w"].lower())

VIEW = (694, 222)
SHOW = (694, 596)
EXT = (848, 701)
view_click = view["s"]
show_click = show["s"] + 0.05
ext_click = ext["s"] + 0.1

shots = [
    [0.0, "001_hidden.png"],
    [view_click + 0.12, "003_view_menu.png"],
    [show_click + 0.12, "004_show_menu.png"],
    [ext_click + 0.15, "006_shown.png"],
    [S[5]["s"], "007_shown2.png"],
]

spec = {
    "layout": "tmd",
    "captures": "captures/fb07",
    "narration": "fb/07/tight.wav",
    "words": "fb/07/tight.json",
    "script": "fb/07/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": shots,
    "cam": [
        [0.0, 585, 465, 460, 0],                           # the Downloads list: name + type columns
        [S[2]["s"] - 0.1, 700, 330, 420, 0.45],            # up to the View button (camera stays inside the window)
        [view_click + 0.1, 720, 420, 520, 0.4],            # the real View menu
        [show_click + 0.1, 790, 470, 520, 0.4],            # Show submenu
        [ext_click + 0.25, 585, 400, 450, 0.45],           # back to the files, extensions now visible
        [S[5]["s"] - 0.05, 455, 428, 300, 0.5],            # close on invoice.pdf.exe
        [S[6]["s"], 590, 420, 520, 0.5],
    ],
    "cursor": [
        [S[2]["s"], 1000, 520],
        [view_click - 0.05, VIEW[0], VIEW[1]],
        [show_click - 0.08, SHOW[0], SHOW[1]],
        [ext_click - 0.08, EXT[0], EXT[1]],
        [ext_click + 0.6, 1080, 560],
    ],
    "clicks": [view_click, show_click, ext_click],
    "keys": [[S[2]["s"] + 0.05, ["Win", "E"], 1.25, 0.58]],
    "boxes": [
        [0.35, [364, 418, 62, 20], 1.6],                           # "invoice.pdf"
        [program["s"], [748, 418, 64, 20], 1.4, [255, 70, 70]],    # Type: Application
        [view["s"] - 0.35, [650, 199, 87, 46], 0.7],               # View
        [show["s"] - 0.25, [604, 582, 179, 28], 0.6],              # Show
        [ext["s"] - 0.55, [788, 687, 207, 28], 0.75],              # File name extensions
        [real["s"] - 0.1, [364, 418, 82, 20], 1.9],                # invoice.pdf.exe
        [real["s"] + 0.25, [748, 418, 64, 20], 1.6],               # Application
        [exe["s"], [426, 418, 19, 20], 2.4, [255, 70, 70]],        # .exe
    ],
    "card": {"t0": 0.0, "t1": round(S[1]["e"] + 0.3, 2), "y": 313 + 520,
             "title": "Is this a PDF?", "sub": "Look closely at the file name",
             "big": "invoice.pdf", "big2": "invoice.pdf.exe", "swap_t": program["s"]},
    "highlight": [],
    "sfx": [[program["s"], "pop"], [ext_click + 0.15, "ding"]],
    "follow": S[6]["s"],
    "follow_y": 0.55,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "view", view_click, "show", show_click, "ext", ext_click, "exe", exe["s"])
