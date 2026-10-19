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
RAW = [[x["d"].rsplit(".",1)[0].capitalize(), EXTS.index(x["d"].rsplit(".",1)[1]), x["p"], CATS.index(x["c"]), TIERS.index(x["t"]), ""] for x in INV]
KEYMAP = json.load(open(os.path.join(DATA, "keymap.json")))
TRENDS = {}
try:
    TRENDS = json.load(open(os.path.join(DATA, "trends", "latest.json")))
except Exception:
    pass
TREND_WORD = {x["d"]: x.get("w") for x in INV if x.get("w")}

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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
{extra_ld}
</head>
<body>
<div class="bg" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span></div>
<header><div class="wrap nav">
<a class="brand" href="/">Claimly<span class="reg">&reg;</span></a>
<nav class="nav-links"><a href="/#finder">AI finder</a><a href="/#shop">Browse</a><a href="/#how">How it works</a><a href="/#faq">FAQ</a><a class="btn btn-cta" href="/#finder">Find a domain</a></nav>
</div></header>
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
<details><summary>Privacy Policy</summary><div class="ptext">We collect only what&rsquo;s needed to complete your order: your email, the domain, your registrar, and how you found us. Payments are handled by PayPal; we never see your card details. We don&rsquo;t sell your data.</div></details>
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
    desc = f"{NFMT} short, brandable domain names from ${MINP}. Describe your business and our AI finds names that fit. Pay by card or PayPal, same-day delivery, full refund if not delivered."
    h = head(title, desc, SITE+"/", ld)
    catchips = f'<a class="chip active" href="/new/">New this week ({len(recent())})</a>' + "".join(f'<a class="chip" href="/domains/{slug(c)}/">{esc(c)}</a>' for c in CATS)
    faqhtml = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in faqs)
    data = json.dumps(RAW, separators=(",",":"))
    return h + f"""
<section class="hero" id="finder"><div class="wrap">
<div class="hero-top"><span class="eyebrow"><span class="spark"></span>AI domain finder &middot; {NFMT} available</span><span class="hero-counter">{NFMT} domains &middot; {len(CATS)} categories</span></div>
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
<div class="searchbar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><input id="search" placeholder="Search {NFMT} names…" autocomplete="off" aria-label="Search domains"></div>
<div class="chips" id="chips"></div>
<span class="count" id="count"></span>
<select class="sort" id="sort" aria-label="Sort"><option value="featured">Featured</option><option value="plo">Price &uarr;</option><option value="phi">Price &darr;</option><option value="az">A&ndash;Z</option></select>
</div></div>

<section class="shop"><div class="wrap">
<div class="grid" id="grid"></div>
<p class="empty" id="empty" style="display:none">No matches for that search &mdash; try another keyword, or <a href="mailto:{EMAIL}?subject=Name%20request" style="color:var(--cobalt);font-weight:600">ask us for a custom shortlist</a>.</p>
<div class="loadmore"><button class="btn btn-cta" id="loadMore" style="display:none">Load more</button></div>
</div></section>

<section class="section-pad" id="how"><div class="wrap">
<h2>How it works</h2>
<p class="section-sub">From finding a name to owning it &mdash; usually the same day.</p>
<div class="steps">
<div class="step"><div class="n">01</div><h3>Find your name</h3><p>Search the catalogue or describe your business to the AI finder. Every name is short, brandable and availability-checked.</p></div>
<div class="step"><div class="n">02</div><h3>Order &amp; pay</h3><p>Enter your email and registrar, then pay by card or PayPal. PayPal&rsquo;s buyer protection applies, and you get a full refund if we can&rsquo;t deliver.</p></div>
<div class="step"><div class="n">03</div><h3>Get your domain</h3><p>We register the domain in your name or transfer it to your registrar account, and email you as soon as it&rsquo;s yours.</p></div>
</div>
</div></section>

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
const grid=document.getElementById('grid'),countEl=document.getElementById('count'),emptyEl=document.getElementById('empty'),
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
 countEl.textContent=list.length.toLocaleString()+' names';
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
<div class="field"><label for="fReg">Where should we deliver it?</label>
<select name="registrar" id="fReg"><option>Not sure &mdash; register it for me</option><option>GoDaddy</option><option>Namecheap</option><option>Cloudflare</option><option>Google / Squarespace</option><option>Tasjeel / AE registrar</option><option>Other (I&rsquo;ll reply by email)</option></select></div>
<div class="field"><label for="fHeard">How did you find Claimly?</label>
<select name="heard_about" id="fHeard" required><option value="">Choose one</option><option>Google search</option><option>Reddit</option><option>X / Twitter</option><option>LinkedIn</option><option>Instagram</option><option>Facebook</option><option>Indie Hackers / Product Hunt</option><option>Friend or colleague</option><option>Domain marketplace (Afternic, Dan, Sedo)</option><option>AI assistant (ChatGPT, Claude…)</option><option>Other</option></select></div>
<input type="hidden" name="referrer" id="fRef"><input type="hidden" name="landing_page" id="fLand">
<input type="hidden" name="utm_source" id="fUs"><input type="hidden" name="utm_medium" id="fUm"><input type="hidden" name="utm_campaign" id="fUc">
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
  claimlySave('claimly_orders',{{domain:CUR.fqdn,price:Number(CUR.price),email:v('email'),registrar:v('registrar'),heard_about:v('heard_about'),referrer:v('referrer'),landing_page:v('landing_page'),utm_source:v('utm_source').slice(0,100),utm_medium:v('utm_medium').slice(0,100),utm_campaign:v('utm_campaign').slice(0,100)}});}}
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
</div>
</div>
<div class="prose">
<h2>What you get</h2>
<p>When you buy {d['fqdn']} we register it in your name, or transfer it to your account at the registrar you choose. You own it outright and renew it yourself each year at your registrar&rsquo;s normal rate. We email you at each step, and if the name can&rsquo;t be delivered for any reason you get a full refund.</p>
<h2>Good fit for</h2>
<p>{esc(d['cat'])} businesses: {CAT_BLURB.get(d['cat'],'new businesses')}. Not quite right? Try the <a href="/#finder" style="color:var(--cobalt);font-weight:600">AI name finder</a> or browse more names below.</p>
</div>
<h2 style="font-family:'Schibsted Grotesk';font-size:22px;margin:34px 0 14px">Similar {esc(d['cat'].lower())} domains</h2>
<div class="linkgrid">{rel}</div>
<p style="margin-top:18px"><a class="btn btn-ghost" href="/domains/{slug(d['cat'])}/">All {len(BYCAT[d['cat']])} {esc(d['cat'].lower())} domains &rarr;</a></p>
</div></main>
<script>window.CLAIMLY_D={jsd};</script>
""" + footer() + modal() + "</body></html>"

# ───────────────────────── category pages ─────────────────────────
def cat_page(c):
    items = sorted(BYCAT[c], key=lambda x: (-["starter","standard","premium"].index(x["tier"]), x["fqdn"]))
    canon = f"{SITE}/domains/{slug(c)}/"
    lo = min(x["price"] for x in items); hi = max(x["price"] for x in items)
    title = f"{len(items)} Brandable {c} Domain Names for Sale | Claimly"
    desc = f"Browse {len(items)} available {c.lower()} domain names from ${lo}, ideal for {CAT_BLURB[c]}. Same-day delivery, pay by card or PayPal."
    il = {"@context":"https://schema.org","@type":"ItemList","name":f"{c} domain names","numberOfItems":len(items),
          "itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/d/{x['fqdn']}/","name":x["fqdn"]} for i,x in enumerate(items[:50])]}
    ld = '<script type="application/ld+json">'+json.dumps(il)+'</script>'
    links = "".join(f'<a href="/d/{x["fqdn"]}/">{x["fqdn"]}<span>${x["price"]}</span></a>' for x in items)
    others = "".join(f'<a class="chip" href="/domains/{slug(o)}/">{esc(o)}</a>' for o in CATS if o != c)
    return head(title, desc, canon, ld) + f"""
<main class="page"><div class="wrap">
<div class="crumbs"><a href="/">Claimly</a> &rsaquo; {esc(c)} domains</div>
<h1>Brandable {esc(c.lower())} domain names</h1>
<p class="section-sub">{len(items)} available names from ${lo} to ${hi}, picked for {CAT_BLURB[c]}. Each price includes the first year of registration, and most orders are delivered the same day.</p>
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
<p class="section-sub">We add fresh, availability-checked names every day. These are the latest {len(items)}.</p>
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

def notfound():
    return head("Page not found | Claimly", "This page doesn't exist.", SITE+"/404.html", robots="noindex") + f"""
<main class="page"><div class="wrap" style="text-align:center;padding:60px 0">
<h1>That page isn&rsquo;t here</h1>
<p class="section-sub" style="margin:0 auto 24px">The name may have been sold, or the link is wrong.</p>
<a class="btn btn-cta" href="/#shop">Browse {NFMT} available names</a>
</div></main>""" + footer() + "</body></html>"

def sitemap():
    urls = [(SITE+"/", "1.0", "daily", TODAY), (SITE+"/new/", "0.9", "daily", TODAY)] + [(f"{SITE}/domains/{slug(c)}/", "0.8", "weekly", TODAY) for c in CATS] + [(f"{SITE}/d/{d['fqdn']}/", "0.6", "monthly", ADDED.get(d["fqdn"], TODAY)) for d in D]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n" for u,p,f,m in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'



def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    SITE_DIR = os.path.join(ROOT, "site")
    for f in os.listdir(SITE_DIR):
        dst = os.path.join(OUT, "assets", f) if f.endswith(".css") else os.path.join(OUT, f)
        shutil.copy(os.path.join(SITE_DIR, f), dst)
    open(os.path.join(OUT, "index.html"), "w").write(home())
    open(os.path.join(OUT, "404.html"), "w").write(notfound())
    os.makedirs(os.path.join(OUT, "new")); open(os.path.join(OUT, "new", "index.html"), "w").write(new_page())
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
