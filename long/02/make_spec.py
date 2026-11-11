"""long02: Windows 11 Running Slow? 10 Fixes That Actually Work (landscape, real Windows screens).
Plan block 1 (Speed up a slow PC). Every beat is one spoken sentence (long/02/final.json, 81 sentences):
the real screenshot, the camera (screen px), a green/red box on the exact control and real clicks.
Screens: captures/long02_01..07 plus the Short captures short03 (Task Manager), short05 (Visual effects)
and fb08 (Temporary files), copied into captures/long02_all/ with a section prefix."""
import json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(D))
T = json.load(open(os.path.join(D, "final.json")))
S = T["sentences"]
SRC = {"a": "long02_01", "b": "short03", "c": "long02_02", "d": "long02_03", "e": "short05",
       "f": "long02_04", "g": "fb08", "h": "long02_05", "i": "long02_06", "j": "long02_07"}
ALL = os.path.join(R, "captures", "long02_all")
os.makedirs(ALL, exist_ok=True)
for k, src in SRC.items():
    for f in os.listdir(os.path.join(R, "captures", src)):
        if f.endswith(".png"):
            dst = os.path.join(ALL, f"{k}_{f}")
            if not os.path.exists(dst):
                shutil.copy(os.path.join(R, "captures", src, f), dst)

RED = [255, 70, 70]
# app window on each capture (screen px) and screens that show the whole desktop on purpose
WINS = {"f": (610, 180, 1250, 900), "j": (360, 170, 1560, 930)}
FULL = {"c_005_restarting.png", "c_006_after.png", "d_004_taskbar.png", "d_005_jumplist.png", "f_005_applied.png"}
WIDE = (940, 530, 840)
# sentence -> beat: shot, cam (cx, cy, h), boxes [(rect, color)], clicks [(x, y, frac, shot_after)], keys
B = {
    # hook: the results you will get
    0: dict(shot="b_003_sorted_cpu.png", cam=(560, 330, 520), boxes=[([218, 263, 646, 28], RED)]),
    1: dict(shot="a_003_startup_list.png", cam=(700, 330, 560)),
    2: dict(shot="g_004_ready.png", cam=(900, 360, 560), boxes=[([899, 283, 143, 20], RED)]),
    3: dict(shot="h_003_on.png", cam=(800, 420, 600)),
    4: dict(shot="g_007_done.png", cam=(900, 330, 560)),
    5: dict(shot="j_005_done.png", cam=(820, 450, 720)),
    # fix 1: startup apps
    6: dict(shot="a_001_tm_open.png", cam=WIDE),
    7: dict(shot="a_001_tm_open.png", cam=(700, 400, 620)),
    8: dict(shot="a_001_tm_open.png", cam=(600, 350, 560), keys=["Ctrl", "Shift", "Esc"]),
    9: dict(shot="a_002_hover_nav.png", cam=(520, 350, 520), boxes=[([172, 328, 40, 36], None)],
            clicks=[(192, 346, 0.7, "a_003_startup_list.png")]),
    10: dict(shot="a_003_startup_list.png", cam=(700, 330, 520), boxes=[([583, 261, 200, 32], None)]),
    11: dict(shot="a_003_startup_list.png", cam=(600, 340, 480), boxes=[([218, 322, 700, 28], RED)]),
    12: dict(shot="a_003_startup_list.png", cam=(890, 330, 760), boxes=[([1472, 163, 88, 48], None)],
             clicks=[(338, 336, 0.25, "a_004_selected.png"), (1516, 187, 0.85, "a_006_disabled.png")]),
    13: dict(shot="a_006_disabled.png", cam=(520, 340, 420), boxes=[([583, 323, 99, 28], None)]),
    14: dict(shot="a_006_disabled.png", cam=(580, 350, 470)),
    15: dict(shot="a_006_disabled.png", cam=WIDE),
    # fix 2: the app slowing you down
    16: dict(shot="b_001_opened.png", cam=WIDE),
    17: dict(shot="b_001_opened.png", cam=(520, 330, 520), keys=["Ctrl", "Shift", "Esc"]),
    18: dict(shot="b_001_opened.png", cam=(560, 320, 480), boxes=[([572, 214, 73, 48], None)],
             clicks=[(608, 238, 0.45, "b_003_sorted_cpu.png")]),
    19: dict(shot="b_003_sorted_cpu.png", cam=(480, 320, 440), boxes=[([218, 263, 646, 28], RED)]),
    20: dict(shot="b_004_sorted_cpu2.png", cam=(500, 300, 420), boxes=[([572, 263, 73, 28], RED)]),
    21: dict(shot="b_004_sorted_cpu2.png", cam=(600, 320, 480), boxes=[([645, 214, 73, 48], None)],
             clicks=[(682, 238, 0.4, "b_005_sorted_mem.png")]),
    22: dict(shot="b_005_sorted_mem.png", cam=(860, 330, 760), boxes=[([1436, 163, 94, 48], None)],
             clicks=[(608, 238, 0.12, "b_006_back_cpu.png"), (338, 277, 0.5, "b_007_selected.png"),
                     (1483, 187, 0.9, "b_009_ended.png")]),
    23: dict(shot="b_009_ended.png", cam=(560, 300, 440), boxes=[([572, 214, 73, 48], None)]),
    # fix 3: restart Windows Explorer
    24: dict(shot="c_001_processes.png", cam=WIDE),
    25: dict(shot="c_001_processes.png", cam=(600, 400, 600)),
    26: dict(shot="c_001_processes.png", cam=(520, 380, 480), boxes=[([218, 357, 646, 28], None)]),
    27: dict(shot="c_001_processes.png", cam=(860, 330, 760), boxes=[([1419, 163, 111, 48], None)],
             clicks=[(338, 371, 0.2, "c_003_selected.png"), (1474, 187, 0.8, "c_005_restarting.png")]),
    28: dict(shot="c_005_restarting.png", cam=(960, 540, 1080), after=(0.6, "c_006_after.png")),
    29: dict(shot="c_006_after.png", cam=(960, 540, 1080)),
    # fix 4: End task on the taskbar
    30: dict(shot="d_001_dev_page.png", cam=WIDE),
    31: dict(shot="d_001_dev_page.png", cam=(800, 300, 560), keys=["Win", "I"]),
    32: dict(shot="d_001_dev_page.png", cam=(1100, 450, 560), boxes=[([640, 430, 950, 52], None)],
             clicks=[(1538, 456, 0.5, "d_003_toggle_on.png")]),
    33: dict(shot="d_004_taskbar.png", cam=(1150, 860, 560), boxes=[([1205, 1032, 44, 48], None)],
             clicks=[(1227, 1056, 0.7, "d_005_jumplist.png")]),
    34: dict(shot="d_005_jumplist.png", cam=(1220, 900, 420), boxes=[([1083, 955, 287, 28], None)]),
    35: dict(shot="d_005_jumplist.png", cam=(1220, 900, 420), clicks=[(1150, 969, 0.35, None)]),
    36: dict(shot="d_003_toggle_on.png", cam=WIDE),
    37: dict(shot="d_003_toggle_on.png", cam=(1000, 450, 700)),
    38: dict(shot="e_001_visual_page_on.png", cam=WIDE),
    # fix 5: animations and transparency
    39: dict(shot="e_001_visual_page_on.png", cam=(940, 450, 720)),
    40: dict(shot="e_001_visual_page_on.png", cam=(900, 330, 600)),
    41: dict(shot="e_001_visual_page_on.png", cam=(800, 300, 560), keys=["Win", "I"]),
    42: dict(shot="e_001_visual_page_on.png", cam=(1100, 380, 560), boxes=[([1502, 383, 72, 40], None)],
             clicks=[(1538, 403, 0.6, "e_003_animation_off.png")]),
    43: dict(shot="e_003_animation_off.png", cam=(1100, 360, 560), boxes=[([1502, 310, 72, 40], None)],
             clicks=[(1538, 330, 0.6, "e_005_transparency_off.png")]),
    44: dict(shot="e_005_transparency_off.png", cam=(1100, 360, 600), boxes=[([1430, 300, 160, 130], None)]),
    # fix 6: adjust for best performance
    45: dict(shot="f_001_dialog.png", cam=(930, 540, 840)),
    46: dict(shot="f_001_dialog.png", cam=(930, 520, 760)),
    47: dict(shot="f_001_dialog.png", cam=(850, 360, 400), boxes=[([636, 341, 360, 22], None)],
             clicks=[(648, 352, 0.6, "f_003_best_selected.png")]),
    48: dict(shot="f_003_best_selected.png", cam=(930, 560, 520)),
    49: dict(shot="f_003_best_selected.png", cam=(900, 690, 420), boxes=[([792, 751, 75, 23], None)],
             clicks=[(830, 762, 0.5, "f_005_applied.png")]),
    50: dict(shot="f_005_applied.png", cam=(960, 540, 1080)),
    # fix 7: temporary files
    51: dict(shot="g_001_storage.png", cam=WIDE),
    52: dict(shot="g_001_storage.png", cam=(900, 400, 600)),
    53: dict(shot="g_001_storage.png", cam=(800, 260, 560), boxes=[([725, 145, 99, 38], None)], keys=["Win", "I"]),
    54: dict(shot="g_001_storage.png", cam=(1000, 380, 560), boxes=[([591, 301, 1000, 69], None)],
             clicks=[(1091, 336, 0.5, "g_003_temp_page.png")]),
    55: dict(shot="g_003_temp_page.png", cam=(1000, 450, 620)),
    56: dict(shot="g_004_ready.png", cam=(900, 350, 480), boxes=[([899, 283, 143, 20], RED)]),
    57: dict(shot="g_004_ready.png", cam=(800, 350, 500), boxes=[([591, 276, 102, 32], None)],
             clicks=[(642, 292, 0.7, "g_006_confirm.png")]),
    58: dict(shot="g_006_confirm.png", cam=(850, 500, 520), boxes=[([753, 581, 184, 32], None)],
             clicks=[(845, 597, 0.6, "g_007_done.png")]),
    59: dict(shot="g_008_done2.png", cam=WIDE),
    # fix 8: Storage Sense
    60: dict(shot="h_001_page_off.png", cam=WIDE),
    61: dict(shot="h_001_page_off.png", cam=(900, 260, 560), boxes=[([866, 165, 180, 38], None)]),
    62: dict(shot="h_001_page_off.png", cam=(800, 400, 520), boxes=[([591, 367, 72, 40], None)],
             clicks=[(627, 387, 0.6, "h_003_on.png")]),
    63: dict(shot="h_003_on.png", cam=(800, 420, 560), boxes=[([591, 326, 436, 27], None)]),
    64: dict(shot="h_003_on.png", cam=(760, 520, 520), boxes=[([587, 548, 288, 40], None)],
             clicks=[(731, 568, 0.2, "h_004_schedule_open.png"), (731, 496, 0.7, "h_006_final.png")]),
    # fix 9: uninstall apps
    65: dict(shot="i_001_apps.png", cam=WIDE),
    66: dict(shot="i_001_apps.png", cam=(800, 260, 560), boxes=[([698, 165, 176, 38], None)], keys=["Win", "I"]),
    67: dict(shot="i_001_apps.png", cam=(1250, 380, 560), boxes=[([1450, 280, 145, 40], None)],
             clicks=[(1522, 300, 0.25, "i_002_sort_open.png"), (1534, 412, 0.65, "i_003_sorted.png")]),
    68: dict(shot="i_003_sorted.png", cam=(1250, 400, 520), boxes=[([1534, 344, 40, 40], None)],
             clicks=[(1554, 364, 0.6, "i_004_menu.png")]),
    69: dict(shot="i_004_menu.png", cam=(1300, 420, 420), boxes=[([1307, 425, 262, 28], RED)],
             moves=[(1438, 439, 0.5)]),
    70: dict(shot="i_003_sorted.png", cam=WIDE),
    # fix 10: optimize drives
    71: dict(shot="j_001_window.png", cam=(960, 550, 840)),
    72: dict(shot="j_001_window.png", cam=(960, 500, 760)),
    73: dict(shot="j_001_window.png", cam=(720, 380, 500), boxes=[([382, 320, 642, 19], None)],
             clicks=[(450, 329, 0.5, "j_002_drive_selected.png")]),
    74: dict(shot="j_002_drive_selected.png", cam=(800, 420, 500), boxes=[([933, 456, 123, 26], None)],
             clicks=[(994, 469, 0.5, "j_004_optimizing.png")]),
    75: dict(shot="j_004_optimizing.png", cam=(720, 360, 460)),
    76: dict(shot="j_005_done.png", cam=(720, 360, 460), boxes=[([382, 320, 642, 19], None)]),
    77: dict(shot="j_005_done.png", cam=(700, 530, 420), boxes=[([376, 502, 540, 70], RED), ([907, 527, 149, 26], None)]),
    # outro
    78: dict(shot="a_006_disabled.png", cam=WIDE),
    79: dict(shot="g_007_done.png", cam=(900, 400, 640)),
    80: dict(shot="b_009_ended.png", cam=WIDE),
}
SECTIONS = {0: "Windows 11 Running Slow? 10 Fixes", 6: "Fix 1: Stop apps starting with Windows",
            16: "Fix 2: Find the app slowing you down", 24: "Fix 3: Restart Windows Explorer",
            30: "Fix 4: Add End task to the taskbar", 39: "Fix 5: Turn off animations",
            45: "Fix 6: Adjust for best performance", 51: "Fix 7: Delete temporary files",
            60: "Fix 8: Turn on Storage Sense", 65: "Fix 9: Uninstall apps you never use",
            71: "Fix 10: Optimize your drive", 78: "Recap"}

shots, cams, boxes, cursor, clicks, keys, titles, on = [], [], [], [], [], [], [], []
assert len(S) == 81, len(S)
for i, s in enumerate(S):
    b = B[i]
    t0, t1 = s["s"] - (0.25 if i else 0), s["e"]
    nxt = S[i + 1]["s"] - 0.25 if i + 1 < len(S) else T["duration"] + 0.6
    shots.append([max(0.0, t0), b["shot"]])
    cx, cy, h = b["cam"]
    # keep the camera inside the app window (no wallpaper at the edges)
    win = WINS.get(b["shot"][0], (160, 110, 1720, 950))
    if b["shot"] in FULL:
        win = None
    if win and h < 1000:
        x0, y0, x1, y1 = win
        w = h * 16 / 9
        h = min(h, y1 - y0, (x1 - x0) * 9 / 16)
        w = h * 16 / 9
        cx = min(max(cx, x0 + w / 2), x1 - w / 2)
        cy = min(max(cy, y0 + h / 2), y1 - h / 2)
    cams.append([max(0.0, t0), cx, cy, h, 0 if i in SECTIONS else 0.55])
    for rect, col in b.get("boxes", []):
        e = [round(t0 + 0.35, 2), rect, round(max(1.2, nxt - t0 - 0.5), 2)]
        if col:
            e.append(col)
        boxes.append(e)
    if b.get("keys"):
        keys.append([round(s["s"] + 0.05, 2), b["keys"], 1.4, 0.2])
    pts = b.get("clicks", []) + [(x, y, f, None) for x, y, f in b.get("moves", [])]
    if pts:
        on.append([round(t0, 2), round(nxt, 2)])
        cursor.append([round(t0, 2), 1100, 700])
        for x, y, f, after in b.get("clicks", []):
            ct = round(s["s"] + f * (s["e"] - s["s"]), 2)
            cursor.append([round(ct - 0.05, 2), x, y])
            clicks.append(ct)
            if after:
                shots.append([round(ct + 0.12, 2), after])
        for x, y, f in b.get("moves", []):
            cursor.append([round(s["s"] + f * (s["e"] - s["s"]), 2), x, y])
    if b.get("after"):
        f, after = b["after"]
        shots.append([round(s["s"] + f * (s["e"] - s["s"]), 2), after])
    if i in SECTIONS:
        titles.append([round(max(0.0, t0) + 0.1, 2), SECTIONS[i], 2.6])

shots.sort(key=lambda x: x[0])
cursor.sort(key=lambda x: x[0])
spec = {
    "size": [1920, 1080],
    "layout": "full",
    "captures": "captures/long02_all",
    "narration": "long/02/final.wav",
    "words": "long/02/final.json",
    "script": "long/02/final.txt",
    "duration": round(T["duration"] + 0.6, 2),
    "handle": "TM_Diamond",
    "captions": True,
    "shots": shots, "cam": cams, "boxes": boxes, "cursor": cursor, "cursor_on": on,
    "clicks": clicks, "keys": keys, "titles": titles,
    "highlight": [], "sfx": [],
    "follow": S[80]["s"],
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", spec["duration"], "shots", len(shots), "clicks", len(clicks), "titles", len(titles))
