"""One place for domain sales, used by build.py (site), catalog.py (Pinterest) and daily_social.py (Instagram).

Holiday season 2026-27: one 50% sale from 23 Nov to 15 Jan, shown under three names. Because the
discount is the same all season, the only deadline we ever state is the real one, 15 Jan
(no "ends Monday" countdowns that would restart the next day).
  23-30 Nov   Black Friday         50% off
   1-25 Dec   Christmas sale       50% off   ("gift a business name")
  26 Dec-15 Jan  New Year sale     50% off   ("New year, new business")
.eco is never discounted, and no price drops below the floor for its extension
(what the first year of registration costs, plus a small margin).
"""
import datetime

SALES = [
    # start, end (inclusive), name, %, until text, countdown target (UTC), short tagline
    ("2026-11-23", "2026-11-30", "Black Friday", 50, "through 15 Jan", "2027-01-16T03:00:00Z", "Christmas & New Year prices start now"),
    ("2026-12-01", "2026-12-25", "Christmas sale", 50, "through 15 Jan", "2027-01-16T03:00:00Z", "Gift a business name"),
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

# Naming packages (/name-my-business/): regular prices and the holiday offer prices
OFFER_END = "2027-01-15"                   # offer prices end after this date
OFFER_TXT = "Holiday price until 15 Jan"
PKG_REG = {"naming_quick": 69, "naming_starter": 149, "naming_shield": 189, "naming_duo": 298,
           "naming_brand": 299, "naming_bilingual": 349, "naming_launch": 499}
PKG_OFFER = {"naming_quick": 49, "naming_starter": 99, "naming_shield": 139, "naming_duo": 159,
             "naming_brand": 199, "naming_bilingual": 249, "naming_launch": 349}

def pkg_price(key, today=None):
    return PKG_OFFER[key] if (today or datetime.date.today()).isoformat() <= OFFER_END else PKG_REG[key]
