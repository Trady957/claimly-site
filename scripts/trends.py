#!/usr/bin/env python3
"""trends.py — reads Google Trends "Trending now" (daily searches) for several countries
early each morning and turns it into a plan for the day:

  data/trends/latest.json   top searches, the categories they point to, and safe words to build names from
  data/trends/YYYY-MM-DD.json  the same, kept as history

Safety: names are only ever built from words on data/generic_words.txt or the generator's own
word lists. People, teams, companies and products in the news are never turned into domains.
"""
import json, os, re, sys, urllib.request, datetime, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import names as G

GEOS = ["US", "GB", "IN", "AE", "SA", "CA", "AU", "DE", "FR", "SG", "NG", "ZA", "BR", "JP"]
# US searches count most (main market), then other English-speaking markets, then the rest
GEO_WEIGHT = {"US": 3.0, "GB": 1.5, "CA": 1.5, "AU": 1.5}
TODAY = datetime.date.today().isoformat()

def traffic(t):
    m = re.match(r"([\d.,]+)\s*([KM]?)", (t or "").replace(",", ""))
    if not m: return 100
    n = float(m.group(1)); return int(n * {"K": 1e3, "M": 1e6}.get(m.group(2), 1))

def fetch(geo):
    req = urllib.request.Request(f"https://trends.google.com/trending/rss?geo={geo}", headers={"User-Agent": "Mozilla/5.0 (claimly-trends)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        x = r.read().decode("utf-8", "replace")
    items = re.findall(r"<item>\s*<title>([^<]*)</title>\s*<ht:approx_traffic>([^<]*)</ht:approx_traffic>", x)
    return [(html_unescape(t).strip(), traffic(v)) for t, v in items]

def html_unescape(s):
    import html; return html.unescape(s)

def load_generic():
    out = {}
    for line in open(os.path.join(DATA, "generic_words.txt")):
        line = line.strip()
        if not line or line.startswith("#"): continue
        w, _, cat = line.partition("=")
        out[w.strip().lower()] = cat.strip() or None
    return out

def analyse(searches):
    generic = load_generic()
    keymap = json.load(open(os.path.join(DATA, "keymap.json")))
    vocab = {w for ws in G.ROOTS.values() for w in ws}
    cat_score = collections.Counter(); words = collections.Counter(); word_cat = {}
    for title, geo, vol in searches:
        for tok in re.findall(r"[a-z]{3,12}", title.lower()):
            if tok.endswith("s") and tok[:-1] in generic: tok = tok[:-1]   # holidays -> holiday? only if listed
            cat = None
            if tok in generic: cat = generic[tok]
            elif tok in keymap: cat = G.CATS[keymap[tok]]
            if not cat and tok not in vocab: continue
            if cat: cat_score[cat] += vol; word_cat[tok] = cat
            if tok in generic or tok in vocab:
                words[tok] += vol
    return cat_score, words, word_cat

def main():
    searches, failed = [], []
    for g in GEOS:
        try:
            searches += [(t, g, int(v * GEO_WEIGHT.get(g, 1.0))) for t, v in fetch(g)]
        except Exception as e:
            failed.append(f"{g}: {e}")
    cat_score, words, word_cat = analyse(searches)
    top = sorted(searches, key=lambda s: -s[2])[:30]
    out = {
        "date": TODAY,
        "geos": GEOS, "failed": failed,
        "top_searches": [{"q": t, "geo": g, "traffic": v} for t, g, v in top],
        "categories": [{"category": c, "score": s} for c, s in cat_score.most_common()],
        "words": [{"word": w, "category": word_cat.get(w), "score": s} for w, s in words.most_common(25)],
    }
    os.makedirs(os.path.join(DATA, "trends"), exist_ok=True)
    for name in ("latest.json", f"{TODAY}.json"):
        json.dump(out, open(os.path.join(DATA, "trends", name), "w"), indent=1, ensure_ascii=False)
    md = [f"## Google Trends {TODAY} ({len(GEOS) - len(failed)} countries)",
          "**Trending categories:** " + (", ".join(f"{c['category']}" for c in out["categories"][:6]) or "none matched today"),
          "**Words used for today's names:** " + (", ".join(w["word"] for w in out["words"][:15]) or "none"),
          "**Top searches:** " + "; ".join(f"{s['q']} ({s['geo']}, {s['traffic']:,}+)" for s in out["top_searches"][:12])]
    if failed: md.append("Could not read: " + ", ".join(failed))
    print("\n\n".join(md))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write("\n\n".join(md) + "\n\n")

if __name__ == "__main__":
    main()
