// netlify/functions/finder.js
// AI name-finder powered by Claude Haiku 4.5. The API key stays server-side.
// Set it in Netlify: Project configuration -> Environment variables -> ANTHROPIC_API_KEY
// If the key is missing, rate-limited or anything fails, this returns {error:...}
// and the storefront falls back to its free in-browser finder.

const ALLOWED = ["https://claimly.ae", "https://www.claimly.ae", "https://claimly-ae.netlify.app"];
const hits = new Map(); // best-effort per-instance rate limit
const LIMIT = 12, WINDOW_MS = 10 * 60 * 1000;

function limited(ip) {
  const now = Date.now();
  const arr = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  arr.push(now);
  hits.set(ip, arr);
  if (hits.size > 5000) hits.clear();
  return arr.length > LIMIT;
}

exports.handler = async (event) => {
  const origin = event.headers.origin || event.headers.Origin || "";
  const okOrigin = !origin || ALLOWED.includes(origin) || /^https:\/\/[a-z0-9-]+--claimly-ae\.netlify\.app$/.test(origin);
  const J = (code, obj) => ({
    statusCode: code,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": okOrigin && origin ? origin : "https://claimly.ae",
      "Vary": "Origin",
    },
    body: JSON.stringify(obj),
  });

  if (event.httpMethod === "OPTIONS") return J(200, { ok: true });
  if (event.httpMethod !== "POST") return J(405, { error: "method" });
  if (!okOrigin) return J(403, { error: "origin" });

  const ip = event.headers["x-nf-client-connection-ip"] || event.headers["x-forwarded-for"] || "anon";
  if (limited(String(ip).split(",")[0].trim())) return J(200, { error: "rate_limited" });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return J(200, { error: "no_key" });

  let body = {};
  try { body = JSON.parse(event.body || "{}"); } catch (e) { return J(400, { error: "bad_json" }); }

  const brief = String(body.brief || "").slice(0, 500);
  const vibe = String(body.vibe || "").slice(0, 20);
  const shortlist = Array.isArray(body.shortlist) ? body.shortlist.slice(0, 80) : [];
  if (!brief || !shortlist.length) return J(200, { error: "empty" });

  const list = shortlist
    .map((d) => `${String(d.fqdn || "").slice(0, 40)} | ${String(d.cat || "").slice(0, 20)} | $${Number(d.price) || 0}`)
    .join("\n");
  const system =
    "You are a branding expert helping a customer choose a domain from an AVAILABLE inventory list. " +
    "Pick the 10 best matches for their idea, best first. Only choose fqdns that appear in the list verbatim. " +
    'Reply with ONLY valid JSON, no prose or markdown: {"picks":[{"fqdn":"exact.fqdn","reason":"<= 8 words why it fits"}]}';
  const user = `Idea: ${brief}\nPreferred vibe: ${vibe || "any"}\n\nAvailable domains (fqdn | category | price):\n${list}`;

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 700,
        system,
        messages: [{ role: "user", content: user }],
      }),
    });
    if (!r.ok) return J(200, { error: "api" });
    const data = await r.json();
    let text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("").trim();
    text = text.replace(/^```json\s*/i, "").replace(/^```\s*/, "").replace(/```$/, "").trim();
    let parsed;
    try { parsed = JSON.parse(text); }
    catch (e) { const m = text.match(/\{[\s\S]*\}/); parsed = m ? JSON.parse(m[0]) : { picks: [] }; }
    const allowed = new Set(shortlist.map((d) => String(d.fqdn || "").toLowerCase()));
    const picks = (Array.isArray(parsed.picks) ? parsed.picks : [])
      .filter((p) => allowed.has(String(p.fqdn || "").toLowerCase()))
      .slice(0, 12)
      .map((p) => ({ fqdn: String(p.fqdn), reason: String(p.reason || "").slice(0, 60) }));
    return J(200, { picks });
  } catch (e) {
    return J(200, { error: "exception" });
  }
};
