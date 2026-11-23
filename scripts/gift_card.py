"""Printable gift card for a domain bought as a gift.

  python3 scripts/gift_card.py bakebloom.com "Sarah Miller" "Merry Christmas! Here's the name for your bakery." "From Tom"

Writes gift-cards/<domain>.jpg (1500x1050, prints well on A5 / 5x7 in) and .pdf. Email it to the buyer
(or to the recipient on the date they asked for). gift-cards/ is not published on the site.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import social as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1500, 1050

def card(domain, to, message="", sender=""):
    im = Image.new("RGB", (W, H), S.BONE); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 26), fill=S.RED); d.rectangle((0, H - 26, W, H), fill=S.RED)
    d.ellipse((1080, -240, 1700, 380), fill="#F7D9D6")
    d.text((90, 90), "A GIFT FOR YOUR NEXT BIG IDEA", font=S.font("Bold", 30, False), fill=S.RED)
    S.block(d, 90, 150, f"For {to}", S.font("Black", 84), S.INK, W - 400, 1.05)
    d.rounded_rectangle((70, 340, W - 70, 600), 40, fill="#FFFFFF", outline="#E2DFDB", width=3)
    size = 150
    while size > 60 and d.textlength(domain, font=S.font("Black", size)) > W - 240: size -= 6
    f = S.font("Black", size); tw = d.textlength(domain, font=f)
    d.text(((W - tw) / 2, 470 - size * 0.62), domain, font=f, fill=S.INK)
    y = 650
    if message:
        y = S.block(d, 90, y, f"“{message}”", S.font("Medium", 40, False), S.INK, W - 180, 1.35) + 16
    if sender:
        d.text((90, y), sender, font=S.font("SemiBold", 34, False), fill=S.MUTED); y += 60
    S.block(d, 90, max(y + 10, 840), "This domain is registered in your name, first year included. Reply to the Claimly email or write to us and we'll help you connect it to a website or email.",
            S.font("Medium", 28, False), S.MUTED, W - 520, 1.35)
    S.wordmark(d, W - 330, H - 150, S.INK)
    out = os.path.join(ROOT, "gift-cards"); os.makedirs(out, exist_ok=True)
    p = os.path.join(out, domain + ".jpg"); im.save(p, quality=94); im.save(p[:-4] + ".pdf", resolution=200)
    return p

if __name__ == "__main__":
    a = sys.argv[1:] + ["", ""]
    print(card(a[0], a[1], a[2], a[3]))
