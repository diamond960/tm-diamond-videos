"""tiktok01: engine/tighten.py fell back to untouched timing (mid-sentence pauses after colons, and whisper
spelled letters differently). Same cut, but merge pauses < 0.65 s and give each word to the speech part it falls in."""
import json, subprocess, sys
sys.path.insert(0, "engine")
import tighten
voice, words_p, script_p, out = "tiktok/01/voice.mp3", "tiktok/01/voice.words.json", "tiktok/01/script.txt", "tiktok/01/tight"
gap, pad = 0.30, 0.06
segs, dur = tighten.speech_segments(voice, 0.65)
lines = [l.strip() for l in open(script_p).read().splitlines() if l.strip()]
assert len(segs) == len(lines), (len(segs), len(lines))
words = json.load(open(words_p))["words"]
pieces, new_words, sentences, t = [], [], [], 0.0
for k, ((a, b), text) in enumerate(zip(segs, lines)):
    a0, b0 = max(0.0, a - pad), min(dur, b + pad)
    lo = (segs[k - 1][1] + a) / 2 if k else -1
    hi = (b + segs[k + 1][0]) / 2 if k + 1 < len(segs) else 1e9
    for w in words:
        m = (w["s"] + w["e"]) / 2
        if lo <= m < hi:
            s = min(max(w["s"], a0), b0); e = min(max(w["e"], a0), b0)
            new_words.append({"w": w["w"], "s": round(t + s - a0, 3), "e": round(t + e - a0, 3)})
    sentences.append({"text": text, "s": round(t + a - a0, 3), "e": round(t + b - a0, 3)})
    pieces.append((a0, b0))
    t += (b0 - a0) + gap
total = t - gap + 0.1
filt, labels = [], []
for i, (a0, b0) in enumerate(pieces):
    filt.append(f"[0:a]atrim={a0:.3f}:{b0:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b0 - a0 - 0.03:.3f}:d=0.03[p{i}]")
    labels.append(f"[p{i}]")
    if i < len(pieces) - 1:
        filt.append(f"anullsrc=r=24000:cl=mono,atrim=0:{gap:.3f}[g{i}]")
        labels.append(f"[g{i}]")
filt.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1,aresample=48000[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-filter_complex", ";".join(filt), "-map", "[out]", "-ac", "1", "-ar", "48000", out + ".wav"], check=True)
json.dump({"duration": round(total, 3), "words": new_words, "sentences": sentences}, open(out + ".json", "w"), indent=1)
print(f"{dur:.2f}s -> {total:.2f}s")
for i, s in enumerate(sentences):
    ws = " ".join(w["w"] for w in new_words if s["s"] - 0.1 <= w["s"] <= s["e"] + 0.1)
    print(f"{i:2d} {s['s']:6.2f}-{s['e']:6.2f}  {ws}")
