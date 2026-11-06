"""fb06: Website won't load? Flush DNS. Real Windows screens from captures/fb06 (engine/realcut.py)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(D, "voice.words.json")))
dur = round(words["duration"] + 0.45, 2)
typing_cmd = [f"{i:03d}_run_type.png" for i in (5, 6, 7)]
typing_ip = [f"{i:03d}_cmd_type.png" for i in range(9, 27)]
shots = [[0.0, "002_edge_error.png"], [2.75, "004_run.png"]]
# "Type C M D": one real screenshot per character
for k, f in enumerate(typing_cmd):
    shots.append([4.95 + 0.32 * k, f])
shots.append([7.15, "008_cmd_open.png"])
# "ipconfig /flushdns": one real screenshot per character, spread over the spoken words
t0, t1 = 8.70, 11.35
for k, f in enumerate(typing_ip):
    shots.append([round(t0 + (t1 - t0) * k / (len(typing_ip) - 1), 3), f])
shots.append([12.25, "027_cmd_result.png"])
spec = {
    "captures": "captures/fb06",
    "narration": "fb/06/voice.mp3",
    "words": "fb/06/voice.words.json",
    "duration": dur,
    "handle": "TM_Diamond",
    "shots": shots,
    "cam": [
        [0.0, 805, 410, 780, 0],           # Edge: "Hmmm... can't reach this page"
        [0.1, 790, 395, 640, 1.6],         # push in on the error
        [2.55, 228, 780, 700, 0.5],        # Run dialog (bottom left)
        [4.7, 226, 800, 640, 0.4],         # closer on the Open box while typing
        [7.15, 520, 300, 620, 0.45],       # terminal prompt
        [8.5, 470, 290, 520, 0.4],
        [10.2, 560, 290, 520, 1.2],        # follow the typing to the right
        [12.25, 515, 330, 720, 0.45],      # result lines
        [16.2, 520, 330, 860, 0.6],        # ease back, result still readable
    ],
    "keys": [[2.24, ["Win", "R"], 1.5, 0.42], [6.70, ["Enter"], 0.9, 0.42], [11.54, ["Enter"], 1.0, 0.62]],
    "typing": [[4.95, 5.6, 3], [8.70, 11.35, 18]],
    "circles": [[13.0, [312, 338, 402, 22], 3.3]],
    "highlight": ["cmd", "flush", "dns", "done"],
    "sfx": [[2.75, "open"], [7.15, "open"], [13.62, "ding"]],
    "follow": 16.35,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "shots", len(shots))
