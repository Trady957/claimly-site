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

SB_URL = "https://bbjreybvwqdzsfbcunlm.supabase.co"
SB_KEY = "sb_publishable_JeEACKfWsGaFXTat1B-WVw_uWkUR8ZK"   # public, insert-only

def report_stats(row):
    """Send today's numbers to the morning dashboard (Supabase table claimly_daily_stats)."""
    if os.environ.get("CLAIMLY_NO_STATS"): return
    try:
        req = urllib.request.Request(SB_URL + "/rest/v1/claimly_daily_stats", data=json.dumps(row).encode(),
            headers={"apikey": SB_KEY, "Content-Type": "application/json", "Prefer": "return=minimal"}, method="POST")
        urllib.request.urlopen(req, timeout=20)
        print("Stats sent to dashboard")
    except Exception as e:
        print("Could not send stats (not fatal):", e)

def main():
    inv = json.load(open(os.path.join(DATA, "inventory.json")))
    sold, taken = set(lines("sold.txt")), set(lines("taken.txt"))
    seen = set(lines("seen.txt"))
    log = []

    # 1. drop sold / taken
    before = len(inv)
    inv = [x for x in inv if x["d"] not in sold and x["d"] not in taken]
    removed_sold = before - len(inv)
    if removed_sold: log.append(f"Removed {removed_sold} sold/taken names")

    # 2. re-check the oldest-checked names
    oldest = sorted(inv, key=lambda x: x.get("k", ""))[:RECHECK]
    res = check_all([x["d"] for x in oldest])
    gone = [d for d, s in res.items() if s == "taken"]
    for x in oldest:
        if res[x["d"]] == "available": x["k"] = TODAY
    inv = [x for x in inv if x["d"] not in gone]
    append("taken.txt", gone)
    log.append(f"Re-checked {len(oldest)} names, {len(gone)} now registered elsewhere: {', '.join(gone) or 'none'}")

    # 3. new names: today's Google Trends first, then categories with the fewest names
    random.seed(TODAY)
    counts = {c: 0 for c in G.CATS}
    for x in inv: counts[x["c"]] = counts.get(x["c"], 0) + 1
    tr = {}
    tp = os.path.join(DATA, "trends", "latest.json")
    if os.path.exists(tp):
        tr = json.load(open(tp))
        if tr.get("date") != TODAY: tr = {}
    hot = [c["category"] for c in tr.get("categories", []) if c["category"] in G.CATS][:5]
    order = hot + [c for c in sorted(G.CATS, key=lambda c: counts[c]) if c not in hot]
    cands = []
    # names built from today's trending generic words (e.g. gold -> goldly.co, getgold.com)
    trend_cands = []
    for w in tr.get("words", [])[:15]:
        word, cat = w["word"], w.get("category") or (hot[0] if hot else "SaaS")
        if cat not in G.CATS: continue
        forms = {G.cap(word) + sfx for sfx in G.SUFFIX if sfx[0] != word[-1]} | \
                {G.cap(pre) + G.cap(word) for pre in G.PREFIX if pre[-1] != word[0]}
        for f in random.sample(sorted(forms), min(12, len(forms))):
            n = G.clean(f)
            if not n: continue
            n = G.cap(n)
            ext = random.choice(["com", "com", "co", "io"] if cat in ("AI", "SaaS", "Crypto") else ["com", "com", "co"])
            d = f"{n.lower()}.{ext}"
            if d not in seen and good(n):
                trend_cands.append((cat, n, ext, d, word))
    random.shuffle(trend_cands)
    for cat in order:
        for n in G.gen_for_cat(cat, 40):
            ext = G.ext_for(cat, n)
            d = f"{n.lower()}.{ext}"
            if d not in seen and ext not in NO_RDAP and ext in G.EXTS and good(n):
                cands.append((cat, n, ext, d, ""))
    random.shuffle(cands)
    # round-robin by category so one category can't take every slot
    by = {}
    for c in cands: by.setdefault(c[0], []).append(c)
    # up to 60% of today's slots come from trending words, the rest from the normal generator
    queue = trend_cands[: ADD * 3]
    while any(by.values()):
        for cat in order:
            if by.get(cat): queue.append(by[cat].pop())
    added, checked = [], []
    for i in range(0, len(queue), 20):
        if len(added) >= ADD: break
        batch = queue[i:i + 20]
        res = check_all([b[3] for b in batch])
        for cat, n, ext, d, word in batch:
            checked.append(d)
            n_trend = sum(1 for a in added if a.get("w"))
            if word and n_trend >= int(ADD * 0.6): continue
            if res[d] == "available" and len(added) < ADD:
                p, tier = shop_price(n, cat, ext)
                item = {"d": d, "p": p, "c": cat, "t": tier, "a": TODAY, "k": TODAY}
                if word: item["w"] = word
                added.append(item)
    append("seen.txt", checked)
    inv = added + inv
    log.append(f"Checked {len(checked)} new candidates, added {len(added)}: " + ", ".join(f"{a['d']} (${a['p']}" + (f", trend: {a['w']})" if a.get('w') else ")") for a in added))
    if hot: log.append("Trending categories today: " + ", ".join(hot))

    json.dump(inv, open(os.path.join(DATA, "inventory.json"), "w"), indent=0, separators=(",", ":"))
    urls = [f"{SITE}/", f"{SITE}/new/", f"{SITE}/sitemap.xml"] + [f"{SITE}/d/{a['d']}/" for a in added] + \
           sorted({f"{SITE}/domains/{a['c'].lower().replace(' ', '-')}/" for a in added})
    open(os.path.join(DATA, "new_urls.txt"), "w").write("\n".join(urls) + "\n")
    report_stats({"run_date": TODAY, "shop_size": len(inv), "added": len(added), "removed_taken": len(gone),
                  "removed_sold": removed_sold, "trending_categories": ", ".join(hot)[:500],
                  "trending_words": ", ".join(w["word"] for w in tr.get("words", [])[:15])[:1000],
                  "new_names": ", ".join(f"{a['d']}|{a['p']}|{a['c']}" for a in added)[:4000]})
    summary = f"## Claimly daily update {TODAY}\n\nShop now has **{len(inv)}** names.\n\n" + "\n".join(f"- {l}" for l in log) + "\n"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(summary)

if __name__ == "__main__":
    main()
