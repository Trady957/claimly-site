"""Pinterest product catalog for Claimly.

Writes, inside dist/ (run after build.py):
  catalog/pinterest.csv     one row per domain (Pinterest data-source format)
  pins/<domain>.jpg         one 1000x1500 branded image per domain
Pinterest re-reads https://claimly.ae/catalog/pinterest.csv daily, so sold or
taken names drop out automatically.
"""
import csv, datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import social as S
import daily_social as DS
import sale as SALE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SITE = "https://claimly.ae"
MAX_ITEMS = 1500
PW, PH = 1000, 1500
EXTS = ("com", "co", "io", "app", "studio", "shop", "store", "tech", "dev", "xyz")

def lines(name):
    p = os.path.join(ROOT, "data", name)
    return set(open(p).read().split()) if os.path.exists(p) else set()

def fit(d, text, weight, maxw, start, minimum=60):
    size = start
    while size > minimum and d.textlength(text, font=S.font(weight, size)) > maxw:
        size -= 4
    return S.font(weight, size)

def pin_image(path, domain, price, cat):
    im = Image.new("RGB", (PW, PH), S.BONE); d = ImageDraw.Draw(im)
    d.ellipse((560, -300, 1300, 440), fill="#F7D9D6")
    d.text((80, 120), f"AVAILABLE TODAY · {cat.upper()}", font=S.font("Bold", 30, False), fill=S.RED)
    phrase = DS.PHRASE.get(cat, cat.lower() + " brand")
    S.block(d, 80, 190, f"A name for your {phrase}", S.font("Black", 70), S.INK, PW - 160, 1.08)
    # the domain, as big as fits
    d.rounded_rectangle((60, 560, PW - 60, 860), 36, fill="#FFFFFF", outline="#E2DFDB", width=3)
    f = fit(d, domain, "Black", PW - 200, 150)
    tw = d.textlength(domain, font=f)
    d.text(((PW - tw) / 2, 710 - f.size * 0.62), domain, font=f, fill=S.INK)
    # price
    now = SALE.price(domain, price)
    fp = S.font("Black", 64); pt = f"${now}"; pw = d.textlength(pt, font=fp)
    d.rounded_rectangle(((PW - pw) / 2 - 50, 920, (PW + pw) / 2 + 50, 1030), 55, fill=S.RED)
    d.text(((PW - pw) / 2, 935), pt, font=fp, fill="#FFFFFF")
    if now != price:   # sale: old price struck through and a badge
        fo = S.font("Bold", 44, False); ot = f"${price}"; ow = d.textlength(ot, font=fo)
        ox = (PW + pw) / 2 + 80
        d.text((ox, 950), ot, font=fo, fill=S.MUTED); d.line((ox - 4, 978, ox + ow + 4, 978), fill=S.MUTED, width=4)
        bt = f"{SALE.SALE_NAME.upper()} PRICE"; fb = S.font("Bold", 30, False); bw = d.textlength(bt, font=fb)
        d.rounded_rectangle((80, 470, 80 + bw + 48, 528), 29, fill=S.INK); d.text((104, 482), bt, font=fb, fill="#FFFFFF")
    S.block(d, 80, 1090, "First year of registration included. We register it for you, usually the same day.",
            S.font("Medium", 36, False), S.MUTED, PW - 160, 1.35)
    S.wordmark(d, 80, PH - 130, S.INK)
    fs = S.font("SemiBold", 32, False)
    d.text((PW - 80 - d.textlength("claimly.ae", font=fs), PH - 117), "claimly.ae", font=fs, fill=S.INK)
    im.save(path, "JPEG", quality=74, optimize=True)

# Naming packages as Pinterest products (same prices as /name-my-business/, see scripts/sale.py)
PKG_PINS = [
    ("naming_starter", "Business naming service: 10 names + your .com", "Stuck on a business name?", "10 names made for your business. Your .com registered.", "10 brandable names made for your business, each with the .com checked and free, delivered in 48 hours. Pick one and we register the domain for you, first year included."),
    ("naming_quick", "Quick business name: 3 names in 24 hours", "Need a name by tomorrow?", "3 names in 24 hours. Your .com registered.", "3 names made for your business in 24 hours, each with the .com checked. We register your favourite, first year included."),
    ("naming_brand", "Brand kit: name, domain, logo, colors", "Starting from zero?", "Name, .com, logo concept, colors and fonts.", "10 names, your domain registered, a wordmark logo concept, color palette, font pairing and taglines, ready in 3 days."),
    ("naming_shield", "Business name + .com, .co and .net", "Found the name? Protect it.", "Your name as .com, .co and .net.", "10 names made for your business, then your favourite registered as .com, .co and .net so no one can copy it, with a social handle check."),
    ("naming_duo", "Naming gift for two businesses", "Starting up with a friend?", "Two businesses named. Two domains.", "Two naming packages in one: 10 names and a registered domain for each business. A great gift for a friend who is starting up."),
]

def pkg_image(path, kicker, head, sub, now, was):
    im = Image.new("RGB", (PW, PH), S.INK); d = ImageDraw.Draw(im)
    d.rectangle((80, 120, 200, 132), fill=S.RED)
    d.text((80, 170), kicker.upper(), font=S.font("Bold", 30, False), fill="#BDB8B5")
    y = S.block(d, 80, 300, head, S.font("Black", 96), S.WHITE, PW - 160, 1.04)
    y = S.block(d, 80, y + 40, sub, S.font("Medium", 44, False), "#DAD6D3", PW - 160, 1.3)
    fp = S.font("Black", 80); pt = f"${now}"; pw = d.textlength(pt, font=fp)
    d.rounded_rectangle((80, 1060, 80 + pw + 80, 1190), 65, fill=S.RED); d.text((120, 1080), pt, font=fp, fill=S.WHITE)
    if was != now:
        fo = S.font("Bold", 48, False); ot = f"${was}"; ow = d.textlength(ot, font=fo)
        ox = 80 + pw + 120; d.text((ox, 1100), ot, font=fo, fill="#8C8784"); d.line((ox - 4, 1130, ox + ow + 4, 1130), fill="#8C8784", width=4)
        d.text((80, 1000), "HOLIDAY PRICE · GIFT IT", font=S.font("Bold", 30, False), fill="#F7D9D6")
    S.wordmark(d, 80, PH - 130, S.WHITE, dot=S.RED)
    fs = S.font("SemiBold", 32, False)
    d.text((PW - 80 - d.textlength("claimly.ae", font=fs), PH - 117), "claimly.ae", font=fs, fill=S.WHITE)
    im.save(path, "JPEG", quality=80, optimize=True)

def pkg_rows():
    rows = []
    for key, title, kicker, sub, desc in PKG_PINS:
        now, was = SALE.pkg_price(key), SALE.PKG_REG[key]
        pkg_image(os.path.join(DIST, "pins", key + ".jpg"), kicker, title.split(":")[0], sub, now, was)
        rows.append({"id": key, "title": title,
                     "description": desc + (f" Holiday price ${now} (normally ${was}) until 15 Jan. Can be given as a gift." if now != was else ""),
                     "link": f"{SITE}/name-my-business/?utm_source=pinterest&utm_medium=catalog&utm_content={key}",
                     "image_link": f"{SITE}/pins/{key}.jpg", "price": f"{was:.2f} USD",
                     "sale_price": f"{now:.2f} USD" if now != was else "", "availability": "in stock", "condition": "new",
                     "brand": "Claimly", "product_type": "Business services > Naming", "google_product_category": "Software > Digital Goods & Currency"})
    return rows

def main():
    inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
    gone = lines("sold.txt") | lines("taken.txt")
    items = [x for x in inv if x["d"] not in gone and x["d"] not in DS.PREMIUM
             and re.fullmatch(r"[a-z]+\.(%s)" % "|".join(EXTS), x["d"]) and DS.two_words(x["d"].split(".")[0])]
    items.sort(key=lambda x: x.get("a", ""), reverse=True)        # newest first
    items = items[:MAX_ITEMS]
    os.makedirs(os.path.join(DIST, "pins"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "catalog"), exist_ok=True)
    rows = []
    for x in items:
        dom, price, cat = x["d"], x["p"], x["c"]
        pin_image(os.path.join(DIST, "pins", dom + ".jpg"), dom, price, cat)
        phrase = DS.PHRASE.get(cat, cat.lower() + " brand")
        rows.append({
            "id": dom,
            "title": f"{dom} domain name",
            "description": (f"{dom} is a short, brandable domain name for {'an' if phrase[0] in 'aeiou' else 'a'} {phrase}. Available to register today for "
                            f"${SALE.price(dom, price)}{f' ({SALE.SALE_NAME} price, was ${price})' if SALE.price(dom, price) != price else ''}, including the first year of registration. Claimly registers it for you and hands it "
                            f"over, usually the same day, with a full refund if it can't be delivered."),
            "link": f"{SITE}/d/{dom}/?utm_source=pinterest&utm_medium=catalog",
            "image_link": f"{SITE}/pins/{dom}.jpg",
            "price": f"{price:.2f} USD",
            # domain sale (same rule as build.py, see scripts/sale.py)
            "sale_price": (f"{SALE.price(dom, price):.2f} USD" if SALE.price(dom, price) != price else ""),
            "availability": "in stock",
            "condition": "new",
            "brand": "Claimly",
            "product_type": f"Domain names > {cat}",
            "google_product_category": "Software > Digital Goods & Currency",
        })
    rows = pkg_rows() + rows                  # naming packages first
    with open(os.path.join(DIST, "catalog", "pinterest.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    print(f"Pinterest catalog: {len(rows)} products ({datetime.date.today()})")

if __name__ == "__main__":
    main()
