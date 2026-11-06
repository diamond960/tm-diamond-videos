"""fb06: Website won't load? Flush DNS.  (OLD full-frame look - new vertical videos copy fb/07, the Team Diamond template)
Real Windows screens (captures/fb06, taken on a real Windows PC by engine/wincap.ps1), edited by engine/realcut.py.
Narration tightened with engine/tighten.py (fb/06/tight.wav + tight.json): every event is placed on the spoken words."""
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
r = word("R", S[1]["s"])
cmd = word("CMD", S[2]["s"])
enter1 = word("enter", S[2]["s"])
ip = word("IP", S[3]["s"])
dns = word("DNS", S[3]["s"])
press2 = word("press", S[4]["s"])
enter2 = word("enter", S[4]["s"])

run_at = r["s"] + 0.15                     # the Run box appears as he says "R"
cmd_open = S[2]["e"] + 0.05                # terminal opens after "press Enter"
type_ip0, type_ip1 = ip["s"], dns["e"]
result_at = enter2["e"] - 0.05

shots = [[0.0, "002_edge_error.png"], [run_at, "004_run.png"]]
for k, f in enumerate(["005_run_type.png", "006_run_type.png", "007_run_type.png"]):
    shots.append([round(cmd["s"] + k * (cmd["e"] - cmd["s"]) / 3, 3), f])
shots.append([cmd_open, "008_cmd_open.png"])
typed = [f"{i:03d}_cmd_type.png" for i in range(9, 27)]
for k, f in enumerate(typed):
    shots.append([round(type_ip0 + (type_ip1 - type_ip0) * k / (len(typed) - 1), 3), f])
shots.append([result_at, "027_cmd_result.png"])

spec = {
    "captures": "captures/fb06",
    "narration": "fb/06/tight.wav",
    "words": "fb/06/tight.json",
    "script": "fb/06/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "shots": shots,
    "cam": [
        [0.0, 805, 410, 780, 0],                       # Edge: "Hmmm... can't reach this page"
        [0.05, 790, 395, 640, 1.6],                    # push in on the error
        [run_at - 0.05, 228, 780, 700, 0.45],          # the real Run box, bottom left
        [cmd["s"] - 0.1, 226, 800, 640, 0.35],         # closer while typing cmd
        [cmd_open, 520, 300, 620, 0.4],                # the real Command Prompt
        [type_ip0 - 0.25, 470, 290, 520, 0.35],
        [type_ip0 + 0.9, 560, 290, 520, 1.2],          # follow the typing to the right
        [result_at, 515, 330, 720, 0.4],               # the result lines
        [S[6]["s"], 520, 330, 860, 0.6],
    ],
    "keys": [[S[1]["s"] + 0.05, ["Win", "R"], 1.3, 0.42],
             [enter1["s"] - 0.05, ["Enter"], 0.8, 0.42],
             [press2["s"], ["Enter"], 0.9, 0.62]],
    "typing": [[cmd["s"], cmd["e"], 3], [type_ip0, type_ip1, 18]],
    "circles": [[S[5]["s"] - 0.1, [312, 338, 402, 22], 2.1]],
    "highlight": ["cmd", "flush", "dns", "done"],
    "sfx": [[run_at, "open"], [cmd_open, "open"], [S[5]["s"], "ding"]],
    "follow": S[6]["s"],
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "run", run_at, "cmd_open", cmd_open, "result", result_at)
