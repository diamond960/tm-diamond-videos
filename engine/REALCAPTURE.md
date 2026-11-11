# Real interface videos (owner rule, 2026-11-06): show the REAL screen, never a drawn mock-up

The owner wants every Windows, PC, Mac, phone and app tutorial to show the actual interface. Drawn recreations
(`winui`, `app` rows, note cards pretending to be windows) are no longer allowed for steps.

## Windows (working now)
1. Write `capture/<name>.ps1` (examples: `capture/fb07.ps1`, `capture/fb06.ps1`). It dot-sources `engine/wincap.ps1` and drives a real
   Windows PC (GitHub Actions `windows-2025` runner, Windows 11 interface, 1920x1080):
   - `Init-Capture '<name>'`, `Shot '<label>' @{rects}`, `Type-Shots 'text' '<label>'` (one real screenshot per
     character), `Key-Combo @($VK.WIN, $VK.R)`, `Click x y`, `Find-Rect 'Accessible name'` (screen rectangle of a real
     button/box for zooms and circles), `Place-Foreground x y w h`, `Save-Log`.
   - Open things the real way: `Start-Process 'ms-settings:display'`, `taskmgr`, `explorer`, Win+R, `msedge <url>`.
   - PowerShell variable names are case-insensitive: never name a variable `$n`, `$out` or `$log` in a capture script
     (they overwrite wincap.ps1's `$script:N`/`Out`/`Log` and the run stops). shots.json is UTF-8 with a BOM (`utf-8-sig`).
   - Push it: the "Capture real Windows screens" workflow runs it and commits `captures/<name>/*.png` + `shots.json`
     (cursor position, foreground window rectangle and title, rects) in ~3 minutes.
   - Keep the bottom-right corner (it shows "Windows Server 2025 / Test Mode") and the desktop icons out of every crop.
     Windows Server shows small extras (e.g. "This task will be created with administrative privileges" in Run);
     frame the camera so they are not the focus, and never mention them.
   - Things a Windows Server runner can't show honestly (Microsoft Store, Copilot, Widgets, Phone Link, consumer-only
     Settings pages, BIOS): don't make that topic.
2. Voice: `jobs/<name>.json` as before, then `python3 engine/tighten.py <dir>/voice.mp3 <dir>/voice.words.json
   <dir>/script.txt <dir>/tight` (cuts the 1 s pauses, gives exact word/sentence times; one script line = one sentence). If it prints
   "keeping original timing" (pauses inside a sentence, e.g. after a colon), see tiktok/01/tighten_fix.py.
   `"caption_y": [[t, 0.74], ...]` in the spec moves the captions down while the camera is on an address bar.
3. `<dir>/make_spec.py` like `fb/07/make_spec.py` (Team Diamond template; `"layout": "tmd"`): place every screenshot, camera move, keycap, typing burst, circle and
   sound on the spoken words from `tight.json`. Camera = centre + height in screen pixels (full -> focus -> full);
   the real screen always fills the 9:16 frame edge to edge (no borders, no paper margins).
4. `python3 engine/realcut.py <dir>/spec.json /tmp/sheet.png --preview t1,t2,...` (look at it), then render
   `python3 engine/realcut.py <dir>/spec.json videos/<name>.mp4`.

Sounds: real recorded CC0 UI sounds in `engine/sfx/kenney/interface-sounds` (Kenney, CC0): clicks, keyboard ticks,
pops, confirmation ding, window open. No music, no loud "viral" effects.

## Team Diamond template (`"layout": "tmd"`, the owner's format - use it for every vertical video)
- realcut puts the real screen in the middle panel (1080x979 at y 313), his logo strip on top
  (templates/tmd/top.png) and his presenter clip below (templates/tmd/bottom.mp4).
- Spec extras: `card` {t0, t1, y, title, sub, big, big2, swap_t | count:[a,b], suffix}, `boxes` [[t, [x,y,w,h], dur, (rgb)]]
  in screen pixels (green by default, red for the answer), `captions` false, `follow_y` 0.55.
- Camera `h` = visible screen height; width = h x 1.103. Use 300-520 so text is readable on a phone.
- Capture tips learned on fb07: Explorer submenus open on a click, not a hover (click the item, fall back to the
  Right arrow key); find each element with Find-Rect and log it so the spec can box it exactly; measure text
  edges from the PNG for tight boxes.
- Reference: fb/07 (capture/fb07.ps1 -> fb/07/make_spec.py -> videos/fb07.mp4).

## iPhone, Android, Mac (not built yet)
Planned: iOS Simulator and Android Emulator screenshots on GitHub runners, and macOS screenshots on a macOS runner.
Until they exist, do not make iPhone, Android or Mac tutorials with drawn screens. Pick a Windows topic instead.
AI apps that need a login (ChatGPT, Claude, Gemini) can't be recorded here either: no such tutorials with fake screens.

## Long YouTube videos (16:9)
Same pipeline with `"size": [1920, 1080]` in the spec: the camera crops the real 1920x1080 screen at 16:9 (wide shots =
the whole screen, focus shots = height 500-700), captions sit at the bottom, `"titles": [[t, "Fix 3: Startup apps", 2.0]]`
gives chapter cards over the real screen. Write one capture script per chapter (capture/longNN_01.ps1, ...) so a failed
step only needs that chapter re-captured. Render time is about 2-3 minutes per minute of video.

## ChatGPT on the capture PC (no account) - tested 2026-11-11

capture/aitest02.ps1: Edge `--start-maximized https://chatgpt.com/`, wait 15 s, check for a human-check page (stop if
there is one - never work around it), click the drawn "Ask ChatGPT" box (UIA can't see web content by name: click
its position from the screenshot), Type-Shots the prompt, Enter, then shots at 1, 2, 3, 5, 8, 12 s to film the answer
streaming in. Real answer in about 2 s. The browser fills the screen, so no desktop watermark shows.
For the full-screen look, try `Init-Capture 'name' 1280 720` so text is bigger relative to the screen (fall back to
1920x1080 if the display can't change), and/or Edge zoom 125% (Ctrl + plus twice) before typing.
Claude can't be filmed here (it needs the owner's login): Claude parts use the owner's recordings in footage/partNN/.

### THE ChatGPT recipe (tested 2026-11-11, use this one): capture/aitest03.ps1
- `Init-Capture 'name' 1280 720` works on the capture PC (screenshots come out 1280x720).
- Edge maximized on https://chatgpt.com/, wait 15 s, human-check stop, then Edge zoom 125%
  (`SendWait('^{ADD}')` twice). At 125% the sidebar collapses to icons and the text is big - readable in the
  full-screen look on a phone.
- ChatGPT puts the cursor in its box on load: press `{ESC}` once and type straight away (no click needed).
  Box on the empty page at 125%: about x 195-1150, y 250-310 (centre 680, 279) - animate the realcut cursor
  there for the viewer. After an answer, the box sits at the bottom (centre about 680, 607).
- Answer starts within 1 s; take shots at 1, 2, 3, 5, 8 s (more for long answers, scroll with `{PGDN}` and shot).
- Full-screen camera for 1280x720 captures: `[640, 360, 720]`; small push-in height >= 470.
