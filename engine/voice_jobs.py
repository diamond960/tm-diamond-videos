"""Runs on GitHub Actions. For each jobs/*.json:
  {"out": "shorts/03/voice", "tts": {"engine": "kokoro", "voice": "am_michael", "speed": 1.05, "text": "..."}}
  or {"out": "...", "url": "https://.../narration.mp3"}
Writes <out>.mp3 and <out>.words.json (word timings from faster-whisper),
then deletes the job file."""
import glob, json, os, subprocess, urllib.request

import numpy as np
import soundfile as sf

_kp = {}


def kokoro_tts(text, voice, speed, wav_path):
    from kokoro import KPipeline
    lang = voice[0]
    if lang not in _kp:
        _kp[lang] = KPipeline(lang_code=lang)
    chunks = []
    for _, _, audio in _kp[lang](text, voice=voice, speed=speed, split_pattern=r"\n+"):
        a = audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio)
        chunks.append(a)
        chunks.append(np.zeros(int(0.12 * 24000), dtype=a.dtype))
    sf.write(wav_path, np.concatenate(chunks), 24000)


def words(path):
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, info = m.transcribe(path, word_timestamps=True, beam_size=5, vad_filter=False)
    out = []
    for sg in segs:
        for w in sg.words:
            out.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    return out, info.duration


for job in sorted(glob.glob("jobs/*.json")):
    spec = json.load(open(job))
    out = spec["out"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    mp3 = out + ".mp3"
    if "url" in spec:
        urllib.request.urlretrieve(spec["url"], mp3)
    else:
        t = spec["tts"]
        wav = out + ".wav"
        kokoro_tts(t["text"], t.get("voice", "am_michael"), t.get("speed", 1.0), wav)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "128k", mp3], check=True)
        os.remove(wav)
    if spec.get("timings", True):
        ws, dur = words(mp3)
        json.dump({"duration": dur, "words": ws}, open(out + ".words.json", "w"), indent=0)
    os.remove(job)
    print("done", out)
