"""Print YouTube chapters for a long video from its script sections and word timings.
Usage: python3 engine/chapters.py long/01/script.txt long/01/voice.words.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from longform import Timeline
tl = Timeline(sys.argv[1], sys.argv[2])
names = {"HOOK": "9 apps, 1 chat"}
for i, (name, li) in enumerate(tl.sections):
    t = 0 if i == 0 else tl.line_start(li)
    m, s = divmod(int(t), 60)
    print(f"{m}:{s:02d} {names.get(name, name.title().replace('Ai ', 'AI ').replace('Vidiq', 'vidIQ').replace('Opusclip', 'OpusClip').replace('Hyperframes', 'HyperFrames').replace('Heygen', 'HeyGen'))}")
