"""segments.py — market-demand word lists for easy, two-word brand names.

Each segment is a market where buyers are actively spending in 2026 (AI agents,
payments, health, clean energy, UAE real estate and food, ...). Names are built
from two real, easy-to-say words, e.g. "crew" + "mind" -> CrewMind.com.

Used by daily_update.py (part of each day's slots) and for one-off batches.
"""
import random

# segment -> (shop category, market words, extensions in order of preference)
SEGMENTS = {
    "AI agents":        ("AI",          ["agent", "mind", "prompt", "model", "logic", "brain", "bot", "neural"], ["com", "co", "io"]),
    "Automation":       ("SaaS",        ["flow", "task", "ops", "sync", "stack", "desk", "relay", "pilot"],       ["com", "co", "io"]),
    "Payments":         ("Finance",     ["pay", "vault", "ledger", "coin", "fund", "cash", "wealth", "invoice"], ["com", "co"]),
    "Health & care":    ("Health",      ["care", "clinic", "vital", "heal", "fit", "calm", "dental", "derm"],    ["com", "co"]),
    "Clean energy":     ("Green",       ["solar", "volt", "carbon", "grid", "watt", "leaf", "terra", "eco"],     ["com", "co"]),
    "Creators":         ("Creator",     ["studio", "reel", "lens", "frame", "stream", "clip", "cast", "ink"],    ["com", "co", "studio"]),
    "Online stores":    ("E-commerce",  ["cart", "shop", "deal", "crate", "shelf", "souq", "basket", "merch"],   ["com", "co", "shop"]),
    "UAE real estate":  ("Real estate", ["home", "nest", "key", "villa", "dwell", "haven", "estate", "abode"],    ["com", "co"]),
    "Cafes & food":     ("Food",        ["brew", "bite", "bake", "roast", "feast", "spice", "plate", "dates"],   ["com", "co"]),
    "Beauty & fashion": ("Fashion",     ["glow", "luxe", "chic", "style", "thread", "silk", "aura", "lash"],     ["com", "co"]),
    "Travel & stays":   ("Travel",      ["trip", "stay", "roam", "dune", "oasis", "jet", "tour", "voyage"],      ["com", "co"]),
    "Learning":         ("Education",   ["learn", "tutor", "skill", "class", "quiz", "mentor", "study", "prep"], ["com", "co"]),
    "Legal & business": ("Legal",       ["law", "clause", "deed", "pact", "notary", "trust", "brief", "claim"],  ["com", "co"]),
    "Pets":             ("Pets",        ["paw", "pet", "pup", "tail", "wag", "fetch", "purr", "woof"],           ["com", "co"]),
}

# short, positive, easy-to-say brand words that pair with any market word
BRAND = ["forge", "pilot", "spark", "nest", "hive", "bloom", "crest", "peak", "harbor", "beacon",
         "atlas", "orbit", "north", "true", "bright", "clear", "swift", "bold", "kind", "calm",
         "golden", "silver", "cedar", "maple", "amber", "coral", "pearl", "falcon", "palm", "dune",
         "oasis", "summit", "haven", "anchor", "arrow", "compass", "lantern", "meadow", "river", "stone",
         "crew", "mate", "base", "works", "lab", "hub", "loop", "lane", "yard", "path",
         "wise", "smart", "happy", "lucky", "simple", "honest", "noble", "royal", "urban", "little"]

def _ok(a, b):
    n = a + b
    if len(n) > 11 or a == b: return False
    if a[-1] == b[0]: return False                   # "nestt", "palmm": hard to read
    if a[-1] in "aeiou" and b[0] in "aeiou": return False  # vowel clash, e.g. "auraoasis"
    return True

def candidates(seed=None, per_segment=60, seen=frozenset()):
    """Yield (category, Name, ext, domain, segment) tuples, round-robin across segments."""
    rnd = random.Random(seed)
    pools = {}
    for seg, (cat, words, exts) in SEGMENTS.items():
        pairs = set()
        for w in words:
            for b in BRAND:
                if _ok(w, b): pairs.add((w, b))
                if _ok(b, w): pairs.add((b, w))
        pairs = sorted(pairs); rnd.shuffle(pairs)
        out = []
        for a, b in pairs:
            name = a.capitalize() + b.capitalize()
            ext = exts[0] if rnd.random() < 0.7 else rnd.choice(exts)
            d = f"{(a + b).lower()}.{ext}"
            if d not in seen: out.append((cat, name, ext, d, seg))
            if len(out) >= per_segment: break
        pools[seg] = out
    while any(pools.values()):
        for seg in SEGMENTS:
            if pools[seg]: yield pools[seg].pop(0)
