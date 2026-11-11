"""short07 = AI for Creators, Part 1: "You're using ChatGPT wrong".
Real ChatGPT (no-account mode) on the capture PC, 1280x720 at Edge 125% (captures/short07): the same request asked
vague ("Give me video ideas" -> a generic list) and then specific (who it's for, what, format -> 3 clear ideas).
Team Diamond template, full-screen framing (owner 2026-11-11: show the whole laptop screen)."""
import json, os, glob
D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "tight.json")))
W, S = T["words"], T["sentences"]
CAP = os.path.join(D, "..", "..", "captures", "short07")


def word(text, after=0.0):
    for w in W:
        if w["w"].strip(".,?!:'").lower() == text.lower() and w["s"] >= after - 0.01:
            return w
    raise KeyError(text)


def frames(label):
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(CAP, f"*_{label}.png")))


dur = round(T["duration"] + 0.35, 2)
generic = word("generic", S[1]["s"])
FULL = (640, 360, 720)

shots = [[0.0, "026_answer1_12.png"]]
# typing the vague prompt, then the answer streaming in
t1 = frames("typed1")
ts, te = S[1]["s"] + 0.1, S[1]["s"] + 1.25
for i, f in enumerate(t1):
    shots.append([round(ts + (te - ts) * i / len(t1), 3), f])
enter1 = te + 0.05
for k, f in enumerate(["021_answer1_1.png", "022_answer1_2.png", "023_answer1_3.png", "024_answer1_5.png", "025_answer1_8.png", "026_answer1_12.png"]):
    shots.append([round(enter1 + 0.12 + k * 0.32, 3), f])
# typing the specific prompt while the voice reads it
t2 = frames("typed2")
ts2, te2 = S[4]["s"], S[4]["e"] - 0.1
for i, f in enumerate(t2):
    shots.append([round(ts2 + (te2 - ts2) * i / len(t2), 3), f])
enter2 = S[5]["s"] - 0.2
for k, f in enumerate(["107_answer2_1.png", "108_answer2_2.png", "109_answer2_3.png", "110_answer2_5.png", "111_answer2_8.png"]):
    shots.append([round(enter2 + 0.12 + k * 0.28, 3), f])

BOX1 = [194, 246, 960, 64]       # the box with the vague prompt
GENERIC = [190, 392, 440, 166]   # the generic list
BOX2 = [194, 572, 960, 66]       # the box with the specific prompt (one line while typing)
IDEAS = [200, 350, 420, 104]     # the 3 clear ideas

spec = {
    "layout": "tmd",
    "framing": "full",
    "captures": "captures/short07",
    "narration": "shorts/07/tight.wav",
    "words": "shorts/07/tight.json",
    "script": "shorts/07/script.txt",
    "duration": dur,
    "handle": "TM_Diamond",
    "captions": False,
    "shots": shots,
    "cam": [
        [0.0, *FULL, 0],
        [S[5]["s"] + 0.6, 640, 400, 600, 0.6],    # small push-in on the better answer
        [S[6]["s"], *FULL, 0.5],
    ],
    "cursor": [
        [S[1]["s"], 900, 420],
        [ts - 0.05, 680, 279],
        [enter1 + 0.4, 900, 470],
        [S[4]["s"] - 0.2, 680, 590],
        [enter2 + 0.4, 900, 470],
    ],
    "cursor_on": [[S[1]["s"], S[6]["s"]]],
    "clicks": [ts - 0.02, ts2 - 0.05],
    "typing": [[ts, te, 14], [ts2, te2, 40]],
    "keys": [[enter1 - 0.05, ["Enter"], 0.7, 0.37], [enter2 - 0.05, ["Enter"], 0.7, 0.37]],
    "boxes": [
        [0.35, GENERIC, round(S[0]["e"] - 0.2, 2), [255, 70, 70]],
        [ts, BOX1, round(te - ts + 0.2, 2)],
        [generic["s"] - 0.1, GENERIC, round(S[3]["e"] - generic["s"], 2), [255, 70, 70]],
        [ts2, BOX2, round(te2 - ts2 - 0.08, 2)],
        [enter2 + 1.3, IDEAS, round(S[6]["s"] - enter2 - 1.3, 2)],
    ],
    "card": {"t0": 0.0, "t1": round(S[0]["e"] + 0.3, 2),
             "title": "PART 1 · AI for Creators", "sub": "You're using ChatGPT wrong", "big": "Boring answers?"},
    "steps": [
        [S[1]["s"], S[2]["s"], "The usual way", "Give me video ideas"],
        [S[2]["s"], S[4]["s"], "The fix", "Who it's for + what you want + the format"],
        [S[4]["s"], S[5]["s"], "Type it like this", "3 ideas, beginner tech channel, under 10 words, numbered"],
        [S[5]["s"], S[6]["s"], "Result", "3 clear, specific ideas"],
    ],
    "titles": [[S[6]["s"], "Part 2: 10 titles, 1 prompt", round(S[7]["s"] - S[6]["s"], 2)]],
    "highlight": [],
    "sfx": [[generic["s"] - 0.1, "pop"], [enter2 + 1.3, "ding"]],
    "follow": S[7]["s"],
}
json.dump(spec, open(os.path.join(D, "spec.json"), "w"), indent=1)
print("duration", dur, "shots", len(shots))
