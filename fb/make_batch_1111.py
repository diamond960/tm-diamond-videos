"""Windows batch 2026-11-11 (fb11-fb15): 15-30 s Facebook reels cut from the real Windows screens recorded for
long/02 (captures/long02_all), in the Team Diamond template with the owner's full-screen framing.
Run: python3 fb/make_batch_1111.py  -> fb/NN/spec.json for each clip that has fb/NN/tight.json.

Beat format, one per spoken sentence (index = sentence number):
  shot  - screenshot shown from the start of the sentence
  cam   - (cx, cy, h) in screen pixels; (960, 540, 1080) = the whole screen
  boxes - [([x, y, w, h], colour or None), ...] drawn from the start of the sentence to its end
  clicks- [(x, y, frac, next_shot), ...] click at frac of the sentence, then show next_shot
  keys  - keycaps at the start of the sentence
  step  - (kicker, text) label in the info band"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = (960, 540, 1080)
RED = [255, 70, 70]
HIDE = [[1722, 976, 198, 54]]   # the capture PC's "Test Mode / Windows Server" desktop watermark

CLIPS = {
    11: dict(
        title="Taskbar frozen? Restart this, not your PC",
        caption="Taskbar frozen? Don't restart your PC, do this 👇 #reels #windows11",
        card=dict(title="Windows fix", sub="Taskbar or Start menu frozen?", big="Don't restart"),
        beats=[
            dict(shot="c_006_after.png", cam=FULL),
            dict(shot="c_001_processes.png", cam=FULL, keys=["Ctrl", "Shift", "Esc"], step=("Step 1", "Open Task Manager")),
            dict(shot="c_001_processes.png", cam=(700, 420, 760), boxes=[([218, 357, 646, 28], None)],
                 clicks=[(338, 371, 0.55, "c_003_selected.png")], step=("Step 2", "Select Windows Explorer")),
            dict(shot="c_003_selected.png", cam=(960, 420, 760), boxes=[([1419, 163, 111, 48], None)],
                 clicks=[(1474, 187, 0.5, "c_005_restarting.png")], step=("Step 3", "Click Restart task")),
            dict(shot="c_005_restarting.png", cam=FULL, after=(0.5, "c_006_after.png"), step=("Done", "Taskbar back, apps still open")),
            dict(shot="c_006_after.png", cam=FULL),
        ]),
    12: dict(
        title="Your PC can delete junk files by itself",
        caption="Your PC can delete junk files by itself 🧹 Turn this on #reels #windows11",
        card=dict(title="Windows fix", sub="Free space without lifting a finger", big="Storage Sense"),
        beats=[
            dict(shot="h_006_final.png", cam=FULL),
            dict(shot="h_001_page_off.png", cam=FULL, boxes=[([866, 165, 180, 38], None)], keys=["Win", "I"],
                 step=("Step 1", "Settings, System, Storage, Storage Sense")),
            dict(shot="h_001_page_off.png", cam=(820, 420, 760), boxes=[([591, 367, 72, 40], None)],
                 clicks=[(627, 387, 0.5, "h_003_on.png")], step=("Step 2", "Turn on automatic cleanup")),
            dict(shot="h_003_on.png", cam=(820, 480, 760), boxes=[([587, 548, 288, 40], None)],
                 clicks=[(731, 568, 0.3, "h_004_schedule_open.png"), (731, 496, 0.75, "h_006_final.png")],
                 step=("Step 3", "Run it every week")),
            dict(shot="h_006_final.png", cam=FULL, boxes=[([591, 326, 436, 27], None)], step=("Done", "Windows cleans up for you")),
            dict(shot="h_006_final.png", cam=FULL),
        ]),
    13: dict(
        title="These apps are eating your storage",
        caption="These apps are eating your storage 😳 Find them in 10 seconds #reels #windows11",
        card=dict(title="Windows fix", sub="Low on space?", big="Biggest apps first"),
        beats=[
            dict(shot="i_003_sorted.png", cam=FULL),
            dict(shot="i_001_apps.png", cam=FULL, boxes=[([698, 165, 176, 38], None)], keys=["Win", "I"],
                 step=("Step 1", "Settings, Apps, Installed apps")),
            dict(shot="i_001_apps.png", cam=(1250, 400, 760), boxes=[([1450, 280, 145, 40], None)],
                 clicks=[(1522, 300, 0.25, "i_002_sort_open.png"), (1534, 412, 0.7, "i_003_sorted.png")],
                 step=("Step 2", "Sort by size")),
            dict(shot="i_003_sorted.png", cam=(1250, 420, 760), boxes=[([1534, 344, 40, 40], None)],
                 clicks=[(1554, 364, 0.6, "i_004_menu.png")], step=("Step 3", "Three dots on an app you never use")),
            dict(shot="i_004_menu.png", cam=(1250, 440, 760), boxes=[([1307, 425, 262, 28], RED)], step=("Step 4", "Uninstall")),
            dict(shot="i_004_menu.png", cam=FULL),
        ]),
    14: dict(
        title="One setting makes an old PC feel faster",
        caption="One setting makes an old PC feel faster ⚡ #reels #windows11",
        card=dict(title="Windows fix", sub="Old PC feeling slow?", big="Best performance"),
        beats=[
            dict(shot="f_003_best_selected.png", cam=FULL),
            dict(shot="f_001_dialog.png", cam=FULL, step=("Step 1", "Adjust the appearance and performance of Windows")),
            dict(shot="f_001_dialog.png", cam=(900, 440, 760), boxes=[([636, 341, 360, 22], None)],
                 clicks=[(648, 352, 0.5, "f_003_best_selected.png")], step=("Step 2", "Adjust for best performance")),
            dict(shot="f_003_best_selected.png", cam=(900, 580, 760), boxes=[([792, 751, 75, 23], None)],
                 clicks=[(830, 762, 0.5, "f_005_applied.png")], step=("Step 3", "Click OK")),
            dict(shot="f_005_applied.png", cam=FULL, step=("Done", "Plainer look, faster PC")),
            dict(shot="f_005_applied.png", cam=FULL),
        ]),
    15: dict(
        title="Your drive needs a tune-up (free in Windows)",
        caption="Your drive needs a tune-up, and Windows does it free 🔧 #reels #windows11",
        card=dict(title="Windows fix", sub="Keep your drive fast", big="Optimize"),
        beats=[
            dict(shot="j_005_done.png", cam=FULL),
            dict(shot="j_001_window.png", cam=FULL, step=("Step 1", "Defragment and Optimize Drives")),
            dict(shot="j_001_window.png", cam=(800, 420, 760), boxes=[([382, 320, 642, 19], None)],
                 clicks=[(450, 329, 0.5, "j_002_drive_selected.png")], step=("Step 2", "Select your C drive")),
            dict(shot="j_002_drive_selected.png", cam=(800, 440, 760), boxes=[([933, 456, 123, 26], None)],
                 clicks=[(994, 469, 0.5, "j_004_optimizing.png")], step=("Step 3", "Click Optimize")),
            dict(shot="j_005_done.png", cam=(800, 460, 760), boxes=[([376, 502, 540, 70], RED)], step=("Tip", "SSD? Windows sends trim instead")),
            dict(shot="j_005_done.png", cam=FULL),
        ]),
}


def build(n, c):
    d = os.path.join(ROOT, "fb", f"{n:02d}")
    T = json.load(open(os.path.join(d, "tight.json")))
    S = T["sentences"]
    assert len(S) == len(c["beats"]), (n, len(S), len(c["beats"]))
    dur = round(T["duration"] + 0.35, 2)
    shots, cam, boxes, clicks, cursor, keys, steps, sfx = [], [], [], [], [], [], [], []
    last_cam = None
    for i, (s, b) in enumerate(zip(S, c["beats"])):
        t0, t1 = s["s"] - (0.12 if i else 0), (S[i + 1]["s"] - 0.12 if i + 1 < len(S) else dur)
        shots.append([round(max(0, t0), 3), b["shot"]])
        cc = b.get("cam", FULL)
        if cc != last_cam:
            cam.append([round(max(0, t0), 3), *cc, 0 if i == 0 else 0.5])
            last_cam = cc
        for rect, col in b.get("boxes", []):
            boxes.append([round(s["s"] + 0.15, 3), rect, round(t1 - s["s"] - 0.2, 2)] + ([col] if col else []))
        for x, y, frac, nxt in b.get("clicks", []):
            tc = round(s["s"] + (s["e"] - s["s"]) * frac, 3)
            cursor.append([round(tc - 0.45, 3), x, y]); cursor.append([round(tc + 0.15, 3), x, y])
            clicks.append(tc); shots.append([round(tc + 0.12, 3), nxt]); sfx.append([round(tc, 3), "click"])
        if b.get("after"):
            frac, nxt = b["after"]
            shots.append([round(s["s"] + (s["e"] - s["s"]) * frac, 3), nxt])
        if b.get("keys"):
            keys.append([round(s["s"] + 0.05, 3), b["keys"], 1.2, 0.37])
        if b.get("step"):
            steps.append([round(s["s"], 3), round(t1, 3), *b["step"]])
    shots.sort(key=lambda x: x[0])
    cursor.sort(key=lambda x: x[0])
    on = [[cursor[0][0] - 0.3, cursor[-1][0] + 0.6]] if cursor else []
    spec = {
        "layout": "tmd", "framing": "full", "hide": HIDE,
        "captures": "captures/long02_all", "narration": f"fb/{n:02d}/tight.wav", "words": f"fb/{n:02d}/tight.json",
        "script": f"fb/{n:02d}/script.txt", "duration": dur, "handle": "TM_Diamond", "captions": False,
        "shots": shots, "cam": cam, "cursor": cursor, "cursor_on": on, "clicks": clicks, "keys": keys, "boxes": boxes,
        "card": dict(t0=0.0, t1=round(S[0]["e"] + 0.3, 2), **c["card"]),
        "steps": steps, "highlight": [], "sfx": sfx, "follow": round(S[-1]["s"], 2),
    }
    json.dump(spec, open(os.path.join(d, "spec.json"), "w"), indent=1)
    post = os.path.join(d, "post.json")
    if not os.path.exists(post):
        json.dump({"title": c["title"], "series": "Windows", "caption": c["caption"], "length_s": dur, "status": "draft",
                   "method": "Team Diamond template, full screen, real Windows screens (captures/long02_all)"},
                  open(post, "w"), indent=1, ensure_ascii=False)
    print(n, "duration", dur)


if __name__ == "__main__":
    for n, c in CLIPS.items():
        if os.path.exists(os.path.join(ROOT, "fb", f"{n:02d}", "tight.json")):
            build(n, c)
