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
    fp = S.font("Black", 64); pt = f"${price}"; pw = d.textlength(pt, font=fp)
    d.rounded_rectangle(((PW - pw) / 2 - 50, 920, (PW + pw) / 2 + 50, 1030), 55, fill=S.RED)
    d.text(((PW - pw) / 2, 935), pt, font=fp, fill="#FFFFFF")
    S.block(d, 80, 1090, "First year of registration included. We register it for you, usually the same day.",
            S.font("Medium", 36, False), S.MUTED, PW - 160, 1.35)
    S.wordmark(d, 80, PH - 130, S.INK)
    fs = S.font("SemiBold", 32, False)
    d.text((PW - 80 - d.textlength("claimly.ae", font=fs), PH - 117), "claimly.ae", font=fs, fill=S.INK)
    im.save(path, "JPEG", quality=74, optimize=True)

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
                            f"${price}, including the first year of registration. Claimly registers it for you and hands it "
                            f"over, usually the same day, with a full refund if it can't be delivered."),
            "link": f"{SITE}/d/{dom}/?utm_source=pinterest&utm_medium=catalog",
            "image_link": f"{SITE}/pins/{dom}.jpg",
            "price": f"{price:.2f} USD",
            "availability": "in stock",
            "condition": "new",
            "brand": "Claimly",
            "product_type": f"Domain names > {cat}",
            "google_product_category": "Software > Digital Goods & Currency",
        })
    with open(os.path.join(DIST, "catalog", "pinterest.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    print(f"Pinterest catalog: {len(rows)} products ({datetime.date.today()})")

if __name__ == "__main__":
    main()
