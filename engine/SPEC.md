# TM_Diamond Shorts pipeline (free)

Everything here runs for free: GitHub Actions makes the voice and word timings, `engine/shorts.py` renders the video in the Claude workspace, and `engine/UPLOAD.md` uploads it to YouTube (a Make upload session plus a GitHub Action, any file size) and cross-posts it to Instagram.

## 1. Voice + word timings (GitHub Actions)

Commit a job file `jobs/<name>.json` and push. The "Voice and timings" workflow runs it, then commits `<out>.mp3` and `<out>.words.json` and deletes the job. It takes about 4-8 minutes. Poll with `git pull` until the `.words.json` file appears, or check `https://api.github.com/repos/diamond960/tm-diamond-videos/actions/runs?per_page=3`.

- Free voice (Kokoro, open source):
  `{"out": "shorts/03/voice", "tts": {"engine": "kokoro", "voice": "<VOICE>", "speed": 1.05, "text": "<script, one sentence per line>"}}`
- Existing audio file, e.g. a Higgsfield Grady MP3 URL:
  `{"out": "shorts/03/voice", "url": "https://.../file.mp3", "text": "<the exact script, one sentence per line>"}`

Always include the script (`text`). The engine then uses the script's own words and punctuation for captions and sentence breaks, and keeps Whisper's timings.

To get any public file into the repo without timings, use `requests/<name>.json`:
`{"files": [{"url": "...", "path": "inbox/x.mp3"}]}` (the "Fetch media" workflow).

Run `python3 engine/plan.py shorts/03/voice.words.json` to print each sentence with its start and end time, plus every word's time.

## 2. Spec (`shorts/NN/spec.json`)

```json
{
  "title": "...",
  "duration": <narration duration + 0.4>,
  "narration": "voice.mp3",
  "bpm": 118,
  "music_db": 19,
  "captions": {"auto": true, "words": "voice.words.json", "highlight": ["itself", "free", "..."]},
  "visuals": [ {"type": "...", "t0": <sentence start>, "t1": <next sentence start>, ...}, ... ],
  "sfx": [ {"t": 0.0, "type": "bass"}, ... ]
}
```

Visuals must tile the whole timeline with no gaps: each `t1` equals the next `t0`, the first starts at 0.0, and the last ends at `duration`. Use one visual per sentence, and two for long sentences. For the loop, the last 0.5 s should repeat the first visual.

Visual types (all centred in the upper-middle area; captions go below):

- `card`: YouTube Studio card with a SCHEDULED badge. `{"crash": true}`
- `emoji`: `{"items": [{"e": "🤖", "t": 1.2, "size": 380, "x": 0, "y": 0}], "cross": {"t": 2.0, "kind": "x"|"ban", "size": 420, "x": 0, "y": 0}}`. Any emoji works, so use this for almost any idea.
- `iconx`: `{"icon": "timeline"|"upload", "cross_t": 6.0}` (red X over an editing timeline or upload button)
- `chat`: `{"name": "Claude", "user": "short user message", "user_t": 9.4}`
- `search`: `{"query": "...", "type_t": .., "type_dur": 1.6, "rows": [{"text": "...", "t": ..}], "arrow_t": ..}`
- `page`: `{"label": "THE HOOK", "lines_t": ..}` (a document writing itself)
- `pills`: `{"items": [{"text": "TEXT", "c": "lime|blue|pink|cyan|yellow|orange", "t": ..}]}` (max 5)
- `waveform`: animated voice bars
- `progress`: `{"fill_t": .., "fill_dur": 2.2, "checks": [{"text": "TITLE", "show": .., "tick": ..}]}`
- `clock`: `{"label": "6:00 PM", "land_t": .., "viewers_t": [..]}`
- `calendar`: `{"pages": [{"t": .., "head": "NOV", "num": "6"}]}`
- `follow`: `{"name": "TM_Diamond", "label": "Follow", "done_label": "Following", "tap_t": ..}` (use for the CTA)
- `bigtext`: `{"text": "3", "c": "lime", "size": 300, "sub": "FREE AI TOOLS", "sub_t": ..}`
- `list`: `{"items": [{"text": "...", "t": .., "e": "🎬", "c": "lime"}]}` (max 4 rows)
- `versus`: `{"cols": [{"title": "ChatGPT", "e": "💬", "c": "green", "t": .., "line": "Best for ...", "line_t": .., "win_t": ..}]}` (2-3 columns)

Colours: w, lime, orange (Claude), red (negatives), blue, pink, cyan, yellow, green.

Sound effects (`sfx`): whoosh, pop, click, bass, tick, ding, error, ping, glitch, flip, typing, riser, zoom,
plus the **viral meme-style pack** (all synthesized here, no copied recordings):

| sfx | sounds like | use it on |
|---|---|---|
| `boom` | deep "vine boom" hit (also shakes the camera) | the hook word, a shocking fact, the twist |
| `scratch` | record scratch | "Wait..." / "Stop!" / a sudden turn |
| `dun` | dramatic "dun dun duuun" (shakes) | a reveal, "this is why" |
| `buzzer` | wrong-answer game-show buzzer | "you're doing it wrong" / the bad way |
| `correct` | quiz "correct!" chime | the right way / the fix working |
| `cash` | cha-ching | money, "free", saving time or money |
| `shutter` | camera click | screenshots, "save this" |
| `tada` | quick fanfare | the final result / payoff |
| `swipe` | fast swipe | quick list items, page changes |
| `airhorn` | short airhorn | at most once, on a big win |

Use 2-4 viral sounds per video, on the moments that matter (hook, twist, wrong way, right way, payoff) -
not on every line, or they stop working.

- A whoosh is added automatically at every visual change.
- Add a bass on the hook (t=0) and on the twist line.
- Add a pop on each reveal (pill, list row, emoji), ticks on checks, typing under search or page, a click on the follow tap, and a ding on a time reveal.
- A `glitch` sfx also makes a visual RGB glitch and flash.
- A `zoom` sfx also makes an emphasis punch-in (snap in, hold, ease out). They are added automatically on every
  highlighted caption line (lime/orange/red words) that isn't within 0.7 s of a cut or another hit, so every
  zoom comes with a sound. Turn off with `"auto_zoom": false`.

## Captions and hashtags (owner's rule)

- Hashtags only when they help people find the video: 0-4 specific, searchable ones that match the topic
  (#windows11, #chatgpt, #pctips, #claudeai, #techtips). Never #reels, #viral, #fyp, #foryou or long tag walls.
- The caption's first line repeats the hook with the main search keyword in plain words (Instagram, Facebook and
  TikTok search read captions). Add a question that invites a comment.
- On TikTok, adding a trending sound in the app at very low volume (about 5%) under the voice can help reach.

## Platform versions

- **YouTube Shorts**: with the background beat (default render) -> `videos/shortNN.mp4`.
- **Instagram Reels / Facebook Reels**: NO background beat; voice + every zoom and sound effect stays
  (`--no-music`; effects are mixed a little louder) -> `videos/shortNN_social.mp4`.
- Length: 18-35 s is the sweet spot for Reels and Shorts (quick reveals 18-25 s, lists/comparisons 28-35 s).
- TikTok (when connected): 61+ s, no beat, because TikTok's Creator Rewards only pay for videos over 1 minute.

## 3. Render, check, publish

```
python3 engine/shorts.py shorts/NN/spec.json /tmp/sheet.png --preview 0.3,2.0,...   # contact sheet to look at
python3 engine/shorts.py shorts/NN/spec.json videos/shortNN.mp4                     # ~1 min; prints size_bytes
python3 engine/shorts.py shorts/NN/spec.json videos/shortNN_social.mp4 --no-music   # Instagram/Facebook version
```

- Default quality is crf 21 with a 3000 kbps peak (sharp on phones, under Instagram's 5 Mbps limit); a 50 s Short is about 8 MB.
- Commit and push `videos/shortNN.mp4`, the spec and the voice files, then publish with `engine/UPLOAD.md`.
- The public file link (for Instagram) is `https://raw.githubusercontent.com/diamond960/tm-diamond-videos/<commit sha>/videos/shortNN.mp4`.

## TikTok daily pack (posted by the owner)

TikTok can't be posted to automatically for free, so every morning the pack goes to the owner's phone:

- **Video** (`tiktok/NN/`): 61-75 s (TikTok only pays for videos over 1 minute), no beat, same pipeline as a Short
  (voice job with `"out": "tiktok/NN/voice"`, spec, `--no-music` render to `videos/tiktokNN.mp4`). Script 170-200 words.
  Check the real duration is over 61 s; if not, add a sentence and redo the voice.
- **Photo carousel**: `python3 engine/carousel.py tiktok/NN/carousel.json tiktok/NN/slides/` makes 1080x1920 JPEG
  slides: a cover, 3-6 tip slides (`kicker` number, `title` up to ~6 words, `body` up to ~20 words, `e` emoji)
  and an end slide. See the docstring in `engine/carousel.py`.
- **Text post**: a hook line plus 3-6 short lines, written for TikTok's text post (the owner pastes it).
- Record everything in `tiktok/NN/pack.json` (`topic`, `video_title`, `caption_video`, `carousel_title`,
  `caption_carousel`, `text_post`, `sent_at`).
