#!/usr/bin/env python3
"""build.py — builds the Claimly site into ./dist (Netlify runs this on every deploy).

Reads data/inventory.json minus data/sold.txt and data/taken.txt.
Outputs: index.html, /d/<domain>/, /domains/<category>/, /new/, sitemap.xml, robots.txt, 404.html.
"""
import json, os, shutil, html, datetime, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "dist")
SITE = "https://claimly.ae"
PAY_BASE = "https://www.paypal.com/paypalme/Claimly26"
# Orders and newsletter sign-ups are saved in Supabase (insert-only for the public key; nobody can read them from the site).
SB_URL = "https://bbjreybvwqdzsfbcunlm.supabase.co"
SB_KEY = "sb_publishable_JeEACKfWsGaFXTat1B-WVw_uWkUR8ZK"
EMAIL = "hello@claimly.ae"
TODAY = datetime.date.today().isoformat()

CATS = ["Finance","AI","SaaS","E-commerce","Local","Health","Creator","Education","Travel","Real estate","Food","Pets","Crypto","Marketing","Legal","Fashion","Gaming","Green"]
EXTS = ["com","ai","io","co","app","dev","xyz","shop","store","studio","tech","eco"]
TIERS = ["starter","standard","premium"]
def _lines(f):
    p = os.path.join(DATA, f)
    return {l.strip().lower() for l in open(p) if l.strip() and not l.startswith("#")} if os.path.exists(p) else set()
_GONE = _lines("sold.txt") | _lines("taken.txt")
INV = [x for x in json.load(open(os.path.join(DATA, "inventory.json"))) if x["d"] not in _GONE]
# newest additions first, otherwise keep the curated order
INV = sorted(INV, key=lambda x: x["a"], reverse=True)
ADDED = {x["d"]: x["a"] for x in INV}
CHECKED = {x["d"]: x.get("k", x["a"]) for x in INV}
RAW = [[x["d"].rsplit(".",1)[0].capitalize(), EXTS.index(x["d"].rsplit(".",1)[1]), x["p"], CATS.index(x["c"]), TIERS.index(x["t"]), ""] for x in INV]
KEYMAP = json.load(open(os.path.join(DATA, "keymap.json")))
TRENDS = {}
try:
    TRENDS = json.load(open(os.path.join(DATA, "trends", "latest.json")))
except Exception:
    pass
TREND_WORD = {x["d"]: x.get("w") for x in INV if x.get("w")}
SEGMENT_NAMES = {x["d"] for x in INV if x.get("s")}   # two real words, picked for high-demand markets

def slug(c): return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
def esc(s): return html.escape(str(s), quote=True)

D = []
for n, e, p, c, t, co in RAW:
    D.append(dict(name=n, ext=EXTS[e], fqdn=n.lower()+"."+EXTS[e], price=p, cat=CATS[c], tier=TIERS[t]))
BYCAT = {c: [d for d in D if d["cat"] == c] for c in CATS}
N = len(D)
NFMT = f"{N:,}"
MINP = min(d["price"] for d in D); MAXP = max(d["price"] for d in D)

CAT_BLURB = {
 "Finance":"fintech apps, accounting firms, advisers, budgeting tools and payments startups",
 "AI":"AI products, agents, data tools and machine-learning startups",
 "SaaS":"software products, B2B tools, dashboards and developer platforms",
 "E-commerce":"online shops, marketplaces, DTC brands and retail businesses",
 "Local":"local services, neighbourhood businesses, city guides and community projects",
 "Health":"clinics, wellness brands, fitness coaches and health apps",
 "Creator":"studios, designers, photographers, agencies and content creators",
 "Education":"tutors, online courses, academies and edtech startups",
 "Travel":"travel agencies, tour operators, booking sites and travel blogs",
 "Real estate":"agents, property managers, rentals and real-estate platforms",
 "Food":"restaurants, cafés, food brands, bakeries and recipe sites",
 "Pets":"pet shops, groomers, vets, pet-sitters and pet-product brands",
 "Crypto":"web3 projects, DeFi tools, wallets and blockchain startups",
 "Marketing":"marketing agencies, growth consultants, SEO and ad-tech tools",
 "Legal":"law firms, notaries, legal-tech and compliance services",
 "Fashion":"clothing labels, boutiques, stylists and accessories brands",
 "Gaming":"game studios, esports teams, streamers and gaming communities",
 "Green":"sustainability brands, solar, climate-tech and eco products",
}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@500;700;900&family=Hanken+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">')

OFFER_BAR = """<a href="/name-my-business/?utm_source=offer-bar" style="display:block;background:var(--ink);color:var(--bone);text-align:center;font-size:14px;padding:9px 16px;text-decoration:none;position:relative;z-index:5"><b>Launch offer:</b> we name your business for $99 <s style="opacity:.6">$149</s> &middot; until 30 Nov <u>See how &rarr;</u></a>"""

def head(title, desc, canon, extra_ld="", robots="index,follow,max-image-preview:large"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#F4F3F1">
<meta property="og:type" content="website"><meta property="og:site_name" content="Claimly">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{SITE}/og-image.png">
<meta name="p:domain_verify" content="a499319593d2ca67933886e9969ee4c6"/>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
{extra_ld}
<script>function loadScript(a){{var b=document.getElementsByTagName("head")[0],c=document.createElement("script");c.type="text/javascript",c.src="https://tracker.metricool.com/resources/be.js",c.onreadystatechange=a,c.onload=a,b.appendChild(c)}}loadScript(function(){{beTracker.t({{hash:"8ba47d0fd40dc1413af50dcb436aff42"}})}});</script>
</head>
<body>
<div class="bg" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span></div>
<header><div class="wrap nav">
<a class="brand" href="/">Claimly<span class="reg">&reg;</span></a>
<nav class="nav-links"><a href="/#finder">AI finder</a><a href="/#shop">Browse</a><a href="/#how">How it works</a><a href="/#faq">FAQ</a><a href="/business-name-ideas/">Name ideas</a><a href="/name-my-business/">Name my business</a><a class="btn btn-cta" href="/#finder">Find a domain</a></nav>
</div></header>
{OFFER_BAR if OFFER_ON else ""}
"""

def footer():
    cats = "".join(f'<a href="/domains/{slug(c)}/">{esc(c)} domains</a>' for c in CATS[:6])
    return f"""<footer>
<div class="wrap foot2">
<div>
<div class="brand" style="font-size:19px;margin-bottom:10px">Claimly<span class="reg">&reg;</span></div>
<p class="blurb">A curated shop of brandable domain names for founders and small businesses &mdash; registered in your name and handed over the same day.</p>
<form class="news" name="newsletter" onsubmit="return claimlyNews(event)">
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<input type="email" name="email" required placeholder="Email for new names &amp; price drops" aria-label="Email address">
<button class="btn btn-cta" type="submit">Subscribe</button>
</form>
<p class="news-ok" id="newsOk">Thanks &mdash; you&rsquo;re on the list.</p>
</div>
<div>
<h4>Explore</h4>
<a href="/#finder">AI finder</a>
<a href="/#shop">Browse names</a>
<a href="/new/">New this week</a>
<a href="/name-my-business/">Name my business</a>
<a href="/business-name-ideas/">Business name ideas</a>
<a href="/guides/">Naming guides</a>
<a href="/launch/">Launch your business</a>
<a href="/partners/">For agencies</a>
{cats}
</div>
<div>
<h4>Contact</h4>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<a href="/#how">How it works</a>
<a href="/#faq">FAQ</a>
</div>
<div class="policy">
<h4>Policies</h4>
<details><summary>Terms of Service</summary><div class="ptext">Listings are subject to availability at the time of purchase. After payment we register the domain and transfer it to you, or register it directly in your name; ownership passes on completion. Prices are in USD and include the first year of registration. Renewals are paid by you to your registrar. Domains are provided for lawful use.</div></details>
<details><summary>Privacy Policy</summary><div class="ptext">We collect only what&rsquo;s needed to complete your order: your email, the domain, and how you found us. Payments are handled by PayPal; we never see your card details. We count anonymous page visits with Metricool to see which pages are useful. We don&rsquo;t sell your data.</div></details>
<details><summary>Refund Policy</summary><div class="ptext">If a domain can&rsquo;t be delivered after payment, you receive a full refund. As domains are unique assets transferred to you, completed transfers are final. Contact us within 7 days for any delivery issue.</div></details>
</div>
</div>
<div class="wrap foot-bottom">
<span>&copy; <span class="yr">{datetime.date.today().year}</span> Claimly. All rights reserved.</span>
<span>Pay by card or PayPal &middot; full refund if not delivered</span>
</div>
</footer>
<script>
(function(){{try{{var k='claimly_attr';if(!sessionStorage.getItem(k)){{var q=new URLSearchParams(location.search),r=document.referrer||'';if(r&&new URL(r).host===location.host)r='';sessionStorage.setItem(k,JSON.stringify({{ref:r,land:location.pathname+location.search,us:q.get('utm_source')||q.get('ref')||'',um:q.get('utm_medium')||'',uc:q.get('utm_campaign')||''}}));}}}}catch(e){{}}}})();
function claimlyAttr(){{try{{return JSON.parse(sessionStorage.getItem('claimly_attr')||'{{}}');}}catch(e){{return {{ref:document.referrer,land:location.pathname}};}}}}
</script>
<script>
function claimlySave(table,row){{return fetch('{SB_URL}/rest/v1/'+table,{{method:'POST',keepalive:true,headers:{{'apikey':'{SB_KEY}','Content-Type':'application/json','Prefer':'return=minimal'}},body:JSON.stringify(row)}}).catch(function(){{}});}}
function claimlyNews(e){{e.preventDefault();var f=e.target;if(!f['bot-field'].value)claimlySave('claimly_subscribers',{{email:f.email.value.trim().slice(0,200)}});f.style.display='none';document.getElementById('newsOk').style.display='block';return false;}}
</script>
"""

# ───────────────────────── home page ─────────────────────────
def home():
    featured = D[:12]
    items = []
    for i, d in enumerate(featured, 1):
        items.append({"@type":"ListItem","position":i,"url":f"{SITE}/d/{d['fqdn']}/","name":d["fqdn"]})
    faqs = [
     ("Is it safe to pay here?","Payment goes through PayPal, so you can pay with a card or a PayPal account and PayPal&rsquo;s buyer protection applies. If we can&rsquo;t deliver your domain for any reason, you get a full refund."),
     ("How do I receive the domain?","After payment we either register the domain directly in your name, or register it and transfer it to your account at your registrar (GoDaddy, Namecheap, Cloudflare and so on). We email you at each step."),
     ("How long does it take?","Most orders are delivered the same day. A transfer between registrars can take up to a few days depending on your registrar; we keep you updated by email."),
     ("What if the name is already taken?","Names are availability-checked, but registrations change constantly. If a name is gone when you order, you get an immediate full refund &mdash; or you can pick another name at the same price."),
     ("Why are prices so low?","We find and screen good unregistered names, then register them only when you buy. No big inventory means low prices. The price includes the first year of registration."),
     ("Can I get a custom name suggestion?","Yes. Email us what you&rsquo;re building and we&rsquo;ll reply with a shortlist of available names that fit."),
    ]
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":html.unescape(re.sub('<[^>]+>','',a))}} for q,a in faqs]}
    ld = ('<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"Organization","name":"Claimly","url":SITE+"/","logo":SITE+"/og-image.png","email":EMAIL})+'</script>\n'
          '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"WebSite","name":"Claimly","url":SITE+"/"})+'</script>\n'
          '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"ItemList","name":"Featured brandable domains","itemListElement":items})+'</script>\n'
          '<script type="application/ld+json">'+json.dumps(faq_ld)+'</script>')
    title = f"Brandable Domain Names from ${MINP} | Claimly"
    desc = f"Short, brandable domain names from ${MINP}. Describe your business and our AI finds names that fit. Pay by card or PayPal, same-day delivery, full refund if not delivered."
    h = head(title, desc, SITE+"/", ld)
    catchips = '<a class="chip active" href="/new/">New this week</a>' + "".join(f'<a class="chip" href="/domains/{slug(c)}/">{esc(c)}</a>' for c in CATS)
    faqhtml = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in faqs)
    data = json.dumps(RAW, separators=(",",":"))
    return h + f"""
<section class="hero" id="finder"><div class="wrap">
<div class="hero-top"><span class="eyebrow"><span class="spark"></span>AI domain finder</span><span class="hero-counter">New names added daily</span></div>
<h1 class="giant">Domains<span class="sr"> &mdash; brandable domain names for your business</span></h1>
<div class="floaters" aria-hidden="true">
<span class="float fa">VaultMint.com <small>$129</small></span>
<span class="float fb">NeuralFig.ai <small>$139</small></span>
<span class="float fc">BrewQuarter.com <small>$69</small></span>
</div>
<div class="hero-bottom">
<div class="hero-pitch"><div class="price-hook">from ${MINP}</div><p class="lede">Short, brandable domain names for founders and small businesses. Describe what you&rsquo;re building and our AI suggests names that fit &mdash; registered in your name, usually the same day.</p></div>
<div class="finder">
<label for="brief">Describe your business or product</label>
<textarea id="brief" placeholder="e.g. a financial planning platform for small businesses"></textarea>
<div class="vibes" id="vibes">
<button class="vibe" data-v="short">Short &amp; clean</button>
<button class="vibe" data-v="playful">Playful</button>
<button class="vibe" data-v="premium">Premium</button>
<button class="vibe" data-v="ai">Tech / AI</button>
</div>
<div class="row"><button class="btn btn-cta" id="findBtn">Find available names</button><span class="hint">Instant &middot; free &middot; no sign-up</span></div>
</div>
</div></div></section>

<div class="trustbar"><div class="wrap">
<span class="trust-item"><span class="dot"></span>Pay by card or PayPal</span>
<span class="trust-item"><span class="dot"></span>PayPal buyer protection</span>
<span class="trust-item"><span class="dot"></span>Usually delivered same day</span>
<span class="trust-item"><span class="dot"></span>Full refund if not delivered</span>
<span class="trust-item"><span class="dot"></span>First year included</span>
</div></div>

<section class="results hide" id="results"><div class="wrap">
<div class="results-head"><h2 id="resTitle">Recommended for you</h2><button class="clearbtn" id="clearRes">Clear &times;</button></div>
<div class="grid" id="resGrid"></div>
</div></section>

<div class="toolbar" id="shop"><div class="wrap toolbar-in">
<div class="searchbar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><input id="search" placeholder="Search names…" autocomplete="off" aria-label="Search domains"></div>
<div class="chips" id="chips"></div>
<select class="sort" id="sort" aria-label="Sort"><option value="featured">Featured</option><option value="plo">Price &uarr;</option><option value="phi">Price &darr;</option><option value="az">A&ndash;Z</option></select>
</div></div>

<section class="shop"><div class="wrap">
<div class="grid" id="grid"></div>
<p class="empty" id="empty" style="display:none">No matches for that search &mdash; try another keyword, or <a href="mailto:{EMAIL}?subject=Name%20request" style="color:var(--cobalt);font-weight:600">ask us for a custom shortlist</a>.</p>
<div class="loadmore"><button class="btn btn-cta" id="loadMore" style="display:none">Load more</button></div>
</div></section>

<section class="section-pad" style="padding-top:0"><div class="wrap"><div style="background:var(--ink);color:var(--bone);border-radius:22px;padding:30px 28px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap">
<div><div style="font-family:'JetBrains Mono';font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7">Can&rsquo;t decide?</div><h2 style="font-family:'Schibsted Grotesk';font-size:clamp(22px,3vw,30px);margin:6px 0 6px">We&rsquo;ll name your business for you</h2><p style="margin:0;opacity:.8;max-width:52ch">10 checked names made for your business, plus your domain registered. Delivered in 48 hours, from ${PKG_FROM}{(' <b style="background:var(--red,#E0231C);color:#fff;border-radius:99px;padding:2px 9px;font-size:13px;margin-left:4px">' + OFFER_TXT + '</b>') if OFFER_ON else ''}.</p></div>
<div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-cta" href="/name-my-business/">See the naming package &rarr;</a><a class="btn" style="border:1px solid var(--bone);color:var(--bone)" href="/name-my-business/#free">Get 3 free ideas</a></div></div></div></section>
<section class="section-pad" id="how"><div class="wrap">
<h2>How it works</h2>
<p class="section-sub">From finding a name to owning it &mdash; usually the same day.</p>
<div class="steps">
<div class="step"><div class="n">01</div><h3>Find your name</h3><p>Search the catalogue or describe your business to the AI finder. Every name is short, brandable and availability-checked.</p></div>
<div class="step"><div class="n">02</div><h3>Order &amp; pay</h3><p>Enter your email, then pay by card or PayPal. PayPal&rsquo;s buyer protection applies, and you get a full refund if we can&rsquo;t deliver.</p></div>
<div class="step"><div class="n">03</div><h3>Get your domain</h3><p>We register the domain in your name or transfer it to your registrar account, and email you as soon as it&rsquo;s yours.</p></div>
</div>
</div></section>

{segments_html()}
{trending_html()}
<section class="section-pad" style="padding-top:0"><div class="wrap">
<h2>Browse by category</h2>
<p class="section-sub">Hand-picked names for every kind of business.</p>
<div class="catlinks">{catchips}</div>
</div></section>

<section class="section-pad" id="faq" style="padding-top:0"><div class="wrap">
<h2>Frequently asked questions</h2>
<p class="section-sub">Everything worth knowing before you buy.</p>
<div class="faq">{faqhtml}</div>
</div></section>
""" + footer() + modal() + f"""
<script>
const RAW={data};const CATS={json.dumps(CATS)};const EXTS={json.dumps(EXTS)};const TIERS={json.dumps(TIERS)};const KEYMAP={json.dumps(KEYMAP,separators=(",",":"))};
const D=RAW.map(a=>({{name:a[0],ext:EXTS[a[1]],price:a[2],cat:CATS[a[3]],tier:TIERS[a[4]],fqdn:a[0].toLowerCase()+"."+EXTS[a[1]]}}));
const PAGE=60;let activeCat='All',q='',sortBy='featured',shown=PAGE;
const grid=document.getElementById('grid'),emptyEl=document.getElementById('empty'),
 chipsEl=document.getElementById('chips'),searchEl=document.getElementById('search'),sortEl=document.getElementById('sort'),loadMore=document.getElementById('loadMore');
chipsEl.innerHTML='<button class="chip active" data-cat="All">All</button>'+CATS.map(c=>`<button class="chip" data-cat="${{c}}">${{c}}</button>`).join('');
chipsEl.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{{activeCat=b.dataset.cat;chipsEl.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));b.classList.add('active');shown=PAGE;render();}});
searchEl.oninput=e=>{{q=e.target.value.toLowerCase().trim();shown=PAGE;render();}};
sortEl.onchange=e=>{{sortBy=e.target.value;render();}};
loadMore.onclick=()=>{{shown+=PAGE;render();}};
function cardHTML(d,why){{return `<div class="spec${{why?' match':''}}" data-f="${{d.fqdn}}" tabindex="0" role="button" aria-label="Buy ${{d.fqdn}} for $${{d.price}}"><div class="spec-name">${{d.fqdn}}</div>${{why?`<span class="why">${{why}}</span>`:''}}<div class="spec-meta"><span class="spec-cat">${{d.cat}}</span><span class="spec-right"><span class="buyflag">Buy now</span><span class="spec-price">$${{d.price}}</span></span></div></div>`;}}
function wire(scope){{scope.querySelectorAll('.spec').forEach(c=>{{const open=()=>openModal(c.dataset.f);c.onclick=open;c.onkeydown=e=>{{if(e.key==='Enter'||e.key===' '){{e.preventDefault();open();}}}};}});}}
function render(){{
 let list=D.filter(d=>(activeCat==='All'||d.cat===activeCat)&&(!q||(d.fqdn+' '+d.cat).toLowerCase().includes(q)));
 if(sortBy==='plo')list=list.slice().sort((a,b)=>a.price-b.price);
 else if(sortBy==='phi')list=list.slice().sort((a,b)=>b.price-a.price);
 else if(sortBy==='az')list=list.slice().sort((a,b)=>a.fqdn.localeCompare(b.fqdn));
 emptyEl.style.display=list.length?'none':'block';
 grid.innerHTML=list.slice(0,shown).map(d=>cardHTML(d)).join('');
 wire(grid);
 loadMore.style.display=list.length>shown?'inline-flex':'none';
}}
render();
let vibe=null;
document.getElementById('vibes').querySelectorAll('.vibe').forEach(b=>b.onclick=()=>{{
 const on=b.classList.contains('on');document.getElementById('vibes').querySelectorAll('.vibe').forEach(x=>x.classList.remove('on'));if(!on)b.classList.add('on');vibe=on?null:b.dataset.v;}});
document.getElementById('findBtn').onclick=runFinder;
document.getElementById('clearRes').onclick=()=>{{document.getElementById('results').classList.add('hide');}};
function tokensOf(t){{return t.split(/[^a-z]+/).filter(x=>x.length>=3);}}
function inferCats(tokens){{const c={{}};tokens.forEach(t=>{{if(KEYMAP[t]!=null)c[KEYMAP[t]]=1;}});return Object.keys(c).map(Number);}}
function scoreAll(tokens,wantCats){{return D.map(d=>{{let s=0;const ci=CATS.indexOf(d.cat);
   if(wantCats.includes(ci))s+=10;
   tokens.forEach(t=>{{if(d.name.toLowerCase().includes(t))s+=7;}});
   if(vibe==='short')s+=Math.max(0,9-d.name.length);
   if(vibe==='premium'&&d.tier==='premium')s+=4;
   if(vibe==='playful'&&/(ly|fox|owl|bay|pop|loop)$/.test(d.name.toLowerCase()))s+=4;
   if(vibe==='ai'&&(d.ext==='ai'||d.ext==='io'||d.cat==='AI'||d.cat==='SaaS'))s+=4;
   s+=Math.random()*0.6;return {{d,s,ci}};}}).sort((a,b)=>b.s-a.s);}}
function showResults(title){{document.getElementById('resTitle').textContent=title;
 const r=document.getElementById('results');r.classList.remove('hide');r.scrollIntoView({{behavior:'smooth',block:'start'}});}}
function heuristicResults(tokens,wantCats){{
 const scored=scoreAll(tokens,wantCats);let top=scored.filter(x=>x.s>=1).slice(0,12);if(!top.length)top=scored.slice(0,12);
 document.getElementById('resGrid').innerHTML=top.map(x=>{{let why='Brandable pick';
   if(wantCats.includes(x.ci))why='Fits '+x.d.cat;const hit=tokens.find(t=>x.d.name.toLowerCase().includes(t));
   if(hit)why='Has "'+hit+'"';else if(vibe==='short'&&x.d.name.length<=6)why='Short & clean';return cardHTML(x.d,why);}}).join('');
 wire(document.getElementById('resGrid'));
 showResults(tokens.length?'Recommended for your business':'A selection to consider');}}
async function runFinder(){{
 const btn=document.getElementById('findBtn'),raw=document.getElementById('brief').value||'';
 const tokens=tokensOf(raw.toLowerCase()),wantCats=inferCats(tokens);
 const shortlist=scoreAll(tokens,wantCats).slice(0,80).map(x=>x.d);
 const label=btn.innerHTML;btn.disabled=true;btn.innerHTML='Searching…';
 let picks=null;
 if(false&&raw.trim()){{try{{
  const ctl=new AbortController();const tm=setTimeout(()=>ctl.abort(),9000);
  const res=await fetch('/.netlify/functions/finder',{{method:'POST',signal:ctl.signal,headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{brief:raw,vibe:vibe,shortlist:shortlist.map(d=>({{fqdn:d.fqdn,cat:d.cat,price:d.price}}))}})}});
  clearTimeout(tm);
  if(res.ok){{const j=await res.json();if(j&&Array.isArray(j.picks)&&j.picks.length)picks=j.picks;}}
 }}catch(e){{}}}}
 btn.disabled=false;btn.innerHTML=label;
 if(picks){{const map={{}};D.forEach(d=>map[d.fqdn]=d);
  const rows=picks.map(p=>({{d:map[(p.fqdn||'').toLowerCase()],why:(p.reason||'').slice(0,28)}})).filter(x=>x.d);
  if(rows.length){{document.getElementById('resGrid').innerHTML=rows.map(x=>cardHTML(x.d,x.why)).join('');
   wire(document.getElementById('resGrid'));showResults('AI-recommended for your business');return;}}}}
 heuristicResults(tokens,wantCats);
}}
const BYF={{}};D.forEach(d=>BYF[d.fqdn]=d);
(function(){{try{{var p=new URLSearchParams(location.search).get('d');if(p&&BYF[p.toLowerCase()])openModal(p.toLowerCase());}}catch(e){{}}}})();
</script>
</body></html>"""

# ───────────────────────── buy modal (shared) ─────────────────────────
def modal():
    return f"""
<div class="modal-bg" id="modalBg" onclick="if(event.target===this)closeModal()">
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="mName">
<button class="x" onclick="closeModal()" aria-label="Close">&times;</button>
<div id="mForm">
<div class="m-kicker">Buy this domain</div>
<div class="m-price"><small>$</small><span id="mPrice">—</span></div>
<div class="m-name" id="mName">name.com</div>
<ul class="m-incl"><li>First year of registration included</li><li>Delivered to you, usually the same day</li><li>Full refund if we can&rsquo;t deliver</li></ul>
<form name="order" id="orderForm">
<input type="hidden" name="domain" id="fDomain"><input type="hidden" name="price" id="fPrice">
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<div class="field"><label for="fEmail">Your email (for delivery)</label><input type="email" name="email" id="fEmail" required placeholder="you@company.com" autocomplete="email"></div>
<div class="field"><label for="fHeard">How did you find Claimly?</label>
<select name="heard_about" id="fHeard" required><option value="">Choose one</option><option>Google search</option><option>Reddit</option><option>X / Twitter</option><option>LinkedIn</option><option>Instagram</option><option>Facebook</option><option>Indie Hackers / Product Hunt</option><option>Friend or colleague</option><option>Domain marketplace (Afternic, Dan, Sedo)</option><option>AI assistant (ChatGPT, Claude…)</option><option>Other</option></select></div>
<input type="hidden" name="referrer" id="fRef"><input type="hidden" name="landing_page" id="fLand">
<input type="hidden" name="utm_source" id="fUs"><input type="hidden" name="utm_medium" id="fUm"><input type="hidden" name="utm_campaign" id="fUc">
<p class="reassure" style="margin:0 0 10px">By placing your order, you confirm this information is correct and you authorize this purchase right now.</p>
<button class="btn btn-cta wide" type="submit" id="payBtn">Continue to secure payment &rarr;</button>
<p class="reassure">Card or PayPal &middot; processed by PayPal &middot; we never see your card</p>
</form>
</div>
<div class="m-done" id="mDone">
<div class="m-kicker">Almost done</div>
<h3>Complete payment in the PayPal tab</h3>
<p>Your order for <strong id="dName"></strong> is saved. In PayPal, pay <strong>$<span id="dPrice"></span></strong> and add <code id="dNote"></code> in the note so we can match your payment.</p>
<p>We&rsquo;ll email you at <strong id="dEmail"></strong> as soon as the domain is yours.</p>
<a class="btn btn-cta wide" id="dLink" target="_blank" rel="noopener">PayPal didn&rsquo;t open? Pay here &rarr;</a>
<p class="reassure">Questions? <a href="mailto:{EMAIL}" style="color:var(--cobalt)">{EMAIL}</a></p>
<p class="reassure" style="margin-top:14px"><strong>Next:</strong> <a href="/launch/" style="color:var(--cobalt)">get a company license, website and email for your new name &rarr;</a></p>
</div>
</div></div>
<script>
const PAY_BASE="{PAY_BASE}";
let CUR=null;
function findD(f){{return (typeof BYF!=='undefined'&&BYF[f])||(window.CLAIMLY_D&&window.CLAIMLY_D.fqdn===f?window.CLAIMLY_D:null);}}
function openModal(f){{const d=findD(f);if(!d)return;CUR=d;
 document.getElementById('mName').textContent=d.fqdn;document.getElementById('mPrice').textContent=d.price;
 document.getElementById('fDomain').value=d.fqdn;document.getElementById('fPrice').value=d.price;
 const a=claimlyAttr();document.getElementById('fRef').value=a.ref||'(direct)';document.getElementById('fLand').value=a.land||'';document.getElementById('fUs').value=a.us||'';document.getElementById('fUm').value=a.um||'';document.getElementById('fUc').value=a.uc||'';
 document.getElementById('mForm').style.display='block';document.getElementById('mDone').classList.remove('on');
 document.getElementById('modalBg').classList.add('open');setTimeout(()=>document.getElementById('fEmail').focus(),50);}}
function closeModal(){{document.getElementById('modalBg').classList.remove('open');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeModal();}});
document.getElementById('orderForm').addEventListener('submit',function(e){{
 e.preventDefault();if(!CUR)return;const f=e.target;if(!f.reportValidity())return;
 const link=PAY_BASE+'/'+CUR.price+'USD';
 const w=window.open(link,'_blank');try{{if(w)w.opener=null;}}catch(_){{}}
 if(!f['bot-field'].value){{const v=n=>(f[n]&&f[n].value||'').trim().slice(0,480);
  claimlySave('claimly_orders',{{domain:CUR.fqdn,price:Number(CUR.price),email:v('email'),heard_about:v('heard_about'),referrer:v('referrer'),landing_page:v('landing_page'),utm_source:v('utm_source').slice(0,100),utm_medium:v('utm_medium').slice(0,100),utm_campaign:v('utm_campaign').slice(0,100)}});}}
 document.getElementById('dName').textContent=CUR.fqdn;document.getElementById('dPrice').textContent=CUR.price;
 document.getElementById('dNote').textContent=CUR.fqdn;document.getElementById('dEmail').textContent=document.getElementById('fEmail').value;
 document.getElementById('dLink').href=link;
 document.getElementById('mForm').style.display='none';document.getElementById('mDone').classList.add('on');
 if(!w)location.href=link;
}});
</script>
"""

# ───────────────────────── domain pages ─────────────────────────
def describe(d):
    n = d["name"]; c = d["cat"]
    L = len(n)
    length_note = ("short and punchy" if L <= 6 else "easy to say and spell" if L <= 9 else "descriptive and memorable")
    ext_note = {"com":"the .com extension people trust and type by default","co":"the short .co extension popular with startups",
                "io":"the .io extension loved by tech and SaaS founders","ai":"the .ai extension for AI products",
                "xyz":"the modern .xyz extension","app":"the .app extension (HTTPS built in) for apps",
                "eco":"the .eco extension for sustainability brands","studio":"the .studio extension for creative work",
                "shop":"the .shop extension for online stores","store":"the .store extension for retail",
                "tech":"the .tech extension for technology brands","dev":"the .dev extension for developers"}.get(d["ext"], "a clean extension")
    return (f"{d['fqdn']} is a brandable domain name that suits {CAT_BLURB.get(c,'new businesses')}. "
            f"At {L} letters it&rsquo;s {length_note}, and it uses {ext_note}.")

import seo_content as _SC
IDEA_LINKS = {}
for _c in CATS:
    _ts = [t for t in _SC.IDEAS if _c in t[3]][:4]
    if _ts:
        IDEA_LINKS[_c] = '<p style="margin-top:10px">Name ideas: ' + " &middot; ".join(f'<a href="/business-name-ideas/{t[0]}/" style="color:var(--cobalt);font-weight:600">{esc(t[1].lower())}</a>' for t in _ts) + '</p>'

def domain_page(d, idx):
    same = [x for x in BYCAT[d["cat"]] if x["fqdn"] != d["fqdn"]]
    rnd = random.Random(d["fqdn"])
    related = rnd.sample(same, min(8, len(same)))
    canon = f"{SITE}/d/{d['fqdn']}/"
    title = f"{d['fqdn']} is for sale — ${d['price']} | Claimly"
    desc = f"Buy {d['fqdn']}, a brandable {d['cat'].lower()} domain name, for ${d['price']}. First year included, delivered same day, full refund if not delivered."
    prod = {"@context":"https://schema.org","@type":"Product","name":d["fqdn"],"description":html.unescape(re.sub('<[^>]+>','',describe(d))),
            "image":SITE+"/og-image.png","url":canon,"category":d["cat"]+" domain names","brand":{"@type":"Brand","name":"Claimly"},
            "offers":{"@type":"Offer","price":str(d["price"]),"priceCurrency":"USD","availability":"https://schema.org/InStock","url":canon,"priceValidUntil":"2027-12-31",
                      "seller":{"@type":"Organization","name":"Claimly"}}}
    crumbs = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Claimly","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":f"{d['cat']} domains","item":f"{SITE}/domains/{slug(d['cat'])}/"},
        {"@type":"ListItem","position":3,"name":d["fqdn"],"item":canon}]}
    ld = '<script type="application/ld+json">'+json.dumps(prod)+'</script>\n<script type="application/ld+json">'+json.dumps(crumbs)+'</script>'
    rel = "".join(f'<a href="/d/{x["fqdn"]}/">{x["fqdn"]}<span>${x["price"]}</span></a>' for x in related)
    jsd = json.dumps({"fqdn":d["fqdn"],"price":d["price"]})
    tier_tag = {"premium":"Premium","standard":"Standard","starter":"Great value"}[d["tier"]]
    return head(title, desc, canon, ld) + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; <a href="/domains/{slug(d['cat'])}/">{esc(d['cat'])} domains</a> &rsaquo; {d['fqdn']}</div>
<div class="dcard">
<div>
<h1 class="dname">{d['fqdn']}</h1>
<div class="dmeta"><span class="tag ok">Available</span><span class="tag">{esc(d['cat'])}</span><span class="tag">{tier_tag}</span><span class="tag">.{d['ext']}</span></div>
<p class="prose" style="margin:0">{describe(d)}</p>
</div>
<div class="dside">
<div class="dprice"><small>$</small>{d['price']}</div>
<p>One-time price &middot; first year of registration included</p>
<button class="btn btn-cta wide" style="margin-top:14px" onclick="openModal('{d['fqdn']}')">Buy {d['fqdn']} &rarr;</button>
<p>Card or PayPal &middot; usually delivered same day &middot; full refund if not delivered</p>
<p style="color:#1E7A4C;font-weight:600;margin-top:8px">&#10003; Checked available on {datetime.date.fromisoformat(CHECKED.get(d['fqdn'], TODAY)).strftime('%-d %b %Y')}</p>
</div>
</div>
<div class="prose">
<h2>What you get</h2>
<p>When you buy {d['fqdn']} we register it in your name, or transfer it to your registrar account if you prefer (just reply to our email). You own it outright and renew it yourself each year at your registrar&rsquo;s normal rate. We email you at each step, and if the name can&rsquo;t be delivered for any reason you get a full refund.</p>
<h2>Good fit for</h2>
<p>{esc(d['cat'])} businesses: {CAT_BLURB.get(d['cat'],'new businesses')}. Not quite right? Try the <a href="/#finder" style="color:var(--cobalt);font-weight:600">AI name finder</a> or browse more names below.</p>
{IDEA_LINKS.get(d['cat'], '')}
<div style="background:var(--bone2);border:1px solid var(--line);border-radius:16px;padding:18px 20px;margin-top:22px;display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap"><div><b style="font-family:'Schibsted Grotesk';font-size:18px">Not sure this is the one?</b><br><span style="color:var(--muted)">Get 10 names made for your business, domains checked, in 48 hours.</span></div><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn btn-cta" href="/name-my-business/?utm_source=domain-page">Name my business{f" &middot; ${PKG_FROM}" if OFFER_ON else ""} &rarr;</a><a class="btn" style="border:1px solid var(--ink)" href="/name-my-business/?utm_source=domain-page#free">3 free ideas</a></div></div>
</div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px;margin:34px 0 14px">Similar {esc(d['cat'].lower())} domains</h2>
<div class="linkgrid">{rel}</div>
<p style="margin-top:18px"><a class="btn btn-ghost" href="/domains/{slug(d['cat'])}/">All {esc(d['cat'].lower())} domains &rarr;</a></p>
</div></main>
<div class="buybar"><span><b>{d['fqdn']}</b> &middot; ${d['price']}</span><button class="btn btn-cta" onclick="openModal('{d['fqdn']}')">Buy now</button></div>
<style>.buybar{{display:none}}@media(max-width:700px){{.buybar{{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:40;justify-content:space-between;align-items:center;gap:10px;background:var(--bone2);border-top:1px solid var(--line);padding:10px max(16px,env(safe-area-inset-right,0px)) calc(10px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px))}}.buybar span{{font-size:14px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}footer{{padding-bottom:80px}}}}</style>
<script>window.CLAIMLY_D={jsd};</script>
""" + footer() + modal() + "</body></html>"

# ───────────────────────── category pages ─────────────────────────
def cat_page(c):
    items = sorted(BYCAT[c], key=lambda x: (-["starter","standard","premium"].index(x["tier"]), x["fqdn"]))
    canon = f"{SITE}/domains/{slug(c)}/"
    lo = min(x["price"] for x in items); hi = max(x["price"] for x in items)
    title = f"Brandable {c} Domain Names for Sale | Claimly"
    desc = f"Browse available {c.lower()} domain names from ${lo}, ideal for {CAT_BLURB[c]}. Same-day delivery, pay by card or PayPal."
    il = {"@context":"https://schema.org","@type":"ItemList","name":f"{c} domain names",
          "itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/d/{x['fqdn']}/","name":x["fqdn"]} for i,x in enumerate(items[:50])]}
    ld = '<script type="application/ld+json">'+json.dumps(il)+'</script>'
    links = "".join(f'<a href="/d/{x["fqdn"]}/">{x["fqdn"]}<span>${x["price"]}</span></a>' for x in items)
    others = "".join(f'<a class="chip" href="/domains/{slug(o)}/">{esc(o)}</a>' for o in CATS if o != c)
    return head(title, desc, canon, ld) + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; {esc(c)} domains</div>
<h1>Brandable {esc(c.lower())} domain names</h1>
<p class="section-sub">Available names from ${lo} to ${hi}, picked for {CAT_BLURB[c]}. Each price includes the first year of registration, and most orders are delivered the same day.</p>
<div class="linkgrid">{links}</div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px;margin:40px 0 14px">Other categories</h2>
<div class="catlinks">{others}</div>
</div></main>
""" + footer() + "</body></html>"

def recent(days=7):
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    return [d for d in D if ADDED.get(d["fqdn"], "") >= cutoff]

def new_page():
    items = recent(14) or D[:50]
    canon = f"{SITE}/new/"
    title = "New Brandable Domain Names This Week | Claimly"
    desc = f"Fresh brandable domain names added to Claimly in the last two weeks, from ${min(x['price'] for x in items)}. New names every day."
    il = {"@context":"https://schema.org","@type":"ItemList","name":"New domain names","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/d/{x['fqdn']}/","name":x["fqdn"]} for i,x in enumerate(items[:50])]}
    groups = {}
    for x in items: groups.setdefault(ADDED.get(x["fqdn"], TODAY), []).append(x)
    body = ""
    for day in sorted(groups, reverse=True):
        nice = datetime.date.fromisoformat(day).strftime("%-d %B %Y")
        links = "".join(f'<a href="/d/{x["fqdn"]}/">{x["fqdn"]}<span>${x["price"]}</span></a>' for x in groups[day])
        body += f'<h2 style="font-family:\'Schibsted Grotesk\';font-size:20px;margin:30px 0 12px">Added {nice}</h2><div class="linkgrid">{links}</div>'
    return head(title, desc, canon, '<script type="application/ld+json">'+json.dumps(il)+'</script>') + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; New this week</div>
<h1>New brandable domain names</h1>
<p class="section-sub">We add fresh, availability-checked names every day. Here are the latest.</p>
{body}
</div></main>""" + footer() + "</body></html>"

def trending_html():
    if not TRENDS.get("date"): return ""
    picks = [d for d in D if TREND_WORD.get(d["fqdn"]) and ADDED.get(d["fqdn"]) == TRENDS["date"]][:8]
    cats = [c["category"] for c in TRENDS.get("categories", []) if c["category"] in CATS][:5]
    if not picks and not cats: return ""
    words = sorted({TREND_WORD[d["fqdn"]] for d in picks})
    links = "".join(f'<a href="/d/{d["fqdn"]}/">{d["fqdn"]}<span>${d["price"]}</span></a>' for d in picks)
    chips = "".join(f'<a class="chip" href="/domains/{slug(c)}/">{esc(c)}</a>' for c in cats)
    nice = datetime.date.fromisoformat(TRENDS["date"]).strftime("%-d %B")
    return f"""<section class="section-pad" id="trending" style="padding-top:0"><div class="wrap">
<h2>Trending in search today</h2>
<p class="section-sub">Fresh names inspired by what the world is searching on Google ({nice}){(": " + ", ".join(words)) if words else ""}.</p>
{f'<div class="linkgrid" style="margin-bottom:16px">{links}</div>' if links else ''}
{f'<div class="catlinks">{chips}</div>' if chips else ''}
</div></section>"""

SEG_OF = {x["d"]: x["s"] for x in INV if x.get("s")}
SEG_IDEA = {"AI agents": "ai-agent", "Automation": "saas", "Payments": "fintech", "Health & care": "clinic",
            "Clean energy": "solar-company", "Creators": "content-creator", "Online stores": "online-store",
            "UAE real estate": "real-estate", "Cafes & food": "coffee-shop", "Beauty & fashion": "salon",
            "Travel & stays": "travel-agency", "Learning": "tutoring", "Legal & business": "law-firm", "Pets": "pet-business"}

def segments_html():
    """Home section: easy two-word names for the markets buyers are spending in."""
    by = {}
    for d in D:
        s = SEG_OF.get(d["fqdn"])
        if s and d["fqdn"].endswith((".com", ".co")): by.setdefault(s, []).append(d)
    if not by: return ""
    rnd = random.Random("seg" + TODAY)
    picks = []
    for s in sorted(by):
        rnd.shuffle(by[s]); picks += by[s][:1]
    rnd.shuffle(picks); picks = picks[:12]
    links = "".join(f'<a href="/d/{d["fqdn"]}/">{d["fqdn"]}<span>${d["price"]}</span></a>' for d in picks)
    chips = "".join(f'<a class="chip" href="/business-name-ideas/{SEG_IDEA[s]}/">{esc(s)}</a>' for s in sorted(by) if s in SEG_IDEA)
    return f"""<section class="section-pad" id="markets" style="padding-top:0"><div class="wrap">
<h2>Easy names for hot markets</h2>
<p class="section-sub">Two real words, easy to say, with the domain still free. Picked for the markets where new businesses are starting right now.</p>
<div class="linkgrid" style="margin-bottom:16px">{links}</div>
<div class="catlinks">{chips}</div>
</div></section>"""

# ───────────────────────── naming package page ─────────────────────────
OFFER_END = "2026-11-30"                       # launch price ends after this date
OFFER_ON = TODAY <= OFFER_END
OFFER_TXT = "Launch price until 30 Nov"
REG = {"naming_quick": 69, "naming_starter": 149, "naming_shield": 189, "naming_duo": 298,
       "naming_brand": 299, "naming_bilingual": 349, "naming_launch": 499}
LAUNCH = {"naming_quick": 49, "naming_starter": 99, "naming_shield": 139, "naming_duo": 159,
          "naming_brand": 199, "naming_bilingual": 249, "naming_launch": 349}
PKG_FROM = LAUNCH["naming_starter"] if OFFER_ON else REG["naming_starter"]
def _pp(k): return LAUNCH[k] if OFFER_ON else REG[k]
# key, name, price, features, badge
PACKAGES = [
    ("naming_quick", "Quick Pick", _pp("naming_quick"), ["3 names made for your business", ".com checked for each", "Your favourite domain registered for you (first year included)", "Delivered within 24 hours"], ""),
    ("naming_starter", "Starter", _pp("naming_starter"), ["10 hand-picked, available names made for your business", "Each name checked for .com / .co availability", "Your favourite domain registered for you (first year included)", "Matching handle check on Instagram, X and LinkedIn", "Delivered by email within 48 hours"], "Most popular"),
    ("naming_shield", "Name + Shield", _pp("naming_shield"), ["Everything in Starter", "Your name also registered as .co and .net, so no one can copy it", "Handle check on Instagram, TikTok, X and LinkedIn", "Delivered within 48 hours"], ""),
    ("naming_brand", "Brand kit", _pp("naming_brand"), ["Everything in Starter", "Simple wordmark logo concept for your chosen name", "Colour palette and font pairing", "Short tagline options", "One round of changes, delivered within 3 days"], ""),
    ("naming_bilingual", "Bilingual Brand", _pp("naming_bilingual"), ["Everything in Brand kit", "Every name checked for Arabic pronunciation and meaning", "Wordmark in English and Arabic", "Arabic and English taglines", "Made for UAE and Saudi customers, delivered within 4 days"], "Gulf favourite"),
    ("naming_launch", "Founder Launch", _pp("naming_launch"), ["Everything in Brand kit", "One-page website live on your new domain", "Business email setup guide (you@yourname.com)", "Instagram starter kit: bio, profile image, 3 post templates", "Delivered within 7 days"], "Everything to launch"),
    ("naming_duo", "Duo: 2 businesses", _pp("naming_duo"), ["Two Starter packages, for you and a friend or a second idea", "10 names + registered domain for each", "Delivered within 48 hours"], ""),
]

FREE_FORM = """<div class="pk-form" id="free" style="scroll-margin-top:90px">
<div id="frFields">
<div style="font-family:'JetBrains Mono';font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)">Not ready to order?</div>
<h2 style="font-family:'Schibsted Grotesk';margin:6px 0 6px;font-size:22px">Get 3 free name ideas</h2>
<p style="margin:0 0 14px;color:var(--muted)">Tell us about your business. We email you 3 name ideas with available domains within 24 hours. Free, no card needed.</p>
<form onsubmit="return frSubmit(event)">
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<div class="field"><label for="frEmail">Your email</label><input type="email" id="frEmail" name="email" required placeholder="you@company.com" autocomplete="email" maxlength="200"></div>
<div class="field"><label for="frBiz">What does your business do?</label><textarea id="frBiz" name="details" required maxlength="1400" style="font-family:'Hanken Grotesk';font-size:15px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--bone);min-height:90px;resize:vertical;width:100%;box-sizing:border-box" placeholder="e.g. Home bakery in Riyadh, custom cakes for birthdays"></textarea></div>
<button class="btn btn-cta wide" type="submit">Send me 3 free names &rarr;</button>
<p class="reassure">One email with your names. No spam.</p>
</form></div>
<div id="frDone" style="display:none;text-align:center"><h3 style="font-family:'Schibsted Grotesk'">Got it! Your 3 names are on the way.</h3><p>Check your inbox within 24 hours (and the spam folder, just in case).</p></div>
</div>
<script>
function frSubmit(e){e.preventDefault();var f=e.target;if(f['bot-field'].value)return false;var a=claimlyAttr();
 claimlySave('claimly_leads',{kind:'free_names',email:f.email.value.trim().slice(0,200),details:f.details.value.trim().slice(0,1400),consent:true,page:location.pathname.slice(0,300),utm_source:(a.us||'').slice(0,100)});
 document.getElementById('frFields').style.display='none';document.getElementById('frDone').style.display='block';return false;}
</script>"""

def package_page():
    canon = f"{SITE}/name-my-business/"
    title = "Name My Business: Business Name + Domain Package | Claimly"
    desc = "Struggling to name your business? Get 10 checked, available brand names and your domain registered for you, from ${PKG_FROM}. Optional logo and brand kit."
    ld = {"@context":"https://schema.org","@type":"Service","name":"Business naming package","provider":{"@type":"Organization","name":"Claimly","url":SITE+"/"},
          "areaServed":"Worldwide","offers":[{"@type":"Offer","name":n,"price":str(pr),"priceCurrency":"USD","url":canon} for _,n,pr,_,_ in PACKAGES]}
    cards = "".join(f"""<div class="pk{' pk-hi' if badge else ''}">
<div class="pk-name">{esc(n)}{f'<span class="pk-tag">{esc(badge)}</span>' if badge else ''}</div>
<div class="pk-price"><small>$</small>{pr}{f' <s style="font-size:22px;color:var(--muted);font-weight:600">${REG[k]}</s>' if OFFER_ON else ''}</div>{f'<div style="color:var(--red,#E0231C);font-weight:700;font-size:14px;margin:-6px 0 10px">{OFFER_TXT}</div>' if OFFER_ON else ''}
<ul>{''.join(f'<li>{esc(x)}</li>' for x in feats)}</ul>
<button class="btn btn-cta wide" type="button" onclick="pickPk('{k}')">Choose {esc(n)}</button>
</div>""" for i,(k,n,pr,feats,badge) in enumerate(PACKAGES))
    opts = "".join(f'<option value="{k}" data-price="{pr}"{" selected" if k=="naming_starter" else ""}>{esc(n)} &middot; ${pr}</option>' for k,n,pr,_,_ in PACKAGES)
    faq = [("How does it work?","Tell us about your business. Within 48 hours you get 10 names that fit it, each with an available domain. Pick your favourite and we register it for you."),
           ("What if I don’t like any of the names?","Reply and tell us why. We send a second set of names at no extra cost."),
           ("Which domain extensions are included?",".com, .co, .io, .app and similar are included in the price. Premium or already-owned names are not."),
           ("Do you work with businesses in the UAE and Saudi Arabia?","Yes. We work with founders everywhere, and we can suggest names that work in both English and Arabic markets.")]
    faq_html = "".join(f"<details class='pk-faq'><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q,a in faq)
    return head(title, desc, canon, '<script type="application/ld+json">'+json.dumps(ld)+'</script>') + f"""
<style>
.pk-wrap{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:26px 0 34px}}
@media(max-width:1000px){{.pk-wrap{{grid-template-columns:1fr 1fr}}}}
.pk{{background:var(--bone2);border:1px solid var(--line);border-radius:18px;padding:24px;display:flex;flex-direction:column}}
.pk-hi{{border:2px solid var(--ink)}}
.pk-name{{font-family:'Schibsted Grotesk';font-weight:800;font-size:20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.pk-tag{{font-size:11.5px;font-weight:700;background:var(--ink);color:var(--bone);padding:3px 9px;border-radius:99px}}
.pk-price{{font-family:'Schibsted Grotesk';font-weight:900;font-size:44px;margin:8px 0 10px}}.pk-price small{{font-size:20px;color:var(--muted)}}
.pk ul{{margin:0 0 20px;padding-left:18px;flex:1}}.pk li{{margin:6px 0;font-size:15px}}
.pk-form{{background:var(--bone2);border:1px solid var(--line);border-radius:18px;padding:24px;max-width:620px;margin:0 auto 34px;scroll-margin-top:90px}}
.pk-form textarea{{font-family:'Hanken Grotesk';font-size:15px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--bone);min-height:110px;resize:vertical}}
.pk-steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:8px 0 30px}}.pk-steps div{{border-top:2px solid var(--ink);padding-top:10px;font-size:15px}}.pk-steps b{{display:block;font-family:'Schibsted Grotesk';margin-bottom:4px}}
.pk-faq{{border-bottom:1px solid var(--line);padding:12px 0}}.pk-faq summary{{font-weight:700;cursor:pointer}}.pk-faq p{{margin:8px 0 0;color:var(--muted)}}
#pkDone{{display:none;text-align:center}}
@media(max-width:760px){{.pk-wrap,.pk-steps{{grid-template-columns:1fr}}}}
</style>
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; Name my business</div>
<h1>Name your business in 48 hours</h1>
<p class="section-sub">Stuck on a name? Tell us what you do. We send you 10 brandable names with available domains, then register your favourite for you.</p>
<div class="pk-steps"><div><b>1. Tell us about it</b>What you do, who it&rsquo;s for, the feel you want.</div><div><b>2. Get 10 names</b>Checked and available, delivered by email.</div><div><b>3. Pick and launch</b>We register your domain. You start building.</div></div>
<div class="pk-wrap">{cards}</div>
<form class="pk-form" id="pkForm" onsubmit="return pkSubmit(event)">
<div id="pkFields">
<h2 style="font-family:'Schibsted Grotesk';margin:0 0 14px;font-size:22px">Start your order</h2>
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<div class="field"><label for="pkKind">Package</label><select id="pkKind" name="kind" required>{opts}</select></div>
<div class="field"><label for="pkEmail">Your email</label><input type="email" id="pkEmail" name="email" required placeholder="you@company.com" autocomplete="email" maxlength="200"></div>
<div class="field"><label for="pkBiz">What does your business do?</label><textarea id="pkBiz" name="business" required maxlength="1500" placeholder="e.g. A home cleaning service in Dubai for busy families. Friendly, trustworthy, modern."></textarea></div>
<div class="field"><label for="pkCountry">Country</label><input id="pkCountry" name="country" maxlength="80" placeholder="e.g. UAE"></div>
<div class="field"><label for="pkNotes">Names or words you like or dislike (optional)</label><input id="pkNotes" name="notes" maxlength="1500"></div>
<div class="field"><label for="pkHeard">How did you find Claimly?</label><select id="pkHeard" name="heard_about" required><option value="">Choose one</option><option>Google search</option><option>LinkedIn</option><option>X / Twitter</option><option>Reddit</option><option>Instagram</option><option>Friend or colleague</option><option>AI assistant (ChatGPT, Claude…)</option><option>Other</option></select></div>
<p class="reassure" style="margin:0 0 10px">By placing your order, you confirm this information is correct and you authorize this purchase right now.</p>
<button class="btn btn-cta wide" type="submit">Continue to secure payment &rarr;</button>
<p class="reassure">Card or PayPal &middot; processed by PayPal &middot; full refund if we can&rsquo;t deliver</p>
</div>
<div id="pkDone"><h3 style="font-family:'Schibsted Grotesk'">Complete payment in the PayPal tab</h3><p>Your order is saved. In PayPal, pay <strong>$<span id="pkPrice"></span></strong> and add your email in the note so we can match it. Your names arrive within 48 hours of payment.</p><p class="reassure">PayPal didn&rsquo;t open? <a id="pkLink" href="#" target="_blank" rel="noopener">Open PayPal</a></p><p class="reassure" style="margin-top:14px"><strong>Next:</strong> <a href="/launch/">company license, website and email for your business &rarr;</a></p></div>
</form>
{FREE_FORM}
<h2 style="font-family:'Schibsted Grotesk';font-size:22px">Questions</h2>
{faq_html}
<p style="margin:28px 0 0">Prefer to pick a name yourself? <a href="/#shop">Browse ready-to-register names</a> from $15.</p>
</div></main>
<script>
function pickPk(k){{document.getElementById('pkKind').value=k;var f=document.getElementById('pkForm');f.scrollIntoView({{behavior:'smooth'}});setTimeout(function(){{document.getElementById('pkEmail').focus()}},400);}}
function pkSubmit(e){{e.preventDefault();var f=e.target;if(f['bot-field'].value)return false;
 var sel=document.getElementById('pkKind'),price=Number(sel.options[sel.selectedIndex].dataset.price),a=claimlyAttr(),v=function(n){{return (f[n].value||'').trim();}};
 claimlySave('claimly_orders',{{kind:sel.value,domain:('Naming package: '+sel.options[sel.selectedIndex].text.split(' \u00b7')[0]).slice(0,80),price:price,email:v('email').slice(0,200),business:v('business').slice(0,1500),country:v('country').slice(0,80),notes:v('notes').slice(0,1500),heard_about:v('heard_about'),referrer:(a.ref||'').slice(0,500),landing_page:(a.land||location.pathname).slice(0,500),utm_source:a.us||'',utm_medium:a.um||'',utm_campaign:a.uc||''}});
 var url='{PAY_BASE}/'+price+'USD';window.open(url,'_blank','noopener');
 document.getElementById('pkPrice').textContent=price;document.getElementById('pkLink').href=url;
 document.getElementById('pkFields').style.display='none';document.getElementById('pkDone').style.display='block';return false;}}
</script>""" + footer() + "</body></html>"

# ───────────────────────── launch + partners pages ─────────────────────────
PARTNERS = json.load(open(os.path.join(ROOT, "data", "partners.json")))
LP_CSS = """<style>
.lp-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:26px 0 34px}
.lp{background:var(--bone2);border:1px solid var(--line);border-radius:18px;padding:24px;display:flex;flex-direction:column;gap:10px}
.lp h2{font-family:'Schibsted Grotesk';font-size:21px;margin:0}.lp p{margin:0;color:var(--muted);flex:1}
.lp .by{font-size:13px;font-weight:700;color:var(--ink)}
.lp-btns{display:flex;gap:10px;flex-wrap:wrap}
.btn-ghost{background:transparent;border:1px solid var(--ink);color:var(--ink)}
.lp-form{background:var(--bone2);border:1px solid var(--line);border-radius:18px;padding:24px;max-width:620px;margin:0 auto 30px;scroll-margin-top:90px}
.lp-form textarea{font-family:'Hanken Grotesk';font-size:15px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--bone);min-height:90px;resize:vertical}
.lp-check{display:flex;gap:10px;align-items:flex-start;font-size:14px;margin:6px 0 14px}.lp-check input{margin-top:3px}
.lp-ok{display:none;text-align:center}
.disclose{font-size:13px;color:var(--muted);text-align:center;margin:0 0 30px}
.pk-wrap{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:26px 0 34px}
.pk{background:var(--bone2);border:1px solid var(--line);border-radius:18px;padding:24px;display:flex;flex-direction:column}
.pk-hi{border:2px solid var(--ink)}.pk-name{font-family:'Schibsted Grotesk';font-weight:800;font-size:20px}
.pk-price{font-family:'Schibsted Grotesk';font-weight:900;font-size:44px;margin:8px 0 4px}.pk-price small{font-size:20px;color:var(--muted)}
.pk-each{color:var(--muted);font-size:14px;margin-bottom:10px}.pk ul{margin:0 0 20px;padding-left:18px;flex:1}.pk li{margin:6px 0;font-size:15px}
@media(max-width:760px){.lp-grid,.pk-wrap{grid-template-columns:1fr}}
</style>"""

def launch_page():
    canon = f"{SITE}/launch/"
    title = "Launch Your Business: License, Website & Email | Claimly"
    desc = "Got your name? Next: a UAE company license, a website and a professional email on your domain. Free introductions to trusted partners."
    cards = ""
    for x in PARTNERS:
        visit = ""
        if x.get("url"):
            visit = f'<a class="btn btn-ghost" href="{esc(x["url"])}" target="_blank" rel="sponsored noopener" onclick="lpClick(\'{x["id"]}\')">Visit {esc(x["partner"])} &rarr;</a>'
        by = f'<div class="by">Partner: {esc(x["partner"])}</div>' if x.get("partner") else ""
        cards += (f'<div class="lp"><h2>{esc(x["title"])}</h2>{by}<p>{esc(x["blurb"])}</p>'
                  f'<div class="lp-btns"><button class="btn btn-cta" type="button" onclick="lpPick(\'{x["id"]}\')">{esc(x["cta"])}</button>{visit}</div></div>')
    opts = "".join(f'<option value="{x["id"]}">{esc(x["title"])}</option>' for x in PARTNERS)
    return head(title, desc, canon) + LP_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; Launch your business</div>
<h1>You have the name. Now launch it.</h1>
<p class="section-sub">What every new business needs next. Tell us what you need and we&rsquo;ll introduce you to a trusted partner, free.</p>
<div class="lp-grid">{cards}</div>
<form class="lp-form" id="lpForm" onsubmit="return lpSubmit(event)">
<div id="lpFields">
<h2 style="font-family:'Schibsted Grotesk';margin:0 0 14px;font-size:22px">Get a free introduction</h2>
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<div class="field"><label for="lpNeed">What do you need?</label><select id="lpNeed" name="need">{opts}</select></div>
<div class="field"><label for="lpName">Your name</label><input id="lpName" name="name" required maxlength="200" autocomplete="name"></div>
<div class="field"><label for="lpEmail">Email</label><input type="email" id="lpEmail" name="email" required maxlength="200" autocomplete="email"></div>
<div class="field"><label for="lpPhone">WhatsApp / phone (optional)</label><input id="lpPhone" name="phone" maxlength="50" autocomplete="tel"></div>
<div class="field"><label for="lpDetails">Tell us a little (business type, country, timing)</label><textarea id="lpDetails" name="details" maxlength="1500"></textarea></div>
<label class="lp-check"><input type="checkbox" name="consent" required> I agree that Claimly may share my details with one partner so they can contact me with an offer.</label>
<button class="btn btn-cta wide" type="submit">Send my request &rarr;</button>
</div>
<div class="lp-ok" id="lpOk"><h3 style="font-family:'Schibsted Grotesk'">Thanks, we&rsquo;re on it.</h3><p>We&rsquo;ll email you within one working day with your introduction.</p></div>
</form>
<p class="disclose">Claimly may earn a referral fee from partners. It never changes the price you pay.</p>
</div></main>
<script>
function lpClick(id){{claimlySave('claimly_partner_clicks',{{partner:id,page:location.pathname.slice(0,300)}});}}
function lpPick(id){{document.getElementById('lpNeed').value=id;claimlySave('claimly_partner_clicks',{{partner:id+':intro',page:location.pathname.slice(0,300)}});document.getElementById('lpForm').scrollIntoView({{behavior:'smooth'}});setTimeout(function(){{document.getElementById('lpName').focus()}},400);}}
function lpSubmit(e){{e.preventDefault();var f=e.target;if(f['bot-field'].value)return false;var a=claimlyAttr(),need=f.need.value,v=function(n){{return (f[n].value||'').trim();}};
 claimlySave('claimly_leads',{{kind:need==='store'?'website':need,name:v('name').slice(0,200),email:v('email').slice(0,200),phone:v('phone').slice(0,50),details:((need==='store'?'Online store. ':'')+v('details')).slice(0,1500),consent:f.consent.checked,page:location.pathname.slice(0,300),utm_source:(a.us||'').slice(0,100)}});
 document.getElementById('lpFields').style.display='none';document.getElementById('lpOk').style.display='block';return false;}}
</script>""" + footer() + "</body></html>"

AGENCY = [("agency_5", "5 naming packages", 545, 109, ["5 Starter packages to use for any of your clients", "10 checked names + domain registered, per client", "Delivered to you, unbranded, to pass on", "48-hour turnaround per brief", "Use them within 6 months"]),
          ("agency_10", "10 naming packages", 990, 99, ["10 Starter packages to use for any of your clients", "Everything in the 5-pack", "Priority 24-hour turnaround", "Upgrade any one to a Brand kit for $120", "Use them within 6 months"])]

def partners_page():
    canon = f"{SITE}/partners/"
    title = "Partner Program for Business Setup Firms & Agencies | Claimly"
    desc = "Business setup consultants and agencies: offer your clients a name and domain in 48 hours. Wholesale naming packages from $99 each."
    cards = ""
    for i, (k, n, pr, each, feats) in enumerate(AGENCY):
        lis = "".join(f"<li>{esc(x)}</li>" for x in feats)
        hi = " pk-hi" if i == 1 else ""
        cards += (f'<div class="pk{hi}"><div class="pk-name">{esc(n)}</div><div class="pk-price"><small>$</small>{pr}</div>'
                  f'<div class="pk-each">${each} per client, paid upfront</div><ul>{lis}</ul>'
                  f'<button class="btn btn-cta wide" type="button" onclick="agPick(\'{k}\')">Choose {esc(n)}</button></div>')
    opts = "".join(f'<option value="{k}" data-price="{pr}">{esc(n)} &middot; ${pr}</option>' for k, n, pr, _, _ in AGENCY) + '<option value="talk" data-price="0">Talk to us first</option>'
    names = json.dumps({k: n for k, n, _, _, _ in AGENCY})
    return head(title, desc, canon) + LP_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; Partners</div>
<h1>Give your clients a name in 48 hours</h1>
<p class="section-sub">For business setup consultants, accountants and agencies. Your clients need a business name and domain before almost anything else. We do the naming; you deliver it under your service.</p>
<div class="pk-wrap">{cards}</div>
<form class="lp-form" id="agForm" onsubmit="return agSubmit(event)">
<div id="agFields">
<h2 style="font-family:'Schibsted Grotesk';margin:0 0 14px;font-size:22px">Become a partner</h2>
<p class="hp"><label>Leave empty <input name="bot-field"></label></p>
<div class="field"><label for="agKind">Option</label><select id="agKind" name="kind">{opts}</select></div>
<div class="field"><label for="agCompany">Company</label><input id="agCompany" name="company" required maxlength="200"></div>
<div class="field"><label for="agName">Your name</label><input id="agName" name="name" required maxlength="200"></div>
<div class="field"><label for="agEmail">Work email</label><input type="email" id="agEmail" name="email" required maxlength="200"></div>
<div class="field"><label for="agPhone">WhatsApp / phone (optional)</label><input id="agPhone" name="phone" maxlength="50"></div>
<p class="reassure" style="margin:0 0 10px">By placing your order, you confirm this information is correct and you authorize this purchase right now.</p>
<button class="btn btn-cta wide" type="submit">Continue &rarr;</button>
<p class="reassure">Bundles are paid upfront by card or PayPal. Unused packages are refundable within 30 days.</p>
</div>
<div class="lp-ok" id="agOk"><h3 style="font-family:'Schibsted Grotesk'" id="agOkH">Thanks!</h3><p id="agOkP"></p></div>
</form>
</div></main>
<script>
var AG_NAMES={names};
function agPick(k){{document.getElementById('agKind').value=k;document.getElementById('agForm').scrollIntoView({{behavior:'smooth'}});setTimeout(function(){{document.getElementById('agCompany').focus()}},400);}}
function agSubmit(e){{e.preventDefault();var f=e.target;if(f['bot-field'].value)return false;var a=claimlyAttr(),sel=f.kind,k=sel.value,price=Number(sel.options[sel.selectedIndex].dataset.price),v=function(n){{return (f[n].value||'').trim();}};
 claimlySave('claimly_leads',{{kind:'agency',name:v('name').slice(0,200),email:v('email').slice(0,200),phone:v('phone').slice(0,50),company:v('company').slice(0,200),details:k,consent:true,page:location.pathname.slice(0,300),utm_source:(a.us||'').slice(0,100)}});
 if(k!=='talk'){{claimlySave('claimly_orders',{{kind:k,domain:'Agency bundle: '+AG_NAMES[k],price:price,email:v('email').slice(0,200),business:v('company').slice(0,1500),referrer:(a.ref||'').slice(0,500),landing_page:(a.land||location.pathname).slice(0,500),utm_source:a.us||'',utm_medium:a.um||'',utm_campaign:a.uc||''}});
  var url='{PAY_BASE}/'+price+'USD';window.open(url,'_blank','noopener');
  document.getElementById('agOkH').textContent='Complete payment in the PayPal tab';
  document.getElementById('agOkP').innerHTML='Your order is saved. Pay <strong>$'+price+'</strong> and add your company name in the note. We will email you within one working day to set up your first brief. <a href="'+url+'" target="_blank" rel="noopener">Open PayPal</a>';}}
 else{{document.getElementById('agOkP').textContent='We will email you within one working day.';}}
 document.getElementById('agFields').style.display='none';document.getElementById('agOk').style.display='block';return false;}}
</script>""" + footer() + "</body></html>"

# ───────────────────────── SEO: business name ideas + guides ─────────────────────────
import seo_content as SC
SEO_CSS = """<style>
.idea-intro{max-width:68ch;font-size:17px;line-height:1.6;color:var(--muted)}
.namegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:22px 0 8px}
.namegrid a{display:flex;justify-content:space-between;align-items:center;gap:10px;background:var(--bone2);border:1px solid var(--line);border-radius:12px;padding:13px 15px;text-decoration:none;color:var(--ink);font-weight:700;font-size:16px}
.namegrid a span{font-size:13px;font-weight:700;color:#fff;background:var(--red,#E0231C);border-radius:99px;padding:3px 9px}
.namegrid a:hover{border-color:var(--ink)}
.tips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:10px 0 0}
.tips div{border-top:2px solid var(--ink);padding-top:10px;font-size:15px;line-height:1.5}
.tips b{display:block;font-family:'Schibsted Grotesk';margin-bottom:4px}
.cta-band{background:var(--ink);color:var(--bone);border-radius:20px;padding:26px;display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;margin:36px 0}
.cta-band h2{font-family:'Schibsted Grotesk';margin:0 0 6px;font-size:24px}.cta-band p{margin:0;opacity:.8;max-width:52ch}
.faq details{border-bottom:1px solid var(--line);padding:13px 0}.faq summary{font-weight:700;cursor:pointer}.faq p{margin:8px 0 0;color:var(--muted);max-width:70ch}
.ideas-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:20px 0}
.ideas-list a{display:block;background:var(--bone2);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink);font-weight:700}
.ideas-list a small{display:block;font-weight:500;color:var(--muted);margin-top:3px}
.guide{max-width:70ch}.guide h2{font-family:'Schibsted Grotesk';font-size:23px;margin:30px 0 8px}.guide p{font-size:17px;line-height:1.65;margin:0}
@media(max-width:760px){.tips{grid-template-columns:1fr}}
</style>"""

def _ideas_names(t, n=24):
    slug_, label, phrase, cats, kws, intro, tips = t
    pool = [x for x in D if x["cat"] in cats and x["fqdn"].split(".")[1] in ("com", "co", "io", "app", "shop", "studio", "store")]
    label_of = lambda x: x["fqdn"].split(".")[0]
    match = [x for x in pool if any(k in label_of(x) for k in kws)]
    rest = [x for x in pool if x not in match]
    rnd = random.Random(slug_ + TODAY)                 # fresh mix every day
    rnd.shuffle(match); rnd.shuffle(rest)
    # easy two-word segment names first, then other keyword matches, then the rest
    match.sort(key=lambda x: x["fqdn"] not in SEGMENT_NAMES)
    pick = (match + rest)[:n]
    pick.sort(key=lambda x: (x["fqdn"].split(".")[1] != "com", len(x["fqdn"])))
    return pick

def idea_page(t):
    slug_, label, phrase, cats, kws, intro, tips = t
    canon = f"{SITE}/business-name-ideas/{slug_}/"
    names = _ideas_names(t)
    lo = min(x["price"] for x in names) if names else 15
    title = f"{label} Name Ideas with Available Domains | Claimly"
    desc = f"Name ideas for your {phrase}, each with an available domain from ${lo}. Plus practical tips for choosing a {phrase} name that customers remember."
    faqs = [(f"How do I choose a name for my {phrase}?", f"Write down what makes your {phrase} different and how you want customers to feel, list 30+ ideas, cut anything hard to say or spell, then check the domain and social handles before you decide."),
            (f"Are these {phrase} names really available?", "Yes. Every name on this page is checked as unregistered before it is listed, and the list refreshes daily. Prices include the first year of registration, and you get a full refund if a name can't be delivered."),
            (f"Can someone name my {phrase} for me?", f"Yes. With the Claimly naming package you describe your {phrase} and get 10 checked names with available domains within 48 hours, from ${PKG_FROM}. We register the one you pick.")]
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Claimly", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Business name ideas", "item": SITE + "/business-name-ideas/"},
              {"@type": "ListItem", "position": 3, "name": f"{label} name ideas", "item": canon}]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": f"{label} name ideas", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/d/{x['fqdn']}/", "name": x["fqdn"]} for i, x in enumerate(names)]}]
    ldh = "".join('<script type="application/ld+json">' + json.dumps(o) + '</script>' for o in ld)
    grid = "".join(f'<a href="/d/{x["fqdn"]}/">{x["fqdn"]}<span>${x["price"]}</span></a>' for x in names)
    tips_h = "".join(f"<div><b>Tip {i}</b>{esc(tip)}</div>" for i, tip in enumerate(tips, 1))
    faq_h = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)
    others = [o for o in SC.IDEAS if o[0] != slug_ and set(o[3]) & set(cats)][:6] or SC.IDEAS[:6]
    oth = "".join(f'<a href="/business-name-ideas/{o[0]}/">{esc(o[1])} names</a>' for o in others)
    cat_links = " · ".join(f'<a href="/domains/{slug(c)}/">all {esc(c.lower())} domains</a>' for c in cats)
    return head(title, desc, canon, ldh) + SEO_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; <a href="/business-name-ideas/">Business name ideas</a> &rsaquo; {esc(label)}</div>
<h1>{esc(label)} name ideas</h1>
<p class="idea-intro">{esc(intro)} Here are names that fit, each with the domain still available to register today.</p>
<div class="namegrid">{grid}</div>
<p style="color:var(--muted);font-size:14px">Prices include the first year of registration. Updated {datetime.date.today().strftime('%-d %B %Y')}. See {cat_links}.</p>
<h2 style="font-family:'Schibsted Grotesk';font-size:24px;margin:38px 0 6px">How to name your {esc(phrase)}</h2>
<div class="tips">{tips_h}</div>
<div class="cta-band"><div><h2>Want names made for your {esc(phrase)}?</h2><p>Describe your business and get 10 checked names with available domains in 48 hours. We register the one you pick.</p></div>
<a class="btn btn-cta" href="/name-my-business/?utm_source=ideas&amp;utm_medium={slug_}">Get my 10 names{f" &middot; ${PKG_FROM}" if OFFER_ON else ""} &rarr;</a></div>
{FREE_FORM}
<h2 style="font-family:'Schibsted Grotesk';font-size:22px;margin:0 0 6px">Questions</h2>
<div class="faq">{faq_h}</div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px;margin:36px 0 10px">More name ideas</h2>
<div class="ideas-list">{oth}</div>
<p><a href="/guides/how-to-name-a-business/">Read: how to name a business in 7 steps &rarr;</a></p>
</div></main>""" + footer() + "</body></html>"

def ideas_hub():
    canon = f"{SITE}/business-name-ideas/"
    title = "Business Name Ideas by Industry, with Available Domains | Claimly"
    desc = "Business name ideas for bakeries, cafés, salons, agencies, startups and more. Every name comes with an available domain, from $15."
    items = "".join(f'<a href="/business-name-ideas/{t[0]}/">{esc(t[1])} names<small>{esc(t[2].capitalize())}</small></a>' for t in SC.IDEAS)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Business name ideas by industry", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/business-name-ideas/{t[0]}/", "name": f"{t[1]} name ideas"} for i, t in enumerate(SC.IDEAS)]}
    return head(title, desc, canon, '<script type="application/ld+json">' + json.dumps(ld) + '</script>') + SEO_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; Business name ideas</div>
<h1>Business name ideas</h1>
<p class="idea-intro">Pick your type of business to see name ideas that fit, each with an available domain you can register today. Every list refreshes daily with newly checked names.</p>
<div class="ideas-list">{items}</div>
<div class="cta-band"><div><h2>Still stuck?</h2><p>Tell us what you do and get 10 names made for your business, with domains checked, in 48 hours.</p></div><a class="btn btn-cta" href="/name-my-business/?utm_source=ideas-hub">See the naming package &rarr;</a></div>
<p><a href="/guides/">Naming guides &rarr;</a></p>
</div></main>""" + footer() + "</body></html>"

def guide_page(g):
    slug_, title_, summary, sections = g
    canon = f"{SITE}/guides/{slug_}/"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": title_, "description": summary, "url": canon,
          "datePublished": "2026-10-25", "dateModified": TODAY, "author": {"@type": "Organization", "name": "Claimly"},
          "publisher": {"@type": "Organization", "name": "Claimly", "logo": {"@type": "ImageObject", "url": SITE + "/og-image.png"}}, "image": SITE + "/og-image.png"}
    body = "".join(f"<h2>{esc(h)}</h2><p>{esc(p)}</p>" for h, p in sections)
    more = "".join(f'<a href="/guides/{o[0]}/">{esc(o[1])}</a>' for o in SC.GUIDES if o[0] != slug_)
    ideas = "".join(f'<a href="/business-name-ideas/{t[0]}/">{esc(t[1])} names</a>' for t in SC.IDEAS[:8])
    return head(f"{title_} | Claimly", summary, canon, '<script type="application/ld+json">' + json.dumps(ld) + '</script>') + SEO_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; <a href="/guides/">Guides</a> &rsaquo; {esc(title_)}</div>
<article class="guide"><h1>{esc(title_)}</h1><p class="idea-intro" style="margin-top:8px">{esc(summary)}</p>{body}</article>
<div class="cta-band"><div><h2>Find a name with the domain ready</h2><p>Browse checked, available names from $15, or get 10 names made for your business in 48 hours.</p></div><a class="btn btn-cta" href="/name-my-business/?utm_source=guide&amp;utm_medium={slug_}">Get 10 names &rarr;</a></div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px">Name ideas by business</h2><div class="ideas-list">{ideas}</div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px">More guides</h2><div class="ideas-list">{more}</div>
</div></main>""" + footer() + "</body></html>"

def guides_hub():
    canon = f"{SITE}/guides/"
    items = "".join(f'<a href="/guides/{g[0]}/">{esc(g[1])}<small>{esc(g[2])}</small></a>' for g in SC.GUIDES)
    return head("Business Naming Guides | Claimly", "Practical guides on naming a business, choosing a domain name and checking a name is available.", canon) + SEO_CSS + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; Guides</div>
<h1>Naming guides</h1>
<p class="idea-intro">Short, practical guides for founders choosing a business name and domain.</p>
<div class="ideas-list">{items}</div>
</div></main>""" + footer() + "</body></html>"

def notfound():
    return head("Page not found | Claimly", "This page doesn't exist.", SITE+"/404.html", robots="noindex") + f"""
<main class="page"><div class="wrap" style="text-align:center;padding:60px 0">
<h1>That page isn&rsquo;t here</h1>
<p class="section-sub" style="margin:0 auto 24px">The name may have been sold, or the link is wrong.</p>
<a class="btn btn-cta" href="/#shop">Browse available names</a>
</div></main>""" + footer() + "</body></html>"

def sitemap():
    urls = [(SITE+"/", "1.0", "daily", TODAY), (SITE+"/new/", "0.9", "daily", TODAY), (SITE+"/name-my-business/", "0.9", "weekly", TODAY), (SITE+"/launch/", "0.7", "weekly", TODAY), (SITE+"/partners/", "0.6", "monthly", TODAY), (SITE+"/business-name-ideas/", "0.9", "daily", TODAY), (SITE+"/guides/", "0.7", "weekly", TODAY)] + [(f"{SITE}/business-name-ideas/{t[0]}/", "0.8", "daily", TODAY) for t in SC.IDEAS] + [(f"{SITE}/guides/{g[0]}/", "0.7", "monthly", TODAY) for g in SC.GUIDES] + [(f"{SITE}/domains/{slug(c)}/", "0.8", "weekly", TODAY) for c in CATS] + [(f"{SITE}/d/{d['fqdn']}/", "0.6", "monthly", ADDED.get(d["fqdn"], TODAY)) for d in D]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n" for u,p,f,m in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'



def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    SITE_DIR = os.path.join(ROOT, "site")
    for f in os.listdir(SITE_DIR):
        dst = os.path.join(OUT, "assets", f) if f.endswith(".css") else os.path.join(OUT, f)
        shutil.copy(os.path.join(SITE_DIR, f), dst)
    if os.path.isdir(os.path.join(ROOT, "social")):   # Instagram images, used by Metricool
        shutil.copytree(os.path.join(ROOT, "social"), os.path.join(OUT, "social"))
    open(os.path.join(OUT, "index.html"), "w").write(home())
    open(os.path.join(OUT, "404.html"), "w").write(notfound())
    os.makedirs(os.path.join(OUT, "new")); open(os.path.join(OUT, "new", "index.html"), "w").write(new_page())
    os.makedirs(os.path.join(OUT, "business-name-ideas")); open(os.path.join(OUT, "business-name-ideas", "index.html"), "w").write(ideas_hub())
    for t in SC.IDEAS:
        os.makedirs(os.path.join(OUT, "business-name-ideas", t[0])); open(os.path.join(OUT, "business-name-ideas", t[0], "index.html"), "w").write(idea_page(t))
    os.makedirs(os.path.join(OUT, "guides")); open(os.path.join(OUT, "guides", "index.html"), "w").write(guides_hub())
    for g in SC.GUIDES:
        os.makedirs(os.path.join(OUT, "guides", g[0])); open(os.path.join(OUT, "guides", g[0], "index.html"), "w").write(guide_page(g))
    for slug_, fn in (("launch", launch_page), ("partners", partners_page)):
        os.makedirs(os.path.join(OUT, slug_)); open(os.path.join(OUT, slug_, "index.html"), "w").write(fn())
    os.makedirs(os.path.join(OUT, "name-my-business")); open(os.path.join(OUT, "name-my-business", "index.html"), "w").write(package_page())
    for i, d in enumerate(D):
        p = os.path.join(OUT, "d", d["fqdn"]); os.makedirs(p)
        open(os.path.join(p, "index.html"), "w").write(domain_page(d, i))
    for c in CATS:
        p = os.path.join(OUT, "domains", slug(c)); os.makedirs(p)
        open(os.path.join(p, "index.html"), "w").write(cat_page(c))
    open(os.path.join(OUT, "sitemap.xml"), "w").write(sitemap())
    open(os.path.join(OUT, "CNAME"), "w").write("claimly.ae\n")   # GitHub Pages custom domain
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /.netlify/\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"built {N} domain pages ({len(recent())} new this week), {len(CATS)} category pages into {OUT}")

if __name__ == "__main__":
    build()
