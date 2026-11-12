"""Windows block 2 "Command Prompt basics", batch 2026-11-12: 15-30 s Facebook reels + TikTok 04, cut from the real
Command Prompt screens recorded at 1280x720 (captures/day20261112, admin ones in captures/day20261112b), Team Diamond
template with the owner's full-screen framing. Run: python3 fb/make_batch_1112.py [names...]
Beat format: fb/batch_lib.py."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch_lib import build, RED, ROOT  # noqa: E402

CAP = "captures/day20261112"
FULL = (640, 360, 720)
HIDE = [[1082, 617, 198, 54]]        # "Test Mode / Windows Server" desktop watermark (1280x720)
GREEN = None                         # default box colour

# Win + R -> cmd -> Enter (shared by the reels that open Command Prompt this way)
RUN = dict(shot="cmd_run", cam=FULL, keys=[(["Win", "R"], 0.0), (["Enter"], 0.84)], seq=("cmd_run_type", 0.45, 0.62), typing=True,
           boxes=[([77, 531, 323, 25], GREEN, 0.4, 0.9)], after=[(0.92, "cmd_open")], step=("Step 1", "Win + R, type cmd, Enter"))

IPV4 = [2, 269, 600, 24]
SUCCESS = [2, 591, 842, 24]
NOTEPAD_ROW = [2, 545, 925, 24]
TASKBAR_NP = [843, 676, 40, 40]

CLIPS = {
    "fb/16": dict(
        title="Find your PC's IP address in 2 seconds",
        card=dict(title="Command Prompt", sub="No apps needed", big="Your IP address"),
        beats=[
            dict(shot="b2e2_result", cam=FULL, boxes=[(IPV4, GREEN, 0.3, 1.0)]),
            dict(RUN),
            dict(shot="b2e2_clean", cam=FULL, seq=("b2e2_type", 0.15, 0.55), typing=True, keys=(["Enter"], 0.7),
                 after=[(0.74, "b2e2_result")], step=("Step 2", "Type ipconfig, press Enter")),
            dict(shot="b2e2_result", cam=(440, 290, 500), boxes=[(IPV4, GREEN)], step=("Step 3", "Find IPv4 Address")),
            dict(shot="b2e2_result", cam=(440, 290, 500), boxes=[([470, 269, 132, 24], GREEN)],
                 step=("Done", "Your PC's address on your network")),
            dict(shot="b2e2_result", cam=FULL),
        ]),
    "fb/18": dict(
        title="See exactly what's inside your PC",
        card=dict(title="Command Prompt", sub="Windows version, processor, RAM", big="What's in my PC?"),
        beats=[
            dict(shot="b2e5_top", cam=FULL),
            dict(RUN),
            dict(shot="b2e5_clean", cam=FULL, seq=("b2e5_type", 0.1, 0.5), typing=True, keys=(["Enter"], 0.62),
                 after=[(0.66, "b2e5_loading:first"), (0.85, "b2e5_loading")], step=("Step 2", "Type systeminfo, press Enter")),
            dict(shot="b2e5_result", cam=FULL, seq=("b2e5_scroll", 0.05, 0.75), after=[(0.85, "b2e5_top")],
                 step=("Step 3", "Scroll up to the top")),
            dict(shot="b2e5_top", cam=FULL, boxes=[([2, 131, 862, 24], GREEN, 0.0, 0.38), ([2, 430, 1138, 47], GREEN, 0.38, 0.68),
                                                    ([2, 637, 490, 24], GREEN, 0.68, 1.2)],
                 step=("Result", "Windows version, processor, RAM")),
            dict(shot="b2e5_top", cam=FULL),
        ]),
    "fb/19": dict(
        title="App frozen? Force it shut with one command",
        card=dict(title="Command Prompt", sub="App frozen and won't close?", big="Force it shut"),
        beats=[
            dict(shot="b2e6_notepad", cam=FULL, boxes=[([338, 111, 604, 411], RED, 0.3, 1.0)]),
            dict(shot="b2e6_back", cam=FULL, seq=("b2e6_type1", 0.4, 0.72), typing=True, keys=(["Enter"], 0.84),
                 after=[(0.88, "b2e6_list")], step=("Step 1", "Type tasklist, press Enter")),
            dict(shot="b2e6_list", cam=FULL, boxes=[(NOTEPAD_ROW, GREEN)], step=("Step 2", "Find the app: notepad.exe")),
            dict(shot="b2e6_list", cam=FULL, seq=("b2e6_type2", 0.05, 0.8), typing=True, keys=(["Enter"], 0.88),
                 boxes=[(TASKBAR_NP, RED, 0.0, 0.9)], after=[(0.92, "b2e6_result")], step=("Step 3", "taskkill /im notepad.exe /f")),
            dict(shot="b2e6_result2", cam=FULL, boxes=[(SUCCESS, GREEN, 0.0, 0.5), (TASKBAR_NP, RED, 0.5, 1.0)],
                 step=("Done", "Closed. Unsaved work in it is lost")),
            dict(shot="b2e6_result2", cam=FULL),
        ]),
    "fb/21": dict(
        title="See every driver on your PC with one command",
        card=dict(title="Command Prompt", sub="Every driver, one list", big="driverquery"),
        beats=[
            dict(shot="b2e9_result", cam=FULL),
            dict(RUN),
            dict(shot="b2e9_clean", cam=FULL, seq=("b2e9_type", 0.05, 0.45), typing=True, keys=(["Enter"], 0.62),
                 after=[(0.66, "b2e9_loading"), (0.8, "b2e9_result")], step=("Step 2", "Type driverquery, press Enter")),
            dict(shot="b2e9_result", cam=FULL, boxes=[([2, 38, 432, 578], GREEN, 0.0, 0.55), ([436, 38, 142, 578], GREEN, 0.55, 1.1)],
                 step=("Result", "Every driver: name and type")),
            dict(shot="b2e9_result", cam=FULL, step=("Tip", "Check here after a bad update")),
            dict(shot="b2e9_result", cam=FULL),
        ]),
}


if __name__ == "__main__":
    want = sys.argv[1:] or list(CLIPS)
    for name in want:
        c = CLIPS[name]
        if not os.path.exists(os.path.join(ROOT, name, "tight.json")):
            print(name, "no tight.json yet"); continue
        dur, S = build(name, c["beats"], c["card"], c.get("captures", CAP), FULL, hide=HIDE, drift=0.01)
        print(name, "duration", dur)
