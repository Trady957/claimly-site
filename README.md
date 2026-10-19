# claimly-site

The claimly.ae storefront. Netlify builds it with `python3 scripts/build.py` on every push.

## What runs automatically
Every day at 07:00 Dubai time, GitHub Actions (`.github/workflows/daily.yml`):
1. Removes names listed in `data/sold.txt` and names someone else registered.
2. Re-checks the 60 oldest-checked names with RDAP and drops any that got registered.
3. Generates new brandable names, checks them, and adds 25 available ones (`data/inventory.json`).
4. Commits. Netlify rebuilds the site: new `/d/<name>/` pages, `/new/`, and `sitemap.xml` with dates.
5. Pings IndexNow (Bing, Yandex and others). Google picks up changes from the sitemap in Search Console.

Run it by hand: GitHub → Actions → "Daily domain update" → Run workflow.

## When a domain sells
Add it on its own line to `data/sold.txt` and commit. It disappears from the site on the next build.

## Files
- `data/inventory.json`: the shop (`d` domain, `p` price, `c` category, `t` tier, `a` date added, `k` last checked)
- `data/seen.txt`: every name ever checked, so none is checked twice
- `data/taken.txt`, `data/sold.txt`: names removed from the shop
- `scripts/names.py`: the name generator (word lists and pricing)
- `site/`: static files copied as-is (css, favicon, og image, verification files, IndexNow key)
- `netlify/functions/finder.js`: the AI finder (needs `ANTHROPIC_API_KEY` in Netlify)
