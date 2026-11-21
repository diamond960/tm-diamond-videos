"""long04: 9 Windows 11 Settings You Should Change Right Now (landscape, real Windows screens, 1920x1080).
Plan block 3 (Windows 11 settings to change). One beat per spoken sentence (long/04/tight.json).
Screens (all real, captured by capture/long04_XX.ps1 on the Windows capture PC):
  a = long04_01 file name extensions, c = long04_03 snap layouts, d = long04_04 dark mode,
  e = long04_05 Start recommendations, f = long04_06 notifications, g = long04_07 taskbar alignment,
  h = long04_08 hidden items, i = long04_09 privacy (General), j = long04_10 Sticky keys shortcut
(long04_02 clipboard history could not be shown on the capture PC: no Win+V panel and no Clipboard page - dropped.)
copied into captures/long04_all/ with the letter as a prefix.
Run: python3 long/04/make_spec.py"""
import glob
import json
import os
import shutil

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(D))
SRC = {"a": "long04_01", "c": "long04_03", "d": "long04_04", "e": "long04_05", "f": "long04_06",
       "g": "long04_07", "h": "long04_08", "i": "long04_09", "j": "long04_10"}
ALL = os.path.join(R, "captures", "long04_all")
os.makedirs(ALL, exist_ok=True)
for k, src in SRC.items():
    for f in os.listdir(os.path.join(R, "captures", src)):
        if f.endswith(".png") and not os.path.exists(os.path.join(ALL, f"{k}_{f}")):
            shutil.copy(os.path.join(R, "captures", src, f), os.path.join(ALL, f"{k}_{f}"))
FILES = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ALL, "*.png")))


def get(ref):
    k, label = ref.split(":", 1)
    out = [f for f in FILES if f.startswith(k + "_") and f[len(k) + 5:-4] == label]
    assert out, ref
    return out[-1]


T = json.load(open(os.path.join(D, "tight.json")))
S = T["sentences"]
RED = [255, 70, 70]
G = None
FULL = (960, 540, 1080)
HIDE = [[1722, 976, 198, 54]]   # "Test Mode / Windows Server" desktop watermark (1920x1080)


def bx(x, y, w, h, col=G, f0=None, f1=None):
    return ([x - 6, y - 5, w + 12, h + 10], col, f0, f1)


TG = lambda y, col=G, f0=None, f1=None: bx(1502, y, 72, 40, col, f0, f1)   # a Settings toggle switch
NAV = {"System": (324, 272), "Personalization": (324, 392), "Accessibility": (324, 552), "Privacy": (324, 592)}

B = {
    # hook
    0: dict(shot="a:shown", boxes=[bx(342, 416, 598, 24, RED, 0.05, 0.5)], after=[(0.55, "d:dark")]),
    1: dict(shot="e:start_page_done", after=[(0.5, "g:left_desktop")]),
    2: dict(shot="h:shown", boxes=[bx(342, 417, 598, 24)]),
    3: dict(shot="i:done", after=[(0.5, "f:before_dnd")]),
    4: dict(shot="j:after_shortcut", cam=(1100, 380, 700), boxes=[TG(289, RED, 0.3, 1.0)]),
    # 1 file name extensions
    5: dict(shot="a:hidden"),
    6: dict(shot="a:hidden", cam=(700, 420, 700), boxes=[bx(342, 416, 598, 24, G, 0.3, 1.0)]),
    7: dict(shot="a:hidden"),
    8: dict(shot="a:hidden", cam=(700, 420, 700), boxes=[bx(342, 416, 598, 24, RED, 0.2, 1.0)]),
    9: dict(shot="a:hidden", clicks=[(694, 222, 0.7, "a:ext_view_menu")]),
    10: dict(shot="a:ext_view_menu", cam=(800, 500, 760),
              clicks=[(694, 596, 0.25, "a:ext_show_menu"), (848, 701, 0.75, "a:shown")]),
    11: dict(shot="a:shown", cam=(700, 420, 700), boxes=[bx(342, 416, 598, 24, RED, 0.3, 1.0)]),
    12: dict(shot="a:shown", cam=(700, 420, 700), boxes=[bx(342, 416, 598, 24, RED)]),
    13: dict(shot="a:shown"),
    14: dict(shot="a:shown", cam=(860, 480, 860)),
    15: dict(shot="a:ext_show_menu", cam=(800, 560, 700), boxes=[bx(788, 687, 207, 28)]),
    # 2 snap layouts
    16: dict(shot="c:two_windows"),
    17: dict(shot="c:two_windows", cam=(950, 480, 900)),
    18: dict(shot="c:two_windows", clicks=[(700, 470, 0.6, "c:two_windows")]),
    19: dict(shot="c:two_windows", keys=[(["Win", "Z"], 0.45)], after=[(0.6, "c:winz")]),
    20: dict(shot="c:winz", cam=(1100, 360, 720), boxes=[bx(1052, 192, 342, 242)]),
    21: dict(shot="c:winz", cam=(1100, 360, 720), keys=[(["1"], 0.45)], boxes=[bx(1065, 206, 98, 64, RED, 0.2, 1.0)]),
    22: dict(shot="c:winz", after=[(0.12, "c:winz_layout1")]),
    23: dict(shot="c:winz_layout1"),
    24: dict(shot="c:side_by_side", cam=(960, 500, 900)),
    25: dict(shot="c:side_by_side"),
    # 3 dark mode
    26: dict(shot="d:light_desktop"),
    27: dict(shot="d:light_desktop", keys=[(["Win", "I"], 0.45)], after=[(0.6, "d:settings_open")]),
    28: dict(shot="d:settings_open", clicks=[(*NAV["Personalization"], 0.25, "d:personalization"), (1090, 570, 0.7, "d:colors")]),
    29: dict(shot="d:colors", cam=(1180, 470, 720), boxes=[bx(591, 424, 1000, 69, G, 0.0, 0.5)],
             clicks=[(1509, 459, 0.6, "d:mode_open")]),
    30: dict(shot="d:mode_open", cam=(1180, 470, 720), clicks=[(1509, 498, 0.45, "d:dark")]),
    31: dict(shot="d:dark", after=[(0.6, "d:dark_desktop")]),
    32: dict(shot="d:mode_open", cam=(1180, 470, 720), boxes=[bx(1450, 444, 118, 33)]),
    # 4 Start recommendations
    33: dict(shot="e:start_before"),
    34: dict(shot="e:start_before", cam=(760, 620, 820)),
    35: dict(shot="e:hover_personalization", clicks=[(*NAV["Personalization"], 0.25, "e:personalization"), (1090, 907, 0.7, "e:start_page")]),
    36: dict(shot="e:start_page", cam=(1100, 700, 720), boxes=[bx(591, 535, 1000, 345)]),
    37: dict(shot="e:before_s1", cam=(1100, 700, 720), clicks=[(1538, 571, 0.65, "e:after_s1")]),
    38: dict(shot="e:after_s1", cam=(1100, 700, 720), boxes=[bx(591, 680, 1000, 70, G, 0.05, 0.7)], clicks=[(1538, 717, 0.75, "e:after_s2")]),
    39: dict(shot="e:after_s2", cam=(1100, 700, 720), clicks=[(1538, 790, 0.7, "e:after_s3")]),
    40: dict(shot="e:after_s3", cam=(1100, 700, 720), clicks=[(1538, 863, 0.6, "e:after_s4")]),
    41: dict(shot="e:start_page_done", keys=[(["Win"], 0.15)], after=[(0.3, "e:start_after")]),
    42: dict(shot="e:start_after", cam=(760, 620, 820)),
    # subscribe + re-hook
    43: dict(shot="e:start_after"),
    44: dict(shot="d:dark"),
    45: dict(shot="f:hover_system"),
    # 5 notifications
    46: dict(shot="f:hover_system", cam=(960, 500, 900)),
    47: dict(shot="f:hover_system", clicks=[(*NAV["System"], 0.3, "f:system"), (1090, 512, 0.7, "f:after_dnd")]),
    48: dict(shot="f:after_dnd", cam=(1100, 380, 720), clicks=[(1538, 330, 0.6, "f:before_dnd")]),
    49: dict(shot="f:before_dnd", cam=(1100, 380, 720), boxes=[bx(591, 293, 1000, 70)]),
    50: dict(shot="f:before_dnd", cam=(1100, 420, 720), boxes=[bx(591, 368, 1000, 69)]),
    51: dict(shot="f:app_list", boxes=[bx(591, 583, 1000, 282)]),
    52: dict(shot="f:app_list", cam=(1100, 640, 720), boxes=[bx(1474, 665, 72, 40), bx(1474, 738, 72, 40)]),
    53: dict(shot="f:app_list", cam=(1100, 640, 720), boxes=[bx(1474, 665, 72, 40, RED)]),
    54: dict(shot="f:app_list"),
    # 6 taskbar alignment
    55: dict(shot="g:centered_desktop", cam=(960, 730, 700), boxes=[bx(700, 1034, 520, 44)]),
    56: dict(shot="g:hover_personalization", clicks=[(*NAV["Personalization"], 0.25, "g:personalization"), (1090, 907, 0.7, "g:taskbar_page")]),
    57: dict(shot="g:taskbar_page", clicks=[(1091, 696, 0.45, "g:behaviors")], after2=[(0.85, "g:behaviors_open")]),
    58: dict(shot="g:behaviors_open", cam=(1180, 470, 720), boxes=[bx(591, 400, 1000, 60, G, 0.0, 0.5)],
             clicks=[(1481, 429, 0.6, "g:align_open")]),
    59: dict(shot="g:align_open", cam=(1180, 470, 720), clicks=[(1481, 394, 0.5, "g:left")]),
    60: dict(shot="g:left_desktop", cam=(960, 730, 700), boxes=[bx(0, 1034, 470, 44)]),
    61: dict(shot="g:left_desktop", keys=[(["Win"], 0.25)], after=[(0.35, "g:left_start")]),
    62: dict(shot="g:align_open", cam=(1180, 470, 720)),
    # 7 hidden items
    63: dict(shot="h:before"),
    64: dict(shot="h:before", cam=(700, 420, 760), boxes=[bx(750, 110, 340, 38)]),
    65: dict(shot="h:before", clicks=[(694, 222, 0.2, "h:hid_view_menu"), (694, 596, 0.45, "h:hid_show_menu"),
                                       (848, 733, 0.78, "h:shown")]),
    66: dict(shot="h:shown", cam=(700, 440, 700), boxes=[bx(342, 417, 598, 24, RED)]),
    67: dict(shot="h:shown", cam=(700, 440, 700), boxes=[bx(342, 417, 598, 24)]),
    68: dict(shot="h:shown"),
    69: dict(shot="h:shown", cam=(860, 480, 860)),
    70: dict(shot="h:hid_show_menu", cam=(800, 580, 700), boxes=[bx(788, 719, 207, 28)]),
    # 8 privacy
    71: dict(shot="i:hover_privacy"),
    72: dict(shot="i:hover_privacy", clicks=[(*NAV["Privacy"], 0.3, "i:privacy"), (1090, 400, 0.7, "i:general")]),
    73: dict(shot="i:general", cam=(1100, 380, 720), boxes=[bx(591, 293, 1000, 70, G, 0.0, 0.33), bx(591, 366, 1000, 70, G, 0.33, 0.66),
                                                          bx(591, 439, 1000, 70, G, 0.66, 1.0)]),
    74: dict(shot="i:general", cam=(1100, 380, 720), boxes=[TG(310), TG(383), TG(456)]),
    75: dict(shot="i:before_p1", cam=(1100, 380, 720), clicks=[(1538, 330, 0.35, "i:after_p1"), (1538, 403, 0.75, "i:after_p2")]),
    76: dict(shot="i:done"),
    # 9 Sticky keys shortcut
    77: dict(shot="j:hover_accessibility"),
    78: dict(shot="j:sticky_page", cam=(1100, 380, 720), keys=[(["Shift"], 0.25), (["Shift"], 0.35), (["Shift"], 0.45),
                                                             (["Shift"], 0.55), (["Shift"], 0.65)],
             boxes=[bx(591, 272, 1000, 70)]),
    79: dict(shot="j:sticky_page"),
    80: dict(shot="j:hover_accessibility", clicks=[(*NAV["Accessibility"], 0.3, "j:accessibility"), (1090, 907, 0.7, "j:keyboard")]),
    81: dict(shot="j:keyboard", clicks=[(1091, 335, 0.5, "j:sticky")]),
    82: dict(shot="j:sticky_page", cam=(1100, 500, 760)),
    83: dict(shot="j:before_shortcut", cam=(1100, 380, 720), clicks=[(1538, 309, 0.7, "j:after_shortcut")]),
    84: dict(shot="j:after_shortcut", cam=(1100, 380, 720), boxes=[TG(289, RED)]),
    # what's next
    85: dict(shot="a:shown", after=[(0.33, "d:dark"), (0.66, "g:left_desktop")]),
    86: dict(shot="e:start_after"),
    87: dict(shot="i:done"),
    88: dict(shot="j:after_shortcut"),
}
SECTIONS = {0: "9 Windows 11 Settings", 5: "1. File name extensions", 16: "2. Snap layouts", 26: "3. Dark mode",
            33: "4. Start menu recommendations", 46: "5. Notifications", 55: "6. Taskbar alignment",
            63: "7. Hidden items", 71: "8. Privacy settings", 77: "9. Sticky keys shortcut", 85: "What's next"}

assert len(S) == len(B) == 89, (len(S), len(B))
dur = round(T["duration"] + 0.6, 2)
shots, cams, boxes, cursor, clicks, keys, titles, on, sfx = [], [], [], [], [], [], [], [], []
last_cam = None
cur = [960, 600]
for i, s in enumerate(S):
    b = B[i]
    t0 = max(0.0, s["s"] - (0.2 if i else 0))
    t1 = S[i + 1]["s"] - 0.2 if i + 1 < len(S) else dur
    span = s["e"] - s["s"]
    at = lambda f: round(s["s"] + span * f, 3)
    shots.append([round(t0, 3), get(b["shot"])])
    cc = b.get("cam", FULL)
    # gentle push-ins only (height >= 700 on the 1920x1080 screen), never past the screen edges
    h = max(700, cc[2]); w = h * 16 / 9
    cx = min(max(cc[0], w / 2), 1920 - w / 2)
    cy = min(max(cc[1], h / 2), 1080 - h / 2)
    cc = (round(cx), round(cy), h)
    if cc != last_cam:
        cams.append([round(t0, 3), *cc, 0 if i == 0 else 0.6])
        last_cam = cc
    if span > 4.0 and not b.get("after") and not b.get("after2") and not b.get("clicks") and not b.get("keys"):
        # long sentence on one screen: a slow camera move halfway (a gentle push-in or back out)
        h2 = 900 if cc[2] >= 1000 else 1080
        w2 = h2 * 16 / 9
        c2 = (round(min(max(cc[0], w2 / 2), 1920 - w2 / 2)), round(min(max(cc[1], h2 / 2), 1080 - h2 / 2)), h2)
        cams.append([at(0.5), *c2, 1.4])
        last_cam = c2
    for rect, col, f0, f1 in b.get("boxes", []):
        b0 = at(f0) if f0 is not None else round(s["s"] + 0.2, 3)
        b1 = at(f1) if f1 is not None else round(t1 - 0.05, 3)
        boxes.append([b0, rect, round(b1 - b0, 2)] + ([col] if col else []))
    for frac, ref in b.get("after", []) + b.get("after2", []):
        shots.append([at(frac), get(ref)])
    for ks, frac in b.get("keys", []):
        keys.append([at(frac), ks, 0.9 if ks == ["Shift"] else 1.1, 0.2])
    if b.get("clicks"):
        on.append([round(t0, 2), round(t1, 2)])
        cursor.append([round(t0, 2), *cur])
        prev = round(t0, 2)
        for x, y, frac, nxt in b["clicks"]:
            tc = at(frac)
            # glide to the target in the 0.5 s before the click
            cursor.append([round(max(prev, tc - 0.55), 3), *cur])
            cursor.append([round(tc - 0.05, 3), x, y])
            clicks.append(tc)
            shots.append([round(tc + 0.12, 3), get(nxt)])
            cur = [x, y]
            prev = tc
    if i in SECTIONS:
        titles.append([round(t0 + 0.1, 2), SECTIONS[i], 2.4])
        if i:
            sfx.append([round(t0 + 0.1, 2), "whoosh"])

shots.sort(key=lambda x: x[0])
cursor.sort(key=lambda x: x[0])
spec = {
    "size": [1920, 1080], "layout": "full",
    "captures": "captures/long04_all",
    "narration": "long/04/tight.wav", "words": "long/04/tight.json", "script": "long/04/captions.txt",
    "duration": dur, "handle": "TM_Diamond", "captions": True, "hide": HIDE, "drift": 0.01,
    "shots": shots, "cam": cams, "boxes": boxes, "cursor": cursor, "cursor_on": on, "clicks": clicks,
    "keys": keys, "typing": [], "titles": titles, "highlight": [], "sfx": sfx,
    "follow": round(S[-1]["s"], 2),
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "shots", len(shots), "cams", len(cams), "titles", len(titles))
