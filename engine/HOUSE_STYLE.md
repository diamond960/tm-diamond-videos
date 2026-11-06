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

## Captions, length and posting times (owner rule, 2026-11-06, from his Facebook Creator Dashboard)
- Captions on every platform: ONE line of 50-100 characters (hook + main keyword) and exactly 2-3 specific
  hashtags. No long captions, lists, "follow for" lines or tag walls. Titles short.
- Facebook Reels: two of every three are 10-14 s (one quick fix, 28-38 spoken words); the third 20-30 s.
- Facebook posts go out between 6:00 and 10:00 PM New York (his prime time).

## Content rules
- Categories: A Windows/PC, B MacBook/macOS, C iPhone/Android, D AI tools, E CMD/PowerShell/coding,
  F laptops/gaming/hardware. Slots: morning A/B, afternoon C/D, evening E/F.
- CMD/PowerShell: say what the command does, where to run it (normal or admin terminal), what result to
  expect, and any risk. Never show destructive commands without a clear warning.
- Hardware/gaming numbers only from a named source with game, hardware, resolution and settings.
- Every video: hook (first second), accurate script, one clear objective, captions, ending, CTA.
- Never: FRP bypass, iCloud unlock, jailbreak, free Windows/Office activation or any security/licence bypass;
  fake hands-on reviews; invented stats; AI-generated labels or "AI voice" lines.
- Calendar: content/calendar.json holds the week's planned ideas. Before inventing a topic, take the next unused idea
  ("used_by": null) whose category fits your slot (A/B morning, C/D afternoon, E/F evening; any category for
  Facebook/TikTok), set its "used_by" to your folder (e.g. "shorts/05") and its "stage" as it moves.
- Topic database: content/topics.json. Check it before picking a topic (no repeats by meaning) and append
  every new topic with its category, date and platform links.

## YouTube: what to make (from this channel's own numbers, 2026-11-06)
These rules override the topic lists inside the Shorts and long-video task prompts.
- What has worked on this channel. Shorts:
  - problem + fix: "White Screen with Cursor? FIX It in Seconds!" (4.1K views), "How to delete any file that refuses to delete" (4.1K), "Slow Internet on Your Laptop? This Setting Is Killing Your Speed!" (2.9K);
  - iPhone mistakes and iOS comparisons: "Don't Do This to Your iPhone Screen!" (6.9K), "iOS 26 vs iOS 18 Ringtones" (8K);
  - practical AI prompt tips: "Claude Prompts You Don't Wanna Skip!" (1.2K), "Secret Commands for Anthropic's Claude" (1.3K).
- What has worked for long videos: step-by-step how-tos for a task people search: "How to Submit/Publish an App to the Apple App Store" (25K), "Publish Your App" (4.8K), "How to Build an IPA File on Xcode" (3.7K), Windows install and Wi-Fi fixes.
- What failed: videos about our own setup ("9 Apps I Connected to Claude", 8 views; "My YouTube Channel Posts Videos By Itself"). NEVER make videos about the TM Diamond pipeline, "my channel runs itself" or "apps I connected". AI videos must be a practical how-to the viewer can copy: a prompt, a feature, a fix.
- Titles: the problem or task in the viewer's own words first ("Windows 11 slow?", "How to publish an app on the App Store"), then the promise. Under 60 characters. No vague curiosity-only titles.
- Every upload: embeddable true, publicStatsViewable true, containsSyntheticMedia false. Never upload the same video twice; check the channel's latest uploads before uploading.
- Long-video order (replaces the list in the long-video task; skip any already made):
  1. How to Publish an App on the Apple App Store in 2026 (Step by Step)
  2. Windows 11 Running Slow? 12 Fixes That Actually Work
  3. How to Publish an App on Google Play in 2026 (Step by Step)
  4. ChatGPT vs Gemini vs Claude: Which AI Should You Use?
  5. Wi-Fi Not Showing on Windows 11? Every Fix, Step by Step
  6. 25 Claude Prompts for Beginners (Copy and Paste)
  7. 10 Windows 11 Settings You Should Change Right Now
  8. How to Install Windows 11 from a USB Drive (2026 Guide)
  9. 15 Windows Keyboard Shortcuts That Save Hours
  10. MacBook or Windows Laptop for Students and Creators? (Buying Guide)

  After that, choose search-led topics in the same style. Video 01's "what's next" promise is dropped.
- Shorts topics: take them from the formats that worked above (Windows problem + fix, iPhone/Android mistakes and hidden settings, AI prompt tips), 15-35 s.
