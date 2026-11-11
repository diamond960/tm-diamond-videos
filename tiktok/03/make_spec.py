"""tiktok03: "6 free fixes for a slow Windows PC" - 69 s TikTok (owner rule: TikTok videos over 1 minute).
Real Windows screens recorded for long/02 (captures/long02_all), Team Diamond template, full-screen framing.
Beats reuse fb/make_batch_1111.py's builder format."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fb"))
from make_batch_1111 import FULL, RED, HIDE

D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
S = T["sentences"]
TM = (700, 380, 760)
beats = [
    dict(shot="b_003_sorted_cpu.png", cam=FULL, boxes=[([218, 263, 646, 28], RED)]),
    dict(shot="f_003_best_selected.png", cam=(900, 480, 760), boxes=[([636, 341, 360, 22], None)], step=("Fix 6", "The one people never find")),
    dict(shot="a_001_tm_open.png", cam=FULL, keys=["Ctrl", "Shift", "Esc"],
         clicks=[(192, 346, 0.8, "a_003_startup_list.png")], step=("Fix 1", "Startup apps")),
    dict(shot="a_003_startup_list.png", cam=TM, boxes=[([1472, 163, 88, 48], None)],
         clicks=[(338, 336, 0.25, "a_004_selected.png"), (1516, 187, 0.75, "a_006_disabled.png")], step=("Fix 1", "Disable what you don't need")),
    dict(shot="b_001_opened.png", cam=TM, boxes=[([572, 214, 73, 48], None)],
         clicks=[(608, 238, 0.6, "b_003_sorted_cpu.png")], step=("Fix 2", "Sort Processes by CPU")),
    dict(shot="b_006_back_cpu.png", cam=TM, boxes=[([218, 263, 646, 28], RED)],
         clicks=[(338, 277, 0.45, "b_007_selected.png"), (1483, 187, 0.8, "b_009_ended.png")], step=("Fix 2", "End the app eating your CPU")),
    dict(shot="c_001_processes.png", cam=TM, boxes=[([1419, 163, 111, 48], None)],
         clicks=[(338, 371, 0.35, "c_003_selected.png"), (1474, 187, 0.75, "c_005_restarting.png")], step=("Fix 3", "Restart Windows Explorer")),
    dict(shot="c_006_after.png", cam=FULL, step=("Fix 3", "Your apps stay open")),
    dict(shot="h_001_page_off.png", cam=FULL, boxes=[([591, 367, 72, 40], None)], keys=["Win", "I"],
         clicks=[(627, 387, 0.75, "h_003_on.png")], step=("Fix 4", "Storage Sense: automatic cleanup")),
    dict(shot="h_003_on.png", cam=(820, 480, 760), boxes=[([587, 548, 288, 40], None)],
         clicks=[(731, 568, 0.3, "h_004_schedule_open.png"), (731, 496, 0.65, "h_006_final.png")], step=("Fix 4", "Every week")),
    dict(shot="i_001_apps.png", cam=FULL, boxes=[([1450, 280, 145, 40], None)],
         clicks=[(1522, 300, 0.4, "i_002_sort_open.png"), (1534, 412, 0.8, "i_003_sorted.png")], step=("Fix 5", "Installed apps, sort by size")),
    dict(shot="i_003_sorted.png", cam=(1250, 420, 760), boxes=[([1307, 425, 262, 28], RED)],
         clicks=[(1554, 364, 0.3, "i_004_menu.png")], step=("Fix 5", "Uninstall what you never use")),
    dict(shot="f_001_dialog.png", cam=FULL, step=("Fix 6", "Adjust the appearance and performance of Windows")),
    dict(shot="f_001_dialog.png", cam=(900, 520, 760), boxes=[([636, 341, 360, 22], None)],
         clicks=[(648, 352, 0.35, "f_003_best_selected.png"), (830, 762, 0.8, "f_005_applied.png")], step=("Fix 6", "Best performance, then OK")),
    dict(shot="f_005_applied.png", cam=FULL, step=("Fix 6", "Plainer look, faster PC")),
    dict(shot="i_003_sorted.png", cam=FULL, step=("Good to know", "None of these delete your files")),
    dict(shot="h_006_final.png", cam=FULL),
    dict(shot="c_006_after.png", cam=FULL),
]
assert len(beats) == len(S), (len(beats), len(S))
dur = round(T["duration"] + 0.35, 2)
shots, cam, boxes, clicks, cursor, keys, steps, sfx = [], [], [], [], [], [], [], []
last = None
for i, (s, b) in enumerate(zip(S, beats)):
    t0 = max(0, s["s"] - (0.12 if i else 0))
    t1 = S[i + 1]["s"] - 0.12 if i + 1 < len(S) else dur
    shots.append([round(t0, 3), b["shot"]])
    if b["cam"] != last:
        cam.append([round(t0, 3), *b["cam"], 0 if i == 0 else 0.5]); last = b["cam"]
    for rect, col in b.get("boxes", []):
        boxes.append([round(s["s"] + 0.15, 3), rect, round(t1 - s["s"] - 0.2, 2)] + ([col] if col else []))
    for x, y, frac, nxt in b.get("clicks", []):
        tc = round(s["s"] + (s["e"] - s["s"]) * frac, 3)
        cursor += [[round(tc - 0.45, 3), x, y], [round(tc + 0.15, 3), x, y]]
        clicks.append(tc); shots.append([round(tc + 0.12, 3), nxt]); sfx.append([tc, "click"])
    if b.get("keys"):
        keys.append([round(s["s"] + 0.05, 3), b["keys"], 1.2, 0.37])
    if b.get("step"):
        steps.append([round(s["s"], 3), round(t1, 3), *b["step"]])
shots.sort(key=lambda x: x[0]); cursor.sort(key=lambda x: x[0])
spec = {"layout": "tmd", "framing": "full", "hide": HIDE, "captures": "captures/long02_all",
        "narration": "tiktok/03/tight.wav", "words": "tiktok/03/tight.json", "script": "tiktok/03/script.txt",
        "duration": dur, "handle": "TM_Diamond", "captions": False, "shots": shots, "cam": cam, "cursor": cursor,
        "cursor_on": [[S[2]["s"], S[15]["s"]]], "clicks": clicks, "keys": keys, "boxes": boxes,
        "card": {"t0": 0.0, "t1": round(S[1]["e"] + 0.2, 2), "title": "Slow Windows PC?", "sub": "Free fixes, no files deleted",
                 "count": [0, 6], "suffix": " fixes", "count_t": 0.3, "count_dur": 1.2},
        "steps": steps, "titles": [[S[16]["s"], "Save this for later", round(S[17]["s"] - S[16]["s"], 2)]],
        "highlight": [], "sfx": sfx, "follow": round(S[17]["s"], 2)}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur)
