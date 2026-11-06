# TM Diamond house style (permanent owner rules, from 2026-11-06)

These rules override anything older in SPEC.md, LONGFORM.md or a task prompt.

## Audio (never break)
- NO background music of any kind: no beats, instrumentals, cinematic, ambient, lo-fi or sound beds.
  The renderers hard-disable music; never add a music file, and never tell the owner to add a trending sound.
- Only: clear narration (kokoro `am_michael`, natural American-English male, speed 1.0-1.05, starts in the first
  second), subtle mouse clicks, keyboard typing, UI pops, notification dings, short whooshes and relevant
  digital sounds, each synced to the exact visual action.
- Sound types to use: `click`, `pop`, `whoosh`, `correct`, `shutter` (only for "save/screenshot"), `zoom` (soft),
  `type` if available. Do NOT use the loud "viral" pack (boom, airhorn, buzzer, scratch, dun, cash, tada) in new videos.
- Render ONE file per video. The YouTube, Facebook, Instagram and TikTok versions are the same file
  (set `social_file_url` = `file_url`).

## Look: the "studio" style (vertical videos)
Spec: `"style": "studio"`, `"series": "<category label>"` (e.g. "windows fix", "ai tools", "iphone tip",
"cmd", "gaming"). Rendered by engine/studio.py through engine/shorts.py. studio/pilot01/make_spec.py is the
reference example.
- Beige paper with a faint graph grid; small mono header `// tm_diamond` + series label.
- Caption at the top builds word by word (dark sans); 3-8 keywords per video in red serif italic
  (`captions.highlight`), 1-3 of them underlined in red marker (`captions.underline`). No caption list needed:
  `"captions": {"words": "voice.words.json", "highlight": [...], "underline": [...]}`.
- Middle band = the content: white instruction cards (`note`), real-looking interface recreations
  (`winui` for Windows; build the same way for macOS/iPhone/Android menus), keycaps (`keys`), red marker
  circles and red arrows on exactly what to click, punch-in zoom on the target, paper-cut wipe between scenes.
- Never invent a menu, button, feature or command. Every on-screen step must match the real interface
  (check official docs). If a screen can't be recreated accurately, show a note card with the exact path instead.
- Something changes every 1.5-3 s, but no random effects: every motion follows the narration.
- Presenter (cartoon of the owner, presenter/poses: talk, idea, point, think, thumbs, shrug, shocked, phone):
  lower-right by default (`"presenter": {"side": "right" | "left", "poses": [[t, "pose"], ...]}`), pose changes
  on sentence starts, pointing toward the content. It only appears once engine/brand.json has
  `"presenter_approved": true` (the renderer enforces this). It must never cover instructions.

## Content rules
- Categories: A Windows/PC, B MacBook/macOS, C iPhone/Android, D AI tools, E CMD/PowerShell/coding,
  F laptops/gaming/hardware. Slots: morning A/B, afternoon C/D, evening E/F.
- CMD/PowerShell: say what the command does, where to run it (normal or admin terminal), what result to
  expect, and any risk. Never show destructive commands without a clear warning.
- Hardware/gaming numbers only from a named source with game, hardware, resolution and settings.
- Every video: hook (first second), accurate script, one clear objective, captions, ending, CTA.
- Never: FRP bypass, iCloud unlock, jailbreak, free Windows/Office activation or any security/licence bypass;
  fake hands-on reviews; invented stats; AI-generated labels or "AI voice" lines.
- Topic database: content/topics.json. Check it before picking a topic (no repeats by meaning) and append
  every new topic with its category, date and platform links.
