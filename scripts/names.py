#!/usr/bin/env python3
"""
Claimly — bulk name generator + storefront builder.
Run:  python3 generate_names.py
Outputs:
  domains-5000.csv   → candidate names to bulk availability-check, then list
  index.html         → scalable storefront (AI name-finder, search, pagination)

IMPORTANT: the names are CANDIDATES, not verified registrations. Bulk-check
availability (expect 40–70% taken), trademark-screen the survivors, and list
only the available ones. Most value is in the *available* subset, not the count.
"""
import csv, json, random, html
random.seed(7)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claimly — Brandable domain names from $30</title>
<meta name="description" content="A curated marketplace of __COUNT__ brandable domain names from $30. Describe your business and our AI recommends available names — trademark-screened, with same-day escrow transfer.">
<meta name="theme-color" content="#F2EFE6">
<meta property="og:type" content="website"><meta property="og:title" content="Claimly — Brandable domain names from $30">
<meta property="og:description" content="A curated marketplace of brandable domain names, $30–$150. Trademark-screened, with same-day escrow transfer.">
<meta property="og:image" content="og-image.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="og-image.png">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@500;700;900&family=Hanken+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Claimly","description":"A curated shop of affordable brandable domain names, $30-150, with an AI name-finder."}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"Claimly"}</script>
<style>
:root{--ink:#141416;--bone:#F4F3F1;--bone2:#FFFFFF;--cobalt:#E0231C;--cobalt-deep:#B5160F;--lilac:#FBE2E0;--muted:#6B6B72;--line:#E4E2DE;--avail:#1F8F5F;--r:18px;--maxw:1180px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bone);color:var(--ink);font-family:'Hanken Grotesk',system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}.wrap{max-width:var(--maxw);margin:0 auto;padding:0 26px}
::selection{background:var(--cobalt);color:#fff}
.bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none}
.bg span{position:absolute;border-radius:50%;filter:blur(74px);opacity:.4;mix-blend-mode:multiply}
.bg .b1{width:48vw;height:48vw;left:-10vw;top:-12vw;background:radial-gradient(circle,#F2625F,transparent 70%);animation:drift1 32s ease-in-out infinite}
.bg .b2{width:42vw;height:42vw;right:-8vw;top:4vw;background:radial-gradient(circle,#CFCFD4,transparent 70%);animation:drift2 38s ease-in-out infinite}
.bg .b3{width:40vw;height:40vw;left:26vw;bottom:-18vw;background:radial-gradient(circle,#E88A88,transparent 70%);animation:drift3 45s ease-in-out infinite}
@keyframes drift1{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(8vw,6vw) scale(1.12)}}
@keyframes drift2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-7vw,5vw) scale(1.1)}}
@keyframes drift3{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(5vw,-7vw) scale(1.15)}}
section,footer{position:relative;z-index:1}
header{position:sticky;top:0;z-index:50;background:rgba(242,239,230,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{font-family:'Schibsted Grotesk';font-weight:900;font-size:23px;letter-spacing:-.03em}
.brand .reg{font-size:11px;vertical-align:super;color:var(--cobalt)}
.nav-links{display:flex;gap:24px;align-items:center}
.nav-links a{font-size:14.5px;font-weight:500}.nav-links a:hover{color:var(--cobalt)}
.btn{display:inline-flex;align-items:center;gap:8px;border:none;cursor:pointer;font-family:'Hanken Grotesk';font-weight:600;font-size:14.5px;padding:11px 18px;border-radius:11px;transition:transform .12s,box-shadow .2s}
.btn-cta{background:var(--cobalt);color:#fff}.btn-cta:hover{transform:translateY(-1px);box-shadow:0 10px 24px rgba(224,35,28,.32)}
.btn.wide{width:100%;justify-content:center}
@media(max-width:680px){.nav-links a:not(.btn){display:none}}
.hero{padding:30px 0 36px;position:relative;overflow:hidden}
.hero-top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;position:relative;z-index:3}
.hero-counter{font-family:'JetBrains Mono';font-size:12.5px;color:var(--muted);letter-spacing:.02em}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono';font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--cobalt-deep);background:var(--lilac);padding:6px 12px;border-radius:99px}
.eyebrow .spark{width:7px;height:7px;border-radius:50%;background:var(--cobalt);animation:pulse 1.8s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(224,35,28,.4)}70%{box-shadow:0 0 0 8px transparent}100%{box-shadow:0 0 0 0 transparent}}
.giant{font-family:'Schibsted Grotesk';font-weight:900;letter-spacing:-.055em;font-size:clamp(92px,27vw,360px);line-height:.8;margin:8px 0 0;color:var(--ink);position:relative;z-index:1}
.floaters{position:absolute;inset:0;pointer-events:none;z-index:2}
.float{position:absolute;background:var(--bone2);border:1px solid var(--line);border-radius:14px;padding:10px 14px;font-family:'JetBrains Mono';font-weight:700;font-size:15px;box-shadow:0 16px 34px rgba(18,17,20,.18);display:inline-flex;gap:8px;align-items:baseline;white-space:nowrap;animation:bob 7s ease-in-out infinite}
.float small{color:var(--cobalt);font-weight:700;font-size:13px}
.float.fa{top:10%;right:7%;--r:5deg;transform:rotate(5deg);animation-delay:0s}
.float.fb{top:40%;right:21%;--r:-4deg;transform:rotate(-4deg);animation-delay:1.3s}
.float.fc{top:13%;right:36%;--r:-9deg;transform:rotate(-9deg);animation-delay:.7s}
@keyframes bob{0%,100%{transform:translateY(0) rotate(var(--r))}50%{transform:translateY(-12px) rotate(var(--r))}}
.hero-bottom{display:grid;grid-template-columns:1fr 1.05fr;gap:32px;align-items:end;margin-top:14px;position:relative;z-index:3}
.price-hook{font-family:'Schibsted Grotesk';font-weight:900;font-size:clamp(30px,4.4vw,46px);line-height:1;margin-bottom:12px}
.lede{font-size:clamp(15px,1.7vw,18px);color:var(--muted);max-width:44ch;margin:0}
@media(max-width:820px){.hero-bottom{grid-template-columns:1fr;gap:22px}.floaters{display:none}.giant{font-size:clamp(72px,23vw,128px)}}
.finder{background:var(--bone2);border:1px solid var(--line);border-radius:20px;box-shadow:0 18px 44px rgba(18,17,20,.13);padding:20px;max-width:680px}
.finder label{font-family:'JetBrains Mono';font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);display:block;margin-bottom:8px}
.finder textarea{width:100%;border:1px solid var(--line);border-radius:12px;background:var(--bone);padding:14px;font-family:'Hanken Grotesk';font-size:16px;color:var(--ink);resize:vertical;min-height:62px}
.finder textarea:focus{outline:none;border-color:var(--cobalt);box-shadow:0 0 0 3px var(--lilac)}
.vibes{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.vibe{font-size:13px;font-weight:600;border:1px solid var(--line);background:var(--bone);padding:7px 13px;border-radius:99px;cursor:pointer;font-family:inherit;color:var(--ink)}
.vibe.on{background:var(--ink);color:var(--bone);border-color:var(--ink)}
.finder .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.finder .btn{padding:13px 22px;font-size:15px}
.hint{font-size:12.5px;color:var(--muted)}
.results{padding:8px 0 0}
.results.hide{display:none}
.results-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:30px 0 16px;flex-wrap:wrap}
.results-head h2{font-family:'Schibsted Grotesk';font-weight:900;font-size:clamp(22px,3vw,30px);margin:0;letter-spacing:-.02em}
.clearbtn{font-size:13px;color:var(--cobalt);cursor:pointer;font-weight:600;border:none;background:none}
.toolbar{position:sticky;top:64px;z-index:40;background:rgba(242,239,230,.9);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:14px 0;margin-top:30px}
.toolbar-in{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.searchbar{display:flex;align-items:center;gap:10px;background:var(--bone2);border:1px solid var(--line);border-radius:11px;padding:9px 14px;flex:1;min-width:200px}
.searchbar svg{color:var(--muted);flex:none}.searchbar input{flex:1;border:none;outline:none;background:transparent;font-family:'JetBrains Mono';font-size:15px;min-width:0;color:var(--ink)}
.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip{font-size:12.5px;font-weight:600;border:1px solid var(--line);background:var(--bone2);padding:6px 12px;border-radius:99px;cursor:pointer;white-space:nowrap;font-family:inherit;color:var(--ink)}
.chip:hover{border-color:var(--cobalt)}.chip.active{background:var(--ink);color:var(--bone);border-color:var(--ink)}
.count{font-size:13px;color:var(--muted);font-family:'JetBrains Mono';white-space:nowrap}
.sort{font-size:13.5px;font-weight:600;border:1px solid var(--line);background:var(--bone2);border-radius:9px;padding:8px 12px;cursor:pointer;color:var(--ink);font-family:inherit}
.shop{padding:28px 0 40px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
@media(max-width:980px){.grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:720px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:480px){.grid{grid-template-columns:1fr}}
.spec{background:var(--bone2);border:1px solid var(--line);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:14px;cursor:pointer;transition:.14s;min-height:118px}
.spec:hover{border-color:var(--cobalt);transform:translateY(-2px);box-shadow:0 12px 26px rgba(18,17,20,.15)}
.spec.match{border-color:var(--cobalt)}
.spec-name{font-family:'JetBrains Mono';font-weight:700;font-size:18px;letter-spacing:-.02em;word-break:break-all;line-height:1.12}
.spec-meta{display:flex;align-items:center;justify-content:space-between;margin-top:auto}
.spec-cat{font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.spec-price{font-family:'Schibsted Grotesk';font-weight:900;font-size:20px}
.spec-right{display:flex;align-items:center;gap:8px}
.buyflag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:#fff;background:var(--cobalt);padding:3px 7px;border-radius:6px;white-space:nowrap}
.ordiv{text-align:center;color:var(--muted);font-size:12.5px;margin-bottom:12px}
.why{font-size:11.5px;color:var(--cobalt-deep);background:var(--lilac);padding:3px 8px;border-radius:6px;align-self:flex-start;font-weight:600}
.loadmore{text-align:center;padding:30px 0 10px}
.empty{text-align:center;color:var(--muted);padding:40px 0}
footer{padding:46px 0 60px;border-top:1px solid var(--line);margin-top:30px}
.foot{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;align-items:center;color:var(--muted);font-size:13.5px}
.modal-bg{position:fixed;inset:0;background:rgba(23,20,25,.5);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;z-index:100;padding:20px}
.modal-bg.open{display:flex}
.modal{background:var(--bone2);border-radius:20px;border:1px solid var(--line);box-shadow:0 30px 70px rgba(18,17,20,.28);max-width:430px;width:100%;padding:30px;position:relative}
.modal .x{position:absolute;top:14px;right:14px;border:none;background:var(--bone);width:34px;height:34px;border-radius:9px;cursor:pointer;font-size:18px}
.m-kicker{font-family:'JetBrains Mono';font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.m-price{font-family:'Schibsted Grotesk';font-weight:900;font-size:34px;margin:4px 0 2px}.m-price small{font-size:17px;color:var(--muted)}
.m-name{font-family:'JetBrains Mono';font-weight:700;font-size:19px;margin-bottom:20px;word-break:break-all}
.field{display:flex;flex-direction:column;gap:6px;margin-bottom:14px}.field label{font-size:13px;font-weight:600;color:var(--muted)}
.field input{font-family:'Hanken Grotesk';font-size:15px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--bone);color:var(--ink)}
.field input:focus{outline:none;border-color:var(--cobalt);box-shadow:0 0 0 3px var(--lilac)}
.reassure{font-size:12.5px;color:var(--muted);text-align:center;margin:12px 0 0}.modal h3{font-family:'Schibsted Grotesk';margin:10px 0 6px}
:focus-visible{outline:2px solid var(--cobalt);outline-offset:2px;border-radius:6px}
.request{padding:44px 0 10px}
.req-card{background:var(--ink);color:var(--bone);border-radius:20px;padding:34px;display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:center}
@media(max-width:760px){.req-card{grid-template-columns:1fr;padding:26px}}
.req-card h2{color:var(--bone);margin:0 0 10px}
.req-card p{color:#e6e6ea;margin:0;font-size:15px}
.req-form{display:flex;flex-direction:column;gap:10px}
.req-form textarea,.req-form input{font-family:inherit;font-size:15px;padding:12px 14px;border-radius:10px;border:1px solid #38383d;background:#1d1d20;color:var(--bone)}
.req-form textarea{min-height:60px;resize:vertical}
.req-form textarea::placeholder,.req-form input::placeholder{color:#9a9aa0}
.req-form textarea:focus,.req-form input:focus{outline:none;border-color:var(--cobalt)}
.req-note{font-size:12px;color:#e6e6ea}
.req-link{display:inline-block;color:var(--cobalt);font-weight:600;cursor:pointer}
.empty .req-link{margin-left:4px}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head>
<body>
<div class="bg" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span></div>
<header><div class="wrap nav">
<a class="brand" href="#">Claimly<span class="reg">&reg;</span></a>
<nav class="nav-links"><a href="#finder">AI finder</a><a href="#shop">Browse</a><a class="btn btn-cta" href="#finder">Find a domain</a></nav>
</div></header>

<section class="hero" id="finder"><div class="wrap">
<div class="hero-top"><span class="eyebrow"><span class="spark"></span>AI domain finder &middot; __COUNT__ available</span><span class="hero-counter">__COUNT__ domains &middot; 18 categories</span></div>
<h1 class="giant">Domains</h1>
<div class="floaters" aria-hidden="true">
<span class="float fa">VaultMint.com <small>$129</small></span>
<span class="float fb">NeuralFig.ai <small>$139</small></span>
<span class="float fc">BrewQuarter.com <small>$69</small></span>
</div>
<div class="hero-bottom">
<div class="hero-pitch"><div class="price-hook">from $30</div><p class="lede">A curated marketplace of brandable domain names for founders and growing companies. Describe your business and our AI surfaces names that fit — each one trademark-screened and transferred to you the same day via secure escrow.</p></div>
<div class="finder">
<label for="brief">Describe your business or product</label>
<textarea id="brief" placeholder="e.g. a financial planning platform for small businesses"></textarea>
<div class="vibes" id="vibes">
<button class="vibe" data-v="short">Short &amp; clean</button>
<button class="vibe" data-v="playful">Playful</button>
<button class="vibe" data-v="premium">Premium</button>
<button class="vibe" data-v="ai">Tech / AI</button>
</div>
<div class="row"><button class="btn btn-cta" id="findBtn">Find available names</button><span class="hint">Instant &middot; trademark-screened &middot; same-day transfer</span></div>
</div>
</div></div></section>

<section class="results hide" id="results"><div class="wrap">
<div class="results-head"><h2 id="resTitle">Recommended for you</h2><button class="clearbtn" id="clearRes">Clear &times;</button></div>
<div class="grid" id="resGrid"></div>
</div></section>

<div class="toolbar" id="shop"><div class="wrap toolbar-in">
<div class="searchbar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><input id="search" placeholder="Search __COUNT__ names…" autocomplete="off"></div>
<div class="chips" id="chips"></div>
<span class="count" id="count"></span>
<select class="sort" id="sort"><option value="featured">Featured</option><option value="plo">Price &uarr;</option><option value="phi">Price &darr;</option><option value="az">A&ndash;Z</option></select>
</div></div>

<section class="shop"><div class="wrap">
<div class="grid" id="grid"></div>
<p class="empty" id="empty" style="display:none">No matches for that search — try a different keyword or category.</p>
<div class="loadmore"><button class="btn btn-cta" id="loadMore" style="display:none">Load more</button></div>
</div></section>


<footer><div class="wrap foot">
<div class="brand" style="font-size:17px">Claimly<span class="reg">&reg;</span></div>
<div>Curated brandable domains from $30 &middot; <a href="mailto:hello@claimly.com">hello@claimly.com</a></div>
<div>&copy; <span id="yr"></span> Claimly</div>
</div></footer>

<div class="modal-bg" id="modalBg" onclick="if(event.target===this)closeModal()">
<div class="modal" role="dialog" aria-modal="true">
<button class="x" onclick="closeModal()" aria-label="Close">&times;</button>
<div class="m-kicker">Buy this domain</div>
<div class="m-price"><small>$</small><span id="mPrice">—</span></div>
<div class="m-name" id="mName">name.com</div>
<a id="buyNow" class="btn btn-cta wide" target="_blank" rel="noopener">Buy now — pay by card or PayPal →</a>
<p id="noLink" class="reassure" style="display:none">Payment link coming soon for this domain.</p>
<p class="reassure">Secure checkout &middot; domain transferred to you after payment</p>
</div></div>

<script>
const RAW=/*__DATA__*/;const CATS=/*__CATS__*/;const EXTS=/*__EXTS__*/;const TIERS=/*__TIERS__*/;const KEYMAP=/*__KEYMAP__*/;
const PAY_BASE="https://www.paypal.com/paypalme/Claimly26"; /* live PayPal.me; per-domain checkout_url (marketplace) overrides this when present */
const D=RAW.map(a=>({name:a[0],ext:EXTS[a[1]],price:a[2],cat:CATS[a[3]],tier:TIERS[a[4]],checkout:a[5]||"",fqdn:a[0].toLowerCase()+"."+EXTS[a[1]]}));
document.getElementById('yr').textContent=new Date().getFullYear();
const PAGE=60;let activeCat='All',q='',sortBy='featured',shown=PAGE;
const grid=document.getElementById('grid'),countEl=document.getElementById('count'),emptyEl=document.getElementById('empty'),
 chipsEl=document.getElementById('chips'),searchEl=document.getElementById('search'),sortEl=document.getElementById('sort'),loadMore=document.getElementById('loadMore');
chipsEl.innerHTML='<button class="chip active" data-cat="All">All</button>'+CATS.map(c=>`<button class="chip" data-cat="${c}">${c}</button>`).join('');
chipsEl.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{activeCat=b.dataset.cat;chipsEl.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));b.classList.add('active');shown=PAGE;render();});
searchEl.oninput=e=>{q=e.target.value.toLowerCase().trim();shown=PAGE;render();};
sortEl.onchange=e=>{sortBy=e.target.value;render();};
loadMore.onclick=()=>{shown+=PAGE;render();};
function cardHTML(d,why){return `<div class="spec${why?' match':''}" data-f="${d.fqdn}" data-p="${d.price}" data-c="${d.checkout||''}" tabindex="0" role="button"><div class="spec-name">${d.fqdn}</div>${why?`<span class="why">${why}</span>`:''}<div class="spec-meta"><span class="spec-cat">${d.cat}</span><span class="spec-right">${(d.checkout||PAY_BASE)?'<span class="buyflag">Buy now</span>':''}<span class="spec-price">$${d.price}</span></span></div></div>`;}
function wire(scope){scope.querySelectorAll('.spec').forEach(c=>{const open=()=>openModal(c.dataset.f,c.dataset.p,c.dataset.c);c.onclick=open;c.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}};});}
function render(){
 let list=D.filter(d=>(activeCat==='All'||d.cat===activeCat)&&(!q||(d.fqdn+' '+d.cat).toLowerCase().includes(q)));
 if(sortBy==='plo')list=list.slice().sort((a,b)=>a.price-b.price);
 else if(sortBy==='phi')list=list.slice().sort((a,b)=>b.price-a.price);
 else if(sortBy==='az')list=list.slice().sort((a,b)=>a.fqdn.localeCompare(b.fqdn));
 countEl.textContent=list.length.toLocaleString()+' names';
 emptyEl.style.display=list.length?'none':'block';
 const page=list.slice(0,shown);
 grid.innerHTML=page.map(d=>cardHTML(d)).join('');
 wire(grid);
 loadMore.style.display=list.length>shown?'inline-flex':'none';
}
render();
let vibe=null;
document.getElementById('vibes').querySelectorAll('.vibe').forEach(b=>b.onclick=()=>{
 const on=b.classList.contains('on');document.getElementById('vibes').querySelectorAll('.vibe').forEach(x=>x.classList.remove('on'));if(!on)b.classList.add('on');vibe=on?null:b.dataset.v;});
document.getElementById('findBtn').onclick=runFinder;
document.getElementById('clearRes').onclick=()=>{document.getElementById('results').classList.add('hide');};
function tokensOf(t){return t.split(/[^a-z]+/).filter(x=>x.length>=3);}
function inferCats(tokens){const c={};tokens.forEach(t=>{if(KEYMAP[t]!=null)c[KEYMAP[t]]=1;});return Object.keys(c).map(Number);}
function scoreAll(tokens,wantCats){return D.map(d=>{let s=0;const ci=CATS.indexOf(d.cat);
   if(wantCats.includes(ci))s+=10;
   tokens.forEach(t=>{if(d.name.toLowerCase().includes(t))s+=7;});
   if(vibe==='short')s+=Math.max(0,9-d.name.length);
   if(vibe==='premium'&&d.tier==='premium')s+=4;
   if(vibe==='playful'&&/(ly|fox|owl|bay|pop|loop)$/.test(d.name.toLowerCase()))s+=4;
   if(vibe==='ai'&&(d.ext==='ai'||d.ext==='io'||d.cat==='AI'||d.cat==='SaaS'))s+=4;
   s+=Math.random()*0.6;return {d,s,ci};}).sort((a,b)=>b.s-a.s);}
function showResults(title){document.getElementById('resTitle').textContent=title;
 const r=document.getElementById('results');r.classList.remove('hide');r.scrollIntoView({behavior:'smooth',block:'start'});}
function heuristicResults(tokens,wantCats){
 const scored=scoreAll(tokens,wantCats);let top=scored.filter(x=>x.s>=1).slice(0,12);if(!top.length)top=scored.slice(0,12);
 document.getElementById('resGrid').innerHTML=top.map(x=>{let why='Brandable pick';
   if(wantCats.includes(x.ci))why='Fits '+x.d.cat;const hit=tokens.find(t=>x.d.name.toLowerCase().includes(t));
   if(hit)why='Has "'+hit+'"';else if(vibe==='short'&&x.d.name.length<=6)why='Short & clean';return cardHTML(x.d,why);}).join('');
 wire(document.getElementById('resGrid'));
 showResults(tokens.length?'Recommended for your business':'A selection to consider');}
async function runFinder(){
 const btn=document.getElementById('findBtn'),raw=document.getElementById('brief').value||'';
 const tokens=tokensOf(raw.toLowerCase()),wantCats=inferCats(tokens);
 const shortlist=scoreAll(tokens,wantCats).slice(0,80).map(x=>x.d);
 const label=btn.innerHTML;btn.disabled=true;btn.innerHTML='Searching…';
 let picks=null;
 try{
  const res=await fetch('/.netlify/functions/finder',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({brief:raw,vibe:vibe,shortlist:shortlist.map(d=>({fqdn:d.fqdn,cat:d.cat,price:d.price}))})});
  if(res.ok){const j=await res.json();if(j&&Array.isArray(j.picks)&&j.picks.length)picks=j.picks;}
 }catch(e){}
 btn.disabled=false;btn.innerHTML=label;
 if(picks){const map={};D.forEach(d=>map[d.fqdn]=d);
  const rows=picks.map(p=>({d:map[(p.fqdn||'').toLowerCase()],why:(p.reason||'').slice(0,28)})).filter(x=>x.d);
  if(rows.length){document.getElementById('resGrid').innerHTML=rows.map(x=>cardHTML(x.d,x.why)).join('');
   wire(document.getElementById('resGrid'));showResults('AI-recommended for your business');return;}}
 heuristicResults(tokens,wantCats);
}
let curF='',curP='';
function openModal(fqdn,price,checkout){curF=fqdn;curP=price;document.getElementById('mName').textContent=fqdn;document.getElementById('mPrice').textContent=price;
 var link=checkout||(PAY_BASE?PAY_BASE+"/"+price:""),bn=document.getElementById('buyNow'),nl=document.getElementById('noLink');
 if(link){bn.href=link;bn.style.display='flex';nl.style.display='none';}else{bn.style.display='none';nl.style.display='block';}
 document.getElementById('modalBg').classList.add('open');}
function closeModal(){document.getElementById('modalBg').classList.remove('open');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
</script>
</body></html>'''

CATS = ["Finance","AI","SaaS","E-commerce","Local","Health","Creator",
        "Education","Travel","Real estate","Food","Pets",
        "Crypto","Marketing","Legal","Fashion","Gaming","Green"]
TIERS = ["starter","standard","premium"]
EXTS  = ["com","ai","io","co","app","dev","xyz","shop","store","studio","tech","eco"]

ROOTS = {
 "Finance":["ledger","vault","mint","coin","fund","cash","capital","asset","credit","bank","pay","budget","wealth","finance","invoice","tax","loan","save","stock","yield","equity","fiscal"],
 "AI":["neural","cortex","model","vector","tensor","logic","mind","brain","infer","agent","synth","data","prompt","learn","nano","quantum","byte","node","signal","cognit","matrix","spark"],
 "SaaS":["flow","ops","sync","stack","task","scope","deploy","cloud","dash","board","metric","queue","grid","pipeline","scale","build","ship","launch","tool","relay","pulse","loop"],
 "E-commerce":["cart","shop","store","market","retail","buy","sell","goods","merch","basket","order","shelf","bazaar","trade","deal","bundle","vend","mall","outlet","pop","stock","crate"],
 "Local":["town","city","local","near","neighbor","block","main","region","place","spot","corner","district","zone","ward","civic","street","plaza","square","metro","village","county","port"],
 "Health":["vital","care","well","med","thrive","pulse","heal","nutri","calm","zen","fit","clinic","remedy","cure","mind","body","rehab","life","glow","bloom","pure","sage"],
 "Creator":["studio","maker","craft","render","frame","canvas","pixel","reel","shot","lens","create","design","ink","motion","scene","edit","film","brush","muse","forge","prism","vivid"],
 "Education":["learn","tutor","skill","edu","bright","mentor","study","class","lesson","teach","scholar","academy","course","grade","campus","quiz","sage","wise","prep","spark","focus","grasp"],
 "Travel":["trip","nomad","stay","voyage","roam","journey","wander","trek","getaway","tour","explore","atlas","globe","route","jet","coast","summit","drift","escape","venture","oasis","horizon"],
 "Real estate":["home","estate","dwell","prop","acre","rent","lot","key","abode","space","house","realty","land","manor","nest","haven","plot","deed","terra","roost","hearth","cove"],
 "Food":["fork","pantry","bite","brew","graze","feast","sip","crumb","plate","dish","kitchen","savory","spice","harvest","fresh","roast","baker","morsel","nibble","taste","crave","zest"],
 "Pets":["rover","paw","pet","furry","tail","whisker","fetch","barker","purr","critter","snout","kennel","pounce","nuzzle","woof","meow","cuddle","bark","pup","fang","fetch","wag"],
 "Crypto":["chain","block","token","coin","crypto","defi","stake","wallet","node","hash","dao","swap","nexus","forge","mint","ledger","orbit","stack","bit","vault"],
 "Marketing":["reach","funnel","growth","brand","convert","leads","boost","viral","pitch","traction","amplify","engage","promo","signal","rank","spark","scale","loop","pulse","bloom"],
 "Legal":["legal","law","counsel","justice","clause","brief","docket","verdict","notary","statute","advocate","lex","writ","accord","bind","trust","case","pact","claim","esquire"],
 "Fashion":["thread","style","vogue","wardrobe","atelier","couture","drape","stitch","fabric","trend","chic","attire","weave","label","linen","velvet","luxe","adorn","muse","aura"],
 "Gaming":["pixel","quest","arena","loot","guild","raid","level","arcade","clutch","respawn","combo","sprite","realm","frag","boss","coop","play","score","pawn","ping"],
 "Green":["eco","green","solar","renew","leaf","terra","bloom","pure","carbon","grove","sprout","verde","clean","earth","cycle","sustain","root","wild","fern","gaia"],
}
PREFIX = ["get","try","go","up","on","my","neo","ever","true","prime","swift","bright","clear","smart","next","well","good","open"]
SUFFIX = ["ly","ify","hub","base","flow","labs","kit","wise","able","ora","ova","ix","evo","era","ary","ery","yard","nest","harbor","peak","loop","lane","bay","works","craft","forge","mint","spark","pulse","grid","layer","scope","stack","sync","wave","fox","owl"]
TECH   = ["hub","base","flow","labs","kit","grid","stack","sync","loop","works","ai","io"]

CONS=["b","d","f","g","k","l","m","n","p","r","s","t","v","z","br","cl","dr","fl","gr","pr","tr","ka","lo","mi","ve","no","ra"]
VOW =["a","e","i","o","u","ai","eo","ia"]
BLOCK=["ass","sex","cum","fck","fuk","sht","nig","rap","kill","die","nazi","porn","damn","hell","xxx"]

def clean(s):
    s=s.lower()
    if not (4<=len(s)<=14): return None
    if any(b in s for b in BLOCK): return None
    if not s.isalpha(): return None
    return s

def coined():
    n=random.choice([2,2,3])
    w="".join(random.choice(CONS)+random.choice(VOW) for _ in range(n))
    return clean(w)

def cap(s): return s[:1].upper()+s[1:]

def gen_for_cat(cat, target):
    roots=ROOTS[cat]; out=set()
    tries=0
    while len(out)<target and tries<target*40:
        tries+=1
        p=random.random()
        if p<0.30:
            w=cap(random.choice(roots))+random.choice(SUFFIX)
        elif p<0.55:
            w=cap(random.choice(PREFIX))+cap(random.choice(roots))
        elif p<0.75:
            w=cap(random.choice(roots))+random.choice(roots)
        elif p<0.90:
            w=cap(random.choice(roots))+random.choice(TECH)
        else:
            c=coined()
            w=cap(c) if c else None
        if not w: continue
        cl=clean(w)
        if cl: out.add(cap(cl))
    return out

MIN_PRICE, MAX_PRICE = 30, 150
TLD_PREMIUM = {"com":1.0,"ai":1.28,"io":1.16,"co":1.02,"app":1.06,"dev":1.0,
               "xyz":0.82,"shop":0.96,"store":0.9,"studio":1.0,"tech":0.95,"eco":0.95}
CAT_DEMAND = {"AI":1.20,"SaaS":1.12,"Finance":1.12,"Crypto":1.16,"Health":1.08,
              "E-commerce":1.05,"Marketing":1.05,"Legal":1.05,"Real estate":1.0,
              "Creator":1.0,"Fashion":1.0,"Gaming":1.0,"Education":0.98,"Travel":0.98,
              "Food":0.95,"Pets":0.95,"Local":0.95,"Green":1.0}
PREFS = {  # category -> [(tld, probability), ...]; remainder defaults to .com
 "AI":[("ai",.30),("io",.12)],
 "SaaS":[("io",.14),("app",.10),("dev",.05),("tech",.04)],
 "Crypto":[("xyz",.22),("io",.12)],
 "E-commerce":[("shop",.18),("store",.10)],
 "Creator":[("studio",.16),("xyz",.04)],
 "Marketing":[("io",.08),("xyz",.05)],
 "Gaming":[("xyz",.12),("io",.06)],
 "Green":[("eco",.18),("xyz",.04)],
}

def price_for(name, cat, ext):
    L=len(name)
    if L<=5: base=random.randint(105,140)
    elif L<=7: base=random.randint(75,110)
    elif L<=9: base=random.randint(50,85)
    else: base=random.randint(30,60)
    base = base * TLD_PREMIUM.get(ext,1.0) * CAT_DEMAND.get(cat,1.0)
    price = max(MIN_PRICE, min(MAX_PRICE, int(round(base/5)*5)))
    tier = "premium" if price>=100 else ("standard" if price>=60 else "starter")
    return price, tier

def ext_for(cat, name):
    r=random.random(); cum=0.0
    for tld,p in PREFS.get(cat,[]):
        cum+=p
        if r<cum: return tld
    if r < cum+0.05: return "co"
    return "com"

# ───────────────────────── pipeline functions ─────────────────────────
def make_keymap():
    km={}
    for ci,cat in enumerate(CATS):
        km[cat.lower().split()[0]]=ci
        for r in ROOTS[cat]:
            km.setdefault(r,ci)
    extra={"money":0,"fintech":0,"crypto":12,"startup":2,"software":2,"app":2,"ecommerce":3,"online":3,"brand":13,
           "doctor":5,"wellness":5,"fitness":5,"gym":5,"artist":6,"photo":6,"video":6,"agency":6,"school":7,
           "kids":7,"hotel":8,"trip":8,"flight":8,"property":9,"rental":9,"restaurant":10,"cafe":10,"coffee":10,
           "dog":11,"cat":11,"animal":11,"ai":1,"machine":1,"robot":1,"data":1,
           "blockchain":12,"web3":12,"nft":12,"wallet":12,"defi":12,
           "marketing":13,"seo":13,"ads":13,"campaign":13,"growth":13,"leads":13,
           "legal":14,"law":14,"lawyer":14,"attorney":14,"contract":14,"justice":14,
           "fashion":15,"clothing":15,"apparel":15,"boutique":15,"style":15,
           "game":16,"gaming":16,"gamer":16,"esports":16,"arcade":16,
           "green":17,"eco":17,"solar":17,"sustainable":17,"climate":17,"energy":17,"renewable":17}
    for k,v in extra.items(): km.setdefault(k,v)
    return km

def generate_rows(target=8000):
    per = target//len(CATS) + 60
    rows=[]; seen=set()
    for cat in CATS:
        for name in gen_for_cat(cat, per):
            if name.lower() in seen: continue
            seen.add(name.lower())
            ext=ext_for(cat,name)
            price,tier=price_for(name,cat,ext)
            rows.append((name,ext,price,cat,tier,""))
    random.shuffle(rows)
    return rows[:target] if len(rows)>=target else rows

def write_csv(rows, path="domains-5000.csv"):
    with open(path,"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["domain","bin_price","currency","min_offer","category","tier","description","checkout_url"])
        for name,ext,price,cat,tier,checkout in rows:
            dom=f"{name.lower()}.{ext}"
            w.writerow([dom,price,"USD",int(price*0.7),cat,tier,
                        f"{dom} — a brandable {cat.lower()} domain. Short, trademark-screened, same-day escrow transfer.", checkout])
    return path

def write_marketplace_csv(rows, path="marketplace-upload.csv"):
    """Afternic/Atom-friendly bulk-upload file. checkout_url is blank until you list;
    paste each listing's Buy-It-Now URL into that column, then rebuild the store."""
    with open(path,"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["domain","price","min_offer","currency","category","description","checkout_url"])
        for name,ext,price,cat,tier,checkout in rows:
            dom=f"{name.lower()}.{ext}"
            w.writerow([dom,price,int(price*0.7),"USD",cat,
                        f"{dom} — brandable {cat.lower()} domain, trademark-screened, same-day escrow transfer.", checkout])
    return path

def rows_from_csv(path):
    """Read a CSV (domain,bin_price,...,category,tier) back into builder rows."""
    rows=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f):
            dom=r["domain"].strip().lower()
            if "." not in dom: continue
            name,ext=dom.rsplit(".",1)
            cat=r.get("category","SaaS").strip() or "SaaS"
            tier=(r.get("tier","standard").strip() or "standard")
            if cat not in CATS: cat="SaaS"
            if tier not in TIERS: tier="standard"
            if ext not in EXTS: EXTS.append(ext)
            try: price=int(float(r.get("bin_price",99) or 99))
            except: price=99
            rows.append((name[:1].upper()+name[1:], ext, price, cat, tier, (r.get("checkout_url","") or "").strip()))
    return rows

def build_index(rows, out="index.html"):
    DATA=[[n, EXTS.index(e), p, CATS.index(c), TIERS.index(t), co] for (n,e,p,c,t,co) in rows]
    htmlout=(TEMPLATE
        .replace("/*__DATA__*/", json.dumps(DATA, separators=(",",":")))
        .replace("/*__CATS__*/", json.dumps(CATS))
        .replace("/*__EXTS__*/", json.dumps(EXTS))
        .replace("/*__TIERS__*/", json.dumps(TIERS))
        .replace("/*__KEYMAP__*/", json.dumps(make_keymap(), separators=(",",":")))
        .replace("__COUNT__", f"{len(rows):,}"))
    with open(out,"w",encoding="utf-8") as f: f.write(htmlout)
    return out, len(htmlout)

if __name__=="__main__":
    import sys
    count=8000
    if "--count" in sys.argv:
        try: count=int(sys.argv[sys.argv.index("--count")+1])
        except: pass
    rows=generate_rows(count)
    print(f"generated {len(rows)} unique candidate names")
    write_csv(rows); print("wrote domains-5000.csv")
    write_marketplace_csv(rows); print("wrote marketplace-upload.csv")
    _,sz=build_index(rows); print(f"wrote index.html ({sz//1024} KB)")
