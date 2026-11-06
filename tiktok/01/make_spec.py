"""tiktok01: 5 File Explorer tricks most people never use.
Real Windows screens (captures/tiktok01, taken on a real Windows PC by engine/wincap.ps1), edited by engine/realcut.py.
Narration tightened by tiktok/01/tighten_fix.py (tight.wav + tight.json): every event sits on the spoken words."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]


def word(text, k):
    for w in W:
        if w["w"].strip(".,?!").lower() == text.lower() and w["s"] >= S[k]["s"] - 0.05:
            return w
    raise KeyError(text)


dur = round(T["duration"] + 0.4, 2)
shots, cam, keys, typing, circles, sfx, cursor, clicks = [], [], [], [], [], [], [], []
def shot(t, f): shots.append([round(t, 3), f])
def c(t, x, y, h, d=0.5): cam.append([round(t, 3), x, y, h, d])

# 0-2.5 hook: the preview pane reading a file without opening it
shot(0.0, "017_preview.png"); c(0.0, 1500, 300, 640, 0); c(0.05, 1300, 360, 820, 2.3)
# 2.9 five tricks: quick real teasers
shot(S[1]["s"], "030_props.png"); c(S[1]["s"], 850, 540, 780, 0.35); c(S[1]["s"] + 0.4, 850, 520, 700, 0.9)
shot(S[1]["s"] + 1.3, "028_nf_done.png"); c(S[1]["s"] + 1.3, 620, 300, 640, 0.35)
sfx.append([S[1]["s"], "whoosh"]); sfx.append([S[1]["s"] + 1.3, "whoosh"])
# 5.7 the last one saves the most time
shot(S[2]["s"], "015_ext_on2.png"); c(S[2]["s"], 640, 360, 1080, 0.5); c(S[2]["s"] + 0.6, 640, 330, 900, 1.0)
# 7.8 Win + E
shot(S[3]["s"], "001_desktop.png"); c(S[3]["s"], 760, 540, 1080, 0.45)
we = word("E", 3)
keys.append([word("press", 3)["s"], ["Win", "E"], 1.4, 0.70])
shot(we["e"] + 0.05, "002_explorer_home.png"); sfx.append([we["e"] + 0.05, "open"])
c(we["e"] + 0.05, 640, 380, 900, 0.5); c(we["e"] + 0.8, 560, 300, 720, 1.2)
# 11.4 Alt + D
ad = word("D", 4)
keys.append([word("Alt", 4)["s"] - 0.05, ["Alt", "D"], 1.3, 0.55])
shot(ad["s"] + 0.1, "003_address_sel.png"); c(ad["s"] + 0.05, 500, 200, 540, 0.45)
circles.append([ad["s"] + 0.35, [370, 108, 330, 32], 1.8])
# 15.3 type C:\Work, Enter
t0, t1 = word("C", 5)["s"], word("work", 5)["e"]
typed = [f"{i:03d}_addr_type.png" for i in range(4, 11)]
for k, f in enumerate(typed):
    shot(t0 + (t1 - t0) * k / (len(typed) - 1), f)
typing.append([t0, t1, len(typed)])
c(t0 - 0.2, 500, 200, 440, 0.4)
en = word("Enter", 5)
keys.append([en["s"] - 0.1, ["Enter"], 0.8, 0.55])
shot(en["e"] + 0.05, "011_work_folder.png"); sfx.append([en["e"] + 0.05, "pop"])
c(en["e"] + 0.05, 560, 330, 760, 0.45)
# 19.4 you're there instantly
c(S[6]["s"] + 0.3, 530, 260, 640, 1.2)
# 21.0 see what your files really are (no extensions yet)
c(S[7]["s"], 470, 300, 520, 0.6)
circles.append([S[7]["s"] + 0.6, [342, 227, 120, 112], 1.7])
# 23.5 View > Show > File name extensions
vw, sh, ex = word("View", 8), word("Show", 8), word("extensions", 8)
cursor += [[S[7]["s"] + 1.0, 560, 420], [vw["s"] - 0.1, 693, 172]]
clicks.append(vw["s"]); shot(vw["s"] + 0.08, "012_view_menu.png")
c(vw["s"], 700, 380, 720, 0.4)
cursor += [[sh["s"] - 0.05, 694, 546]]
clicks.append(sh["s"] + 0.05); shot(sh["s"] + 0.12, "013_show_menu.png")
c(sh["s"], 800, 560, 640, 0.45)
circles.append([word("File", 8)["s"], [788, 637, 207, 28], 1.4])
cursor += [[ex["s"], 892, 651]]
clicks.append(ex["e"] - 0.1); shot(ex["e"], "015_ext_on2.png"); sfx.append([ex["e"], "pop"])
# 26.8 every file shows its real type
c(S[9]["s"], 500, 290, 560, 0.5)
circles.append([word("txt", 9)["s"] - 0.3 if any(w["w"].strip(".,").lower() == "txt" for w in W) else S[9]["s"] + 2.2, [342, 227, 120, 112], 2.4])
c(S[9]["s"] + 2.6, 530, 300, 640, 1.4)
# 32.1 spot a file pretending
c(S[10]["s"], 560, 330, 860, 1.2); c(S[10]["s"] + 1.6, 530, 300, 700, 1.2)
# 35.4 click a file, Alt + P
ck = word("click", 11)
cursor += [[S[10]["e"], 700, 420], [ck["s"], 641, 267]]
clicks.append(ck["s"] + 0.1); shot(ck["s"] + 0.15, "016_notes_selected.png")
c(ck["s"], 520, 290, 600, 0.5)
ap = word("P", 11)
keys.append([word("Alt", 11)["s"] - 0.05, ["Alt", "P"], 1.3, 0.70])
shot(ap["s"] + 0.1, "017_preview.png"); sfx.append([ap["s"] + 0.1, "open"])
c(ap["s"] + 0.1, 1180, 330, 860, 0.5)
# 38.2 the preview pane opens
c(S[12]["s"] + 0.4, 1520, 300, 620, 0.7)
circles.append([S[12]["s"] + 0.9, [1430, 190, 250, 160], 2.2])
c(S[12]["s"] + 2.6, 1400, 330, 760, 1.0)
# 42.2 Ctrl + Shift + N
n = word("N", 13)
keys.append([word("Ctrl", 13)["s"] - 0.05, ["Ctrl", "Shift", "N"], 1.5, 0.70])
shot(n["s"] + 0.1, "019_new_folder.png"); sfx.append([n["s"] + 0.1, "pop"])
c(S[13]["s"], 640, 340, 860, 0.5); c(n["s"] + 0.1, 520, 330, 560, 0.45)
# 44.6 a new folder, ready to name
circles.append([S[14]["s"] + 0.3, [342, 328, 300, 30], 1.8])
# 46.9 type a name, Enter
t0 = S[15]["s"]; t1 = word("press", 15)["s"]
typed = [f"{i:03d}_nf_type.png" for i in range(20, 28)]
for k, f in enumerate(typed):
    shot(t0 + (t1 - t0) * k / (len(typed) - 1), f)
typing.append([t0, t1, len(typed)])
en = word("Enter", 15)
keys.append([en["s"] - 0.1, ["Enter"], 0.8, 0.70])
shot(en["e"], "028_nf_done.png"); sfx.append([en["e"], "ding"])
c(en["e"], 560, 320, 640, 0.6)
# 48.8 trick five
c(S[16]["s"], 600, 400, 960, 0.6)
# 50.7 select any file, Alt + Enter
sl = word("Select", 17)
cursor += [[S[16]["e"], 760, 430], [sl["s"] + 0.2, 641, 295]]
clicks.append(sl["s"] + 0.3); shot(sl["s"] + 0.35, "029_photo_selected.png")
c(sl["s"], 520, 300, 600, 0.5)
ae = word("Enter", 17)
keys.append([word("Alt", 17)["s"] - 0.05, ["Alt", "Enter"], 1.3, 0.70])
shot(ae["s"] + 0.15, "030_props.png"); sfx.append([ae["s"] + 0.15, "open"])
c(ae["s"] + 0.1, 850, 540, 800, 0.5)
# 53.4 size, location and dates
c(S[18]["s"] + 0.5, 800, 560, 700, 0.7)
circles.append([word("size", 18)["s"] - 0.1, [660, 488, 290, 150], 2.4])
c(S[18]["s"] + 3.0, 820, 540, 800, 1.0)
# 57.8 save this
shot(S[19]["s"], "031_props2.png"); c(S[19]["s"], 760, 540, 1080, 1.0)
# 61.9 loop back: Alt + D
shot(S[21]["s"], "003_address_sel.png"); c(S[21]["s"], 560, 260, 760, 0.6)
keys.append([word("Alt", 21)["s"] - 0.05, ["Alt", "D"], 1.2, 0.55])
c(word("Alt", 21)["s"], 530, 200, 560, 0.5)

spec = {
    "captures": "captures/tiktok01",
    "narration": "tiktok/01/tight.wav",
    "words": "tiktok/01/tight.json",
    "script": "tiktok/01/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "shots": sorted(shots, key=lambda s: s[0]),
    "cam": sorted(cam, key=lambda s: s[0]),
    "cursor": cursor,
    "clicks": clicks,
    "keys": keys,
    "typing": typing,
    "circles": circles,
    "highlight": ["five", "alt", "d", "extensions", "preview", "folder", "properties", "enter"],
    "sfx": sfx,
    "follow": S[20]["s"],
    "caption_y": [[0, 0.17], [S[4]["s"], 0.74], [S[7]["s"], 0.17], [S[21]["s"], 0.66]],
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "shots", len(shots), "cam", len(cam))
gaps = [b[0] - a[0] for a, b in zip(spec["cam"], spec["cam"][1:])]
print("max cam gap", round(max(gaps), 2))
