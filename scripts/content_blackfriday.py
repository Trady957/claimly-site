"""Black Friday / Cyber Monday 2026 posts for Instagram and Pinterest (24-30 Nov).

For each day writes social/blackfriday/<date>/1.jpg (cover) and 2.jpg (5 real shop names
at the sale price), and social/blackfriday/captions.md with the caption, hashtags,
Pinterest title/description and links. Run: python3 scripts/content_blackfriday.py
"""
import datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
import sale as SALE
from daily_social import PREMIUM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "blackfriday")
SITE = "https://claimly.ae"

def lines(f):
    p = os.path.join(ROOT, "data", f)
    return {l.strip().lower() for l in open(p) if l.strip() and not l.startswith("#")} if os.path.exists(p) else set()

# date, cats, title on the names slide, cover kicker, cover headline, cover sub, caption hook, landing page, hashtags
DAYS = [
 ("2026-11-24", None, "Black Friday picks: .com names on sale", "Black Friday at Claimly",
  "Up to 30% off brand names.", "Every name is checked as available. First year included. Until Cyber Monday.",
  "Black Friday starts today at Claimly. Brandable domain names are up to 30% off until Monday 30 Nov, and every price includes the first year of registration.",
  "/", "#blackfriday #domainnames #businessname #startup #smallbusiness #branding #entrepreneur #dubai #uae"),
 ("2026-11-25", ["Marketing", "Creator"], "Names for your agency", "Black Friday · agencies",
  "Starting an agency? Get the name first.", "Short names with the .com or .co free, up to 30% off.",
  "Starting a marketing, ad or creative agency? Your name is the first thing a client judges. These are free to register today, at Black Friday prices.",
  "/business-name-ideas/agency/", "#agency #marketingagency #creativeagency #adagency #businessname #branding #blackfriday #dubaibusiness"),
 ("2026-11-26", ["Food"], "Names for your café or food brand", "Black Friday · food & café",
  "Your café needs a name people remember.", "Names with the domain ready, up to 30% off until Monday.",
  "Opening a café, bakery or food brand? A name people can say across the counter and find on Instagram. These ones come with the domain, at Black Friday prices.",
  "/business-name-ideas/coffee-shop/", "#cafe #coffeeshop #foodbusiness #bakery #businessname #smallbusiness #blackfriday #uaefood"),
 ("2026-11-27", None, "A .com for less than lunch", "Today is Black Friday",
  "A .com for less than lunch.", "Real brandable names from $15, first year included. Ends Monday.",
  "It's Black Friday. A brand name with the .com costs less than lunch this week: from $15, first year of registration included, and we register it for you the same day.",
  "/", "#blackfriday #blackfriday2026 #domainnames #dotcom #startup #businessname #sidehustle #entrepreneur"),
 ("2026-11-28", ["Fashion", "Health"], "Names for beauty, fashion & wellness", "Black Friday · beauty & fashion",
  "Launching a beauty or fashion brand?", "Names that look good on a label, with the domain free.",
  "Launching a skincare line, a boutique or a wellness studio? These names look good on a label and a bio link, and they're on sale until Monday.",
  "/business-name-ideas/skincare-brand/", "#beautybrand #fashionbrand #skincare #boutique #wellness #businessname #blackfriday #smallbusinessuae"),
 ("2026-11-29", ["AI", "SaaS"], "Names for your AI or software startup", "Weekend sale · startups",
  "Building an AI startup?", "Short, brandable .com and .co names, up to 30% off until tomorrow.",
  "Building an AI tool or a software startup? Short brand names with the .com or .co free, on sale until Cyber Monday.",
  "/business-name-ideas/ai-startup/", "#aistartup #saas #startup #founder #techstartup #businessname #domainnames #blackfriday"),
 ("2026-11-30", None, "Last day: Cyber Monday names", "Cyber Monday · last day",
  "Last day for sale prices.", "Prices go back tonight. Up to 30% off, first year included.",
  "Cyber Monday is the last day. Black Friday prices on every brandable name end tonight, so if you've had one in mind, today is the day.",
  "/", "#cybermonday #lastchance #domainnames #businessname #startup #smallbusiness #entrepreneur #uae"),
]

def pick(inv, cats, used, n=5, max_now=None):
    gone = lines("sold.txt") | lines("taken.txt")
    ok = [x for x in inv if re.fullmatch(r"[a-z]+\.(com|co)", x["d"]) and x["d"] not in gone and x["d"] not in PREMIUM
          and x["d"] not in used and (cats is None or x["c"] in cats) and x.get("s")   # curated two-real-word names
          and SALE.price(x["d"], x["p"]) < x["p"] and len(x["d"].split(".")[0]) <= 10]
    if max_now: ok = [x for x in ok if SALE.price(x["d"], x["p"]) <= max_now]
    ok.sort(key=lambda x: (x["d"].split(".")[1] != "com", len(x["d"]), x["d"]))
    out, seen_cat = [], {}
    for x in ok:                                   # spread across categories on mixed days
        if cats is None and seen_cat.get(x["c"], 0) >= 1: continue
        lab = x["d"].split(".")[0]
        if any(lab[:4] == o["d"][:4] or lab[-3:] == o["d"].split(".")[0][-3:] for o in out): continue   # no repeated word parts
        out.append(x); seen_cat[x["c"]] = seen_cat.get(x["c"], 0) + 1
        if len(out) == n: break
    return out

def main():
    inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
    used, md = set(), ["# Black Friday / Cyber Monday posts (24-30 Nov 2026)\n",
                       "Each day: a 2-image carousel (1.jpg cover, 2.jpg names) for Instagram, and the same 2.jpg as a Pinterest pin.",
                       f"Images are published at {SITE}/social/blackfriday/<date>/1.jpg and 2.jpg after the next site build.\n"]
    for date, cats, title, kicker, head, sub, hook, page, tags in DAYS:
        day = datetime.date.fromisoformat(date)
        names = pick(inv, cats, used, max_now=(24 if date == "2026-11-27" else None))
        used |= {x["d"] for x in names}
        folder = os.path.join(OUT, date); os.makedirs(folder, exist_ok=True)
        S.statement(os.path.join(folder, "1.jpg"), kicker, head, sub)
        S.names(os.path.join(folder, "2.jpg"), f"Black Friday prices · until 30 Nov", title,
                [(x["d"], SALE.price(x["d"], x["p"], day)) for x in names], "Was " + ", ".join(f"${x['p']}" for x in names) + ". First year included. Link in bio.")
        lst = "\n".join(f"• {x['d']}: ${SALE.price(x['d'], x['p'], day)} (was ${x['p']})" for x in names)
        link = f"{SITE}{page}?utm_source=instagram&utm_medium=social&utm_campaign=blackfriday"
        pin = f"{SITE}{page}?utm_source=pinterest&utm_medium=social&utm_campaign=blackfriday"
        md += [f"## {day.strftime('%a %-d %b')}: {title}\n",
               f"Images: social/blackfriday/{date}/1.jpg, 2.jpg  \nLink in bio / story link: {link}\n",
               "**Instagram caption**\n", f"{hook}\n\n{lst}\n\nTap the link in bio to claim yours. We register it in your name, usually the same day.\n\n{tags}\n",
               "**Story:** post 2.jpg with a link sticker to the link above, text: \"Black Friday prices until Monday\".\n",
               "**Pinterest pin** (image 2.jpg, board: Business name ideas)  ",
               f"Title: {title} | Black Friday domain sale  ",
               f"Description: {hook} {', '.join(x['d'] for x in names)}.  ",
               f"Link: {pin}\n"]
        print(date, ", ".join(f"{x['d']} ${SALE.price(x['d'], x['p'], day)}" for x in names))
    open(os.path.join(OUT, "captions.md"), "w").write("\n".join(md))

if __name__ == "__main__":
    main()
