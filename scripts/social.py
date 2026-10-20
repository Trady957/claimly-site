"""Branded Instagram images for Claimly (1080x1350, 4:5).

Templates:
  statement(path, kicker, headline, sub)            red background, big white headline
  names(path, kicker, title, items, cta)            bone background, list of domains with prices
  tip(path, n, total, title, body)                  carousel slide with a big number
  cover(path, kicker, title, sub)                   carousel cover (ink background)
Images are written into social/ and published at https://claimly.ae/social/...
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
RED, INK, BONE, BONE2, MUTED, WHITE = "#E0231C", "#141314", "#F4F3F1", "#FFFFFF", "#6B6766", "#FFFFFF"
import os
_REPO_FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts") + "/"
FD = _REPO_FONTS if os.path.exists(_REPO_FONTS + "InterDisplay-Black.otf") else "/usr/share/fonts/opentype/inter/"

def font(weight, size, display=True):
    return ImageFont.truetype(f"{FD}{'InterDisplay' if display else 'Inter'}-{weight}.otf", size)

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines

def block(d, x, y, text, f, fill, maxw, lh=1.12):
    for line in wrap(d, text, f, maxw):
        d.text((x, y), line, font=f, fill=fill)
        y += int(f.size * lh)
    return y

def wordmark(d, x, y, color, dot=RED, size=46):
    f = font("Black", size)
    d.text((x, y), "Claimly", font=f, fill=color)
    w = d.textlength("Claimly", font=f)
    r = size * 0.13
    d.ellipse((x + w + 4, y + size * 0.78 - r, x + w + 4 + 2 * r, y + size * 0.78 + r), fill=dot)

def footer(d, dark):
    c = WHITE if dark else INK
    wordmark(d, 80, H - 120, c, dot=(INK if dark else RED))
    f = font("SemiBold", 30, display=False)
    t = "claimly.ae"
    d.text((W - 80 - d.textlength(t, font=f), H - 108), t, font=f, fill=c)

def statement(path, kicker, headline, sub):
    im = Image.new("RGB", (W, H), RED); d = ImageDraw.Draw(im)
    d.ellipse((620, -260, 1340, 460), fill="#EA4A3F")
    d.text((80, 120), kicker.upper(), font=font("Bold", 30, False), fill=WHITE)
    y = block(d, 80, 260, headline, font("Black", 104), WHITE, W - 160, 1.04)
    block(d, 80, y + 50, sub, font("Medium", 40, False), "#FFE3E1", W - 200, 1.35)
    footer(d, True); im.save(path, quality=92)

def names(path, kicker, title, items, cta):
    im = Image.new("RGB", (W, H), BONE); d = ImageDraw.Draw(im)
    d.text((80, 110), kicker.upper(), font=font("Bold", 28, False), fill=RED)
    y = block(d, 80, 160, title, font("Black", 76), INK, W - 160, 1.06) + 40
    fd, fp = font("Bold", 50), font("Bold", 32, False)
    for dom, price in items:
        d.rounded_rectangle((80, y, W - 80, y + 118), 26, fill=BONE2, outline="#E2DFDB", width=2)
        d.text((118, y + 30), dom, font=fd, fill=INK)
        pt = f"${price}"; pw = d.textlength(pt, font=fp)
        d.rounded_rectangle((W - 118 - pw - 44, y + 34, W - 118, y + 84), 25, fill=RED)
        d.text((W - 118 - pw - 22, y + 39), pt, font=fp, fill=WHITE)
        y += 140
    block(d, 80, y + 20, cta, font("SemiBold", 34, False), MUTED, W - 160, 1.3)
    footer(d, False); im.save(path, quality=92)

def cover(path, kicker, title, sub):
    im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
    d.rectangle((80, 120, 200, 132), fill=RED)
    d.text((80, 160), kicker.upper(), font=font("Bold", 30, False), fill="#BDB8B5")
    y = block(d, 80, 300, title, font("Black", 110), WHITE, W - 160, 1.03)
    block(d, 80, y + 40, sub, font("Medium", 40, False), "#BDB8B5", W - 200, 1.35)
    d.text((80, H - 230), "Swipe  →", font=font("Bold", 34, False), fill=RED)
    footer(d, True); im.save(path, quality=92)

def tip(path, n, total, title, body):
    im = Image.new("RGB", (W, H), BONE); d = ImageDraw.Draw(im)
    d.text((80, 90), f"{n:02d}", font=font("Black", 260), fill=RED)
    d.text((W - 80 - 90, 110), f"{n}/{total}", font=font("Bold", 30, False), fill=MUTED)
    y = block(d, 80, 470, title, font("Black", 78), INK, W - 160, 1.06)
    block(d, 80, y + 40, body, font("Medium", 40, False), MUTED, W - 180, 1.4)
    footer(d, False); im.save(path, quality=92)
