// PM Dota book recorder: BOTH tokens' OWN books (YES and NO as separate books) for every Dota winner market. No deps (Node 22). Read-only.
// Usage: node pm_dota_books.js <outDir> [endISO]
// Discovery (every 5 min): gamma-api events of Dota series 10309, active and not closed; keeps markets whose question is a
// 'Game N Winner' or the match winner (BO). A market is polled from start -20 min to start +5 h (or all day if start unknown).
// Poll: CLOB /book?token_id= for each token every 2 s, written only on change: {recv_ms,token,outcome,q,cond,bid,ask,bids,asks} (top 10 levels).
// Same row layout as agent/tasks/dota-live-capture-2026-11-20/capture.js books.jsonl; feeds/dotacap_books_adapter.py converts it for ps_lead_test.py.
// markets.jsonl = {cond,q,outcomes,tokens,smt,start} once per market (format read by feeds/ps_lead_test.py).
const fs = require('fs'), path = require('path');
const OUT = process.argv[2], END = process.argv[3] ? Date.parse(process.argv[3]) : Infinity;
fs.mkdirSync(OUT, { recursive: true });
const app = (n, o) => fs.appendFileSync(path.join(OUT, n), JSON.stringify(o) + '\n');
const log = (m) => fs.appendFileSync(path.join(OUT, 'recorder.log'), new Date().toISOString() + ' ' + m + '\n');
const UA = { 'User-Agent': 'pkarbs-dota-recorder' };
const GAMMA = process.env.GAMMA_URL || 'https://gamma-api.polymarket.com', CLOB = process.env.CLOB_URL || 'https://clob.polymarket.com';
const DISC_MS = +process.env.DISC_MS || 300000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let stop = false; process.on('SIGTERM', () => { stop = true; });
const live = () => !stop && Date.now() < END;
const mk = new Map(), last = {};
async function discover() {
  while (live()) {
    try {
      // page through ALL active Dota events (limit 100 per page; a busy BLAST day has more than 100 events)
      for (let off = 0, n = 100; n === 100 && off < 900; off += 100) {
        const r = await fetch(GAMMA + '/events?series_id=10309&active=true&closed=false&limit=100&offset=' + off, { headers: { ...UA, 'Accept-Encoding': 'gzip' } });
        if (r.status !== 200) { log('gamma status ' + r.status); break; }
        const evs = await r.json(); n = evs.length;
        for (const e of evs) for (const m of e.markets || []) {
          if (!/Game\s*\d+\s*Winner|\(BO\d\)/i.test(m.question || '')) continue;
          const start = Date.parse(m.gameStartTime || e.startTime || '') || null;
          const known = mk.get(m.conditionId);
          if (known) {
            // RESCHEDULED market: Polymarket moves gameStartTime; a cached start left the window closed forever (23 Nov bug)
            if (start && start !== known.st) {
              log('reschedule ' + m.question + ' ' + new Date(known.st || 0).toISOString() + ' -> ' + new Date(start).toISOString());
              known.st = start; known.start = new Date(start).toISOString();
              app('markets.jsonl', { cond: known.cond, q: known.q, outcomes: known.outcomes, tokens: known.tokens, smt: known.smt, start: known.start });
            }
            continue;
          }
          let toks, oc; try { toks = JSON.parse(m.clobTokenIds); oc = JSON.parse(m.outcomes); } catch { continue; }
          if (!toks || toks.length !== 2) continue;
          const row = { cond: m.conditionId, q: m.question, outcomes: oc, tokens: toks, smt: m.sportsMarketType || null, start: start && new Date(start).toISOString() };
          mk.set(m.conditionId, { ...row, st: start }); app('markets.jsonl', row); log('market ' + m.question);
        }
      }
    } catch (e) { log('discover error ' + e.message); }
    await sleep(DISC_MS);
  }
}
async function one(m, i) {
  const tok = m.tokens[i];
  try {
    const r = await fetch(CLOB + '/book?token_id=' + tok, { headers: UA }); const recv = Date.now();
    if (r.status !== 200) { if (r.status === 429) await sleep(3000); return; }
    const b = await r.json();
    const lv = (a, d) => (a || []).map((x) => [+x.price, +x.size]).sort((p, q) => d ? q[0] - p[0] : p[0] - q[0]).slice(0, 10);
    const bids = lv(b.bids, true), asks = lv(b.asks, false), k = JSON.stringify([bids, asks]);
    if (last[tok] === k) return; last[tok] = k;
    app('books.jsonl', { recv_ms: recv, token: tok, outcome: m.outcomes[i], q: m.q, cond: m.cond, bid: bids[0]?.[0] ?? null, ask: asks[0]?.[0] ?? null, bids, asks });
  } catch (e) { log('book error ' + e.message); }
}
async function books() {
  let cyc = 0;
  while (live()) {
    const t0 = Date.now(); cyc++;
    // markets with a known start inside [-20 min, +5 h] every cycle; unknown start only every 15th cycle (about 30 s)
    const jobs = [];
    for (const m of mk.values()) {
      if (m.st ? (t0 >= m.st - 20 * 60000 && t0 <= m.st + 5 * 3600000) : cyc % 15 === 0) { jobs.push([m, 0]); jobs.push([m, 1]); }
    }
    for (let i = 0; i < jobs.length; i += 16) await Promise.all(jobs.slice(i, i + 16).map(([m, k]) => one(m, k)));
    await sleep(Math.max(0, 2000 - (Date.now() - t0)));
  }
}
log('start ' + new Date().toISOString());
Promise.all([discover(), books()]).then(() => { log('done'); process.exit(0); });
