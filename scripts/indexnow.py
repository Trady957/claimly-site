#!/usr/bin/env python3
"""Tell Bing, Yandex, Seznam and others (IndexNow) about today's new pages.
Google doesn't use IndexNow; it re-reads sitemap.xml, which lists every page with its date."""
import json, os, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key = open(os.path.join(ROOT, "data", "indexnow_key.txt")).read().strip()
urls = [u.strip() for u in open(os.path.join(ROOT, "data", "new_urls.txt")) if u.strip()]
body = json.dumps({"host": "claimly.ae", "key": key, "keyLocation": f"https://claimly.ae/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow:", r.status, f"({len(urls)} URLs)")
except Exception as e:
    print("IndexNow ping failed (not fatal):", e)
