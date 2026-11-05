"""Long video 01: I Connected 9 Apps to Claude and Built an AI Video Studio."""

VOICE = "draft_voice"   # switch to "voice" when the Grady narration is in
SPEC = {
    "script": "long/01/script.txt",
    "words": f"long/01/{VOICE}.words.json",
    "narration": f"long/01/{VOICE}.mp3",
}


def build(tl):
    L = tl.find
    sfx = []
    scenes = []

    def at(line, word=None):
        return [line, word] if word is not None else line

    def add(sc):
        scenes.append(sc)
        return sc

    def rows(line_words, line):
        out = []
        for text, e, w in line_words:
            a = at(line if not isinstance(w, tuple) else w[0], w if not isinstance(w, tuple) else w[1])
            out.append({"text": text, "e": e, "at": a})
            sfx.append({"at": a, "type": "pop", "vol": 0.5})
        return out

    # ---------------- HOOK
    l0 = 0
    add({"type": "hook", "at": l0, "lines": [
        {"text": "PLANNED. WRITTEN.", "at": at(l0, "planned")},
        {"text": "EDITED. SCHEDULED.", "at": at(l0, "edited")},
        {"text": "FROM ONE CHAT", "c": "lime", "at": at(l0, "one")}],
        "emoji": [{"e": "💬", "at": at(l0, "one"), "y": -300, "size": 180}]})
    sfx += [{"at": l0, "type": "bass"}, {"at": at(l0, "one"), "type": "pop"}]
    l1 = L("No editing app open")
    add({"type": "hook", "at": l1, "lines": [
        {"text": "EDITING APP", "at": l1, "strike_at": at(l1, "open")},
        {"text": "TIMELINE", "at": at(l1, "timeline"), "strike_at": [l1, 1.6]}]})
    sfx += [{"at": at(l1, "open"), "type": "error"}, {"at": [l1, 1.6], "type": "error"}]
    l2 = L("Just Claude, connected")
    add({"type": "bigstat", "at": l2, "big": "9 APPS", "label": "1 CHAT", "e": "🔌"})
    sfx.append({"at": at(l2, "nine"), "type": "bass", "vol": 0.7})
    l3 = L("By the end of this video")
    add({"type": "hook", "at": l3, "lines": [
        {"text": "BY THE END:", "at": l3, "c": "grey", "size": 70},
        {"text": "WHICH 9 APPS", "at": at(l3, "which")},
        {"text": "WHAT EACH ONE DOES", "at": at(l3, "what"), "c": "lime"},
        {"text": "HOW THEY WORK TOGETHER", "at": at(l3, "how")}]})
    l4 = L("And stay for app number eight")
    add({"type": "bigstat", "at": l4, "big": "APP #8", "e": "⭐", "label": "STAY FOR THIS ONE"})
    l5 = L("That's the one that found me")
    add({"type": "bigstat", "at": at(l5, "over"), "big": "400K+", "label": "SEARCHES A MONTH",
         "sub": "and very little competition", "sub_at": at(l5, "little"), "e": "🔎"})
    sfx.append({"at": at(l5, "over"), "type": "ding", "vol": 0.6})

    # ---------------- WHY
    l6 = L("Quick context")
    add({"type": "hook", "at": l6, "lines": [
        {"text": "TM_DIAMOND", "at": L("My channel is TM_Diamond"), "c": "lime"},
        {"text": "TECH TUTORIALS", "at": at(L("My channel is TM_Diamond"), "tech")}],
        "emoji": [{"e": "💻", "at": l6, "y": -290, "size": 170}]})
    l8 = L("doing everything by hand")
    l9 = L("Writing scripts")
    add({"type": "app", "at": l8, "name": "The old way", "e": "😩", "headline": "BY HAND", "c": "red",
         "rows": rows([("Writing scripts", "✍️", "writing"), ("Cutting clips", "✂️", "cutting"),
                       ("Making thumbnails", "🖼️", "making"), ("Guessing titles", "🤷", "guessing")], l9)})
    l10 = L("So I asked Claude one simple question")
    l11 = L("What do I need to connect")
    l12 = L("Claude gave me a list")
    l13 = L("I tapped Connect")
    apps = [("Descript", "📝"), ("OpusClip", "✂️"), ("Tella", "🎥"), ("HyperFrames", "✨"), ("Higgsfield", "🤖"),
            ("Canva", "🎨"), ("Adobe", "🅰️"), ("vidIQ", "📈"), ("Google Drive", "📁")]
    span = max(0.4, (tl.line_start(l13) - tl.line_start(l12)) / 10)
    add({"type": "chat", "at": l10, "title": "Claude",
         "user": "What do I need to connect so you can help me edit videos, add sound effects, motion graphics and animation?",
         "user_at": l11, "reply": "Here are 9 apps to connect:", "reply_at": l12,
         "apps": [{"name": n, "e": e, "at": [l12, 0.4 + i * span], "done_at": [l13, 0.3 + i * 0.18]} for i, (n, e) in enumerate(apps)]})
    sfx.append({"at": l11, "type": "typing", "vol": 0.7})
    sfx += [{"at": [l13, 0.3 + i * 0.18], "type": "tick", "vol": 0.45} for i in range(9)]

    # ---------------- APPS
    def chapter(n, title, e, line):
        add({"type": "chapter", "at": line, "num": f"APP {n}", "title": title, "e": e})
        sfx.append({"at": line, "type": "riser", "vol": 0.35, "dt": -0.6})

    a1 = L("App one: Descript")
    chapter(1, "DESCRIPT", "📝", a1)
    d1 = L("Descript lets you edit video by editing text")
    add({"type": "transcript", "at": d1, "strike_line": 1, "strike_at": at(L("when you delete a sentence"), "delete"),
         "lines": ["Hi everyone, welcome back to the channel.", "Um, so, uh, let me just... start again.",
                   "Today I'll show you how to edit video", "with nothing but a chat window.",
                   "Delete a line, and the clip is gone."]})
    sfx.append({"at": at(L("when you delete a sentence"), "delete"), "type": "glitch", "vol": 0.6})
    d3 = L("Once it's connected, Claude can talk to Descript")
    d4 = L("It can trim mistakes")
    d5 = L("It can even export your timeline")
    add({"type": "app", "at": d3, "name": "Descript + Underlord", "e": "📝", "headline": "UNDERLORD",
         "rows": rows([("Trim mistakes", "✂️", "trim"), ("Remove um and uh", "🗑️", "remove"),
                       ("Add captions", "💬", "captions"), ("Pull in stock footage", "🎞️", "stock")], d4)
         + rows([("Export to Premiere or Resolve", "📤", "export")], d5)})

    a2 = L("App two: AI Producer by OpusClip")
    chapter(2, "OPUSCLIP", "✂️", a2)
    o1 = L("This one turns raw footage")
    o2 = L("It does the rough cut")
    o3 = L("It finds B-roll")
    add({"type": "app", "at": o1, "name": "AI Producer by OpusClip", "e": "✂️", "headline": "RAW → WATCHABLE",
         "rows": rows([("Rough cut", "✂️", "rough"), ("Animated captions", "💬", "captions"), ("Auto zooms", "🔍", "zooms")], o2)
         + rows([("B-roll", "🎞️", "b-roll"), ("Sound effects on the cuts", "🔊", "sound"), ("Studio-clean voice", "🎙️", "voice")], o3)})
    o4 = L("And it can turn one long video into short clips")
    add({"type": "bigstat", "at": o4, "big": "1 → MANY", "label": "SHORTS & REELS", "e": "📱"})

    a3 = L("App three: Tella")
    chapter(3, "TELLA", "🎥", a3)
    t1 = L("Tella is made for screen recordings")
    t2 = L("Through Claude, it can add zooms")
    add({"type": "app", "at": t1, "name": "Tella", "e": "🎥", "headline": "SCREEN RECORDINGS",
         "rows": rows([("Zooms & highlights", "🔍", "zooms"), ("Blur private info", "🫥", "blur"),
                       ("Text & sound effects", "🔊", "text"), ("Cut out silences", "🤫", "silences")], t2)})
    t3 = L("And it can publish straight to YouTube")
    add({"type": "app", "at": t3, "name": "Tella - Publish", "e": "🚀", "headline": "PUBLISH ANYWHERE",
         "rows": rows([("YouTube", "▶️", "youtube"), ("Instagram", "📸", "instagram"), ("Facebook", "👍", "facebook"),
                       ("LinkedIn & X", "💼", "linkedin"), ("Schedule 30 days ahead", "📅", "scheduled")], t3)})

    a4 = L("App four: HyperFrames by HeyGen")
    chapter(4, "HYPERFRAMES", "✨", a4)
    h1 = L("HyperFrames builds animated slides")
    h2 = L("Titles that fly in")
    add({"type": "hook", "at": h1, "lines": [
        {"text": "ANIMATED SLIDES", "at": at(h1, "animated")},
        {"text": "MOTION GRAPHICS", "at": at(h1, "motion"), "c": "lime"},
        {"text": "TITLES THAT FLY IN", "at": h2},
        {"text": "EXPLAINER SCENES", "at": at(h2, "explainer"), "c": "lime"}]})
    h3 = L("Claude writes it, and HeyGen renders it")
    add({"type": "flow", "at": h3, "steps": [
        {"text": "Claude writes it", "e": "✍️", "at": h3},
        {"text": "HeyGen renders it", "e": "⚙️", "at": at(h3, "heygen")},
        {"text": "A real video file", "e": "🎬", "at": at(h3, "real")}]})

    a5 = L("App five: Higgsfield")
    chapter(5, "HIGGSFIELD", "🤖", a5)
    g1 = L("This is the AI generation powerhouse")
    g2 = L("AI video clips, images")
    add({"type": "app", "at": g1, "name": "Higgsfield", "e": "🤖", "headline": "AI POWERHOUSE",
         "rows": rows([("AI video clips", "🎥", "video"), ("Images", "🖼️", "images"), ("3D models", "🧊", "3d"),
                       ("Voices & dubbing", "🎙️", "voices"), ("Upscaling", "🔼", "upscaling")], g2)})
    g3 = L("If I need a shot I can't film")
    add({"type": "hook", "at": g3, "lines": [
        {"text": "A SHOT I CAN'T FILM?", "at": g3},
        {"text": "HIGGSFIELD MAKES IT", "at": at(g3, "higgsfield"), "c": "lime"}],
        "emoji": [{"e": "🎬", "at": g3, "y": -290, "size": 170}]})

    a6 = L("App six: Canva")
    chapter(6, "CANVA", "🎨", a6)
    c1 = L("Thumbnails, title graphics")
    add({"type": "app", "at": c1, "name": "Canva", "e": "🎨", "headline": "DESIGNS",
         "rows": rows([("Thumbnails", "🖼️", "thumbnails"), ("Title graphics", "🔤", "title"),
                       ("Facebook & Instagram posts", "📱", "posts")], c1)})
    c2 = L("One honest note: Canva")
    add({"type": "bigstat", "at": c2, "big": "PAID", "label": "CANVA AI VIDEO", "c": "orange", "e": "💳",
         "sub": "Designs still work on the free plan", "sub_at": L("On my free account")})

    a7 = L("App seven: Adobe")
    chapter(7, "ADOBE", "🅰️", a7)
    ad1 = L("Through Claude, Adobe can resize")
    ad2 = L("It can also do Photoshop-style edits")
    add({"type": "app", "at": ad1, "name": "Adobe", "e": "🅰️", "headline": "RESIZE & RETOUCH",
         "rows": rows([("Resize for every platform", "📐", "resize"), ("Quick highlight cuts", "✂️", "quick"),
                       ("Enhance speech", "🎙️", "enhance")], ad1)
         + rows([("Remove backgrounds", "🪄", "remove"), ("Fix colors & add effects", "🎨", "fix")], ad2)})
    ad3 = L("Resizing alone fixed a real problem")
    add({"type": "resize", "at": ad3, "steps": [
        {"ratio": [16, 9], "label": "YOUTUBE", "at": ad3},
        {"ratio": [9, 16], "label": "REELS", "at": at(ad3, "facebook")},
        {"ratio": [1, 1], "label": "FEED", "at": L("My videos had borders")}]})
    ad4 = L("My videos had borders")
    add({"type": "cards", "at": at(ad4, "facebook"), "cards": [
        {"title": "FACEBOOK WARNING", "text": "Bordered videos can look like reposted content", "e": "⚠️",
         "at": at(ad4, "facebook"), "c": "orange"}]})

    # ---------------- MID ASK
    q1 = L("Quick pause")
    q2 = L("If this is useful, subscribe")
    add({"type": "subscribe", "at": q1, "tap_at": at(q2, "subscribe")})
    sfx += [{"at": at(q2, "subscribe"), "type": "click"}, {"at": at(q2, "subscribe"), "type": "pop"}]
    q3 = L("Okay. App eight")
    add({"type": "bigstat", "at": q3, "big": "APP #8", "label": "THE ONE I PROMISED", "e": "⭐"})
    sfx.append({"at": at(q3, "eight"), "type": "bass"})

    # ---------------- APP 8 VIDIQ
    a8 = L("App eight: vidIQ")
    chapter(8, "VIDIQ", "📈", a8)
    v1 = L("vidIQ gives Claude real YouTube data")
    v2 = L("What people search")
    add({"type": "app", "at": v1, "name": "vidIQ", "e": "📈", "headline": "REAL YOUTUBE DATA",
         "rows": rows([("What people search", "🔎", "search"), ("How much competition", "⚔️", "competition"),
                       ("Videos blowing up", "🚀", "blowing"), ("My own channel stats", "📊", "channel")], v2)})
    v3 = L("So I asked Claude to research my niche")
    add({"type": "chat", "at": v3, "title": "Claude", "user": "Research my niche: Claude and AI video editing on YouTube.",
         "user_at": v3, "reply": "Here's what people are searching, and how much competition there is.",
         "reply_at": at(v3, "here's")})
    sfx.append({"at": v3, "type": "typing", "vol": 0.6})
    v4 = L("Claude AI full course gets")
    v5 = L("Video editing with Claude gets")
    v6 = L("It grew almost five hundred percent")
    v8 = L("Claude YouTube automation is around")
    add({"type": "stats", "at": v4, "rows": [
        {"kw": "claude ai full course", "num": 996000, "at": v4},
        {"kw": "video editing with claude", "num": 415000, "comp": 31, "at": v5, "tag": "~500% IN A MONTH", "tag_at": v6},
        {"kw": "claude youtube automation", "num": 216000, "comp": 28, "at": v8}]})
    sfx += [{"at": v4, "type": "ding", "vol": 0.5}, {"at": v5, "type": "ding", "vol": 0.5}, {"at": v6, "type": "pop"},
            {"at": v8, "type": "ding", "vol": 0.5}]
    v9 = L("And viewers in India, Bangladesh and Pakistan")
    add({"type": "app", "at": v9, "name": "Where the searches come from", "e": "🌍", "headline": "TOP COUNTRIES",
         "rows": rows([("India", "🇮🇳", "india"), ("Bangladesh", "🇧🇩", "bangladesh"), ("Pakistan", "🇵🇰", "pakistan")], v9)})
    v10 = L("It also showed me who's winning")
    v11 = L("One beginner's guide to Claude")
    add({"type": "bigstat", "at": v10, "big": "2.3M", "label": "VIEWS", "e": "🔥",
         "sub": "One beginner's guide to Claude", "sub_at": v11})
    v12 = L("And small channels are breaking out too")
    add({"type": "hook", "at": v12, "lines": [
        {"text": "SMALL CHANNELS", "at": v12}, {"text": "ARE BREAKING OUT", "at": at(v12, "breaking"), "c": "lime"}],
        "emoji": [{"e": "📈", "at": v12, "y": -280, "size": 170}]})
    v13 = L("A Nigerian channel with about eleven thousand")
    add({"type": "bigstat", "at": v13, "big": "~300K", "label": "VIEWS", "e": "🇳🇬",
         "sub": "~11K-subscriber channel · a whole movie made with Google Flow", "sub_at": at(v13, "showing")})
    v15 = L("The research also checked my own channel")
    v16 = L("My long videos hold people")
    add({"type": "bigstat", "at": v15, "big": "~2:00", "label": "AVERAGE VIEW", "c": "orange", "e": "⏱️",
         "sub": "my long videos", "sub_at": v16})
    v17 = L("So now every video gets a stronger hook")
    v18 = L("Which, hopefully, is why")
    add({"type": "hook", "at": v17, "lines": [
        {"text": "A STRONGER HOOK", "at": at(v17, "stronger")},
        {"text": "A REASON TO KEEP WATCHING", "at": at(v17, "reason"), "c": "lime"}],
        "emoji": [{"e": "😉", "at": v18, "y": -290, "size": 170}]})

    # ---------------- APP 9 DRIVE
    a9 = L("App nine: Google Drive")
    chapter(9, "GOOGLE DRIVE", "📁", a9)
    gd1 = L("It's the simplest one")
    gd2 = L("Big video files are hard to send")
    add({"type": "hook", "at": gd1, "emoji": [{"e": "📁", "at": gd1, "y": -300, "size": 150}], "lines": [
        {"text": "THE SIMPLEST ONE", "at": gd1},
        {"text": "BIG VIDEO FILES", "at": gd2, "c": "lime"},
        {"text": "PHONE → CHAT = PAIN", "at": at(gd2, "phone"), "c": "red"}]})
    gd3 = L("Now I drop my raw clips in Google Drive")
    add({"type": "flow", "at": gd3, "steps": [
        {"text": "Drop clips in Drive", "e": "📁", "at": gd3},
        {"text": "Tell Claude the name", "e": "💬", "at": at(gd3, "tell")},
        {"text": "Sent to the editor", "e": "🚀", "at": at(gd3, "passes")}]})

    # ---------------- WORKFLOW
    w0 = L("So how does it all work together")
    steps = [("One. vidIQ", "vidIQ finds the topic", "🔎"), ("Two. Claude writes", "Claude writes the script", "✍️"),
             ("Three. Higgsfield", "Voiceover", "🎙️"), ("Four. Descript", "Cuts, captions, zooms", "✂️"),
             ("Five. Canva", "Thumbnail", "🖼️"), ("Six. Claude writes the title", "Title, tags, hashtags", "🏷️"),
             ("Seven. An automation", "Make uploads + schedules", "📅")]
    add({"type": "flow", "at": w0, "steps": [{"text": t, "e": e, "at": L(k)} for k, t, e in steps]})
    sfx += [{"at": L(k), "type": "pop", "vol": 0.6} for k, _, _ in steps]
    w8 = L("And I can still step in")
    add({"type": "app", "at": w8, "name": "You stay in control", "e": "🕹️", "headline": "STEP IN ANY TIME",
         "rows": rows([("Change a line in the script", "✏️", "change"), ("Swap the thumbnail", "🔄", "swap"),
                       ("Cancel a scheduled post", "🛑", "cancel")], w8)})

    # ---------------- HONEST
    hp = L("Now the honest part")
    add({"type": "hook", "at": hp, "lines": [{"text": "THE HONEST PART", "at": hp, "c": "orange"},
                                             {"text": "NOBODY TELLS YOU THIS", "at": at(hp, "nobody")}],
         "emoji": [{"e": "🤝", "at": hp, "y": -290, "size": 170}]})
    f1 = L("First, some features need paid plans")
    f2 = L("Second, every app has its own credits")
    f3 = L("Third, YouTube doesn't pay")
    add({"type": "cards", "at": f1, "cards": [
        {"title": "1. PAID PLANS", "text": "Canva AI video is paid. Claude Motion is a Team and Enterprise beta.", "e": "💳", "at": f1},
        {"title": "2. CREDITS", "text": "Every app has its own credits and limits.", "e": "🪙", "at": f2},
        {"title": "3. NO SPAM", "text": "YouTube doesn't pay for mass-produced content.", "e": "🚫", "at": f3, "c": "red"}]})
    sfx += [{"at": f1, "type": "pop"}, {"at": f2, "type": "pop"}, {"at": f3, "type": "pop"}]
    g_1 = L("So the goal isn't to spam")
    g_2 = L("The goal is to use AI to make real tutorials")
    add({"type": "hook", "at": g_1, "lines": [
        {"text": "SPAM AI VIDEOS", "at": g_1, "c": "red", "strike_at": at(g_1, "videos")},
        {"text": "REAL TUTORIALS, FASTER", "at": at(g_2, "real"), "c": "lime"},
        {"text": "GENUINELY USEFUL", "at": at(g_2, "genuinely")}]})
    sfx.append({"at": at(g_1, "videos"), "type": "error"})

    # ---------------- ENDING
    e1 = L("That's my AI video studio")
    add({"type": "bigstat", "at": e1, "big": "9 APPS · 1 CHAT", "label": "MY AI VIDEO STUDIO", "e": "🎬"})
    sfx.append({"at": e1, "type": "bass", "vol": 0.7})
    e2 = L("In the next video")
    e3 = L("Subscribe so you don't miss it")
    add({"type": "subscribe", "at": e2, "tap_at": at(e3, "subscribe"),
         "next": "How to edit a full video with Claude, step by step", "next_at": e2})
    sfx += [{"at": at(e3, "subscribe"), "type": "click"}, {"at": at(e3, "subscribe"), "type": "pop"}]

    return dict(SPEC, scenes=scenes, sfx=sfx, bpm=100, music_db=23,
                progress={"show_at": a1, "hide_at": w0, "apps_at": [a1, a2, a3, a4, a5, a6, a7, a8, a9], "tease": 8},
                highlight=["descript", "opusclip", "tella", "hyperframes", "higgsfield", "canva", "adobe", "vidiq",
                           "drive", "nine", "eight", "underlord", "paid", "free", "hook", "make", "youtube", "thousand",
                           "million", "minutes"])
