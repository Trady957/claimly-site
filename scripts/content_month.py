"""One month of Claimly social content (27 Oct - 25 Nov 2026).

Per day: 1 feed piece (Reel, carousel or statement post), 3 Stories, 1 Pinterest pin.
Output: social/month1/<NN>-<date>/... and social/month1/plan.json (captions + files).
Run once:  python3 scripts/content_month.py
"""
import datetime, json, os, random, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import social as S
import daily_social as DS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "month1")
BASE = "https://claimly.ae/social/month1"
START = datetime.date(2026, 10, 27)
DAYS = 30
random.seed(2026)

def slug(c): return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")

# ---------------------------------------------------------------- names
inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
gone = set(open(os.path.join(ROOT, "data", "sold.txt")).read().split()) | set(open(os.path.join(ROOT, "data", "taken.txt")).read().split())
used = set()
dd = os.path.join(ROOT, "social", "daily")
for f in os.listdir(dd):
    if f.endswith(".json") and f != "latest.json":
        used |= {n["domain"] for n in json.load(open(os.path.join(dd, f))).get("names", [])}
pool = {}
for x in inv:
    d = x["d"]
    if d in gone or d in used or d in DS.PREMIUM: continue
    if not re.fullmatch(r"[a-z]+\.(com|co|io|app)", d): continue
    if not DS.two_words(d.split(".")[0]) or len(d) > 15: continue
    pool.setdefault(x["c"], []).append(x)
for c in pool: random.shuffle(pool[c]); pool[c].sort(key=lambda x: (x["d"].split(".")[1] != "com", len(x["d"])))
CATS = [c for c in DS.PHRASE if len(pool.get(c, [])) >= 25]

def take(cat, n):
    out = pool[cat][:n]; del pool[cat][:n]; return out

HASH = {"Finance": "#fintech #financebrand", "AI": "#aistartup #techstartup", "SaaS": "#saas #softwarestartup",
        "E-commerce": "#ecommerce #onlinestore", "Local": "#localbusiness #shoplocal", "Health": "#wellnessbrand #healthbusiness",
        "Creator": "#creator #contentcreator", "Education": "#edtech #educationbusiness", "Travel": "#travelbrand #travelbusiness",
        "Real estate": "#realestate #propertybusiness", "Food": "#foodbusiness #cafebusiness", "Pets": "#petbusiness #petbrand",
        "Crypto": "#crypto #web3", "Marketing": "#marketingagency #agencylife", "Legal": "#lawfirm #consulting",
        "Fashion": "#fashionbrand #fashionstartup", "Gaming": "#gamingstudio #indiegame", "Green": "#ecobrand #sustainablebusiness"}
BASE_TAGS = "#businessname #startup #smallbusiness #dubaibusiness #saudibusiness #branding"
HOOK = {"Finance": "Starting a finance or fintech brand?", "AI": "Building an AI startup?", "SaaS": "Launching a software product?",
        "E-commerce": "Opening an online store?", "Local": "Starting a local business?", "Health": "Launching a health or wellness brand?",
        "Creator": "Growing your creator brand?", "Education": "Starting an education business?", "Travel": "Building a travel brand?",
        "Real estate": "Starting in real estate?", "Food": "Opening a café or food brand?", "Pets": "Starting a pet business?",
        "Crypto": "Launching a crypto project?", "Marketing": "Starting a marketing agency?", "Legal": "Opening a law or consulting firm?",
        "Fashion": "Launching a fashion label?", "Gaming": "Starting a gaming studio?", "Green": "Building an eco brand?"}

def names_caption(cat, items, kind="post"):
    lines = "\n".join(f"→ {x['d']} · ${x['p']}" for x in items)
    lead = "Watch till the end 👀\n\n" if kind == "reel" else ""
    return (f"{lead}{HOOK.get(cat, 'Starting a business?')}\n\nAvailable to register today:\n{lines}\n\n"
            f"Prices include the first year. Link in bio.\n\nأسماء متاحة اليوم مع الدومين، السعر يشمل السنة الأولى 👆\n\n"
            f"{BASE_TAGS} {HASH.get(cat, '')}")

# ---------------------------------------------------------------- feed content banks
STATEMENTS = [
    ("Naming package", "Stuck on a name? We'll send you 10.", "Tell us what you do. Get 10 checked names with available domains in 48 hours. From $149.",
     "Stuck on a business name? 💭\n\nTell us what you do and we'll send you 10 names that fit, each with an available domain. Pick one and we register it for you.\n\nFrom $149 · link in bio\n\nعالق في اسم مشروعك؟ نرسل لك ١٠ أسماء مع دومين متاح خلال ٤٨ ساعة."),
    ("Price", "Brandable names from $15.", "First year of registration included. No auctions, no hidden fees. New names every morning.",
     "A great name doesn't have to cost thousands. 💸\n\nOur brandable domains start at $15, with the first year of registration included. No auctions, no hidden fees.\n\nBrowse at the link in bio.\n\nأسماء تجارية مع دومين تبدأ من ١٥ دولار، السنة الأولى مشمولة."),
    ("Launch", "License. Website. Email.", "Got the name? We'll introduce you to partners for the next three steps, free.",
     "Got your business name? Here's what comes next 🚀\n\n1️⃣ A company license\n2️⃣ A website on your domain\n3️⃣ A professional email\n\nWe introduce you to trusted partners, free: claimly.ae/launch (link in bio).\n\nعندك الاسم؟ الخطوة التالية: الرخصة، الموقع، والإيميل."),
    ("Fresh names", "New names added every morning.", "Every name is checked as unregistered before it goes live. Check back daily.",
     "Every morning we add fresh, checked domain names to the shop ☀️\n\nEach one is checked as unregistered before it goes live, so what you see is available to register today.\n\nSee today's names at the link in bio.\n\nأسماء جديدة كل صباح، كلها متاحة للتسجيل."),
    ("Agencies", "Agencies: give clients a name in 48 hours.", "Wholesale naming packages for setup firms and agencies, from $99 per client.",
     "Run a business setup firm or agency? 🤝\n\nYour clients need a name before almost anything else. We deliver 10 checked names + domain in 48 hours, unbranded, from $99 per client.\n\nDetails: claimly.ae/partners (link in bio).\n\nللوكالات وشركات تأسيس الأعمال: باقات تسمية بالجملة."),
    ("Phone test", "Your name should pass the phone test.", "Say it once on a call. If they can type it without asking, it's a keeper.",
     "The phone test ☎️\n\nSay your business name once on a call. If the other person can type it into Google without asking how to spell it, it's a keeper.\n\nNeed names that pass? Link in bio.\n\nاختبار الهاتف: اسم يسهل كتابته بعد سماعه مرة واحدة."),
    ("Business cards", "Check the domain before you print.", "Logos, cards and signs are expensive to redo. Secure the domain first.",
     "Before you print business cards, design a logo or order a sign: check the domain 🛑\n\nRedoing branding because the .com was taken costs far more than the domain itself.\n\nFind an available name at the link in bio.\n\nتأكد من الدومين قبل طباعة الكروت والشعار."),
    ("Gulf naming", "Naming in the Gulf? Test it twice.", "A great name sounds good in English and Arabic, and means nothing awkward in either.",
     "Starting a business in the UAE or Saudi Arabia? 🇦🇪🇸🇦\n\nTest your name in English AND Arabic: easy to say, nothing awkward in either language, short enough for WhatsApp.\n\nWe check every name for that. Link in bio.\n\nاختبر اسم مشروعك بالعربي والإنجليزي."),
    ("Register first", "Love the name? Register it today.", "Good names get taken every day. A domain costs less than one lunch meeting.",
     "Found a name you love? Register it today ⏳\n\nThousands of domains are registered every day. Holding your name costs less than a lunch meeting and saves you from starting over.\n\nLink in bio.\n\nأعجبك اسم؟ سجّله اليوم قبل أن يأخذه غيرك."),
    ("Short", "Short names win.", "Shorter names are easier to remember, type and fit on a logo. Ours are mostly under 11 letters.",
     "Short names win 🏆\n\nThey're easier to remember, easier to type and fit on a logo, an app icon and a shop sign. Most of our names are under 11 letters.\n\nBrowse them at the link in bio.\n\nالأسماء القصيرة أسهل في الحفظ والكتابة."),
]
CAROUSELS = [
    ("How to pick a business name", [("Write what you do in 5 words", "Your name should hint at it, or at the feeling you want."), ("Make a long list", "Aim for 30 options before you judge any of them."), ("Do the phone test", "Say each one out loud. Drop anything you have to spell."), ("Check the domain", "No available domain? Move on, don't settle for a weird spelling."), ("Sleep on your top 3", "The one you still like tomorrow is usually right.")]),
    (".com, .co or .io?", [(".com", "The default. Best if your customers aren't technical."), (".co", "Short, modern, popular with startups. Make sure people won't type .com."), (".io", "Tech and software. Developers love it; mainstream customers less so."), (".app / .shop", "Say exactly what you are. Great for products and stores."), ("Our tip", "Pick the extension your customers will remember, not the trendiest one.")]),
    ("What makes a name brandable", [("It's short", "Under 11 letters is ideal."), ("It's easy to say", "No tricky spellings or double letters."), ("It suggests, not describes", "It hints at what you do and leaves room to grow."), ("It's distinctive", "It won't be confused with a big brand."), ("The domain is free", "If you can't own it online, keep looking.")]),
    ("Before you register a domain", [("Search social handles", "Is the name free on Instagram and TikTok?"), ("Google it", "Make sure no one big uses a similar name."), ("Check trademarks", "Search your country's trademark database."), ("Say it in Arabic too", "Avoid awkward meanings in the Gulf."), ("Register it in your name", "You should be the owner, not your web designer.")]),
    ("Naming mistakes that cost money", [("Choosing before checking", "Then the domain is taken and you rebrand."), ("Being too literal", "\"DubaiPhoneRepair\" can't grow with you."), ("Hard-to-spell names", "You lose customers who can't find you."), ("Copying a competitor", "You'll always look like the second choice."), ("Waiting too long", "Someone else registers it first.")]),
]
TIPS = ["Say your name out loud 3 times. Still like it?", "Avoid hyphens in domain names.", "Avoid numbers that could be spelled out.",
        "Check the Instagram handle before you commit.", "Shorter names fit better on a logo.", "Test your name in Arabic and English.",
        "Don't name your business after a city if you'll expand.", "Register your domain before you print anything.",
        "Ask 5 strangers to spell your name.", "A good name today beats a perfect name in 3 months.",
        "Own your domain in your own name.", "Pick a name you can say on the phone without spelling it.",
        "Your name should hint, not describe.", ".com is the safest choice for mainstream customers.",
        "Avoid names that sound like big brands.", "Write your shortlist on a business card mock-up.",
        "Make sure it looks good in lowercase.", "Real words joined together are easy to remember.",
        "Check how it sounds in a voice note.", "If you hesitate saying it, keep looking.",
        "Your name will be on every invoice. Love it.", "Avoid double letters at word joins.",
        "A memorable name saves on marketing.", "Check that it doesn't mean something odd in other languages.",
        "Use the name in a sentence: 'I bought it from ___'.", "Domain first, logo second.",
        "Keep the name easy to type on a phone.", "Ask: will it still fit in 5 years?", "Be distinctive, not descriptive.",
        "Can a child say it? Good sign."]

# ---------------------------------------------------------------- templates (stories & pins)
SW, SH = 1080, 1920
def story_name(path, dom, price, cat):
    im = Image.new("RGB", (SW, SH), S.BONE); d = ImageDraw.Draw(im)
    d.ellipse((560, -260, 1340, 520), fill="#F7D9D6")
    d.text((90, 250), "NAME OF THE DAY", font=S.font("Bold", 40, False), fill=S.RED)
    S.block(d, 90, 320, f"For your {DS.PHRASE.get(cat, 'business')}", S.font("Black", 80), S.INK, SW - 180, 1.08)
    d.rounded_rectangle((70, 780, SW - 70, 1080), 40, fill="#FFFFFF", outline="#E2DFDB", width=3)
    f = fitf(d, dom, SW - 220, 140); tw = d.textlength(dom, font=f)
    d.text(((SW - tw) / 2, 930 - f.size * 0.62), dom, font=f, fill=S.INK)
    fp = S.font("Black", 72); pt = f"${price}"; pw = d.textlength(pt, font=fp)
    d.rounded_rectangle(((SW - pw) / 2 - 60, 1140, (SW + pw) / 2 + 60, 1260), 60, fill=S.RED)
    d.text(((SW - pw) / 2, 1155), pt, font=fp, fill="#FFFFFF")
    t = "Tap the link in bio to grab it"; ft = S.font("SemiBold", 44, False)
    d.text(((SW - d.textlength(t, font=ft)) / 2, 1340), t, font=ft, fill=S.MUTED)
    S.wordmark(d, 90, SH - 200, S.INK, size=56); im.save(path, quality=88)

def story_poll(path, a, b, cat):
    im = Image.new("RGB", (SW, SH), S.INK); d = ImageDraw.Draw(im)
    d.text((90, 250), "YOUR VOTE", font=S.font("Bold", 40, False), fill="#BDB8B5")
    S.block(d, 90, 320, "Which name would you pick?", S.font("Black", 96), "#FFFFFF", SW - 180, 1.05)
    for i, (x, lab) in enumerate(((a, "A"), (b, "B"))):
        y = 720 + i * 330
        d.rounded_rectangle((70, y, SW - 70, y + 260), 40, fill="#FFFFFF")
        d.text((120, y + 30), lab, font=S.font("Black", 60), fill=S.RED)
        f = fitf(d, x["d"], SW - 340, 110)
        d.text((220, y + 130 - f.size * 0.62), x["d"], font=f, fill=S.INK)
        d.text((220, y + 190), f"${x['p']} · {cat}", font=S.font("SemiBold", 36, False), fill=S.MUTED)
    t = "Add the poll sticker here ↓"; ft = S.font("SemiBold", 40, False)
    d.text(((SW - d.textlength(t, font=ft)) / 2, 1440), t, font=ft, fill="#6B6766")
    S.wordmark(d, 90, SH - 200, "#FFFFFF", dot=S.RED, size=56); im.save(path, quality=88)

def story_tip(path, n, tip):
    im = Image.new("RGB", (SW, SH), S.RED); d = ImageDraw.Draw(im)
    d.ellipse((560, -260, 1340, 520), fill="#EA4A3F")
    d.text((90, 250), f"NAMING TIP #{n}", font=S.font("Bold", 40, False), fill="#FFFFFF")
    y = S.block(d, 90, 520, tip, S.font("Black", 110), "#FFFFFF", SW - 180, 1.05)
    S.block(d, 90, y + 80, "Need a name? 10 checked names + domain in 48h. Link in bio.", S.font("Medium", 44, False), "#FFE3E1", SW - 180, 1.35)
    S.wordmark(d, 90, SH - 200, "#FFFFFF", dot=S.INK, size=56); im.save(path, quality=88)

def fitf(d, text, maxw, start, minimum=56):
    size = start
    while size > minimum and d.textlength(text, font=S.font("Black", size)) > maxw: size -= 4
    return S.font("Black", size)

def pin_list(path, cat, items):
    W2, H2 = 1000, 1500
    im = Image.new("RGB", (W2, H2), S.BONE); d = ImageDraw.Draw(im)
    d.text((70, 90), f"AVAILABLE TODAY · {cat.upper()}", font=S.font("Bold", 30, False), fill=S.RED)
    y = S.block(d, 70, 150, f"{len(items)} name ideas for your {DS.PHRASE.get(cat, 'business')}", S.font("Black", 78), S.INK, W2 - 140, 1.06) + 40
    for x in items:
        d.rounded_rectangle((70, y, W2 - 70, y + 130), 28, fill="#FFFFFF", outline="#E2DFDB", width=2)
        f = fitf(d, x["d"], W2 - 360, 56)
        d.text((105, y + 65 - f.size * 0.62), x["d"], font=f, fill=S.INK)
        fp = S.font("Bold", 34, False); pt = f"${x['p']}"; pw = d.textlength(pt, font=fp)
        d.rounded_rectangle((W2 - 105 - pw - 44, y + 38, W2 - 105, y + 92), 27, fill=S.RED)
        d.text((W2 - 105 - pw - 22, y + 44), pt, font=fp, fill="#FFFFFF")
        y += 150
    S.block(d, 70, y + 20, "Domain + first year included. Tap to see them on claimly.ae", S.font("SemiBold", 34, False), S.MUTED, W2 - 140, 1.3)
    S.wordmark(d, 70, H2 - 120, S.INK)
    fs = S.font("SemiBold", 32, False); d.text((W2 - 70 - d.textlength("claimly.ae", font=fs), H2 - 107), "claimly.ae", font=fs, fill=S.INK)
    im.save(path, quality=86)

# ---------------------------------------------------------------- reels
FPS, RW, RH = 30, 1080, 1920
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def reel(path, cat, items):
    title = f"5 names for your {DS.PHRASE.get(cat, 'business')}"
    total = int(FPS * 11.5)
    bg = Image.new("RGB", (RW, RH), S.BONE)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "23", "-c:a", "aac",
                          "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    fT, fN, fP = S.font("Black", 92), S.font("Black", 84), S.font("Bold", 40, False)
    for i in range(total):
        t = i / FPS
        im = bg.copy(); d = ImageDraw.Draw(im)
        if t < 9.3:
            a = ease(t / 0.6)
            d.text((90, 210 - 40 * (1 - a)), f"AVAILABLE TODAY · {cat.upper()}", font=S.font("Bold", 40, False), fill=S.RED)
            S.block(d, 90, 280 - 40 * (1 - a), title, fT, S.INK, RW - 180, 1.05)
            for k, x in enumerate(items):
                start = 1.0 + k * 1.3
                if t < start: continue
                e = ease((t - start) / 0.45)
                y = 700 + k * 200; xoff = int((1 - e) * 700)
                d.rounded_rectangle((70 + xoff, y, RW - 70 + xoff, y + 170), 34, fill="#FFFFFF", outline="#E2DFDB", width=3)
                f = fitf(d, x["d"], RW - 420, 84)
                d.text((115 + xoff, y + 85 - f.size * 0.62), x["d"], font=f, fill=S.INK)
                pt = f"${x['p']}"; pw = d.textlength(pt, font=fP)
                d.rounded_rectangle((RW - 115 - pw - 50 + xoff, y + 55, RW - 115 + xoff, y + 115), 30, fill=S.RED)
                d.text((RW - 115 - pw - 25 + xoff, y + 62), pt, font=fP, fill="#FFFFFF")
        else:
            e = ease((t - 9.3) / 0.5)
            im = Image.new("RGB", (RW, RH), S.RED); d = ImageDraw.Draw(im)
            S.block(d, 90, 640 + 60 * (1 - e), "All available today.", S.font("Black", 110), "#FFFFFF", RW - 180, 1.04)
            S.block(d, 90, 930 + 60 * (1 - e), "Domain + first year included. Link in bio.", S.font("Medium", 52, False), "#FFE3E1", RW - 180, 1.3)
            d.text((90, 1180), "claimly.ae", font=S.font("Black", 80), fill="#FFFFFF")
        S.wordmark(d, 90, RH - 210, S.INK if t < 9.3 else "#FFFFFF", dot=S.RED if t < 9.3 else S.INK, size=56)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def reel_cover(path, cat, items):
    S.names(path, f"Available today · {cat}", f"5 names for your {DS.PHRASE.get(cat, 'business')}",
            [(x["d"], x["p"]) for x in items], "Domain + first year included. Link in bio.")

# ---------------------------------------------------------------- build the month
def main():
    os.makedirs(OUT, exist_ok=True)
    plan = []
    ci = 0
    st_i, car_i = 0, 0
    for n in range(DAYS):
        day = START + datetime.timedelta(days=n)
        folder = f"{n+1:02d}-{day.isoformat()}"; fd = os.path.join(OUT, folder); os.makedirs(fd, exist_ok=True)
        url = lambda f: f"{BASE}/{folder}/{f}"
        cat = CATS[ci % len(CATS)]; ci += 1
        entry = {"day": n + 1, "date": day.isoformat(), "weekday": day.strftime("%a"), "category": cat}
        # feed
        if n % 2 == 0:
            items = take(cat, 5)
            reel(os.path.join(fd, "reel.mp4"), cat, items); reel_cover(os.path.join(fd, "reel-cover.jpg"), cat, items)
            entry["feed"] = {"type": "REEL", "title": f"Reel: 5 names for your {DS.PHRASE[cat]}", "media": [url("reel.mp4")],
                             "cover": url("reel-cover.jpg"), "caption": names_caption(cat, items, "reel"), "domains": [x["d"] for x in items]}
        elif n % 6 == 1 and car_i < len(CAROUSELS):
            title, slides = CAROUSELS[car_i]; car_i += 1
            files = []
            S.cover(os.path.join(fd, "carousel-0.jpg"), "Save this for later", title, "Swipe through. Save it for when you name your next business.")
            files.append(url("carousel-0.jpg"))
            for k, (h, b) in enumerate(slides, 1):
                S.tip(os.path.join(fd, f"carousel-{k}.jpg"), k, len(slides), h, b); files.append(url(f"carousel-{k}.jpg"))
            cap = (f"{title} 👇 Swipe through and save it.\n\n" + "\n".join(f"{k}. {h}" for k, (h, _) in enumerate(slides, 1)) +
                   "\n\nWant names that pass every check? 10 names + domain in 48 hours. Link in bio.\n\nاحفظ المنشور 🔖\n\n"
                   "#namingtips #businessname #startuptips #branding #entrepreneur #dubaibusiness #saudibusiness #smallbusiness")
            entry["feed"] = {"type": "CAROUSEL", "title": f"Carousel: {title}", "media": files, "caption": cap}
        else:
            k, head, sub, cap = STATEMENTS[st_i % len(STATEMENTS)]; st_i += 1
            S.statement(os.path.join(fd, "post.jpg"), f"Claimly · {k}", head, sub)
            entry["feed"] = {"type": "POST", "title": f"Post: {head}", "media": [url("post.jpg")],
                             "caption": cap + f"\n\n{BASE_TAGS}"}
        # stories
        scat = CATS[(ci + 5) % len(CATS)]
        one = take(scat, 1)[0]; pair = take(CATS[(ci + 9) % len(CATS)], 2)
        story_name(os.path.join(fd, "story-1.jpg"), one["d"], one["p"], scat)
        story_poll(os.path.join(fd, "story-2.jpg"), pair[0], pair[1], CATS[(ci + 9) % len(CATS)])
        story_tip(os.path.join(fd, "story-3.jpg"), n + 1, TIPS[n % len(TIPS)])
        entry["stories"] = [
            {"file": url("story-1.jpg"), "how": f"Add a Link sticker → https://claimly.ae/d/{one['d']}/?utm_source=instagram&utm_medium=story"},
            {"file": url("story-2.jpg"), "how": f"Add a Poll sticker: A = {pair[0]['d']}, B = {pair[1]['d']}"},
            {"file": url("story-3.jpg"), "how": "Add a Link sticker → https://claimly.ae/name-my-business/?utm_source=instagram&utm_medium=story"}]
        # pinterest pin
        pcat = CATS[(ci + 13) % len(CATS)]; pitems = take(pcat, 5)
        pin_list(os.path.join(fd, "pin.jpg"), pcat, pitems)
        entry["pin"] = {"file": url("pin.jpg"), "board": {"Food": "Café & Food Brand Names", "AI": "Tech & AI Startup Names", "SaaS": "Tech & AI Startup Names", "Crypto": "Tech & AI Startup Names", "Gaming": "Tech & AI Startup Names"}.get(pcat, "Business Name Ideas"),
                        "title": f"5 name ideas for your {DS.PHRASE[pcat]} (domains available)",
                        "description": f"Brandable, available domain names for a {DS.PHRASE[pcat]}: " + ", ".join(x['d'] for x in pitems) + ". First year of registration included.",
                        "link": f"https://claimly.ae/domains/{slug(pcat)}/?utm_source=pinterest&utm_medium=pin"}
        plan.append(entry)
        print("day", n + 1, cat, entry["feed"]["type"], flush=True)
    json.dump(plan, open(os.path.join(OUT, "plan.json"), "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
