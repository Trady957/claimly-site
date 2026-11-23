"""Christmas and New Year 2026-27 posts for Instagram and Pinterest, aimed at US buyers.

For each post date writes social/holidays/<date>/1.jpg (cover) and 2.jpg (5 real shop names
at that day's sale price, see scripts/sale.py), and social/holidays/captions.md with captions,
US hashtags, a suggested US posting time and Pinterest pin text.
Run: python3 scripts/content_holidays.py
"""
import datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
import sale as SALE
from daily_social import PREMIUM
import seo_content as SC
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "holidays")
SITE = "https://claimly.ae"
US = "#smallbusiness #smallbusinessowner #entrepreneur #startup #businessname #domainname #shopsmall #usa"

# date, shop categories (None = mix), names-slide title, cover kicker, cover headline, cover sub, caption hook, page, extra hashtags
POSTS = [
 ("2026-12-01", None, "Christmas sale: names at half price", "Christmas sale starts",
  "Brand names, half price.", "Up to 50% off every name through 15 Jan. First year included.",
  "Our Christmas sale starts today: brandable names with the .com are up to 50% off, and the price includes the first year of registration.",
  "/", "#christmassale #holidaysale"),
 ("2026-12-03", ["E-commerce", "Fashion", "Local"], "Names for your Etsy shop", "Christmas sale · Etsy sellers",
  "Selling on Etsy this Christmas?", "Get the .com for your shop name before someone else does.",
  "Busy Etsy season? Lock in the .com for your shop name now, so you can move to your own website in the new year. These are up to 50% off.",
  "/business-name-ideas/etsy-shop/", "#etsyseller #etsyshop #handmade #makersgonnamake"),
 ("2026-12-05", None, "Gift a business name", "The gift for a future founder",
  "Know someone starting a business?", "Give them their name and .com. Up to 50% off.",
  "Got a friend, sister or partner who keeps talking about starting a business? Give them the name and the .com this Christmas. We register it in their name.",
  "/", "#giftideas #giftsforher #giftsforhim #christmasgifts"),
 ("2026-12-08", ["E-commerce", "Health", "Pets"], "Names for your Shopify store", "Christmas sale · online stores",
  "Opening a Shopify store?", "Short .com names shoppers trust at checkout.",
  "Starting a Shopify store for 2027? A short .com builds trust at checkout and on ads. These names are free to register today, up to 50% off.",
  "/business-name-ideas/shopify-store/", "#shopify #shopifystore #ecommerce #onlinebusiness"),
 ("2026-12-10", ["Local", "Finance", "Marketing"], "Names for your LLC", "Christmas sale · forming an LLC",
  "Filing an LLC in January?", "Pick the name and the .com first.",
  "Planning to file your LLC in January? Choose a name that's free as a .com first, then check your state's registry. Up to 50% off.",
  "/business-name-ideas/llc/", "#llc #businessowner #startabusiness #womeninbusiness"),
 ("2026-12-12", ["Food"], "Names for your bakery or food brand", "Christmas sale · food",
  "Baking for the holidays?", "Turn the side gig into a brand.",
  "Selling cookies, cakes or candy this holiday season? Turn it into a brand with a name people remember and a .com to order from.",
  "/business-name-ideas/bakery/", "#homebaker #cottagebakery #foodbusiness #holidaybaking"),
 ("2026-12-15", ["Local", "Creator", "Marketing"], "Names for your side hustle", "Christmas sale · side hustles",
  "Your side hustle needs a name.", "Short, serious names with the .com free.",
  "Side hustle getting real? Give it a name you can grow into and an email on your own .com. Up to 50% off.",
  "/business-name-ideas/side-hustle/", "#sidehustle #sidehustleideas #workfromhome #extraincome"),
 ("2026-12-17", ["Health", "Fashion"], "Names for beauty & wellness brands", "Christmas sale · beauty",
  "Launching a beauty brand in 2027?", "Names that look good on a label.",
  "Launching skincare, candles or a wellness brand next year? These names look good on a label, and the .com is free today.",
  "/business-name-ideas/skincare-brand/", "#beautybrand #skincarebrand #candlebusiness #wellness"),
 ("2026-12-19", None, "Last-minute gift: a business name", "Last-minute gift idea",
  "No shipping needed.", "A business name and .com, registered the same day.",
  "Need a last-minute gift? A business name doesn't need shipping. Pick one, and we register the .com in their name, usually the same day.",
  "/", "#lastminutegifts #christmasgifts #giftideas #christmas2026"),
 ("2026-12-22", ["AI", "SaaS"], "Names for your 2027 startup", "Christmas sale · startups",
  "Building something in 2027?", "Short .com names for AI and software startups.",
  "Spending the holidays on your startup idea? Grab a short, brandable .com for it now. Up to 50% off.",
  "/business-name-ideas/ai-startup/", "#aistartup #saas #founder #buildinpublic"),
 ("2026-12-24", None, "A gift you can still give tonight", "Christmas Eve",
  "Still need a gift?", "A business name, registered in their name. Merry Christmas from Claimly.",
  "Merry Christmas Eve! Still missing a gift for someone who wants to start a business? Order tonight, tick 'This is a gift', and we'll email you a printable gift card with their domain.",
  "/", "#christmaseve #merrychristmas #christmassale"),
 ("2026-12-26", None, "New year, new business", "New Year sale",
  "New year, new business.", "Up to 50% off every name until January 15.",
  "If 2027 is the year you start the business, start with the name: up to 50% off until January 15.",
  "/", "#newyearnewbusiness #2027goals #newyear"),
 ("2026-12-29", ["E-commerce", "Fashion", "Local"], "Names for your online store", "New Year sale · online stores",
  "Starting an online store in 2027?", "Your brand name and .com, half price.",
  "Starting an online store in 2027? Get a brand name with the .com free, up to 50% off until January 15.",
  "/business-name-ideas/online-store/", "#onlinestore #ecommerce #shopify #etsy"),
 ("2027-01-01", None, "Names to start 2027 with", "Happy New Year",
  "This is the year.", "Start with the name. Up to 50% off until January 15.",
  "Happy New Year! If starting a business is on your resolution list, the name is step one. These are free to register today.",
  "/", "#happynewyear #newyearsresolution #2027goals #startabusiness"),
 ("2027-01-05", ["Local", "Finance", "Marketing"], "Names for your LLC", "New Year sale · LLC",
  "Filing your LLC this month?", "Check the .com before you file.",
  "Filing your LLC this month? Pick a name that's free as a .com first, then check your state's business registry. Up to 50% off until January 15.",
  "/business-name-ideas/llc/", "#llc #startabusiness #businessowner #2027goals"),
 ("2027-01-08", ["Local", "Creator", "Marketing"], "Names for your side hustle", "New Year sale · side hustles",
  "2027 side hustle?", "Give it a real name and a real .com.",
  "Making your side hustle official in 2027? Give it a real name and an email on your own .com, at New Year prices.",
  "/business-name-ideas/side-hustle/", "#sidehustle #extraincome #newyearnewme"),
 ("2027-01-12", ["Health"], "Names for fitness & wellness", "New Year sale · fitness",
  "Launching a fitness brand?", "January is the month people look for one.",
  "January is when people search for a coach, a gym or a wellness brand. Launch yours with a name and a .com that's easy to find.",
  "/business-name-ideas/fitness/", "#fitnessbusiness #personaltrainer #wellness #newyearfitness"),
 ("2027-01-14", None, "Last days of the New Year sale", "Ends tomorrow",
  "Half price ends tomorrow.", "The New Year sale ends January 15.",
  "The New Year sale ends tomorrow, January 15. After that, prices go back to normal, so if a name caught your eye, now is the time.",
  "/", "#lastchance #newyearsale #startabusiness"),
]

def lines(f):
    p = os.path.join(ROOT, "data", f)
    return {l.strip().lower() for l in open(p) if l.strip() and not l.startswith("#")} if os.path.exists(p) else set()

PARTS = Counter()                       # word parts already used across all posts

def parts(lab):
    return {lab[:4], lab[-4:]}

def pick(inv, cats, used, day, kws=(), n=5):
    gone = lines("sold.txt") | lines("taken.txt")
    ok = [x for x in inv if re.fullmatch(r"[a-z]+\.(com|co)", x["d"]) and x["d"] not in gone and x["d"] not in PREMIUM
          and x["d"] not in used and (cats is None or x["c"] in cats) and x.get("s")
          and SALE.price(x["d"], x["p"], day) < x["p"] and len(x["d"].split(".")[0]) <= 10]
    ok.sort(key=lambda x: (not any(k in x["d"].split(".")[0] for k in kws), x["d"].split(".")[1] != "com",
                           sum(PARTS[p] for p in parts(x["d"].split(".")[0])), len(x["d"]), x["d"]))
    out, seen_cat = [], {}
    for x in ok:
        if cats is None and seen_cat.get(x["c"], 0) >= 1: continue
        lab = x["d"].split(".")[0]
        if any(lab[:4] == o["d"][:4] or lab[-3:] == o["d"].split(".")[0][-3:] for o in out): continue
        if any(PARTS[p] >= 2 for p in parts(lab)): continue
        out.append(x); seen_cat[x["c"]] = seen_cat.get(x["c"], 0) + 1
        if len(out) == n: break
    return out

def main():
    inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
    used = set()
    bf = os.path.join(ROOT, "social", "blackfriday", "captions.md")       # don't repeat Black Friday names
    if os.path.exists(bf):
        used |= set(re.findall(r"• ([a-z]+\.(?:com|co))", open(bf).read()))
    ideas = {"/business-name-ideas/" + t[0] + "/": t[4] for t in SC.IDEAS}
    md = ["# Christmas & New Year posts (1 Dec 2026 - 14 Jan 2027), US audience\n",
          "Each post: a 2-image carousel (1.jpg cover, 2.jpg names) for Instagram, and 2.jpg as a Pinterest pin.",
          "Post at 12:30 pm Eastern (9:30 am Pacific, 9:30 pm Dubai), when US shoppers are online. Pins can go any time.",
          f"Images are published at {SITE}/social/holidays/<date>/1.jpg and 2.jpg after the next site build.",
          "Names are checked daily; if one sells before its post date, regenerate with: python3 scripts/content_holidays.py\n"]
    for date, cats, title, kicker, head, sub, hook, page, tags in POSTS:
        day = datetime.date.fromisoformat(date)
        s = SALE.current(day)
        names = pick(inv, cats, used, day, ideas.get(page, ()))
        used |= {x["d"] for x in names}
        for x in names: PARTS.update(parts(x["d"].split(".")[0]))
        folder = os.path.join(OUT, date); os.makedirs(folder, exist_ok=True)
        S.statement(os.path.join(folder, "1.jpg"), kicker, head, sub)
        S.names(os.path.join(folder, "2.jpg"), f"{s[2]} · {s[4]}", title,
                [(x["d"], SALE.price(x["d"], x["p"], day)) for x in names],
                "Was " + ", ".join(f"${x['p']}" for x in names) + ". First year included. Link in bio.")
        lst = "\n".join(f"• {x['d']}: ${SALE.price(x['d'], x['p'], day)} (was ${x['p']})" for x in names)
        camp = "christmas" if s[2].startswith("Christmas") else "newyear"
        link = f"{SITE}{page}?utm_source=instagram&utm_medium=social&utm_campaign={camp}"
        pin = f"{SITE}{page}?utm_source=pinterest&utm_medium=social&utm_campaign={camp}"
        md += [f"## {day.strftime('%a %b %-d')}: {title}\n",
               f"Images: social/holidays/{date}/1.jpg, 2.jpg  \nLink in bio / story link: {link}\n",
               "**Instagram caption**\n",
               f"{hook}\n\n{lst}\n\nTap the link in bio to claim yours. We register it in your name, usually the same day. Prices in USD, first year included.\n\n{tags} {US}\n",
               "**Pinterest pin** (image 2.jpg, board: Business name ideas)  ",
               f"Title: {title} | {s[2]}, up to {s[3]}% off  ",
               f"Description: {hook} {', '.join(x['d'] for x in names)}.  ",
               f"Link: {pin}\n"]
        print(date, ", ".join(f"{x['d']} ${SALE.price(x['d'], x['p'], day)}" for x in names))
    open(os.path.join(OUT, "captions.md"), "w").write("\n".join(md))

if __name__ == "__main__":
    main()
