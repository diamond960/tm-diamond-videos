"""short03: What's slowing your PC? Check this - Task Manager, sort by CPU / Memory, End task.
Plan block 1 (Speed up a slow PC), episode 2. Team Diamond template (fb/07 look), real Task Manager on Windows (dark mode).
The busy app is a small real program ("HeavyApp") started on the capture PC so there is something to find."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]


def word(text, after=0.0, nth=0):
    hits = [w for w in W if w["w"].strip(".,?!").lower() == text.lower() and w["s"] >= after - 0.01]
    return hits[nth]


dur = round(T["duration"] + 0.35, 2)
cpu_w = word("cpu", S[3]["s"])
top_w = word("top", S[4]["s"])
mem_w = word("memory", S[5]["s"])
need_w = word("need", S[6]["s"])
end_w = word("end", S[6]["s"])

CPU = (608, 238)
MEM = (682, 238)
ROW = (338, 277)
END = (1483, 187)
cpu_click = cpu_w["s"] + 0.05
mem_click = mem_w["s"]
resort = S[6]["s"] - 0.25
row_click = need_w["e"] + 0.05
end_click = end_w["s"]

spec = {
    "layout": "tmd",
    "captures": "captures/short03",
    "narration": "shorts/03/tight.wav",
    "words": "shorts/03/tight.json",
    "script": "shorts/03/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": [
        [0.0, "001_opened.png"],
        [cpu_click + 0.12, "003_sorted_cpu.png"],
        [mem_click + 0.12, "005_sorted_mem.png"],
        [resort + 0.12, "006_back_cpu.png"],
        [row_click + 0.1, "007_selected.png"],
        [end_click + 0.2, "009_ended.png"],
    ],
    "cam": [
        [0.0, 455, 380, 400, 0],                        # Task Manager: names + CPU column
        [S[2]["s"] - 0.1, 520, 400, 460, 0.4],          # "Task Manager opens"
        [S[3]["s"], 560, 330, 380, 0.45],               # in on the CPU column header
        [cpu_click + 0.3, 455, 380, 380, 0.45],         # the app at the top
        [mem_click - 0.4, 520, 380, 380, 0.4],          # Memory column
        [resort, 455, 380, 380, 0.4],                   # back to CPU, the top app
        [row_click + 0.3, 1380, 300, 380, 0],           # cut to the End task button
        [end_click + 0.5, 455, 380, 380, 0],            # cut back: the app is gone, CPU drops
        [S[7]["s"], 520, 400, 460, 0.5],
    ],
    "cursor": [
        [S[3]["s"], 900, 520],
        [cpu_click - 0.05, CPU[0], CPU[1]],
        [mem_click - 0.08, MEM[0], MEM[1]],
        [resort - 0.05, CPU[0], CPU[1]],
        [row_click - 0.05, ROW[0], ROW[1]],
        [end_click - 0.08, END[0], END[1]],
        [end_click + 0.7, 1100, 560],
    ],
    "clicks": [cpu_click, mem_click, resort, row_click, end_click],
    "keys": [[S[1]["s"] + 0.05, ["Ctrl", "Shift", "Esc"], 1.35, 0.58]],
    "boxes": [
        [S[3]["s"] + 0.2, [572, 214, 73, 48], 1.0],                     # CPU header
        [top_w["s"] - 0.3, [222, 265, 640, 26], 1.9, [255, 70, 70]],     # HeavyApp row, 45.8% CPU
        [mem_w["s"] - 0.35, [645, 214, 73, 48], 0.9],                   # Memory header
        [row_click - 0.2, [222, 265, 640, 26], 0.6],                    # select the app
        [end_click - 0.45, [1436, 163, 94, 48], 0.9],                   # End task
        [end_click + 0.45, [572, 214, 73, 48], 1.4],                    # CPU total drops
    ],
    "card": {"t0": 0.0, "t1": round(S[0]["e"] + 0.3, 2), "y": 313 + 520,
             "title": "Why is your PC so slow?", "sub": "One app was using this much CPU",
             "count": [0, 46], "suffix": "% CPU", "count_t": 0.3, "count_dur": 1.4},
    "highlight": [],
    "sfx": [[end_click + 0.3, "ding"]],
    "follow": S[7]["s"],
    "follow_y": 0.55,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "cpu", cpu_click, "mem", mem_click, "row", row_click, "end", end_click)
