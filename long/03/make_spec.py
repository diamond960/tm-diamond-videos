"""long03: 10 Command Prompt Commands Every Windows User Should Know (landscape, real Windows screens).
Plan block 2 (Command Prompt basics). One beat per spoken sentence (long/03/tight.json, 94 sentences).
Screens (all real, 1280x720, Command Prompt in Windows Terminal):
  a = captures/day20261112 (open cmd, flushdns, ipconfig, ping google, systeminfo, tasklist/taskkill, driverquery)
  b = captures/day20261112b (Command Prompt as administrator, chkdsk, sfc /scannow)
  c = captures/long03_03 (ping 127.0.0.1, ping -t), d = captures/long03_07 (winget upgrade, --all),
  e = captures/long03_10 (shutdown /s /t 3600, shutdown /a)
copied into captures/long03_all/ with the letter as a prefix.
Run: python3 long/03/make_spec.py"""
import glob
import json
import os
import shutil

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(D))
SRC = {"a": "day20261112", "b": "day20261112b", "c": "long03_03", "d": "long03_07", "e": "long03_10"}
ALL = os.path.join(R, "captures", "long03_all")
os.makedirs(ALL, exist_ok=True)
for k, src in SRC.items():
    for f in os.listdir(os.path.join(R, "captures", src)):
        if f.endswith(".png") and not os.path.exists(os.path.join(ALL, f"{k}_{f}")):
            shutil.copy(os.path.join(R, "captures", src, f), os.path.join(ALL, f"{k}_{f}"))
FILES = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ALL, "*.png")))


def frames(ref):
    k, label = ref.split(":", 1)
    out = [f for f in FILES if f.startswith(k + "_") and f[len(k) + 5:-4] == label]
    assert out, ref
    return out


def get(ref):
    if ref.endswith(".png"):
        f = ref.replace(":", "_", 1)
        assert f in FILES, ref
        return f
    if ref.endswith(":first"):
        return frames(ref[:-6])[0]
    return frames(ref)[-1]


T = json.load(open(os.path.join(D, "tight.json")))
S = T["sentences"]
RED = [255, 70, 70]
G = None
FULL = (640, 360, 720)
HIDE = [[1082, 617, 198, 54]]   # "Test Mode / Windows Server" desktop watermark (1280x720)


def bx(x, y, w, h, col=G, f0=None, f1=None):
    return ([x - 6, y - 5, w + 12, h + 10], col, f0, f1)


def typed(label, f0, f1, enter, result, ref=None):
    """type the command (real per-character shots), Enter keycap, then the real result"""
    b = dict(shot=f"{label}_clean" if ref is None else ref, seq=(label + "_type", f0, f1), typing=True)
    if enter is not None:
        b["keys"] = [(["Enter"], enter)]
        b["after"] = [(enter + 0.05, result)] if result else []
    return b


B = {
    # hook
    0: dict(shot="a:b2e6_result2", boxes=[bx(9, 594, 822, 19, G, 0.05, 0.5), bx(8, 226, 943, 19, G, 0.55, 1.0)],
            after=[(0.5, "b:b2e4_result")]),
    1: dict(shot="a:b2e1_result", cam=(560, 240, 560), boxes=[bx(9, 157, 522, 19)]),
    2: dict(shot="c:p1_result", after=[(0.5, "d:w1_result")]),
    3: dict(shot="b:b2e4_result", cam=(560, 250, 560), boxes=[bx(8, 226, 943, 19, RED)]),
    4: dict(shot="d:w1_result", boxes=[bx(9, 592, 237, 18, RED, 0.3, 1.0)], after=[(0.75, "d:048_w2_run.png")]),
    # open Command Prompt
    5: dict(shot="a:cmd_desktop"),
    6: dict(shot="a:cmd_desktop", keys=[(["Win", "R"], 0.35)], after=[(0.55, "a:cmd_run")]),
    7: dict(shot="a:cmd_run", seq=("a:cmd_run_type", 0.05, 0.45), typing=True, keys=[(["Enter"], 0.75)],
            after=[(0.82, "a:cmd_open")]),
    8: dict(shot="a:cmd_open", cam=(640, 300, 600)),
    9: dict(shot="b:adm_start", keys=[(["Win"], 0.05)], seq=("b:adm_search_type", 0.25, 0.95), typing=True),
    10: dict(shot="b:adm_search", cam=(700, 330, 560), boxes=[bx(646, 412, 160, 20)],
             clicks=[(730, 422, 0.6, "b:adm_hover")]),
    11: dict(shot="b:adm_open"),
    # 1 flushdns
    12: dict(shot="a:b2e1_clean"),
    13: dict(shot="a:b2e2_result", cam=(560, 300, 600)),
    14: dict(shot="a:b2e1_clean", cam=(640, 300, 600)),
    15: dict(typed("a:b2e1", 0.05, 0.75, 0.85, "a:b2e1_result"), cam=(560, 220, 520)),
    16: dict(shot="a:b2e1_result", cam=(480, 200, 480), boxes=[bx(9, 157, 522, 19)]),
    17: dict(shot="a:b2e1_result"),
    18: dict(shot="a:b2e1_result", cam=(560, 240, 560)),
    # 2 ipconfig
    19: dict(shot="a:b2e2_clean"),
    20: dict(typed("a:b2e2", 0.05, 0.6, 0.72, "a:b2e2_result"), cam=(560, 240, 560)),
    21: dict(shot="a:b2e2_result", cam=(480, 280, 480), boxes=[bx(46, 272, 549, 15)]),
    22: dict(shot="a:b2e2_result", cam=(500, 260, 520), boxes=[bx(46, 272, 549, 15, RED)]),
    23: dict(shot="a:b2e2_result", cam=(520, 300, 520), boxes=[bx(45, 295, 586, 15, G, 0.0, 1.0), bx(45, 318, 525, 19, G, 0.45, 1.0)]),
    24: dict(shot="a:b2e2_result", cam=(480, 320, 480), boxes=[bx(45, 318, 525, 19, RED)]),
    25: dict(shot="a:b2e2_result"),
    # 3 ping
    26: dict(shot="c:p1_clean"),
    27: dict(shot="c:p1_clean", cam=(560, 240, 560)),
    28: dict(typed("c:p1", 0.0, 0.6, 0.68, None), after=[(0.74, "c:p1_run:first"), (0.82, "c:017_p1_run.png"),
                                                       (0.9, "c:018_p1_run.png"), (0.97, "c:p1_result")]),
    29: dict(shot="c:p1_result"),
    30: dict(shot="c:p1_result", cam=(480, 200, 480), boxes=[bx(9, 134, 562, 88)]),
    31: dict(shot="c:p1_result", cam=(500, 290, 480), boxes=[bx(57, 271, 618, 21), bx(57, 318, 513, 20, G, 0.5, 1.0)]),
    32: dict(shot="a:b2e3_clean", seq=("a:b2e3_type", 0.05, 0.7), typing=True, keys=[(["Enter"], 0.78)],
             after=[(0.85, "a:b2e3_result")]),
    33: dict(shot="a:b2e3_result", cam=(500, 220, 500), boxes=[bx(9, 134, 210, 88, RED, 0.0, 0.5), bx(57, 271, 642, 21, RED, 0.5, 1.0)]),
    34: dict(shot="a:b2e3_result"),
    35: dict(shot="a:b2e3_result", cam=(560, 220, 560)),
    36: dict(shot="c:p1_result"),
    37: dict(shot="c:p3_stopped", cam=(480, 190, 480), keys=[(["Ctrl", "C"], 0.7)],
             boxes=[bx(9, 64, 453, 20, G, 0.05, 0.6), bx(9, 272, 106, 38, G, 0.65, 1.0)]),
    # 4 sfc /scannow
    38: dict(shot="b:b2e4_clean"),
    39: dict(shot="b:b2e4_clean", cam=(640, 300, 600)),
    40: dict(shot="b:adm_hover", boxes=[bx(646, 412, 160, 20)]),
    41: typed("b:b2e4", 0.05, 0.7, 0.8, "b:b2e4_run:first"),
    42: dict(shot="b:b2e4_run:first", seq=("b:b2e4_run", 0.0, 1.0), cam=(560, 200, 520)),
    43: dict(shot="b:b2e4_result", cam=(480, 170, 480), boxes=[bx(8, 180, 319, 19)]),
    44: dict(shot="b:b2e4_result", cam=(560, 240, 520), boxes=[bx(8, 226, 943, 19)]),
    45: dict(shot="b:b2e4_result"),
    # subscribe + re-hook
    46: dict(shot="d:w1_result", after=[(0.5, "a:b2e6_result2")]),
    47: dict(shot="a:b2e5_top"),
    # 5 systeminfo
    48: dict(shot="a:b2e5_clean"),
    49: dict(typed("a:b2e5", 0.0, 0.4, 0.5, "a:b2e5_loading:first"), after2=[(0.85, "a:b2e5_top")]),
    50: dict(shot="a:b2e5_top", boxes=[bx(9, 156, 682, 18, G, 0.0, 0.45), bx(9, 427, 1125, 48, G, 0.45, 0.8),
                                       bx(9, 317, 622, 21, G, 0.8, 1.0)]),
    51: dict(shot="a:b2e5_top", boxes=[bx(9, 640, 478, 20, G, 0.0, 0.4)], seq=("a:b2e5_scroll", 0.42, 0.9), rev=True,
             after2=[(0.92, "a:b2e5_result")]),
    52: dict(shot="a:b2e5_result", boxes=[bx(9, 41, 594, 18)]),
    # 6 tasklist + taskkill
    53: dict(shot="a:b2e6_back"),
    54: dict(shot="a:b2e6_notepad", boxes=[([330, 110, 620, 420], None, None, None)]),
    55: dict(typed("a:b2e6", 0.0, 0.35, 0.42, "a:b2e6_list", ref="a:b2e6_back"), seq=("a:b2e6_type1", 0.0, 0.35)),
    56: dict(shot="a:b2e6_list", cam=(560, 470, 500), boxes=[bx(10, 548, 909, 20, RED)]),
    57: dict(shot="a:b2e6_list", seq=("a:b2e6_type2", 0.02, 0.95), typing=True, cam=(560, 470, 500)),
    58: dict(shot="a:b2e6_type2", cam=(560, 470, 500), keys=[(["Enter"], 0.1)], after=[(0.18, "a:b2e6_result")],
             boxes=[bx(9, 570, 574, 20, G, 0.3, 1.0)]),
    59: dict(shot="a:b2e6_result2", cam=(560, 470, 500), boxes=[bx(9, 594, 822, 19)]),
    60: dict(shot="a:b2e6_result2"),
    # 7 winget
    61: dict(shot="d:w1_clean"),
    62: typed("d:w1", 0.05, 0.6, 0.72, "d:w1_run:first"),
    63: dict(shot="d:017_w1_run.png", cam=(640, 180, 520), boxes=[bx(9, 196, 525, 18, G, 0.1, 0.7), bx(11, 216, 169, 18, G, 0.4, 0.8)],
             keys=[(["Y"], 0.72), (["Enter"], 0.84)], after=[(0.9, "d:w1_agreed")]),
    64: dict(shot="d:w1_result"),
    65: dict(shot="d:w1_result", cam=(640, 230, 560), boxes=[bx(8, 196, 1231, 18)]),
    66: dict(typed("d:w2", 0.25, 0.85, 0.9, "d:048_w2_run.png")),
    67: dict(shot="d:048_w2_run.png", seq=("d:w2_run", 0.0, 1.0)),
    68: dict(shot="d:w2_stopped"),
    # 8 chkdsk
    69: dict(shot="b:b2e8_clean"),
    70: dict(shot="b:adm_hover", seq=("b:b2e8_type", 0.45, 0.82), typing=True, keys=[(["Enter"], 0.88)],
             after=[(0.3, "b:b2e8_clean"), (0.93, "b:b2e8_run:first")]),
    71: dict(shot="b:b2e8_run:first", seq=("b:b2e8_run", 0.0, 1.0)),
    72: dict(shot="b:b2e8_result", cam=(480, 480, 480), boxes=[bx(9, 593, 486, 18)]),
    73: dict(shot="b:b2e8_result", cam=(480, 300, 480), boxes=[bx(8, 272, 691, 19)]),
    74: dict(shot="b:b2e8_result", cam=(480, 400, 480), boxes=[bx(22, 410, 329, 15)]),
    75: dict(shot="b:b2e8_result"),
    76: dict(shot="b:b2e8_result", cam=(640, 330, 620)),
    # 9 driverquery
    77: dict(shot="a:b2e9_clean"),
    78: typed("a:b2e9", 0.0, 0.6, 0.7, "a:b2e9_loading"),
    79: dict(shot="a:b2e9_result", after2=[]),
    80: dict(shot="a:b2e9_result", cam=(480, 360, 560)),
    81: dict(shot="a:b2e9_result", cam=(480, 380, 520), boxes=[bx(8, 340, 839, 18)]),
    82: dict(shot="a:b2e9_result"),
    # 10 shutdown timer
    83: dict(shot="e:s1_clean"),
    84: typed("e:s1", 0.05, 0.85, 0.92, "e:s1_run:first"),
    85: dict(shot="e:s1_run", cam=(480, 160, 480), boxes=[bx(9, 64, 478, 18, G)]),
    86: dict(shot="e:s1_run"),
    87: dict(shot="e:s1_run", cam=(560, 240, 560)),
    88: dict(shot="e:s1_run", seq=("e:s2_type", 0.05, 0.7), typing=True, keys=[(["Enter"], 0.8)], after=[(0.86, "e:s2_run")]),
    89: dict(shot="e:s2_run", cam=(480, 180, 480), boxes=[bx(9, 110, 382, 18)]),
    90: dict(shot="e:s2_run", seq=("e:s3_type", 0.0, 0.35), typing=True, keys=[(["Enter"], 0.4)],
             after=[(0.46, "e:s3_result")], boxes=[bx(9, 179, 932, 20, G, 0.5, 1.0)]),
    91: dict(shot="a:b2e1_result", after=[(0.35, "c:p1_result"), (0.7, "d:w1_result")]),
    92: dict(shot="b:b2e4_result"),
    93: dict(shot="a:b2e6_result2"),
}
SECTIONS = {0: "10 Command Prompt Commands", 5: "Open Command Prompt", 12: "1. ipconfig /flushdns",
            19: "2. ipconfig", 26: "3. ping", 38: "4. sfc /scannow", 48: "5. systeminfo",
            53: "6. tasklist + taskkill", 61: "7. winget upgrade", 69: "8. chkdsk", 77: "9. driverquery",
            83: "10. shutdown /s /t", 92: "What's next"}

assert len(S) == len(B) == 94, (len(S), len(B))
dur = round(T["duration"] + 0.6, 2)
shots, cams, boxes, cursor, clicks, keys, titles, typing, on, sfx = [], [], [], [], [], [], [], [], [], []
last_cam = None
for i, s in enumerate(S):
    b = B[i]
    t0 = max(0.0, s["s"] - (0.2 if i else 0))
    t1 = S[i + 1]["s"] - 0.2 if i + 1 < len(S) else dur
    span = s["e"] - s["s"]
    at = lambda f: round(s["s"] + span * f, 3)
    shots.append([round(t0, 3), get(b["shot"])])
    cc = b.get("cam", FULL)
    # small push-ins only (height >= 470 on a 1280x720 screen), never past the screen edges
    h = max(470, cc[2]); w = h * 16 / 9
    cx = min(max(cc[0], w / 2), 1280 - w / 2)
    if h < 720 and cc[0] < 700:
        cx = w / 2   # terminal text starts at the left edge: keep it in the picture
    cy = min(max(cc[1], h / 2), 720 - h / 2)
    cc = (round(cx), round(cy), h)
    # a picture or camera change at least every ~4 s
    if cc == last_cam and not b.get("seq") and not b.get("after") and span > 4.0 and cc == FULL:
        cc = (569, 330, 640)
    if cc != last_cam:
        cams.append([round(t0, 3), *cc, 0 if i == 0 else 0.55])
        last_cam = cc
    if span > 4.2 and not b.get("seq") and not b.get("after") and not b.get("after2") and not b.get("clicks"):
        # long sentence on one screen: a slow camera move halfway (zoom out a little, or a gentle push-in)
        h2 = min(720, round(cc[2] * 1.15)) if cc[2] < 720 else 650
        w2 = h2 * 16 / 9
        c2 = (round(w2 / 2 if cc[0] < 700 else min(max(cc[0], w2 / 2), 1280 - w2 / 2)), round(min(max(cc[1], h2 / 2), 720 - h2 / 2)), h2)
        cams.append([at(0.5), *c2, 1.2])
        last_cam = c2
    for rect, col, f0, f1 in b.get("boxes", []):
        b0 = at(f0) if f0 is not None else round(s["s"] + 0.2, 3)
        b1 = at(f1) if f1 is not None else round(t1 - 0.05, 3)
        boxes.append([b0, rect, round(b1 - b0, 2)] + ([col] if col else []))
    if b.get("seq"):
        label, f0, f1 = b["seq"]
        fr = frames(label)
        if b.get("rev"):
            fr = fr[::-1]
        a, z = at(f0), at(f1)
        for k, f in enumerate(fr):
            shots.append([round(a + (z - a) * k / max(1, len(fr)), 3), f])
        if b.get("typing"):
            typing.append([a, z, len(fr)])
    for frac, ref in b.get("after", []) + b.get("after2", []):
        shots.append([at(frac), get(ref)])
    for ks, frac in b.get("keys", []) + b.get("keys2", []):
        keys.append([at(frac), ks, 1.1, 0.2])
    if b.get("clicks"):
        on.append([round(t0, 2), round(t1, 2)])
        cursor.append([round(t0, 2), 900, 560])
        for x, y, frac, nxt in b["clicks"]:
            tc = at(frac)
            cursor.append([round(tc - 0.05, 3), x, y])
            clicks.append(tc)
            shots.append([round(tc + 0.12, 3), get(nxt)])
    if i in SECTIONS:
        titles.append([round(t0 + 0.1, 2), SECTIONS[i], 2.4])
        if i:
            sfx.append([round(t0 + 0.1, 2), "whoosh"])

shots.sort(key=lambda x: x[0])
cursor.sort(key=lambda x: x[0])
spec = {
    "size": [1920, 1080], "layout": "full",
    "captures": "captures/long03_all",
    "narration": "long/03/tight.wav", "words": "long/03/tight.json", "script": "long/03/captions.txt",
    "duration": dur, "handle": "TM_Diamond", "captions": True, "hide": HIDE, "drift": 0.01,
    "shots": shots, "cam": cams, "boxes": boxes, "cursor": cursor, "cursor_on": on, "clicks": clicks,
    "keys": keys, "typing": typing, "titles": titles, "highlight": [], "sfx": sfx,
    "follow": round(S[-1]["s"], 2),
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "shots", len(shots), "cams", len(cams), "titles", len(titles))
