"""tiktok02: 6 ways to make a slow Windows 11 PC faster (plan block 1, Speed up a slow PC).
Team Diamond template (layout "tmd", like fb/07): logo strip on top, the real Windows screen in the middle panel,
the presenter strip below. Real screens: captures/tiktok02 (Task Manager + Settings on a real Windows PC, dark mode).
Narration tightened with engine/tighten.py; every shot, camera move, box, click and keycap sits on the spoken words."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]
assert len(S) == 25, len(S)


def word(text, k, n=1):
    for w in W:
        if w["w"].strip(".,?!:").lower() == text.lower() and w["s"] >= S[k]["s"] - 0.05:
            n -= 1
            if n == 0:
                return w
    raise KeyError(text)


RED = [255, 70, 70]
WIN = (160, 110, 1720, 950)          # app window on every capture (keep the camera inside it)
dur = round(T["duration"] + 0.4, 2)
shots, cam, boxes, cursor, on, clicks, keys, sfx = [], [], [], [], [], [], [], []


def shot(t, f): shots.append([round(max(0.0, t), 3), f])


def c(t, cx, cy, h, d=0.5):
    w = h * 1.103
    cx = min(max(cx, WIN[0] + w / 2), WIN[2] - w / 2)
    cy = min(max(cy, WIN[1] + h / 2), WIN[3] - h / 2)
    cam.append([round(max(0.0, t), 3), round(cx), round(cy), h, d])


def box(t, r, d, col=None):
    e = [round(t, 2), r, round(d, 2)]
    if col: e.append(col)
    boxes.append(e)


def click(t, x, y, after=None, snd=None):
    cursor.append([round(t - 0.05, 2), x, y]); clicks.append(round(t, 2))
    if after: shot(t + 0.12, after)
    if snd: sfx.append([round(t + 0.12, 2), snd])


def span(k):  # cursor visible during sentence k
    on.append([round(S[k]["s"] - 0.2, 2), round(S[k]["e"] + 0.35, 2)])
    cursor.append([round(S[k]["s"] - 0.2, 2), 1100, 700])


def nxt(k): return S[k + 1]["s"] - S[k]["s"] if k + 1 < len(S) else 2.0


# 0-1 hook: the app eating the CPU, then the fixes you will see (card on top)
shot(0, "006_sorted_cpu.png"); c(0, 520, 330, 440, 0); c(1.6, 470, 300, 380, 1.6)
box(0.3, [218, 263, 646, 28], 3.0, RED)
shot(S[1]["s"], "019_sense_final.png"); c(S[1]["s"], 720, 420, 480, 0); c(S[1]["s"] + 0.2, 720, 440, 440, 1.2)
shot(S[1]["s"] + 1.5, "022_sorted.png"); c(S[1]["s"] + 1.5, 1300, 400, 460, 0); c(S[1]["s"] + 1.7, 1300, 420, 420, 1.0)
sfx += [[round(S[1]["s"], 2), "whoosh"], [round(S[1]["s"] + 1.5, 2), "whoosh"]]
# 2 fix six teaser: Uninstall
shot(S[2]["s"], "024_hover_uninstall.png"); c(S[2]["s"], 1350, 420, 420, 0.4); c(S[2]["s"] + 1.2, 1400, 430, 360, 1.0)
box(S[2]["s"] + 0.4, [1307, 425, 262, 28], 2.0, RED)
# 3 Fix one: Ctrl + Shift + Esc
shot(S[3]["s"] - 0.2, "001_tm_open.png"); c(S[3]["s"] - 0.2, 700, 360, 520, 0); sfx.append([round(S[3]["s"] - 0.2, 2), "whoosh"])
keys.append([word("Control", 3)["s"] - 0.05, ["Ctrl", "Shift", "Esc"], 1.6, 0.2])
c(word("Task", 3)["s"], 420, 330, 440, 0.6)
# 4 Click Startup apps
span(4); c(S[4]["s"], 420, 330, 420, 0.4)
box(S[4]["s"] - 0.1, [172, 328, 40, 36], 1.2)
click(word("Startup", 4)["s"] + 0.25, 192, 346, "002_startup_list.png")
c(word("apps", 4)["e"], 560, 320, 440, 0.5)
# 5 Select an app, click Disable
span(5)
click(word("Select", 5)["s"] + 0.2, 338, 336, "003_startup_selected.png")
box(word("Select", 5)["s"] + 0.3, [218, 322, 700, 28], 1.2)
dc = word("Disable", 5)
c(word("click", 5)["s"] - 0.3, 1400, 260, 420, 0.45)
box(word("click", 5)["s"], [1472, 163, 88, 48], 1.0)
click(dc["s"] + 0.15, 1516, 187, "004_startup_disabled.png", "pop")
# 6 now it won't launch
c(S[6]["s"], 520, 330, 380, 0.5)
box(S[6]["s"] + 0.2, [583, 322, 99, 28], nxt(6) - 0.3, RED)
# 7 Fix two: Processes, CPU column
sfx.append([round(S[7]["s"], 2), "whoosh"]); span(7)
c(S[7]["s"], 420, 300, 440, 0.4)
box(word("Processes", 7)["s"] - 0.3, [172, 208, 40, 36], 0.9)
click(word("Processes", 7)["s"] + 0.2, 192, 226, "005_processes.png")
c(word("Processes", 7)["e"], 560, 300, 420, 0.5)
box(word("CPU", 7)["s"] - 0.3, [572, 214, 73, 48], 1.2)
click(word("CPU", 7)["s"] + 0.2, 608, 238, "006_sorted_cpu.png")
# 8 busiest app on top
c(S[8]["s"], 470, 290, 360, 0.5)
box(S[8]["s"] + 0.2, [218, 263, 646, 28], nxt(8) - 0.3, RED)
# 9 select it, End task
span(9)
click(word("select", 9)["s"] + 0.15, 338, 277, "007_hog_selected.png")
c(word("click", 9)["s"] - 0.3, 1400, 260, 420, 0.45)
box(word("click", 9)["s"], [1436, 163, 94, 48], 0.9)
click(word("End", 9)["s"] + 0.15, 1483, 187, "008_hog_ended.png", "ding")
c(word("task", 9)["e"] + 0.15, 480, 290, 380, 0.5)
# 10 Fix three: taskbar frozen? Windows Explorer
sfx.append([round(S[10]["s"], 2), "whoosh"])
shot(S[10]["s"] - 0.1, "009_wex_list.png"); c(S[10]["s"] - 0.1, 600, 450, 520, 0.4)
c(S[10]["s"] + 1.2, 480, 470, 400, 0.8)
box(S[10]["s"] + 0.6, [218, 459, 646, 28], 1.4)
# 11 select Windows Explorer, Restart task
span(11)
click(word("Select", 11)["s"] + 0.2, 338, 473, "010_wex_selected.png")
c(word("click", 11)["s"] - 0.35, 1400, 260, 420, 0.45)
box(word("click", 11)["s"] - 0.05, [1419, 163, 111, 48], 1.0)
click(word("Restart", 11)["s"] + 0.15, 1474, 187, "011_restarting.png", "pop")
c(word("task", 11)["e"], 560, 380, 520, 0.6)
# 12 taskbar reloads
shot(S[12]["s"] + 0.3, "012_after_restart.png"); c(S[12]["s"] + 0.3, 520, 360, 460, 0.8)
c(S[12]["s"] + 1.6, 600, 420, 520, 0.8)
# 13 Fix four: Settings > Accessibility > Visual effects
sfx.append([round(S[13]["s"], 2), "whoosh"])
shot(S[13]["s"] - 0.1, "013_visual_on.png"); c(S[13]["s"] - 0.1, 600, 380, 520, 0)
box(word("Accessibility", 13)["s"], [184, 534, 280, 36], 1.0)
c(word("Visual", 13)["s"] - 0.2, 800, 260, 380, 0.45)
box(word("Visual", 13)["s"], [590, 162, 370, 44], 1.4)
# 14 toggles off: the labels first, then the switches
span(14); c(S[14]["s"], 860, 370, 400, 0.5)
an = word("Animation", 14)
box(an["s"] - 0.25, [644, 388, 121, 31], 0.8)
c(an["s"] + 0.25, 1390, 360, 400, 0.45)
click(word("effects", 14)["s"] + 0.1, 1538, 403, "014_animation_off.png", "pop")
box(word("Transparency", 14)["s"] - 0.2, [1502, 310, 72, 40], 1.0)
click(word("effects", 14, 2)["s"], 1538, 330, "015_transparency_off.png", "pop")
# 15 payoff: both off
c(S[15]["s"], 1380, 360, 420, 0.6); c(S[15]["s"] + 1.2, 1350, 360, 460, 0.8)
box(S[15]["s"] + 0.3, [1440, 300, 150, 130], nxt(15) - 0.5, RED)
# 16 Fix five: Storage Sense
sfx.append([round(S[16]["s"], 2), "whoosh"])
shot(S[16]["s"] - 0.1, "016_sense_off.png"); c(S[16]["s"] - 0.1, 760, 300, 440, 0)
box(word("Sense", 16, 1)["s"] - 0.3, [586, 162, 464, 44], 1.6)
c(S[16]["s"] + 1.6, 720, 420, 420, 0.6)
# 17 turn it on, schedule
span(17)
box(S[17]["s"], [591, 367, 72, 40], 0.7)
click(word("on", 17)["s"], 627, 387, "017_sense_on.png", "pop")
box(word("how", 17)["s"] - 0.25, [587, 548, 288, 40], 0.6)
click(word("how", 17)["s"], 731, 568, "018_schedule_open.png")
c(word("how", 17)["s"], 720, 500, 420, 0.4)
box(word("often", 17)["s"] + 0.05, [597, 479, 268, 33], 0.6)
click(word("runs", 17)["s"], 731, 495, "019_sense_final.png")
# 18 payoff
c(S[18]["s"], 740, 440, 460, 0.6)
box(S[18]["s"] + 0.2, [588, 532, 286, 36], nxt(18) - 0.4)
# 19 Fix six: Apps > Installed apps
sfx.append([round(S[19]["s"], 2), "whoosh"])
shot(S[19]["s"] - 0.1, "020_apps.png"); c(S[19]["s"] - 0.1, 700, 300, 440, 0)
box(word("Installed", 19)["s"] - 0.2, [591, 162, 285, 44], 1.4)
c(S[19]["s"] + 1.7, 1200, 360, 460, 0.6)
# 20 sort by size
span(20)
box(S[20]["s"] - 0.1, [1450, 280, 145, 40], 0.7)
click(word("Sort", 20)["s"] + 0.1, 1522, 300, "021_sort_open.png")
c(word("Sort", 20)["s"] + 0.1, 1380, 360, 380, 0.4)
box(word("size", 20)["s"], [1460, 396, 148, 33], 0.8)
click(word("large", 20)["s"] + 0.1, 1534, 412, "022_sorted.png")
c(word("small", 20)["e"], 1250, 400, 440, 0.5)
# 21 three dots, Uninstall
span(21)
box(word("three", 21)["s"] - 0.1, [1534, 344, 40, 40], 1.0)
click(word("dots", 21)["s"] + 0.1, 1554, 364, "023_menu.png")
c(word("dots", 21)["s"] + 0.1, 1400, 400, 380, 0.45)
box(word("Uninstall", 21)["s"] - 0.3, [1307, 425, 262, 28], 1.5, RED)
cursor.append([round(word("Uninstall", 21)["s"], 2), 1438, 439]); shot(word("Uninstall", 21)["s"] + 0.05, "024_hover_uninstall.png")
# 22 save this
shot(S[22]["s"], "022_sorted.png"); c(S[22]["s"], 900, 430, 500, 0.6); c(S[22]["s"] + 1.0, 1250, 420, 460, 1.0)
# 23 follow
shot(S[23]["s"], "004_startup_disabled.png"); c(S[23]["s"], 560, 340, 460, 0.6)
# 24 loop back to fix one
shot(S[24]["s"], "006_sorted_cpu.png"); c(S[24]["s"], 520, 330, 440, 0.5)
c(word("fix", 24)["s"], 470, 300, 380, 0.6)
box(word("slow", 24)["s"], [218, 263, 646, 28], 1.6, RED)

shots.sort(key=lambda x: x[0]); cursor.sort(key=lambda x: x[0]); cam.sort(key=lambda x: x[0])
spec = {
    "layout": "tmd",
    "captures": "captures/tiktok02",
    "narration": "tiktok/02/tight.wav",
    "words": "tiktok/02/tight.json",
    "script": "tiktok/02/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": shots, "cam": cam, "boxes": boxes, "cursor": cursor, "cursor_on": on,
    "clicks": clicks, "keys": keys,
    "card": {"t0": 0.0, "t1": round(S[1]["e"] + 0.3, 2), "y": 313 + 560,
             "title": "Slow Windows 11 PC?", "sub": "No extra apps needed",
             "big": "6", "big2": "6 free fixes", "swap_t": round(word("six", 1)["s"], 2)},
    "highlight": [], "sfx": sorted(sfx),
    "follow": S[23]["s"],
    "follow_y": 0.55,
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
gaps = [b[0] - a[0] for a, b in zip(cam, cam[1:])]
print("duration", dur, "shots", len(shots), "cam", len(cam), "max cam gap", round(max(gaps), 2), "clicks", len(clicks))
