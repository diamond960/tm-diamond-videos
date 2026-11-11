# TM Diamond house style (permanent owner rules, from 2026-11-06)

These rules override anything older in SPEC.md, LONGFORM.md or a task prompt.

## ORGANIZED, NOT RANDOM (owner rule, 2026-11-06)
- Every topic comes from content/plan.json, in order: one theme at a time (block), one long YouTube video per block
  and short "One-Minute Tech Fixes" episodes taken from it. Never pick a random or trending topic outside the plan.
  Shorts/Facebook/TikTok mention the full video on the channel when the block's long video is live.

## FACEBOOK: THE OWNER UPLOADS IT HIMSELF (owner rule, 2026-11-06)
- Never post to Facebook automatically (no Make `fb_reel` jobs). The owner uploads Facebook videos himself so he can
  put them in his Page playlist "One-Minute Tech Fixes". The Facebook task sends him each new video file + a
  ready caption at 5:37 PM New York, and marks it `"status": "sent_to_owner"`.
- Instagram keeps posting automatically. TikTok: a ready-to-post pack goes to the owner (automatic TikTok posting
  needs his approval of the publish step).

## THE TEAM DIAMOND TEMPLATE (owner's own format, 2026-11-06 - every vertical video uses it)
The owner sent his own example video; every vertical video (Facebook, Instagram, TikTok, YouTube Shorts) now copies it.
OWNER APPROVED (2026-11-06, 8:25 AM): "This is how I want the edit to look ... keep it that way" - videos/fb07.mp4 is the
approved look. Copy it exactly (layout, zoom, hook card, green/red boxes, cursor, keycaps, sounds, no captions, no music);
do not experiment with new styles or effects unless the owner asks.
Spec: `"layout": "tmd"` in realcut (fb/07/make_spec.py is the reference).
- Three bands on 1080x1920: top 0-312 = his red-grid TEAM DIAMOND logo strip (templates/tmd/top.png);
  middle 313-1292 = the REAL screen, zoomed so text is easy to read (camera height 300-520 screen px);
  bottom 1292-1920 = his presenter clip (templates/tmd/bottom.mp4, looped). Never cover or replace the bands.
- Windows in dark mode (set the theme in the capture script). Keep the camera inside the app window
  (no desktop wallpaper, no "Test Mode/Windows Server" watermark, no desktop icons).
- Hook card in the first 3 s (`card`): title + grey sub + a big word that changes on the reveal word
  (`big` -> `big2`, the new part in red) or a number that counts up (`count`).
- Thin green rounded boxes (`boxes`) on each thing to click, red boxes on the danger/answer; a yellow click ring
  under the cursor; white keycaps for shortcuts; no on-screen captions (`"captions": false`).
- The follow pill at the end. Narration tightened with engine/tighten.py. No music.

## REAL INTERFACE ONLY (owner rule, 2026-11-06 - overrides the studio-style rules below)
- Every tutorial shows the REAL interface: real screenshots taken on a real Windows PC, edited with zooms,
  a cursor, keycaps, red circles and captions. Follow engine/REALCAPTURE.md (wincap.ps1 -> tighten.py -> realcut.py;
  fb/07 is the reference - fb/06 used the old full-frame look). Drawn mock-ups (`winui`, `app` rows, cards pretending to be windows) are banned for steps.
- Vertical videos use the Team Diamond template above (real screen in the middle band). No extra paper margins,
  white frames or letterbox around the screen (Facebook flagged our old framed videos as "has a border").
- Until the phone/Mac/AI-app capture pipelines exist, make only Windows/PC topics that a Windows runner can show.
- Sound: narration + real recorded CC0 UI sounds (engine/sfx/kenney) on the exact actions. No music.
- Pacing: tighten the narration (no dead air); hook in the first second; most Facebook Reels 10-15 s.

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
- Long-video order (replaces the list in the long-video task; skip any already made). Real screens only, so only
  topics a Windows PC can show for real (REALCAPTURE.md):
  (content/plan.json blocks 1-5 follow this order)
  1. Windows 11 Running Slow? 12 Fixes That Actually Work
  2. 15 Command Prompt Commands Every Windows User Should Know
  3. 10 Windows 11 Settings You Should Change Right Now
  4. Free Up Disk Space on Windows 11 (Every Safe Method)
  5. 15 Windows Keyboard Shortcuts That Save Hours
  6. Task Manager Explained: Hidden Features Most People Miss
  7. How to Back Up Your Windows PC for Free (Built-in Tools)
  8. Wi-Fi or Internet Problems on Windows 11? Every Fix, Step by Step (needs real Wi-Fi screens)
  App Store / Google Play publishing (the channel's best long video ever) needs real App Store Connect / Play Console
  screens: make it only when the owner sends his own screen recording of those pages.
- Shorts topics: take them from the formats that worked above (Windows problem + fix, iPhone/Android mistakes and hidden settings, AI prompt tips), 15-35 s.

## TRAILER SHORTS FOR LONG VIDEOS (2026-11-11)

Every long video gets at least one Short cut from one of its fixes (real captures, Team Diamond template), ending on a
"Fix N of 10" band then a "Full video below" band. The owner links it in Studio (Related video). Reference: shorts/06.

## 2026-11-11 OWNER: ZOOM OUT, ONE SERIES AT A TIME, POST EVERYWHERE (overrides older rules below/above)

- ZOOM OUT: "people don't see the full thing... I want them to see the full laptop screen... zoom out a little bit,
  not zooming in." Every vertical video uses `"layout": "tmd", "framing": "full"`: the whole 16:9 screen right
  under the logo strip, an info band under it (hook card first, then a "STEP n" label for each step, then the
  "Part n of the series" / follow card), the presenter strip at the bottom. Camera = the whole screen
  `[960, 540, 1080]` (for 1920x1080 captures) most of the time; a small push-in (camera height >= 700 for
  1920x1080, >= 470 for 1280x720) ONLY when the target is tiny (a taskbar menu, a small button), then back out.
  Hide the capture PC's desktop watermark with `"hide"` (it says Test Mode / Windows Server) when the desktop shows.
  Keycaps at y fraction 0.37 (on the screen, not the band). Reference: shorts/06/make_spec_full.py.
- ONE SERIES AT A TIME, NUMBERED: the current series is the first block in content/plan.json with unused
  episodes. Today that's "AI for Creators" (ChatGPT & Claude). Every video says its part number (hook card kicker
  "PART 3", title "... (Part 3)", caption) and the last line teases the next part ("Part 4: ...").
- WHAT WORKS (research 2026-11-11): viewers decide in about 1.4-2.3 s, so open on the RESULT (the real answer on
  screen) with a one-line hook; most Reels/TikToks start muted, so every step has its on-screen STEP label; one idea
  per video; 20-40 s; end with the next part.
- POST EVERYWHERE: the owner now wants us to post on YouTube Shorts, Facebook Page (Reel, via Make fb_reel) and
  Instagram (Reel, via vidIQ) ourselves. TikTok needs the owner's tap: send him the file + caption to post.
  (The 2026-11-06 "owner uploads Facebook himself" rule is replaced.)

## 2026-11-11 (later) OWNER: DEVICE SERIES + PLATFORM LENGTHS - see engine/SCHEDULE.md (overrides the AI-series note above)

"Cover everything about Windows, MacBook, iPhone, Android, serially. 5-6 videos on Facebook (15, 20, 25, 30 s depending
on the tutorial), 1-2 on Instagram, TikTok 1 minute plus (never 15 s), YouTube do the best." Windows first; the AI for
Creators series is paused after Part 1. Facebook reels end with the follow card (no "full video below" - there is no
link on Facebook). TikTok = one 61-75 s video a day combining the block's tips (tiktok/03 is the reference).
