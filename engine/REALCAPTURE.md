# Real interface videos (owner rule, 2026-11-06): show the REAL screen, never a drawn mock-up

The owner wants every Windows, PC, Mac, phone and app tutorial to show the actual interface. Drawn recreations
(`winui`, `app` rows, note cards pretending to be windows) are no longer allowed for steps.

## Windows (working now)
1. Write `capture/<name>.ps1` (example: `capture/fb06.ps1`). It dot-sources `engine/wincap.ps1` and drives a real
   Windows PC (GitHub Actions `windows-2025` runner, Windows 11 interface, 1920x1080):
   - `Init-Capture '<name>'`, `Shot '<label>' @{rects}`, `Type-Shots 'text' '<label>'` (one real screenshot per
     character), `Key-Combo @($VK.WIN, $VK.R)`, `Click x y`, `Find-Rect 'Accessible name'` (screen rectangle of a real
     button/box for zooms and circles), `Place-Foreground x y w h`, `Save-Log`.
   - Open things the real way: `Start-Process 'ms-settings:display'`, `taskmgr`, `explorer`, Win+R, `msedge <url>`.
   - Push it: the "Capture real Windows screens" workflow runs it and commits `captures/<name>/*.png` + `shots.json`
     (cursor position, foreground window rectangle and title, rects) in ~3 minutes.
   - Keep the bottom-right corner (it shows "Windows Server 2025 / Test Mode") and the desktop icons out of every crop.
     Windows Server shows small extras (e.g. "This task will be created with administrative privileges" in Run);
     frame the camera so they are not the focus, and never mention them.
   - Things a Windows Server runner can't show honestly (Microsoft Store, Copilot, Widgets, Phone Link, consumer-only
     Settings pages, BIOS): don't make that topic.
2. Voice: `jobs/<name>.json` as before, then `python3 engine/tighten.py <dir>/voice.mp3 <dir>/voice.words.json
   <dir>/script.txt <dir>/tight` (cuts the 1 s pauses, gives exact word/sentence times; one script line = one sentence).
3. `<dir>/make_spec.py` like `fb/06/make_spec.py`: place every screenshot, camera move, keycap, typing burst, circle and
   sound on the spoken words from `tight.json`. Camera = centre + height in screen pixels (full -> focus -> full);
   the real screen always fills the 9:16 frame edge to edge (no borders, no paper margins).
4. `python3 engine/realcut.py <dir>/spec.json /tmp/sheet.png --preview t1,t2,...` (look at it), then render
   `python3 engine/realcut.py <dir>/spec.json videos/<name>.mp4`.

Sounds: real recorded CC0 UI sounds in `engine/sfx/kenney/interface-sounds` (Kenney, CC0): clicks, keyboard ticks,
pops, confirmation ding, window open. No music, no loud "viral" effects.

## iPhone, Android, Mac (not built yet)
Planned: iOS Simulator and Android Emulator screenshots on GitHub runners, and macOS screenshots on a macOS runner.
Until they exist, do not make iPhone, Android or Mac tutorials with drawn screens. Pick a Windows topic instead.
AI apps that need a login (ChatGPT, Claude, Gemini) can't be recorded here either: no such tutorials with fake screens.
