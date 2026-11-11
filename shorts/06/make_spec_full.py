"""short06: Windows 11 has a hidden End task button - trailer Short for long/02 (fix 4 of 10).
Narration = long/02's own fix-4 lines (same voice), cut and tightened (the voice runner was down).
Team Diamond template (fb/07 look). Real screens: captures/short06 (Settings > System > For developers on a real
Windows PC, dark mode; then Notepad's taskbar jump list > End task, and Notepad really closes)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]


def word(text, after=0.0):
    for w in W:
        if w["w"].strip(".,?!:'").lower() == text.lower() and w["s"] >= after - 0.01:
            return w
    raise KeyError(text)


dur = round(T["duration"] + 2.2, 2)   # ~2 s after the last line for the "full video below" band
devs = word("developers", S[1]["s"])
on = word("on", S[2]["s"])
taskbar = word("taskbar", S[3]["s"])
end4 = word("end", S[4]["s"])
it5 = word("it", S[5]["s"])

TOGGLE = (1538, 456)
TB = (1205, 1056)
ENDTASK = (1128, 969)
toggle_click = on["s"] + 0.05
rclick = taskbar["e"] + 0.05
end_click = it5["s"] + 0.02

spec = {
    "layout": "tmd",
    "framing": "full",
    "hide": [[1722, 976, 198, 54]],
    "captures": "captures/short06",
    "narration": "shorts/06/tight.wav",
    "words": "shorts/06/tight.json",
    "script": "shorts/06/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": [
        [0.0, "001_dev_page.png"],
        [toggle_click + 0.12, "003_toggle_on.png"],
        [S[3]["s"] - 0.1, "004_taskbar.png"],
        [rclick + 0.1, "006_jumplist.png"],
        [end_click + 0.15, "008_closed.png"],
        [S[6]["s"] - 0.1, "003_toggle_on.png"],
    ],
    "cam": [
        [0.0, 960, 540, 1080, 0],                         # the whole screen
        [S[2]["s"] - 0.1, 1150, 470, 860, 0.6],           # a gentle push toward the End Task toggle
        [S[3]["s"] - 0.1, 960, 540, 1080, 0],             # cut: whole screen, Notepad on the taskbar
        [S[3]["s"] + 0.6, 1150, 720, 720, 0.6],           # small push: the taskbar menu is tiny at full size
        [end_click + 0.5, 960, 540, 1080, 0.6],           # back out: whole screen, Notepad is gone
        [S[6]["s"] - 0.1, 960, 540, 1080, 0],             # cut: whole screen, End Task now On
    ],
    "cursor": [
        [S[2]["s"], 1250, 620],
        [toggle_click - 0.08, TOGGLE[0], TOGGLE[1]],
        [toggle_click + 0.25, TOGGLE[0], TOGGLE[1]],
        [S[3]["s"], 1300, 760],
        [rclick - 0.1, TB[0], TB[1]],
        [rclick + 0.25, TB[0], TB[1]],
        [end4["s"] - 0.1, ENDTASK[0], ENDTASK[1]],
        [end_click + 0.1, ENDTASK[0], ENDTASK[1]],
        [end_click + 0.6, 1320, 820],
    ],
    "cursor_on": [[S[2]["s"], S[6]["s"] - 0.1]],
    "clicks": [toggle_click, rclick, end_click],
    "keys": [[S[1]["s"] + 0.05, ["Win", "I"], 1.25, 0.37]],
    "boxes": [
        [0.4, [596, 424, 992, 64], round(S[0]["e"] - 0.3, 2)],                       # End Task: Enable end task in taskbar
        [devs["s"] - 0.3, [584, 160, 336, 54], 1.0],                                  # System > For developers
        [S[2]["s"] + 0.1, [1494, 430, 88, 52], round(toggle_click - S[2]["s"] + 0.5, 2)],  # the toggle
        [taskbar["s"] - 0.4, [1181, 1032, 48, 48], 0.9, [255, 70, 70]],              # Notepad on the taskbar
        [S[4]["s"], [1061, 955, 286, 28], round(end_click - S[4]["s"] + 0.1, 2)],     # End task
        [S[6]["s"] + 0.2, [1494, 430, 88, 52], round(dur - S[6]["s"] - 0.3, 2)],      # On
    ],
    "card": {"t0": 0.0, "t1": round(S[0]["e"] + 0.3, 2),
             "title": "Frozen app?", "sub": "Windows 11 has a hidden button", "big": "End task"},
    "titles": [
        [S[6]["s"], "Fix 4 of 10", 1.9],
        [S[6]["s"] + 1.9, "Full video below", round(dur - S[6]["s"] - 1.9, 2)],
    ],
    "steps": [
        [S[1]["s"], S[2]["s"], "Step 1", "Settings, System, For developers"],
        [S[2]["s"], S[3]["s"], "Step 2", "Turn on End task"],
        [S[3]["s"], S[4]["s"], "Step 3", "Right-click the app on your taskbar"],
        [S[4]["s"], S[6]["s"], "Step 4", "Click End task"],
    ],
    "highlight": [],
    "sfx": [[toggle_click + 0.1, "pop"], [end_click + 0.2, "ding"], [S[6]["s"] + 1.9, "pop"]],
}
json.dump(spec, open(os.path.join(D, "spec_full.json"), "w"), indent=1)
print("duration", dur, "toggle", toggle_click, "rclick", rclick, "end", end_click)
