"""One place for the domain sale, used by build.py (site), catalog.py (Pinterest) and daily_social.py (Instagram).

Black Friday / Cyber Monday 2026: 30% off every domain (not .eco) until Monday 30 Nov.
The daily build on Tuesday 1 Dec (03:00 UTC) puts prices back by itself.
"""
import datetime

SALE_END = "2026-11-30"
SALE_PCT = 30
SALE_NAME = "Black Friday"
SALE_UNTIL = "until Cyber Monday (30 Nov)"
FLOOR = 15                                 # lowest sale price in USD
SALE_ENDS_UTC = "2026-12-01T03:00:00Z"     # countdown target on the site

def on(today=None):
    return (today or datetime.date.today()).isoformat() <= SALE_END

def applies(domain):
    return not domain.endswith(".eco")

def price(domain, p, today=None):
    """Sale price for a domain, or the normal price when no sale is running."""
    if not (on(today) and applies(domain)):
        return p
    # never below FLOOR: a .com costs about $10-11 to register, so the cheapest names keep their price
    return max(round(p * (100 - SALE_PCT) / 100), min(p, FLOOR))
