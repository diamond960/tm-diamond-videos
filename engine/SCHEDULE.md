# TM_Diamond posting schedule (owner, 2026-11-11 - latest; New York time)

"Cover everything about Windows, MacBook, iPhone, Android... serially... 5 or 6 videos on Facebook, one or two on
Instagram, TikTok 1 minute plus, YouTube do the best... know when and what to be posting."

## Order
One device series at a time, one topic block at a time, in content/plan.json order:
Windows (blocks 1-5, 7-9) -> MacBook -> iPhone -> Android. AI for Creators is paused (Part 1 posted 2026-11-11).
Mac/iPhone/Android each start only after a real-screen capture test works (Mac: GitHub macOS runner; iPhone:
Xcode iPhone simulator or the owner's own recordings; Android: Android emulator on a Linux runner).

## Every day
| Time (NY) | What | Who |
|---|---|---|
| 5:47 AM | Batch maker: tops the Facebook queue up to 10 reels (makes up to 5 new 15-30 s reels from the current block), makes the day's TikTok (61-75 s, 5-6 tips of the block), uploads the day's best reel as a YouTube Short for 6:00 PM, marks 2 reels for Instagram | daily batch task |
| 9:13 AM, 12:13 PM, 3:13 PM, 6:13 PM, 9:13 PM | Facebook Page: the oldest queued reel (fb/*/post.json "status": "queued") | Facebook task |
| 12:04 PM, 7:04 PM | Instagram: the oldest reel marked "ig_pick" with no "instagram" field | Instagram task |
| 6:00 PM | YouTube Short goes live (scheduled by the batch maker) | - |
| 7:23 PM | TikTok: the day's 61-75 s video as a post card + the file; the owner taps Post (TikTok requires it) | TikTok task |
| Saturday 11:41 AM | Long video of the current series (live Sunday 10:00 AM) | long-video task |
| Monday 8:13 AM | Weekly numbers and one adjustment | weekly check |

## Lengths
- Facebook reels: 15-30 s, as long as the tutorial needs (one tip each). Caption: one line, 50-100 characters,
  hook + #reels + 1-2 topic hashtags.
- Instagram: the same reels, caption one line 50-100 characters, 2-3 specific hashtags, never #reels/#viral/#fyp.
- TikTok: 61-75 s (Creator Rewards only pays for videos over 1 minute), one video combining 5-6 tips of the block,
  caption one line 50-100 characters with 2-3 specific hashtags. No added music.
- YouTube Shorts: the day's best reel, title "... #shorts". Long video 6-10 min weekly.

## Folders
- fb/NN/ - one reel: script.txt, voice, tight.json, spec.json, post.json {"title", "series", "block", "episode",
  "caption", "ig_caption", "ig_pick", "file_url", "length_s", "status": "queued"|"posted", "facebook": {...},
  "instagram": {...}, "youtube": {...}}; video videos/fbNN.mp4.
- tiktok/NN/ - the day's TikTok: script.txt, spec.json, pack.json {"title", "caption", "file_url", "status": "ready"|"sent"}; videos/tiktokNN.mp4.
- fb/make_batch_1111.py is the reference for cutting reels from a block's real captures (one capture session per
  block, many reels).
