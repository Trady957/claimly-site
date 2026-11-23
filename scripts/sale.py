"""One place for domain sales, used by build.py (site), catalog.py (Pinterest) and daily_social.py (Instagram).

Holiday season 2026-27 (each sale switches on and off by itself with the daily build):
  23-30 Nov   Black Friday         30% off
   1-25 Dec   Christmas sale       50% off   ("gift a business name")
  26 Dec-15 Jan  New Year sale     50% off   ("New year, new business")
.eco is never discounted, and no price drops below the floor for its extension
(what the first year of registration costs, plus a small margin).
"""
import datetime

SALES = [
    # start, end (inclusive), name, %, until text, countdown target (UTC), short tagline
    ("2026-11-23", "2026-11-30", "Black Friday", 30, "until Cyber Monday (30 Nov)", "2026-12-01T03:00:00Z", ""),
    ("2026-12-01", "2026-12-25", "Christmas sale", 50, "until Christmas Day (25 Dec)", "2026-12-26T03:00:00Z", "Gift a business name"),
    ("2026-12-26", "2027-01-15", "New Year sale", 50, "until 15 Jan", "2027-01-16T03:00:00Z", "New year, new business"),
]

FLOOR = {"io": 45, "studio": 30, "tech": 30, "store": 25, "shop": 20, "co": 18, "app": 18, "dev": 18}
FLOOR_DEFAULT = 15                         # .com, .xyz and anything else

def current(today=None):
    t = (today or datetime.date.today()).isoformat()
    for s in SALES:
        if s[0] <= t <= s[1]:
            return s
    return None

def on(today=None):
    return current(today) is not None

def applies(domain):
    return not domain.endswith(".eco")

def floor(domain):
    return FLOOR.get(domain.rsplit(".", 1)[-1], FLOOR_DEFAULT)

def price(domain, p, today=None):
    """Sale price for a domain, or the normal price when no sale is running."""
    s = current(today)
    if not s or not applies(domain):
        return p
    return max(round(p * (100 - s[3]) / 100), min(p, floor(domain)))

# Names used by build.py / catalog.py / daily_social.py for today's sale (empty when none is running)
_s = current()
SALE_START, SALE_END, SALE_NAME, SALE_PCT, SALE_UNTIL, SALE_ENDS_UTC, SALE_TAG = _s if _s else ("", "", "", 0, "", "", "")
