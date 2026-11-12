"""tiktok/04: "6 Command Prompt commands every Windows user should know" (61-75 s for TikTok Creator Rewards).
Real Command Prompt screens recorded at 1280x720 (captures/day20261112), Team Diamond template, full-screen framing.
Run: python3 tiktok/04/make_spec.py  (beat format: fb/batch_lib.py)"""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "fb"))
from batch_lib import build, RED, ROOT  # noqa: E402
from make_batch_1112 import CAP, FULL, HIDE, RUN, IPV4, SUCCESS, NOTEPAD_ROW, TASKBAR_NP  # noqa: E402

G = None
FLUSHED = [2, 154, 536, 24]
BEATS = [
    dict(shot="b2e2_result", cam=FULL),
    dict(shot="b2e6_notepad", cam=FULL, boxes=[([338, 111, 604, 411], RED, 0.1, 0.5), (SUCCESS, G, 0.58, 1.0)],
         after=[(0.55, "b2e6_result2")]),
    dict(RUN, step=("Start", "Win + R, type cmd, Enter")),
    dict(shot="b2e2_clean", cam=FULL, seq=("b2e2_type", 0.3, 0.72), typing=True, keys=(["Enter"], 0.82),
         after=[(0.88, "b2e2_result")], step=("Command 1", "ipconfig")),
    dict(shot="b2e2_result", cam=(440, 290, 500), boxes=[(IPV4, G)], step=("Command 1", "Your PC's address: IPv4")),
    dict(shot="b2e1_clean", cam=FULL, seq=("b2e1_type", 0.2, 0.82), typing=True, keys=(["Enter"], 0.88),
         after=[(0.93, "b2e1_result")], step=("Command 2", "ipconfig /flushdns")),
    dict(shot="b2e1_result", cam=FULL, boxes=[(FLUSHED, G)], step=("Command 2", "Website won't load? Try this")),
    dict(shot="b2e5_clean", cam=FULL, seq=("b2e5_type", 0.3, 0.72), typing=True, keys=(["Enter"], 0.8),
         after=[(0.85, "b2e5_loading:first")], step=("Command 3", "systeminfo")),
    dict(shot="b2e5_result", cam=FULL, seq=("b2e5_scroll", 0.0, 0.3), after=[(0.33, "b2e5_top")],
         boxes=[([2, 131, 862, 24], G, 0.36, 0.66), ([2, 637, 490, 24], G, 0.66, 1.1)], step=("Command 3", "Windows version and RAM")),
    dict(shot="b2e9_clean", cam=FULL, seq=("b2e9_type", 0.3, 0.72), typing=True, keys=(["Enter"], 0.8),
         after=[(0.85, "b2e9_result")], step=("Command 4", "driverquery")),
    dict(shot="b2e9_result", cam=FULL, boxes=[([2, 38, 432, 578], G, 0.0, 0.6), ([436, 38, 142, 578], G, 0.6, 1.1)],
         step=("Command 4", "Every driver, by name and type")),
    dict(shot="b2e6_back", cam=FULL, seq=("b2e6_type1", 0.3, 0.7), typing=True, keys=(["Enter"], 0.8),
         after=[(0.85, "b2e6_list")], step=("Command 5", "tasklist")),
    dict(shot="b2e6_list", cam=FULL, boxes=[([2, 38, 312, 578], G)], step=("Command 5", "Every running app, by name")),
    dict(shot="b2e6_list", cam=FULL, boxes=[(NOTEPAD_ROW, RED)], step=("Command 6", "taskkill")),
    dict(shot="b2e6_list", cam=FULL, seq=("b2e6_type2", 0.05, 0.84), typing=True, keys=(["Enter"], 0.9),
         boxes=[(TASKBAR_NP, RED, 0.0, 0.9)], after=[(0.93, "b2e6_result")], step=("Command 6", "taskkill /im notepad.exe /f")),
    dict(shot="b2e6_result2", cam=FULL, boxes=[(SUCCESS, G, 0.0, 0.5), (TASKBAR_NP, RED, 0.5, 1.0)],
         step=("Command 6", "Closed. Unsaved work in it is lost")),
    dict(shot="b2e5_top", cam=FULL),
    dict(shot="b2e5_top", cam=FULL),
]

if __name__ == "__main__":
    card = dict(title="Command Prompt", sub="Every Windows user should know", count=[0, 6], suffix=" commands",
                count_t=0.3, count_dur=1.2)
    dur, S = build("tiktok/04", BEATS, card, CAP, FULL, hide=HIDE, drift=0.01,
                   titles=None)
    p = os.path.join(ROOT, "tiktok/04/spec.json")
    spec = json.load(open(p))
    spec["card"]["t1"] = round(S[1]["e"] + 0.2, 2)
    spec["titles"] = [[S[16]["s"], "Save this for later", round(S[17]["s"] - S[16]["s"], 2)]]
    json.dump(spec, open(p, "w"), indent=1)
    print("tiktok/04 duration", dur)
