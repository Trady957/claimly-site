#!/usr/bin/env python3
"""daily_update.py — runs every morning in GitHub Actions.

1. Removes sold names (data/sold.txt) and names someone else registered.
2. Re-checks the oldest-checked names in the shop and drops any that got registered.
3. Generates fresh brandable candidates, checks each with RDAP (the official
   registry lookup) and adds up to --add available names (default 25).
4. Writes data/new_urls.txt for the search-engine ping (IndexNow).

Usage:  python3 scripts/daily_update.py [--add 25] [--recheck 60]
"""
import json, os, sys, random, math, datetime, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import names as G  # the original generator (word lists, pricing rules)

TODAY = datetime.date.today().isoformat()
ARGS = sys.argv[1:]
def arg(name, default):
    return int(ARGS[ARGS.index(name) + 1]) if name in ARGS else default
ADD, RECHECK = arg("--add", 25), arg("--recheck", 60)
SITE = "https://claimly.ae"
NO_RDAP = {"ai"}  # no reliable public RDAP: never auto-added

def rdap(domain):
    if domain.rsplit(".", 1)[1] in NO_RDAP:
        return "uncertain"
    req = urllib.request.Request("https://rdap.org/domain/" + domain,
        headers={"User-Agent": "claimly-daily/1.0", "Accept": "application/rdap+json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return "taken" if r.status == 200 else "uncertain"
        except urllib.error.HTTPError as e:
            if e.code == 404: return "available"
            if e.code == 429: time.sleep(3 * (attempt + 1)); continue
            return "uncertain"
        except Exception:
            time.sleep(2 * (attempt + 1))
    return "uncertain"

def check_all(domains, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(zip(domains, ex.map(rdap, domains)))

def lines(f):
    p = os.path.join(DATA, f)
    return [l.strip().lower() for l in open(p) if l.strip() and not l.startswith("#")] if os.path.exists(p) else []

def append(f, items):
    if items:
        with open(os.path.join(DATA, f), "a") as fh:
            fh.write("".join(i + "\n" for i in items))

ROOTWORDS = {w for ws in G.ROOTS.values() for w in ws} | set(G.PREFIX) | set(G.SUFFIX) | set(G.TECH)
def good(n):
    """Keep names that are short and sayable: real-word blends up to 11 letters, coined names up to 7."""
    n = n.lower()
    if len(n) > 11: return False
    has_word = any(w in n for w in ROOTWORDS if len(w) >= 3)
    return has_word or len(n) <= 7

def shop_price(name, cat, ext):
    p, tier = G.price_for(name, cat, ext)          # generator scale ($30–150)
    return max(15, min(75, math.ceil(p / 10) * 5)), tier   # Claimly scale ($15–75)

def main():
    inv = json.load(open(os.path.join(DATA, "inventory.json")))
    sold, taken = set(lines("sold.txt")), set(lines("taken.txt"))
    seen = set(lines("seen.txt"))
    log = []

    # 1. drop sold / taken
    before = len(inv)
    inv = [x for x in inv if x["d"] not in sold and x["d"] not in taken]
    if before - len(inv): log.append(f"Removed {before - len(inv)} sold/taken names")

    # 2. re-check the oldest-checked names
    oldest = sorted(inv, key=lambda x: x.get("k", ""))[:RECHECK]
    res = check_all([x["d"] for x in oldest])
    gone = [d for d, s in res.items() if s == "taken"]
    for x in oldest:
        if res[x["d"]] == "available": x["k"] = TODAY
    inv = [x for x in inv if x["d"] not in gone]
    append("taken.txt", gone)
    log.append(f"Re-checked {len(oldest)} names, {len(gone)} now registered elsewhere: {', '.join(gone) or 'none'}")

    # 3. new names, spread across categories (fewest names first)
    random.seed(TODAY)
    counts = {c: 0 for c in G.CATS}
    for x in inv: counts[x["c"]] = counts.get(x["c"], 0) + 1
    order = sorted(G.CATS, key=lambda c: counts[c])
    cands = []
    for cat in order:
        for n in G.gen_for_cat(cat, 40):
            ext = G.ext_for(cat, n)
            d = f"{n.lower()}.{ext}"
            if d not in seen and ext not in NO_RDAP and ext in G.EXTS and good(n):
                cands.append((cat, n, ext, d))
    random.shuffle(cands)
    # round-robin by category so one category can't take every slot
    by = {}
    for c in cands: by.setdefault(c[0], []).append(c)
    queue = []
    while any(by.values()):
        for cat in order:
            if by.get(cat): queue.append(by[cat].pop())
    added, checked = [], []
    for i in range(0, len(queue), 20):
        if len(added) >= ADD: break
        batch = queue[i:i + 20]
        res = check_all([b[3] for b in batch])
        for cat, n, ext, d in batch:
            checked.append(d)
            if res[d] == "available" and len(added) < ADD:
                p, tier = shop_price(n, cat, ext)
                added.append({"d": d, "p": p, "c": cat, "t": tier, "a": TODAY, "k": TODAY})
    append("seen.txt", checked)
    inv = added + inv
    log.append(f"Checked {len(checked)} new candidates, added {len(added)}: " + ", ".join(f"{a['d']} (${a['p']})" for a in added))

    json.dump(inv, open(os.path.join(DATA, "inventory.json"), "w"), indent=0, separators=(",", ":"))
    urls = [f"{SITE}/", f"{SITE}/new/", f"{SITE}/sitemap.xml"] + [f"{SITE}/d/{a['d']}/" for a in added] + \
           sorted({f"{SITE}/domains/{a['c'].lower().replace(' ', '-')}/" for a in added})
    open(os.path.join(DATA, "new_urls.txt"), "w").write("\n".join(urls) + "\n")
    summary = f"## Claimly daily update {TODAY}\n\nShop now has **{len(inv)}** names.\n\n" + "\n".join(f"- {l}" for l in log) + "\n"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(summary)

if __name__ == "__main__":
    main()
