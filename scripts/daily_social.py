"""Make today's Instagram "names of the day" image from the freshest shop names.

Writes social/daily/<date>.jpg and social/daily/<date>.json (plus latest.json).
The images are published at https://claimly.ae/social/daily/... and a daily
scheduled task turns them into Metricool drafts.
"""
import datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
import names as G

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "daily")
TODAY = datetime.date.today()

PHRASE = {"Finance": "finance or fintech brand", "AI": "AI or tech startup", "SaaS": "software startup",
          "E-commerce": "online store", "Local": "local business", "Health": "health or wellness brand",
          "Creator": "creator brand", "Education": "education business", "Travel": "travel brand",
          "Real estate": "real estate business", "Food": "café or food brand", "Pets": "pet business",
          "Crypto": "crypto project", "Marketing": "marketing agency", "Legal": "law or consulting firm",
          "Fashion": "fashion label", "Gaming": "gaming studio", "Green": "eco brand"}
WORDS = sorted({w for ws in G.ROOTS.values() for w in ws} | set(G.PREFIX) | set(G.SUFFIX) | set(G.TECH), key=len, reverse=True)
WORDS = [w.lower() for w in WORDS if len(w) >= 2]
PREMIUM = {"linenkit.com", "reellens.com", "woofyard.com", "meowwise.com", "platefox.com", "roastfox.com",
           "manorkit.com", "coveplot.com", "roverwag.com", "fernpure.com"}

def two_words(label):
    """True when the name is made of two known words (e.g. goodroast, mintloop)."""
    for a in WORDS:
        if label.startswith(a) and len(a) >= 3 and label[len(a):] in WORDS:
            return True
    return False

def main():
    inv = json.load(open(os.path.join(ROOT, "data", "inventory.json")))
    sold = set(open(os.path.join(ROOT, "data", "sold.txt")).read().split())
    used = set()
    for f in os.listdir(OUT) if os.path.isdir(OUT) else []:
        if f.endswith(".json") and f != "latest.json":
            used |= {n["domain"] for n in json.load(open(os.path.join(OUT, f))).get("names", [])}
    ok = lambda x: (re.fullmatch(r"[a-z]+\.(com|co)", x["d"]) and x["d"] not in PREMIUM and x["d"] not in sold
                    and x["d"] not in used and x["p"] <= 60 and two_words(x["d"].split(".")[0]))
    pool = [x for x in inv if ok(x)]
    fresh = [x for x in pool if x.get("a", "") >= (TODAY - datetime.timedelta(days=7)).isoformat()] or pool
    by = {}
    for x in fresh: by.setdefault(x["c"], []).append(x)
    cats = [c for c in G.CATS if len(by.get(c, [])) >= 5]
    if not cats:
        print("Not enough names for today's post"); return
    cat = cats[TODAY.toordinal() % len(cats)]          # rotate categories day by day
    pick = sorted(by[cat], key=lambda x: (len(x["d"]), x["d"]))[:5]
    os.makedirs(OUT, exist_ok=True)
    stem = TODAY.isoformat()
    title = f"Names for your {PHRASE.get(cat, cat.lower() + ' brand')}"
    S.names(os.path.join(OUT, stem + ".jpg"), f"Available today · {cat}", title,
            [(x["d"], x["p"]) for x in pick], "Prices include the first year. Link in bio.")
    meta = {"date": stem, "category": cat, "title": title,
            "image_url": f"https://claimly.ae/social/daily/{stem}.jpg",
            "names": [{"domain": x["d"], "price": x["p"]} for x in pick]}
    for name in (stem + ".json", "latest.json"):
        json.dump(meta, open(os.path.join(OUT, name), "w"), indent=1, ensure_ascii=False)
    print("Social post:", cat, ", ".join(x["d"] for x in pick))

if __name__ == "__main__":
    main()
