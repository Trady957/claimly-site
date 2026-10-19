#!/usr/bin/env python3
"""seo.py — pulls search numbers for claimly.ae every morning and sends them to the dashboard.

Bing Webmaster Tools: needs GitHub secret BING_API_KEY
  (Bing Webmaster → Settings (gear) → API access → API key → Generate).
Google Search Console: needs GitHub secret GSC_SERVICE_ACCOUNT (the JSON key of a Google
  service account that was added as a user of the claimly.ae property in Search Console).

Either part is skipped quietly if its secret isn't set. Nothing here can change your
Search Console or Bing settings: both use read-only access.
"""
import json, os, re, datetime, urllib.request, urllib.parse

SITE = "https://claimly.ae/"
SB_URL = "https://bbjreybvwqdzsfbcunlm.supabase.co"
SB_KEY = "sb_publishable_JeEACKfWsGaFXTat1B-WVw_uWkUR8ZK"   # public, insert-only
TODAY = datetime.date.today()

def sb_insert(table, rows):
    if not rows: return
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{table}", data=json.dumps(rows).encode(),
        headers={"apikey": SB_KEY, "Content-Type": "application/json", "Prefer": "return=minimal"}, method="POST")
    urllib.request.urlopen(req, timeout=30)

def get_json(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "claimly-seo/1.0"}), timeout=timeout) as r:
        return json.loads(r.read().decode())

def bing_date(s):
    m = re.search(r"/Date\((-?\d+)", str(s or ""))
    return datetime.datetime.utcfromtimestamp(int(m.group(1)) / 1000).date() if m else None

def bing():
    key = os.environ.get("BING_API_KEY")
    if not key:
        print("Bing: no BING_API_KEY secret yet, skipped"); return
    base = "https://ssl.bing.com/webmaster/api.svc/json/{}?" + urllib.parse.urlencode({"siteUrl": SITE, "apikey": key})
    days = {}
    for r in get_json(base.format("GetRankAndTrafficStats")).get("d") or []:
        d = bing_date(r.get("Date"))
        if d and d >= TODAY - datetime.timedelta(days=30):
            days[d] = {"source": "bing", "day": d.isoformat(), "clicks": int(r.get("Clicks") or 0), "impressions": int(r.get("Impressions") or 0), "position": None, "indexed_pages": None}
    try:
        crawl = sorted((get_json(base.format("GetCrawlStats")).get("d") or []), key=lambda r: bing_date(r.get("Date")) or TODAY)
        if crawl:
            last = crawl[-1]; d = bing_date(last.get("Date")) or TODAY
            row = days.setdefault(d, {"source": "bing", "day": d.isoformat(), "clicks": 0, "impressions": 0, "position": None, "indexed_pages": None})
            row["indexed_pages"] = int(last.get("InIndex") or 0)
    except Exception as e:
        print("Bing crawl stats skipped:", e)
    queries = []
    agg = {}
    for r in get_json(base.format("GetQueryStats")).get("d") or []:
        q = (r.get("Query") or "").strip()[:300]
        if not q: continue
        a = agg.setdefault(q, {"clicks": 0, "impressions": 0, "pos_w": 0.0})
        imp = int(r.get("Impressions") or 0)
        a["clicks"] += int(r.get("Clicks") or 0); a["impressions"] += imp
        a["pos_w"] += float(r.get("AvgImpressionPosition") or 0) * max(imp, 1)
    for q, a in sorted(agg.items(), key=lambda kv: -kv[1]["impressions"])[:20]:
        queries.append({"run_date": TODAY.isoformat(), "source": "bing", "query": q, "clicks": a["clicks"], "impressions": a["impressions"],
                        "position": round(a["pos_w"] / max(a["impressions"], 1), 1)})
    sb_insert("claimly_seo_daily", list(days.values())); sb_insert("claimly_seo_queries", queries)
    print(f"Bing: {len(days)} days, {len(queries)} queries sent")

def google():
    info = os.environ.get("GSC_SERVICE_ACCOUNT")
    if not info:
        print("Google: no GSC_SERVICE_ACCOUNT secret yet, skipped"); return
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_info(json.loads(info), scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    s = AuthorizedSession(creds)
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites/" + urllib.parse.quote(SITE, safe="") + "/searchAnalytics/query"
    start, end = (TODAY - datetime.timedelta(days=30)).isoformat(), TODAY.isoformat()
    r = s.post(url, json={"startDate": start, "endDate": end, "dimensions": ["date"], "rowLimit": 100}, timeout=60); r.raise_for_status()
    days = [{"source": "google", "day": x["keys"][0], "clicks": int(x.get("clicks", 0)), "impressions": int(x.get("impressions", 0)),
             "position": round(float(x.get("position", 0)), 1), "indexed_pages": None} for x in r.json().get("rows", [])]
    r = s.post(url, json={"startDate": (TODAY - datetime.timedelta(days=28)).isoformat(), "endDate": end, "dimensions": ["query"], "rowLimit": 20}, timeout=60); r.raise_for_status()
    queries = [{"run_date": TODAY.isoformat(), "source": "google", "query": x["keys"][0][:300], "clicks": int(x.get("clicks", 0)),
                "impressions": int(x.get("impressions", 0)), "position": round(float(x.get("position", 0)), 1)} for x in r.json().get("rows", [])]
    sb_insert("claimly_seo_daily", days); sb_insert("claimly_seo_queries", queries)
    print(f"Google: {len(days)} days, {len(queries)} queries sent")

if __name__ == "__main__":
    for part in (bing, google):
        try: part()
        except Exception as e: print(f"{part.__name__} failed (not fatal):", e)
