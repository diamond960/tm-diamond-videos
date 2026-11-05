"""Print the sentences of a narration with start/end times, from <voice>.words.json.
Usage: python3 engine/plan.py shorts/03/voice.words.json"""
import json, sys
d = json.load(open(sys.argv[1]))
sent, out = [], []
for w in d["words"]:
    sent.append(w)
    if w["w"].rstrip().endswith((".", "?", "!", "…")):
        out.append(sent); sent = []
if sent:
    out.append(sent)
for i, s in enumerate(out, 1):
    nxt = out[i][0]["s"] if i < len(out) else d["duration"]
    print(f"{i:2d}  start {s[0]['s']:6.2f}  end {s[-1]['e']:6.2f}  next {nxt:6.2f}  | " + " ".join(x["w"] for x in s))
    for x in s:
        print(f"        {x['s']:6.2f} {x['w']}")
print(f"narration duration {d['duration']:.2f}")
