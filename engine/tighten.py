"""tighten.py - cut the long pauses out of a narration and give exact sentence/word times.

Pro editors jump-cut dead air. Kokoro leaves ~1 s between lines, and the word timings drift after
each pause. This finds the real speech with ffmpeg silencedetect, rebuilds the narration with short
gaps, and maps every script line to its own speech segment so captions and visuals land exactly.

Usage: python3 engine/tighten.py fb/06/voice.mp3 fb/06/voice.words.json fb/06/script.txt fb/06/tight [gap_s]
Writes <out>.wav and <out>.json = {"duration", "words": [{"w","s","e"}], "sentences": [{"text","s","e"}]}
"""
import json
import re
import subprocess
import sys


def speech_segments(path, merge_gap=0.32):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).group(3)) + 60 * int(re.search(r"Duration: (\d+):(\d+)", out).group(2))
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    # speech = complement of silences
    sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
    segs, t = [], 0.0
    for a, b in sil:
        if a > t + 0.02:
            segs.append([t, a])
        t = b
    if dur > t + 0.02:
        segs.append([t, dur])
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < merge_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(list(s))
    merged = [m for m in merged if m[1] - m[0] >= 0.12]
    return merged, dur


def line_word_counts(script):
    counts = []
    for line in script.splitlines():
        toks = [x for x in re.split(r"\s+", line.strip()) if re.search(r"\w", x)]
        n, run = 0, False
        for tk in toks:
            single = len(re.sub(r"\W", "", tk)) == 1 and tk.strip(",.?!").isupper()
            if single and run:
                continue
            n += 1
            run = single
        if n:
            counts.append((line.strip(), n))
    return counts


def main():
    voice, words_p, script_p, out = sys.argv[1:5]
    gap = float(sys.argv[5]) if len(sys.argv) > 5 else 0.30
    pad = 0.06
    segs, dur = speech_segments(voice)
    words = json.load(open(words_p))["words"]
    lines = line_word_counts(open(script_p).read())
    if len(lines) != len(segs) or sum(n for _, n in lines) != len(words):
        print(f"WARNING: {len(lines)} lines vs {len(segs)} speech parts, {sum(n for _, n in lines)} vs {len(words)} words; keeping original timing")
        segs = [[0, dur]]
        lines = [(" ".join(l for l, _ in lines), len(words))]
    # new timeline
    pieces, new_words, sentences, t, wi = [], [], [], 0.0, 0
    for (a, b), (text, n) in zip(segs, lines):
        a0, b0 = max(0.0, a - pad), min(dur, b + pad)
        pieces.append((a0, b0))
        ns, ne = t + (a - a0), t + (b - a0)
        ws = words[wi: wi + n]
        # keep the relative rhythm of the words inside this line, stretched onto the real speech span
        o0, o1 = ws[0]["s"], max(ws[-1]["e"], ws[0]["s"] + 0.05)
        for w in ws:
            f0 = (w["s"] - o0) / (o1 - o0)
            f1 = (w["e"] - o0) / (o1 - o0)
            new_words.append({"w": w["w"], "s": round(ns + f0 * (ne - ns), 3), "e": round(ns + f1 * (ne - ns), 3)})
        sentences.append({"text": text, "s": round(ns, 3), "e": round(ne, 3)})
        wi += n
        t += (b0 - a0) + gap
    total = t - gap + 0.1
    # audio: concat the speech pieces with short gaps
    filt, labels = [], []
    for i, (a0, b0) in enumerate(pieces):
        filt.append(f"[0:a]atrim={a0:.3f}:{b0:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b0 - a0 - 0.03:.3f}:d=0.03[p{i}]")
        labels.append(f"[p{i}]")
        if i < len(pieces) - 1:
            filt.append(f"anullsrc=r=24000:cl=mono,atrim=0:{gap:.3f}[g{i}]")
            labels.append(f"[g{i}]")
    filt.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1,aresample=48000[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-filter_complex", ";".join(filt), "-map", "[out]",
                    "-ac", "1", "-ar", "48000", out + ".wav"], check=True)
    json.dump({"duration": round(total, 3), "words": new_words, "sentences": sentences}, open(out + ".json", "w"), indent=1)
    print(f"{dur:.2f}s -> {total:.2f}s")
    for s in sentences:
        print(f"  {s['s']:6.2f}-{s['e']:6.2f}  {s['text']}")


if __name__ == "__main__":
    main()
