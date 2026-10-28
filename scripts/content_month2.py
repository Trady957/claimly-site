"""Claimly Instagram month 2 (29 Oct - 27 Nov 2026): 3 Reels + 3 posts every day.

Per day:
  r1  Reel: 5 available names for one market (animated list)
  r2  Reel: a bundle / offer (animated text scenes)
  r3  Reel: name of the day, "A or B?", or a naming tip (animated text scenes)
  p1  Post: bundle / offer (red statement)
  p2  Carousel: naming tips, or 5 names for one market (one name per slide)
  p3  Post: naming tip (statement) or a list of 5 names
Output: social/month2/<NN>-<date>/... and social/month2/plan.json (captions, files, times).
Run once:  python3 scripts/content_month2.py [--only N]   (needs Pillow + ffmpeg)
"""
import datetime, json, os, random, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import social as S
import daily_social as DS
import segments as SEG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "month2")
BASE = "https://claimly.ae/social/month2"
START = datetime.date(2026, 10, 29)
DAYS = 30
OFFER_END = datetime.date(2026, 11, 30)
random.seed(20261029)
TZ = "Asia/Dubai"
# posting times (Dubai). Month 1 already posts at 18:00.
TIMES = {"r1": "09:30", "p1": "11:30", "r2": "13:30", "p2": "16:00", "r3": "20:00", "p3": "21:30"}

def slug(c): return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
TAGS = "#businessname #startup #smallbusiness #dubaibusiness #saudibusiness #branding"
AR_NAMES = "أسماء متاحة اليوم مع الدومين، السعر يشمل السنة الأولى 👆"

# ---------------------------------------------------------------- name pool
inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
gone = set(open(os.path.join(ROOT, "data", "sold.txt")).read().split()) | set(open(os.path.join(ROOT, "data", "taken.txt")).read().split())
used = set()
for f in os.listdir(os.path.join(ROOT, "social", "daily")):
    if f.endswith(".json") and f != "latest.json":
        used |= {n["domain"] for n in json.load(open(os.path.join(ROOT, "social", "daily", f))).get("names", [])}
m1 = os.path.join(ROOT, "social", "month1", "plan.json")
if os.path.exists(m1):
    used |= set(re.findall(r"[a-z]+\.(?:com|co|io|app|studio|shop)", open(m1).read()))
WEAK = re.compile(r"(ova|evo|ix|ary|ery|ora|ly|ify|able|era)$")
SEGN = {x["d"]: x["s"] for x in inv if x.get("s")}
pool = {}
for x in inv:
    d = x["d"]
    if d in gone or d in used or d in DS.PREMIUM: continue
    if not re.fullmatch(r"[a-z]+\.(com|co|io|studio|shop)", d) or len(d) > 16: continue
    lab = d.split(".")[0]
    if d not in SEGN and (not DS.two_words(lab) or WEAK.search(lab)): continue
    pool.setdefault(x["c"], []).append(x)
for c in pool:
    random.shuffle(pool[c])
    pool[c].sort(key=lambda x: (x["d"] not in SEGN, x["d"].split(".")[1] != "com", len(x["d"])))
CATS = [c for c in DS.PHRASE if len(pool.get(c, [])) >= 20]
PH = DS.PHRASE

def take(cat, n):
    out = pool[cat][:n]; pool[cat] = pool[cat][n:]
    return out

HASH = {"Finance": "#fintech #financebrand", "AI": "#aistartup #aiagents", "SaaS": "#saas #softwarestartup",
        "E-commerce": "#ecommerce #onlinestore", "Local": "#localbusiness #shoplocal", "Health": "#clinic #wellnessbrand",
        "Creator": "#contentcreator #creatorbrand", "Education": "#edtech #tutoring", "Travel": "#travelbrand #tourism",
        "Real estate": "#realestate #dubairealestate", "Food": "#cafebusiness #foodbusiness", "Pets": "#petbusiness #petbrand",
        "Crypto": "#crypto #web3", "Marketing": "#marketingagency #agency", "Legal": "#lawfirm #consulting",
        "Fashion": "#beautybrand #fashionbrand", "Gaming": "#gamingstudio #indiegame", "Green": "#solar #cleanenergy"}
HOOK = {"Finance": "Starting a finance or payments brand?", "AI": "Building an AI agent or AI startup?", "SaaS": "Launching a software product?",
        "E-commerce": "Opening an online store?", "Local": "Starting a local business?", "Health": "Opening a clinic or wellness brand?",
        "Creator": "Growing your creator brand?", "Education": "Starting a tutoring or course business?", "Travel": "Building a travel brand?",
        "Real estate": "Starting in UAE real estate?", "Food": "Opening a café or food brand?", "Pets": "Starting a pet business?",
        "Crypto": "Launching a crypto project?", "Marketing": "Starting a marketing agency?", "Legal": "Opening a law or consulting firm?",
        "Fashion": "Launching a beauty or fashion brand?", "Gaming": "Starting a gaming studio?", "Green": "Starting a solar or clean-energy company?"}

def names_caption(cat, items, lead=""):
    lines = "\n".join(f"→ {x['d']} · ${x['p']}" for x in items)
    return (f"{lead}{HOOK.get(cat, 'Starting a business?')}\n\nAvailable to register today:\n{lines}\n\n"
            f"Two real words, easy to say, domain + first year included. Link in bio.\n\n{AR_NAMES}\n\n{TAGS} {HASH.get(cat, '')}")

# ---------------------------------------------------------------- offers (bundles)
# key, kicker, headline, sub, scenes for the reel [(kicker, big, small)], caption
OFFERS = [
    ("Quick Pick", "3 names + your domain. $49.", "Made for your business, .com checked, domain registered for you. Delivered in 24 hours.",
     [("NEED A NAME FAST?", "3 names. 24 hours.", "Made for your business, not a generator."), ("QUICK PICK", "Your .com registered for you.", "First year included."), ("LAUNCH PRICE", "$49", "Normally $69. Until 30 Nov.")],
     "Need a name by tomorrow? ⚡\n\nQuick Pick: 3 names made for your business, .com checked, and your favourite domain registered for you. Delivered in 24 hours.\n\n$49 (normally $69) until 30 Nov · link in bio\n\nثلاثة أسماء لمشروعك مع تسجيل الدومين خلال ٢٤ ساعة، بـ ٤٩ دولار."),
    ("Starter", "10 names. Your domain. $99.", "Tell us what you do. Get 10 checked names in 48 hours. We register your favourite.",
     [("STUCK ON A NAME?", "We'll send you 10.", "Each one with an available domain."), ("STARTER", "Pick one. We register it.", "Handles checked on Instagram, X, LinkedIn."), ("LAUNCH PRICE", "$99", "Normally $149. Until 30 Nov.")],
     "Stuck on a business name? 💭\n\nStarter: 10 names made for your business, each with an available domain. Pick one and we register it for you. 48 hours.\n\n$99 instead of $149 until 30 Nov · link in bio\n\n١٠ أسماء مع دومين متاح خلال ٤٨ ساعة بـ ٩٩ دولار بدل ١٤٩."),
    ("Name + Shield", "Lock your name down.", "Your .com plus .co and .net, so no one can copy it. Plus 10 names and handle checks.",
     [("FOUND THE NAME?", "Protect it.", "Copycats register the .co and .net."), ("NAME + SHIELD", ".com + .co + .net", "All registered for you, plus 10 names."), ("LAUNCH PRICE", "$139", "Normally $189. Until 30 Nov.")],
     "Found the perfect name? Protect it 🛡️\n\nName + Shield: 10 names made for you, then your chosen name registered as .com, .co AND .net, so no one can copy it. Handles checked on Instagram, TikTok, X and LinkedIn.\n\n$139 (normally $189) until 30 Nov · link in bio\n\nاحمِ اسم مشروعك: نسجّل .com و .co و .net لك."),
    ("Brand kit", "Name + logo + colours. $199.", "10 names, your domain, a wordmark logo, colours, fonts and taglines in 3 days.",
     [("STARTING FROM ZERO?", "Get the whole look.", "Name, domain, logo, colours, fonts."), ("BRAND KIT", "Ready in 3 days.", "Plus tagline options and one round of changes."), ("LAUNCH PRICE", "$199", "Normally $299. Until 30 Nov.")],
     "From idea to brand in 3 days 🎨\n\nBrand kit: 10 names + your domain registered + a wordmark logo, colour palette, fonts and taglines.\n\n$199 instead of $299 until 30 Nov · link in bio\n\nاسم + دومين + شعار + ألوان + خطوط خلال ٣ أيام."),
    ("Bilingual Brand", "One brand. Two languages.", "Names checked in Arabic and English, a wordmark in both, and taglines in both.",
     [("SELLING IN THE GULF?", "Your name must work in Arabic too.", "No awkward meanings. Easy to say."), ("BILINGUAL BRAND", "Logo in English + Arabic.", "Plus taglines in both languages."), ("LAUNCH PRICE", "$249", "Normally $349. Until 30 Nov.")],
     "Selling in the UAE or Saudi Arabia? 🇦🇪🇸🇦\n\nBilingual Brand: names checked for Arabic pronunciation and meaning, your domain registered, a wordmark in English AND Arabic, and taglines in both.\n\n$249 (normally $349) until 30 Nov · link in bio\n\nهوية بلغتين: اسم وشعار وشعار نصي بالعربي والإنجليزي."),
    ("Founder Launch", "Launch-ready in 7 days.", "Name, domain, logo, a one-page website live on your domain, and an Instagram starter kit.",
     [("WANT TO LAUNCH THIS MONTH?", "Everything in 7 days.", "Name, domain, logo, colours."), ("FOUNDER LAUNCH", "Your website, live.", "One page on your new domain + Instagram kit."), ("LAUNCH PRICE", "$349", "Normally $499. Until 30 Nov.")],
     "Launch-ready in 7 days 🚀\n\nFounder Launch: name + domain + logo + colours, a one-page website live on your new domain, business email setup guide and an Instagram starter kit.\n\n$349 instead of $499 until 30 Nov · link in bio\n\nكل ما تحتاجه للإطلاق خلال ٧ أيام: اسم، دومين، شعار وموقع."),
    ("Duo", "Two businesses. $159.", "Two Starter packages: for you and a friend, or your second idea. Save $139.",
     [("GOT A FRIEND STARTING TOO?", "Name both businesses.", "Two Starter packages in one."), ("DUO", "20 names. 2 domains.", "48 hours each."), ("LAUNCH PRICE", "$159", "Normally $298. Until 30 Nov.")],
     "Starting a business with a friend nearby? 👯\n\nDuo: two Starter packages, 10 names + a registered domain for each business. Share it, or use it for your second idea.\n\n$159 instead of $298 until 30 Nov · link in bio\n\nباقة لشخصين: ١٠ أسماء ودومين لكل مشروع بـ ١٥٩ دولار."),
    ("Free ideas", "3 free name ideas.", "DM us NAME + what your business does. We reply with 3 ideas and available domains.",
     [("NOT READY TO PAY?", "Get 3 names free.", "With available domains."), ("HOW", "DM us the word NAME", "+ what your business does."), ("FREE", "No card. No catch.", "Or use the form at claimly.ae")],
     "Want 3 free name ideas? 🎁\n\nDM us the word NAME + what your business does. We reply with 3 ideas, each with an available domain. No card, no catch.\n\nأرسل لنا كلمة NAME مع وصف مشروعك لثلاث أفكار مجانية."),
    ("Agencies", "Agencies: 5 names for $545.", "Business setup firms and agencies: 10 names + domain per client, unbranded, 48 hours.",
     [("RUN A SETUP FIRM OR AGENCY?", "Your clients need names.", "Before the licence, the logo, the website."), ("WHOLESALE", "5 clients: $545", "10 clients: $990. Unbranded."), ("48 HOURS", "Per client.", "Details: claimly.ae/partners")],
     "Business setup firm or agency? 🤝\n\nGive every client a name and domain in 48 hours. Unbranded naming packages: 5 for $545 or 10 for $990.\n\nDetails: claimly.ae/partners (link in bio)\n\nباقات تسمية بالجملة لشركات التأسيس والوكالات."),
]

def countdown(day):
    left = (OFFER_END - day).days
    return ("Last call", f"{left} days left at $99.", "The launch price ends 30 Nov. After that, Starter goes back to $149.",
            [("LAUNCH PRICE", f"{left} days left.", "Ends 30 Nov."), ("STARTER", "$99", "10 names + your domain."), ("AFTER 30 NOV", "$149", "Order now, start whenever you're ready.")],
            f"⏳ {left} days left at the launch price.\n\nStarter is $99 (normally $149) until 30 Nov: 10 names + your domain registered, in 48 hours. Brand kit is $199 instead of $299.\n\nLink in bio.\n\nباقي {left} يوم على سعر الإطلاق.")

# ---------------------------------------------------------------- tips, reels and carousels banks
TIP_POSTS = [  # headline, sub
    ("Two real words beat one made-up word.", "BrewDune is easier to remember than Brewzio."),
    ("If you have to spell it, lose it.", "Every \"how do you spell that?\" costs you a customer."),
    ("Your name will be on every invoice.", "Pick one you're proud to say 1,000 times."),
    ("Domain first. Logo second.", "A logo for a name you can't own online is wasted money."),
    ("Say it in a voice note.", "If it sounds clear on WhatsApp, it works."),
    ("Don't name it after your city.", "You'll expand. Your name should come with you."),
    ("Avoid the word \"solutions\".", "It tells customers nothing and sounds like everyone else."),
    ("A great name saves on ads.", "People remember it, search it and tell friends."),
    ("Hyphens kill domains.", "Nobody says \"dash\" out loud. Drop them."),
    ("Check TikTok too.", "Your handle matters as much as your domain now."),
    ("Short names fit everywhere.", "App icons, shop signs, cups, invoices."),
    ("Be distinctive, not descriptive.", "\"Best Dubai Cleaning\" can't grow. \"PureNest\" can."),
    ("Test it on a stranger.", "Say it once. Can they type it into Google?"),
    ("Arabic check before printing.", "A meaning in Arabic can make or break you in the Gulf."),
    ("Good names get taken daily.", "Thousands of domains are registered every day."),
]
NAME_WHY = ["Two real words, easy to say, and the domain is free.", "Short, warm and easy to remember.", "Sounds like a real company from day one.",
            "Easy to say in English and Arabic.", "Fits on a sign, a cup and an app icon.", "Passes the phone test: say it once, they can type it."]
REEL_TIPS = [  # hook, tip, fix
    ("Your business name is costing you customers.", "If people can't spell it, they can't find you.", "Pick two real words. Easy to say, easy to type."),
    ("Stop using \"solutions\" in your name.", "It sounds like every other company.", "Use a word that hints at the feeling you sell."),
    ("Before you design a logo...", "Check the domain is free.", "Redoing a brand costs far more than a domain."),
    ("The 5-second name test.", "Say it once to a friend.", "If they can type it without asking, keep it."),
    ("Naming a business in Dubai?", "Say it in Arabic too.", "No awkward meaning, easy to pronounce."),
    ("Don't put your city in your name.", "It boxes you in when you expand.", "Choose a name that can travel."),
    ("The .co trick.", "Your .com is taken? Try .co.", "Short, modern, trusted by startups."),
    ("Why short names win.", "They fit on signs, cups and app icons.", "Aim for under 11 letters."),
    ("Don't wait to register.", "Good names get taken every day.", "A domain costs less than one coffee meeting."),
    ("Hyphens in a domain?", "Nobody says \"dash\" out loud.", "Pick a name that needs no punctuation."),
]
CAROUSELS = [
    ("5 signs your business name is wrong", [("You have to spell it", "Every time, on every call."), ("It sounds like a competitor", "Customers will mix you up."), ("The .com is taken", "You'll lose traffic to someone else."), ("It's too literal", "It can't grow with your business."), ("You don't love saying it", "You'll say it thousands of times.")]),
    ("How to name a café", [("Pick the mood", "Cosy, fast, luxury or local?"), ("Use warm words", "Roast, brew, crumb, golden."), ("Shout test", "Say it like a barista calling an order."), ("Check Instagram", "Cafés are found there first."), ("Grab the domain", "Before your sign goes up.")]),
    ("How to name a clinic", [("Calm beats clever", "Patients want trust, not puns."), ("Keep it short", "For signs, SMS and Google Maps."), ("Avoid medical claims", "Check your health authority's rules."), ("Test in Arabic", "Easy to say for every patient."), ("Own the .com", "Patients search before they book.")]),
    ("How to name a real estate agency", [("Use home words", "Nest, key, haven, abode."), ("Look confident", "Buyers trust calm, solid names."), ("Read it from a car", "Your sign must work at speed."), ("Don't name one area", "You'll sell in more than one."), ("Secure the .com", "Portals link to your website.")]),
    ("How to name an AI startup", [("Skip \"AI\" in the name", "Every competitor already has it."), ("Name the helper", "Mate, crew, pilot feel friendly."), ("Two short words", "Easy to say in a demo call."), (".com, .co or .io", "All fine for tech buyers."), ("Move fast", "Good AI names go daily.")]),
    ("How to name an online store", [("Easy to type on a phone", "Most orders happen there."), ("No hyphens or numbers", "They lose clicks."), ("Leave room to grow", "Don't name one product."), ("Try .shop", "When the .com is taken."), ("Check the ad preview", "Short names get more clicks.")]),
    ("Arabic + English naming checklist", [("Easy to pronounce in both", "No sounds that trip people up."), ("No awkward meanings", "Check with a native speaker."), ("Short for WhatsApp", "Most deals happen there."), ("Works in both scripts", "Your logo may need both."), ("Licence rules", "Check your free zone's naming rules.")]),
    ("What to do after you pick a name", [("Register the domain", "Today, not next week."), ("Claim the handles", "Instagram, TikTok, X, LinkedIn."), ("Check trademarks", "In your country and industry."), ("Set up email", "you@yourname.com builds trust."), ("Then the logo", "Design comes after ownership.")]),
    ("How to name a beauty brand", [("Pick a price point", "Luxe, playful or natural?"), ("Soft sounds", "Glow, silk, aura, luxe."), ("Looks good small", "On labels and booking apps."), ("Instagram first", "Beauty is discovered there."), ("Own the .com", "For your booking link.")]),
    ("How to name a solar company", [("Energy + solid", "Solar + anchor, volt + crest."), ("Sound trustworthy", "You're selling a 20-year promise."), ("Room to grow", "Batteries and EV chargers come next."), ("Van test", "Readable on a moving van."), (".com or .co", "Both look good on a quote.")]),
    ("Free name generators vs a naming service", [("Generators", "Give names whose .com is gone."), ("Generators", "Make random sounds, not brands."), ("A naming service", "Checks every domain first."), ("A naming service", "Fits names to your customers."), ("Claimly", "10 names + your domain, $99.")]),
    ("How to name a pet business", [("Playful works here", "Paw, wag, purr, pup."), ("Pick your animals", "Dogs, cats or all pets?"), ("Collar-tag test", "Short enough to print small."), ("Van test", "For grooming and walking."), ("Own the .com", "Owners book online.")]),
    ("How much should a business name cost?", [("DIY: free", "But hours of work and a taken .com."), ("Generator: free", "Random names, no checks."), ("Claimly Quick Pick: $49", "3 names + domain in 24 hours."), ("Claimly Starter: $99", "10 names + domain in 48 hours."), ("Agency: $2,000+", "Same goal, much higher price.")]),
    ("How to name a tutoring business", [("Parents choose", "Sound caring and smart."), ("Bright words", "Spark, bright, mentor, clear."), ("Not one subject", "You'll teach more later."), ("Easy for kids", "They'll say it too."), ("Grab the domain", "Parents look you up first.")]),
    ("Our bundles, explained", [("Quick Pick · $49", "3 names + domain in 24 hours."), ("Starter · $99", "10 names + domain in 48 hours."), ("Brand kit · $199", "Plus logo, colours, fonts."), ("Bilingual · $249", "English + Arabic brand."), ("Founder Launch · $349", "Plus a website live on your domain.")]),
]

# ---------------------------------------------------------------- image templates
W, H = S.W, S.H
def fitf(d, text, maxw, start, minimum=48, weight="Black"):
    size = start
    while size > minimum and d.textlength(text, font=S.font(weight, size)) > maxw: size -= 4
    return S.font(weight, size)

def name_slide(path, n, total, dom, price, phrase, why):
    im = Image.new("RGB", (W, H), S.BONE); d = ImageDraw.Draw(im)
    d.text((80, 100), f"{n}/{total} · FOR YOUR {phrase.upper()}"[:60], font=S.font("Bold", 28, False), fill=S.RED)
    d.rounded_rectangle((60, 360, W - 60, 680), 40, fill="#FFFFFF", outline="#E2DFDB", width=3)
    f = fitf(d, dom, W - 200, 130); tw = d.textlength(dom, font=f)
    d.text(((W - tw) / 2, 520 - f.size * 0.62), dom, font=f, fill=S.INK)
    fp = S.font("Black", 64); pt = f"${price}"; pw = d.textlength(pt, font=fp)
    d.rounded_rectangle(((W - pw) / 2 - 50, 740, (W + pw) / 2 + 50, 850), 55, fill=S.RED)
    d.text(((W - pw) / 2, 752), pt, font=fp, fill="#FFFFFF")
    S.block(d, 100, 930, why, S.font("Medium", 42, False), S.MUTED, W - 200, 1.35)
    S.footer(d, False); im.save(path, quality=90)

# ---------------------------------------------------------------- reels
FPS, RW, RH = 30, 1080, 1920
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def _encoder(path):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
                             "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "24", "-c:a", "aac",
                             "-movflags", "+faststart", path], stdin=subprocess.PIPE)

THEMES = [(S.BONE, S.INK, S.RED, S.MUTED), (S.INK, "#FFFFFF", S.RED, "#BDB8B5"), (S.RED, "#FFFFFF", "#FFFFFF", "#FFE3E1")]

def _scene_frame(sc, t, theme, big_size=120):
    bg, fg, accent, muted = theme
    kicker, big, small = sc
    im = Image.new("RGB", (RW, RH), bg); d = ImageDraw.Draw(im)
    if bg == S.RED: d.ellipse((560, -260, 1340, 520), fill="#EA4A3F")
    a = ease(t / 0.5); b = ease((t - 0.35) / 0.5)
    d.text((90, 560 - 30 * (1 - a)), kicker, font=S.font("Bold", 40, False), fill=accent if bg != S.RED else "#FFFFFF")
    fbig = S.font("Black", big_size if len(big) > 6 else 260)
    y = S.block(d, 90, 640 - 50 * (1 - a), big, fbig, fg, RW - 180, 1.04)
    if t > 0.35:
        S.block(d, 90, y + 50 + 30 * (1 - b), small, S.font("Medium", 54, False), muted, RW - 180, 1.3)
    return im, d

def scenes_reel(path, scenes, cta="Link in bio · claimly.ae", per=2.8):
    p = _encoder(path)
    total_scenes = scenes + [("CLAIMLY.AE", "Link in bio.", cta)]
    for si, sc in enumerate(total_scenes):
        theme = THEMES[2] if si == len(total_scenes) - 1 else THEMES[si % 2]
        for i in range(int(FPS * per)):
            im, d = _scene_frame(sc, i / FPS, theme)
            dark = theme[0] != S.BONE
            S.wordmark(d, 90, RH - 210, "#FFFFFF" if dark else S.INK, dot=S.INK if theme[0] == S.RED else S.RED, size=56)
            # progress bar
            frac = (si + i / (FPS * per)) / len(total_scenes)
            d.rectangle((0, 0, int(RW * frac), 10), fill=S.RED if theme[0] != S.RED else "#FFFFFF")
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def names_reel(path, cat, items):
    title = f"{len(items)} names for your {PH.get(cat, 'business')}"
    total = int(FPS * 11.5); bg = Image.new("RGB", (RW, RH), S.BONE)
    p = _encoder(path)
    fT, fP = S.font("Black", 92), S.font("Bold", 40, False)
    for i in range(total):
        t = i / FPS
        if t < 9.3:
            im = bg.copy(); d = ImageDraw.Draw(im); a = ease(t / 0.6)
            d.text((90, 210 - 40 * (1 - a)), f"AVAILABLE TODAY · {cat.upper()}", font=S.font("Bold", 40, False), fill=S.RED)
            S.block(d, 90, 280 - 40 * (1 - a), title, fT, S.INK, RW - 180, 1.05)
            for k, x in enumerate(items):
                start = 1.0 + k * 1.3
                if t < start: continue
                e = ease((t - start) / 0.45); y = 700 + k * 200; xo = int((1 - e) * 700)
                d.rounded_rectangle((70 + xo, y, RW - 70 + xo, y + 170), 34, fill="#FFFFFF", outline="#E2DFDB", width=3)
                f = fitf(d, x["d"], RW - 420, 84)
                d.text((115 + xo, y + 85 - f.size * 0.62), x["d"], font=f, fill=S.INK)
                pt = f"${x['p']}"; pw = d.textlength(pt, font=fP)
                d.rounded_rectangle((RW - 115 - pw - 50 + xo, y + 55, RW - 115 + xo, y + 115), 30, fill=S.RED)
                d.text((RW - 115 - pw - 25 + xo, y + 62), pt, font=fP, fill="#FFFFFF")
            S.wordmark(d, 90, RH - 210, S.INK, size=56)
        else:
            e = ease((t - 9.3) / 0.5)
            im = Image.new("RGB", (RW, RH), S.RED); d = ImageDraw.Draw(im)
            S.block(d, 90, 640 + 60 * (1 - e), "All available today.", S.font("Black", 110), "#FFFFFF", RW - 180, 1.04)
            S.block(d, 90, 930 + 60 * (1 - e), "Or get 10 names made for you: $99 until 30 Nov. Link in bio.", S.font("Medium", 52, False), "#FFE3E1", RW - 180, 1.3)
            S.wordmark(d, 90, RH - 210, "#FFFFFF", dot=S.INK, size=56)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def reveal_reel(path, dom, price, phrase, why):
    """Name of the day: big domain reveal letter by letter."""
    p = _encoder(path); lab = dom
    for i in range(int(FPS * 9)):
        t = i / FPS
        im = Image.new("RGB", (RW, RH), S.INK); d = ImageDraw.Draw(im)
        d.text((90, 360), "NAME OF THE DAY", font=S.font("Bold", 42, False), fill=S.RED)
        S.block(d, 90, 430, f"For your {phrase}", S.font("Black", 80), "#FFFFFF", RW - 180, 1.08)
        n = min(len(lab), int(max(0, t - 0.8) / 2.2 * len(lab)) + (1 if t > 0.8 else 0))
        f = fitf(d, lab, RW - 180, 150)
        d.text((90, 860), lab[:n], font=f, fill="#FFFFFF")
        if t > 3.4:
            e = ease((t - 3.4) / 0.5)
            fp = S.font("Black", 80); pt = f"${price}"; pw = d.textlength(pt, font=fp)
            d.rounded_rectangle((90, 1100 + 40 * (1 - e), 90 + pw + 100, 1230 + 40 * (1 - e)), 65, fill=S.RED)
            d.text((140, 1115 + 40 * (1 - e)), pt, font=fp, fill="#FFFFFF")
        if t > 4.6:
            S.block(d, 90, 1320, why, S.font("Medium", 50, False), "#BDB8B5", RW - 180, 1.3)
        if t > 6.6:
            d.text((90, 1560), "Grab it: link in bio", font=S.font("Bold", 52, False), fill=S.RED)
        S.wordmark(d, 90, RH - 210, "#FFFFFF", dot=S.RED, size=56)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def ab_reel(path, a, b, phrase):
    p = _encoder(path)
    for i in range(int(FPS * 9)):
        t = i / FPS
        im = Image.new("RGB", (RW, RH), S.BONE); d = ImageDraw.Draw(im)
        d.text((90, 300), "YOUR VOTE", font=S.font("Bold", 42, False), fill=S.RED)
        S.block(d, 90, 370, f"Which name for a {phrase}?", S.font("Black", 92), S.INK, RW - 180, 1.05)
        for k, (x, lab) in enumerate(((a, "A"), (b, "B"))):
            st = 1.2 + k * 1.2
            if t < st: continue
            e = ease((t - st) / 0.45); y = 860 + k * 330; xo = int((1 - e) * 700)
            d.rounded_rectangle((70 + xo, y, RW - 70 + xo, y + 270), 40, fill="#FFFFFF", outline="#E2DFDB", width=3)
            d.text((120 + xo, y + 40), lab, font=S.font("Black", 70), fill=S.RED)
            f = fitf(d, x["d"], RW - 360, 100)
            d.text((230 + xo, y + 135 - f.size * 0.62), x["d"], font=f, fill=S.INK)
            d.text((230 + xo, y + 195), f"${x['p']} · available today", font=S.font("SemiBold", 36, False), fill=S.MUTED)
        if t > 4.5:
            S.block(d, 90, 1560, "Comment A or B below", S.font("Black", 72), S.INK, RW - 180, 1.1)
        S.wordmark(d, 90, RH - 210, S.INK, size=56)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def cover(path, kicker, title, sub, dark=True):
    S.cover(path, kicker, title, sub) if dark else S.statement(path, kicker, title, sub)

# ---------------------------------------------------------------- build
def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    plan = []
    for n in range(DAYS):
        day = START + datetime.timedelta(days=n)
        folder = f"{n+1:02d}-{day.isoformat()}"; fd = os.path.join(OUT, folder); os.makedirs(fd, exist_ok=True)
        url = lambda f: f"{BASE}/{folder}/{f}"
        render = only is None or only == n + 1
        cat = CATS[n % len(CATS)]
        posts = []
        # r1: names reel
        items = take(cat, 5)
        if render:
            names_reel(os.path.join(fd, "r1.mp4"), cat, items)
            S.names(os.path.join(fd, "r1-cover.jpg"), f"Available today · {cat}", f"5 names for your {PH[cat]}", [(x["d"], x["p"]) for x in items], "Domain + first year included. Link in bio.")
        posts.append({"slot": "r1", "time": TIMES["r1"], "type": "REEL", "title": f"Reel: 5 names for your {PH[cat]}", "media": [url("r1.mp4")], "cover": url("r1-cover.jpg"),
                      "caption": names_caption(cat, items, "Watch till the end 👀\n\n"), "domains": [x["d"] for x in items]})
        # offers: countdown on the last 10 days every 3rd day, otherwise rotate
        off_r = countdown(day) if (OFFER_END - day).days <= 10 and n % 3 == 0 else OFFERS[n % len(OFFERS)]
        off_p = OFFERS[(n + 4) % len(OFFERS)]
        kick, head, sub, scenes, cap = off_r
        if render:
            scenes_reel(os.path.join(fd, "r2.mp4"), scenes)
            S.statement(os.path.join(fd, "r2-cover.jpg"), f"Claimly · {kick}", head, sub)
        posts.append({"slot": "r2", "time": TIMES["r2"], "type": "REEL", "title": f"Reel: {kick}", "media": [url("r2.mp4")], "cover": url("r2-cover.jpg"),
                      "caption": cap + f"\n\n{TAGS} #launchoffer"})
        # r3: name of the day / A or B / tip
        kind3 = ("reveal", "ab", "tip")[n % 3]
        c3 = CATS[(n + 7) % len(CATS)]
        if kind3 == "reveal":
            x = take(c3, 1)[0]; why = NAME_WHY[n % len(NAME_WHY)]
            if render:
                reveal_reel(os.path.join(fd, "r3.mp4"), x["d"], x["p"], PH[c3], why)
                S.statement(os.path.join(fd, "r3-cover.jpg"), "Name of the day", x["d"], f"For your {PH[c3]}. ${x['p']}, domain + first year included.")
            cap3 = (f"Name of the day ✨\n\n{x['d']} · ${x['p']}\nFor your {PH[c3]}. {why}\n\nGrab it before someone else does: link in bio.\n\n"
                    f"اسم اليوم: {x['d']} 👆\n\n{TAGS} {HASH.get(c3, '')}")
            t3, dom3 = f"Reel: name of the day {x['d']}", [x["d"]]
        elif kind3 == "ab":
            pair = take(c3, 2)
            if render:
                ab_reel(os.path.join(fd, "r3.mp4"), pair[0], pair[1], PH[c3])
                S.names(os.path.join(fd, "r3-cover.jpg"), "Your vote", f"Which name for a {PH[c3]}?", [(y["d"], y["p"]) for y in pair], "Comment A or B below. Both available today.")
            cap3 = (f"Which name would you pick for a {PH[c3]}? 🤔\n\nA → {pair[0]['d']} · ${pair[0]['p']}\nB → {pair[1]['d']} · ${pair[1]['p']}\n\n"
                    f"Comment A or B 👇 Both are available today.\n\nأي اسم تختار؟ اكتب A أو B 👇\n\n{TAGS} {HASH.get(c3, '')}")
            t3, dom3 = f"Reel: A or B ({PH[c3]})", [y["d"] for y in pair]
        else:
            hook, tip, fix = REEL_TIPS[(n // 3) % len(REEL_TIPS)]
            if render:
                scenes_reel(os.path.join(fd, "r3.mp4"), [("NAMING TIP", hook, ""), ("THE PROBLEM", tip, ""), ("THE FIX", fix, "")], cta="10 names + your domain in 48h. $99 until 30 Nov.", per=2.6)
                S.statement(os.path.join(fd, "r3-cover.jpg"), "Naming tip", hook, fix)
            cap3 = (f"{hook} 👇\n\n{tip}\n{fix}\n\nWant names that pass every test? 10 names + your domain in 48 hours, $99 until 30 Nov. Link in bio.\n\n"
                    f"نصيحة لاسم مشروعك 💡\n\n#namingtips {TAGS}")
            t3, dom3 = f"Reel: tip – {hook}", []
        posts.append({"slot": "r3", "time": TIMES["r3"], "type": "REEL", "title": t3, "media": [url("r3.mp4")], "cover": url("r3-cover.jpg"), "caption": cap3, "domains": dom3})
        # p1: offer post
        kick, head, sub, _, cap = off_p
        if render: S.statement(os.path.join(fd, "p1.jpg"), f"Claimly · {kick}", head, sub)
        posts.append({"slot": "p1", "time": TIMES["p1"], "type": "POST", "title": f"Post: {kick}", "media": [url("p1.jpg")], "caption": cap + f"\n\n{TAGS} #launchoffer"})
        # p2: carousel (tips on even days, names on odd days)
        if n % 2 == 0:
            title, slides = CAROUSELS[(n // 2) % len(CAROUSELS)]
            files = []
            if render: S.cover(os.path.join(fd, "p2-0.jpg"), "Save this for later", title, "Swipe through. Save it for when you name your next business.")
            files.append(url("p2-0.jpg"))
            for k, (h, b) in enumerate(slides, 1):
                if render: S.tip(os.path.join(fd, f"p2-{k}.jpg"), k, len(slides), h, b)
                files.append(url(f"p2-{k}.jpg"))
            cap2 = (f"{title} 👇 Swipe and save.\n\n" + "\n".join(f"{k}. {h}" for k, (h, _) in enumerate(slides, 1)) +
                    "\n\nWant us to do it for you? Quick Pick $49 · Starter $99 · Brand kit $199 until 30 Nov. Link in bio.\n\nاحفظ المنشور 🔖\n\n#namingtips " + TAGS)
            posts.append({"slot": "p2", "time": TIMES["p2"], "type": "CAROUSEL", "title": f"Carousel: {title}", "media": files, "caption": cap2})
        else:
            c2 = CATS[(n + 3) % len(CATS)]; its = take(c2, 5); files = []
            if render: S.cover(os.path.join(fd, "p2-0.jpg"), f"Available today · {c2}", f"5 names for your {PH[c2]}", "Swipe to see them. Each one's domain is free right now.")
            files.append(url("p2-0.jpg"))
            for k, x in enumerate(its, 1):
                if render: name_slide(os.path.join(fd, f"p2-{k}.jpg"), k, len(its), x["d"], x["p"], PH[c2], NAME_WHY[(n + k) % len(NAME_WHY)])
                files.append(url(f"p2-{k}.jpg"))
            posts.append({"slot": "p2", "time": TIMES["p2"], "type": "CAROUSEL", "title": f"Carousel: 5 names for your {PH[c2]}", "media": files,
                          "caption": names_caption(c2, its, "Swipe 👉\n\n"), "domains": [x["d"] for x in its]})
        # p3: tip statement (even) or names list (odd)
        if n % 2 == 0:
            head, sub = TIP_POSTS[(n // 2) % len(TIP_POSTS)]
            if render: S.statement(os.path.join(fd, "p3.jpg"), f"Naming tip #{n//2 + 1}", head, sub)
            posts.append({"slot": "p3", "time": TIMES["p3"], "type": "POST", "title": f"Post: {head}", "media": [url("p3.jpg")],
                          "caption": f"{head} 💡\n\n{sub}\n\nNeed a name that passes every test? 3 names + domain in 24 hours for $49. Link in bio.\n\nنصيحة اليوم لاسم مشروعك.\n\n#namingtips {TAGS}"})
        else:
            c4 = CATS[(n + 11) % len(CATS)]; its = take(c4, 5)
            if render: S.names(os.path.join(fd, "p3.jpg"), f"Available today · {c4}", f"Names for your {PH[c4]}", [(x["d"], x["p"]) for x in its], "Domain + first year included. Link in bio.")
            posts.append({"slot": "p3", "time": TIMES["p3"], "type": "POST", "title": f"Post: names for your {PH[c4]}", "media": [url("p3.jpg")],
                          "caption": names_caption(c4, its), "domains": [x["d"] for x in its]})
        posts.sort(key=lambda q: q["time"])
        plan.append({"day": n + 1, "date": day.isoformat(), "weekday": day.strftime("%a"), "timezone": TZ, "posts": posts})
        print("day", n + 1, day, "rendered" if render else "planned", flush=True)
    json.dump(plan, open(os.path.join(OUT, "plan.json"), "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    main(only)
