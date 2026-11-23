"""Posts that sell the naming packages (/name-my-business/), US audience, 25 Nov 2026 - 13 Jan 2027.

For each date writes social/packages/<date>/1.jpg (cover), 2-4.jpg (how it works),
5.jpg (price) and social/packages/captions.md. They sit on the days between the
holiday name posts (social/holidays). Run: python3 scripts/content_packages.py
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
import sale as SALE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social", "packages")
SITE = "https://claimly.ae"
US = "#smallbusiness #entrepreneur #startup #businessname #branding #smallbusinessowner #usa"
NAME = {"naming_quick": "Quick Pick", "naming_starter": "Starter", "naming_shield": "Name + Shield",
        "naming_brand": "Brand kit", "naming_duo": "Duo"}
WHAT = {"naming_quick": "3 names made for your business in 24 hours, .com checked, and your favourite registered for you",
        "naming_starter": "10 names made for your business in 48 hours, each with the .com checked and free, and your favourite registered for you",
        "naming_shield": "10 names made for your business, then your favourite registered as .com, .co and .net so no one can copy it",
        "naming_brand": "10 names, your domain registered, a wordmark logo concept, colors, fonts and taglines, in 3 days",
        "naming_duo": "two Starter packages in one: 10 names and a registered domain for each business"}
STEPS = {"naming_quick": [("Tell us about it", "What you do, who it's for and the feel you want. Two minutes."), ("Get 3 names", "Made for your business, .com checked, within 24 hours."), ("We register it", "Pick one and we register the domain in your name.")],
         "naming_brand": [("Tell us about it", "What you do, who it's for and the feel you want."), ("Get 10 names", "Each with the .com checked. Pick your favourite."), ("Get the look", "Wordmark logo concept, colors, fonts and taglines in 3 days.")]}
STEPS_DEFAULT = [("Tell us about it", "What you do, who it's for and the feel you want. Two minutes."), ("Get 10 names", "Made for your business, each with the .com checked and free, in 48 hours."), ("We register it", "Pick your favourite and we register the domain in your name.")]

# date, package, cover kicker, cover headline, cover sub, caption hook, hashtags
POSTS = [
 ("2026-11-25", "naming_starter", "Black Friday week", "Stuck on a business name?", "We'll send you 10. Each one with the .com free.",
  "Been stuck on a business name for weeks? Tell us what you do, and in 48 hours you get 10 names made for your business, each with the .com checked and free. Pick one, and we register it for you.", "#blackfriday #namingagency"),
 ("2026-12-02", "naming_quick", "Need it fast?", "A name by tomorrow.", "3 names in 24 hours. Your .com registered.",
  "Need a business name by tomorrow? Quick Pick: 3 names made for your business in 24 hours, .com checked, and we register your favourite.", "#sidehustle #startabusiness"),
 ("2026-12-04", "naming_starter", "The perfect Christmas gift", "Give someone their business name.", "10 names made for their idea. Their .com registered.",
  "Know someone who keeps talking about starting a business? Give them the name. Tick \"This is a gift\", tell us about their idea, and we email you a printable gift card today. They get 10 names in 48 hours and pick their favourite.", "#christmasgifts #giftideas #giftsforher"),
 ("2026-12-09", "naming_brand", "Starting from zero?", "Name, logo, colors. Done.", "Brand kit: everything you need to launch, in 3 days.",
  "Starting from zero? The Brand kit gets you 10 names, your domain registered, a wordmark logo concept, a color palette, fonts and taglines, in 3 days.", "#brandidentity #logodesign #branding"),
 ("2026-12-11", "naming_shield", "Found the name?", "Protect it before someone copies it.", "Your name as .com, .co and .net.",
  "Found the perfect name? Copycats grab the .co and .net. Name + Shield gets you 10 names, then registers your favourite as .com, .co and .net, with a social handle check.", "#brandprotection #trademark #startup"),
 ("2026-12-16", "naming_duo", "Starting up with a friend?", "Name two businesses.", "Two Starter packages in one.",
  "Starting a business with a friend, or got two ideas? Duo is two Starter packages in one: 10 names and a registered domain for each.", "#bestfriends #cofounder #giftideas"),
 ("2026-12-18", "naming_starter", "Last week for Christmas gifts", "A gift that starts a business.", "Order by Dec 23. We email the gift card today.",
  "Still shopping for the friend who wants to be their own boss? Give them a naming package. We send you a printable gift card right away, so it's ready for Christmas morning.", "#christmasgifts #lastminutegifts #entrepreneurgifts"),
 ("2026-12-23", "naming_quick", "Last-minute gift", "No shipping. Still in time.", "Printable gift card in your inbox today.",
  "Last-minute gift? A naming package needs no shipping. Order today, tick \"This is a gift\", and print the card tonight.", "#lastminutegifts #christmas2026 #giftideas"),
 ("2026-12-30", "naming_starter", "Before the new year", "Start 2027 with a name.", "10 names + your .com in 48 hours.",
  "Want to start 2027 with your business name sorted? Order before New Year's Eve and you'll have 10 names in your inbox by January 1.", "#newyearnewbusiness #2027goals"),
 ("2027-01-02", "naming_brand", "New year, new brand", "Launch with a real brand.", "Name, .com, logo concept, colors and fonts in 3 days.",
  "New year, new business? Launch it with a real brand: 10 names, your domain registered, a logo concept, colors, fonts and taglines, in 3 days.", "#newyear #brandidentity #2027goals"),
 ("2027-01-06", "naming_starter", "Forming an LLC this month?", "Name it before you file.", "10 names, each free as a .com.",
  "Filing your LLC this month? Get 10 names made for your business, each with the .com checked and free, then confirm with your state's registry before you file.", "#llc #startabusiness #businessowner"),
 ("2027-01-13", "naming_starter", "Holiday price ends Jan 15", "Last days at $99.", "Starter goes back to $149 after January 15.",
  "Last days at the holiday price: Starter is $99 (normally $149) until January 15. 10 names made for your business, your .com registered.", "#lastchance #businessname #smallbusiness"),
]

def main():
    md = ["# Naming package posts (25 Nov 2026 - 13 Jan 2027), US audience\n",
          "Each post: a 5-image carousel (1 cover, 2-4 how it works, 5 price). They go on the days between the holiday name posts.",
          "Post at 12:30 pm Eastern (9:30 pm Dubai). Use 1.jpg or 5.jpg as the Pinterest pin. The Pinterest catalog also lists the packages automatically.",
          f"Images are published at {SITE}/social/packages/<date>/N.jpg after the next site build.\n"]
    for date, key, kicker, head, sub, hook, tags in POSTS:
        day = datetime.date.fromisoformat(date)
        now, was = SALE.pkg_price(key, day), SALE.PKG_REG[key]
        f = os.path.join(OUT, date); os.makedirs(f, exist_ok=True)
        S.cover(os.path.join(f, "1.jpg"), kicker, head, sub)
        for i, (t, b) in enumerate(STEPS.get(key, STEPS_DEFAULT), 1):
            S.tip(os.path.join(f, f"{i + 1}.jpg"), i, 3, t, b)
        S.statement(os.path.join(f, "5.jpg"), f"{NAME[key]} · holiday price" if now != was else NAME[key],
                    f"${now}",
                    (f"Normally ${was}. Holiday price until January 15. " if now != was else "") + "Full refund if we can't deliver. Link in bio.")
        link = f"{SITE}/name-my-business/?utm_source=instagram&utm_medium=social&utm_campaign=packages&utm_content={key}"
        md += [f"## {day.strftime('%a %b %-d')}: {NAME[key]}, {head}\n",
               f"Images: social/packages/{date}/1-5.jpg  \nLink in bio / story link: {link}\n",
               "**Instagram caption**\n",
               f"{hook}\n\n{NAME[key]}: {WHAT[key]}. ${now}" + (f" instead of ${was}, until January 15" if now != was else "") +
               f". Full refund if we can't deliver.\n\nTap the link in bio to start.\n\n{tags} {US}\n",
               "**Pinterest pin** (image 1.jpg or 5.jpg, board: Business naming service)  ",
               f"Title: {head} | {NAME[key]} naming package, ${now}  ",
               f"Description: {hook}  ",
               f"Link: {SITE}/name-my-business/?utm_source=pinterest&utm_medium=social&utm_campaign=packages&utm_content={key}\n"]
        print(date, NAME[key], now)
    open(os.path.join(OUT, "captions.md"), "w").write("\n".join(md))

if __name__ == "__main__":
    main()
