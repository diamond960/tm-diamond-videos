# TM_Diamond long videos (16:9, 8-12 minutes)

The goal is watch hours. Every long video is a genuinely useful, fact-checked tutorial with a strong hook, chapters and a reason to keep watching.

## Files per video (`long/NN/`)

- `script.txt`: the narration, ONE sentence per line. Section headers are lines starting with `## ` (these become YouTube chapters; the first one is the hook). There's an example in `long/01/script.txt`.
- `build.py`: the visual plan. Copy `long/01/build.py` as the pattern. It defines `VOICE`, `SPEC` (script/words/narration paths) and `build(tl)`, which returns the scenes, sfx, progress bar and caption highlights. Everything is anchored to lines found with `tl.find("unique words from the line")`, so it re-times itself if the voice changes.
- Voice: commit `jobs/longNN.json` = `{"out": "long/NN/voice", "tts": {"engine": "kokoro", "voice": "am_michael", "speed": 1.0, "text": "<script.txt without the ## lines>"}}`. Wait for `long/NN/voice.words.json` (about 8-12 minutes for a 9-minute script). Then set `VOICE = "voice"` in build.py.
- `thumb.json` for `engine/thumbnail.py`: `{"line1": "...", "line2": "...", "badge": "...", "emoji": ["💻", "⚡"], "accent": "lime"}`. Keep it to 1-3 big words per line.

## Scene types (`engine/longform.py`)

- `hook`: `{"lines": [{"text", "at", "c", "size", "strike_at"}], "emoji": [{"e", "at", "x", "y", "size"}]}`. Big kinetic statements. The first line must appear at the scene start, so the stage is never empty.
- `chapter`: `{"num": "STEP 1", "title": "...", "e": "📝"}`. Full-screen section card.
- `chat`: `{"title": "Claude", "user": "...", "user_at", "reply": "...", "reply_at", "apps": [{"name", "e", "at", "done_at"}]}`. A chat window with typing.
- `app`: `{"name", "e", "headline", "c", "rows": [{"text", "e", "at"}]}`. A window with up to 6 feature or step rows; the big emoji on the left follows the current row. Use this for steps, tips and settings.
- `transcript`: Descript-style text edit demo.
- `stats`: `{"rows": [{"kw", "num", "comp", "at", "tag", "tag_at"}]}`. Animated numbers. Only use REAL, sourced numbers.
- `bigstat`: `{"big", "label", "sub", "sub_at", "e", "c"}`. One giant number or word.
- `flow`: `{"steps": [{"text", "e", "at"}]}`. Up to 8 steps that light up in turn.
- `cards`: `{"cards": [{"title", "text", "e", "at", "c"}]}`. 1-3 cards.
- `resize`: aspect-ratio morph demo.
- `subscribe`: `{"tap_at", "next", "next_at"}`. Use for the CTA and end screen.

Optional `progress`: `{"show_at", "hide_at", "apps_at": [...], "tease": n}`. A numbered tracker along the top for list videos ("tip 3 of 10"); `tease` makes a later item glow so people wait for it.

## Retention rules

- **Hook (first 20 s):** promise the outcome, show proof, and tease the best item for later ("stay for number 8").
- **No dead time:** a new visual at least every ~8 seconds, one `app` row per step as it's spoken, sfx on reveals, a chapter card per section.
- **Mid-video:** a short subscribe ask at about 40%, followed straight away by a re-hook into the teased item.
- **Ending:** recap in one line, then point to a specific next video (`subscribe` scene with `next`). Never say "that's it, bye".
- **Honesty:** facts must be checked. Never fake screenshots of real people, never invent numbers, never claim hands-on use of a gadget we didn't use (do buying guides and spec comparisons instead).

## Render, check, publish

```
python3 engine/longform.py long/NN/build.py /tmp/sheet.png --preview <24 times spread across the video>   # look at it
python3 engine/longform.py long/NN/build.py videos/longNN_draft.mp4                                       # ~10 min
ffmpeg -v error -y -i videos/longNN_draft.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 128k -movflags +faststart videos/longNN.mp4
python3 engine/chapters.py long/NN/script.txt long/NN/voice.words.json    # chapters for the description
python3 engine/thumbnail.py long/NN/thumb.json long/NN/thumbnail.jpg
```

Commit `videos/longNN.mp4` (must be under 95 MB), the script, build, thumb.json, thumbnail and voice files, then publish with `engine/UPLOAD.md` (upload session, thumbnail, playlist).
