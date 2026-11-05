# Publishing (free): YouTube upload session + Instagram Reels

Make's free plan only moves files under 5 MB, so videos never pass through Make. Make only opens a YouTube
**resumable upload session** (a few hundred bytes of JSON), and a GitHub Action streams the video bytes
into that session. This works for Shorts and long videos of any size.

Make scenario **6912009** (team 3369346, on demand), run with `mcp__Make__scenarios_run`
(`scenarioId: 6912009, responsive: true, data: {...}`). It writes every result to Make data store
**193828**; read it with `mcp__Make__data-store-records_list {dataStoreId: 193828}` and look up your `job` key.
`job_type` picks the route:

| job_type | inputs | data store record (`key` = job) |
|---|---|---|
| `session` | `total_size` (bytes of the mp4), `metadata_json` (video resource, see below) | `session_url`, `status` 200 |
| `thumbnail` | `video_id`, `thumbnail_url` (public jpg, e.g. raw.githubusercontent.com/...<sha>/long/NN/thumbnail.jpg) | `note` "thumbnail set" |
| `api` | `api_path` (after https://www.googleapis.com/youtube, e.g. `/v3/playlistItems?part=snippet`), `api_method`, `metadata_json` (request body) | `session_url` = returned id, `status` |

Use a unique `job` key every time (e.g. `long02-session`, `short05-session`, `long02-thumbnail`, `playlist-add-long02`).

## 1. YouTube upload (Shorts and long videos)

1. Commit and push the finished `videos/<name>.mp4` (under 95 MB).
2. Build the video resource and pass it as a JSON **string** in `metadata_json`:
   ```json
   {"snippet": {"title": "...", "description": "...", "tags": ["..."], "categoryId": "28",
                "defaultLanguage": "en", "defaultAudioLanguage": "en"},
    "status": {"privacyStatus": "private", "publishAt": "2026-11-09T15:00:00Z",
               "selfDeclaredMadeForKids": false, "containsSyntheticMedia": false, "embeddable": true}}
   ```
   `privacyStatus` must be `private` when `publishAt` is set; YouTube makes it public at that time.
   Shorts: vertical, under 3 minutes, title ends with ` #shorts`.
3. Run 6912009 with `{job: "<name>-session", job_type: "session", total_size: <bytes>, metadata_json: "<string>"}`.
   `total_size` must be the exact byte size (`stat -c%s videos/<name>.mp4`).
4. Read data store 193828, key `<name>-session`: `status` must be 200 and `session_url` must start with
   `https://www.googleapis.com/upload/youtube/v3/videos?`. (A run with the same job key overwrites the record,
   so check it belongs to this run.)
5. Write `uploads/<name>.job.json` = `{"session_url": "<session_url>", "file": "videos/<name>.mp4"}`, commit and push
   straight away. The "YouTube upload" workflow PUTs the file into the session, writes `uploads/<name>.result.json`
   (`{"http", "video_id", "status", "error"}`) and deletes the job file.
6. `git pull` every ~30 s (up to 15 minutes) until `uploads/<name>.result.json` exists. Success = `http` 200 or 201,
   a `video_id`, and `status.uploadStatus` "uploaded" with the right `publishAt`. On failure, read the workflow log
   (`https://api.github.com/repos/diamond960/tm-diamond-videos/actions/runs`), then start again from step 3 with a
   new job key (a session URL works only once).

## 2. Long videos only: thumbnail + playlist

- Thumbnail: run 6912009 `{job: "longNN-thumbnail", job_type: "thumbnail", video_id, thumbnail_url}`; the record note
  must be "thumbnail set".
- Playlist "AI Video Tutorials (Claude, AI Tools, Automation)" = **PLLq1qbdATaDQ**. Add AI / Claude / AI-tool videos:
  run 6912009 `{job: "playlist-add-longNN", job_type: "api", api_method: "POST", api_path: "/v3/playlistItems?part=snippet",
  metadata_json: "{\"snippet\": {\"playlistId\": \"PLLq1qbdATaDQ\", \"resourceId\": {\"kind\": \"youtube#video\", \"videoId\": \"<id>\"}}}"}`.
  For a Windows or gadget video, create a matching playlist once (`api_path: "/v3/playlists?part=snippet,status"`, body
  `{"snippet": {"title": "...", "description": "..."}, "status": {"privacyStatus": "public"}}`; the record's
  `session_url` is the new playlist id), note its id in this file, then add videos to it the same way.
- End screens can't be set through the API.

## 3. Instagram Reels (vidIQ, free)

Instagram's API publishes immediately (no scheduling), so Reels are posted by the run that happens at the slot time.

1. `mcp__vidIQ__vidiq_instagram_connected_accounts`: use the account with `publishingAvailable: true`. If there is
   none, skip Instagram (the owner has to connect it with `vidiq_connect_instagram_account` mode oauth).
2. `mcp__vidIQ__vidiq_video_upload {url: "https://raw.githubusercontent.com/diamond960/tm-diamond-videos/<sha>/videos/shortNN_social.mp4", title}`
   (the no-beat version; `social_file_url` in posted.json)
   gives a hosted `videoUrl` (free).
3. `mcp__vidIQ__vidiq_instagram_publish_reel {platformAccountId, videoUrl, caption}`, then keep calling it with the
   returned `containerId` (or `mcpJobId` after `vidiq_job_poll` says ready) every ~5 s until `PUBLISHED`.
   Never start a second container for the same video.
4. Caption: hook line, 2-4 short value lines, "Full tutorials on YouTube: TM_Diamond", then 5-8 hashtags
   (mix of broad and niche, e.g. #ai #claudeai #aitools #techtips #windows11 #productivity).
5. Record it in `shorts/NN/posted.json` as `"instagram": {"posted_at": "...", "permalink": "..."}`.

## 4. Facebook Reels (Make, free)

Page: **TMDiamond** (page id 572956285911279), through Make connection 12169332 (the owner's Facebook login,
which manages the Page; nothing is ever posted to his personal profile).

1. Video: the NO-BEAT version, 9:16, 3-90 s. Link it through jsDelivr (Facebook needs a proper video/mp4 link):
   `https://cdn.jsdelivr.net/gh/diamond960/tm-diamond-videos@<sha>/videos/<file>.mp4` (files must be under 20 MB).
2. Run 6912009 `{job: "fb-<name>", job_type: "fb_reel", video_url, title, caption}`. Facebook processes the
   Reel for up to a minute, so the MCP call can time out with "Bad Gateway" while the run keeps going: then wait
   ~60 s and check `executions_list` / the data store. Record key `fb-<name>` -> `session_url` = Facebook video id.
   The Reel is at `https://www.facebook.com/reel/<video id>`. Never post the same video twice.
3. Caption: hook line, 2-4 short value lines, a question that asks for a comment, "Follow for daily Windows + AI
   tips", 4-6 hashtags (#windows11 #pctips #techtips #windows #chatgpt #ai). No "AI voice"/AI labels.
4. Study the Page: run 6912009 `{job: "fb-study-<date>", job_type: "fb_study"}` -> the record lists the last 40
   videos (date | length | title/description). Facebook doesn't give view counts through this route.
