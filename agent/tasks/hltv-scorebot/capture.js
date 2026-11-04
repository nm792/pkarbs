// HLTV scorebot (kill-by-kill) + Polymarket order book capture, 4 Nov 2026.
// Usage: node capture.js <config.json> <outDir> <windowStartISO> <windowEndISO>
//
// Follows the scorebot connection of the open-source gigobyte/HLTV client (npm "hltv" 3.5.0,
// lib/endpoints/connectToScorebot.js):
//   1. read the match page https://www.hltv.org/matches/<id>/- and its #scoreboardElement attributes
//      data-scorebot-url (comma list, take last) and data-scorebot-id;
//   2. socket.io v2 connect to that URL, emit 'readyForMatch' JSON {token:'', listId:<scorebot id>};
//   3. receive 'log' (kills, bomb, round start/end), 'scoreboard' (score + players), 'fullLog'.
// Plain HTTP with an honest User-Agent. No bot-check circumvention: if HLTV answers with a Cloudflare challenge
// (403/503, cf-mitigated) we do NOT try to get past it. We record the refusal, then try the configured public scorebot
// URL with listId = HLTV id (the scorebot id has equalled the match id), and record whether that is accepted.
// Either way, every request and its status is written to http.jsonl / scorebot.jsonl so the owner thread can see it.
//
// Polymarket side: every 5 min, gamma events for CS2 (series 10310) that are tier 1 and started within the last 6 h or
// start within 1 h; for each Match Winner / Map N Winner market, the first token's full book via POST clob /books
// every book_poll_s, written only when it changes.
//
// Files (all rows carry recv_ms = local receive time; host clock must be NTP-synced, checked at start):
//   scorebot.jsonl  {recv_ms, hltv_id, ev: 'log'|'scoreboard'|'fullLog'|'connect'|'disconnect'|'connect_error'|..., data}
//   books.jsonl     {recv_ms, sent_ms, token, cond, kind, slug, ts, bids, asks}
//   markets.jsonl   discovered PM markets; http.jsonl  every HLTV page request + status; capture.log  human log.
// Stop early: touch <outDir>/STOP (or SIGTERM).
const fs = require('fs'), path = require('path');
const [, , CFG, OUT, WSTART, WEND] = process.argv;
if (!WEND) { console.error('usage: node capture.js config.json outDir startISO endISO'); process.exit(2); }
const cfg = JSON.parse(fs.readFileSync(CFG, 'utf8'));
const GAMMA = process.env.GAMMA_BASE || 'https://gamma-api.polymarket.com';
const CLOB = process.env.CLOB_BASE || 'https://clob.polymarket.com';
const HLTV = process.env.HLTV_BASE || 'https://www.hltv.org';
const FALLBACK = process.env.SCOREBOT_URLS ? process.env.SCOREBOT_URLS.split(',') : cfg.scorebot_fallback_urls;
fs.mkdirSync(OUT, { recursive: true });
const F = (n) => path.join(OUT, n);
const log = (m) => fs.appendFileSync(F('capture.log'), new Date().toISOString() + ' ' + m + '\n');
const app = (n, o) => fs.appendFileSync(F(n), JSON.stringify(o) + '\n');
const start = Date.parse(WSTART), end = Date.parse(WEND);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let stop = false;
process.on('SIGTERM', () => { log('SIGTERM'); stop = true; });
process.on('SIGINT', () => { log('SIGINT'); stop = true; });
const stopTimer = setInterval(() => { if (fs.existsSync(F('STOP'))) { if (!stop) log('STOP file'); stop = true; } }, 5000);
const live = () => !stop && Date.now() < end;
const UA = 'pkarbs-research/1.0 (contact nm@delphic.co)';

// ------------------------------------------------------------------ HLTV scorebot
const sockets = {};
const counts = {};
async function scorebotUrlFor(id) {
  let status = null, err = null;
  const url = `${HLTV}/matches/${id}/-`;
  try {
    const sent = Date.now();
    const r = await fetch(url, { headers: { 'User-Agent': UA }, signal: AbortSignal.timeout(20000) });
    status = r.status; const body = await r.text();
    app('http.jsonl', { recv_ms: Date.now(), sent_ms: sent, url, status, bytes: body.length, cf: r.headers.get('cf-mitigated') });
    if (status === 200) {
      const u = /data-scorebot-url="([^"]+)"/.exec(body), i = /data-scorebot-id="([^"]+)"/.exec(body);
      if (u && i) return [u[1].split(',').pop().trim(), i[1], 'page'];
      err = 'no #scoreboardElement attrs';
    }
  } catch (e) { err = e.message; }
  log(`hltv page ${id}: status=${status} ${err || ''} -> public scorebot url ${FALLBACK[0]}`);
  return [FALLBACK[0], String(id), 'fallback0'];
}

async function connect(m, urlIdx) {
  const io = require('socket.io-client');
  const id = m.hltv_id;
  const [url, listId, how] = urlIdx == null ? await scorebotUrlFor(id) : [FALLBACK[urlIdx], String(id), 'fallback' + urlIdx];
  const init = JSON.stringify({ token: '', listId });
  log(`connect ${id} url=${url} listId=${listId} via=${how}`);
  const s = io.connect(url, { reconnection: true, reconnectionDelay: 2000, reconnectionDelayMax: 30000, timeout: 20000,
    forceNew: true, extraHeaders: { 'User-Agent': UA } });
  sockets[id] = s;
  let opened = false;
  const rec = (ev, data) => {
    counts[id] = counts[id] || {}; counts[id][ev] = (counts[id][ev] || 0) + 1;
    app('scorebot.jsonl', { recv_ms: Date.now(), hltv_id: id, ev, data });
  };
  s.on('connect', () => { opened = true; rec('connect', { url, listId, how }); s.emit('readyForMatch', init); });
  s.on('reconnect', () => { rec('reconnect', null); s.emit('readyForMatch', init); });
  s.on('disconnect', (r) => rec('disconnect', String(r)));
  s.on('connect_error', (e) => { rec('connect_error', String((e && e.message) || e)); });
  for (const ev of ['log', 'scoreboard', 'fullLog']) s.on(ev, (d) => rec(ev, typeof d === 'string' ? safeParse(d) : d));
  // Fallback path never connected within 60 s: try the next listed public scorebot URL (once each), then give up.
  setTimeout(() => {
    if (opened || stop || !how.startsWith('fallback')) return;
    const next = (urlIdx == null ? 0 : urlIdx) + 1;
    s.close(); delete sockets[id];
    if (next < FALLBACK.length) connect(m, next); else log(`give up ${id}: no scorebot URL accepted the connection`);
  }, 60000);
}
const safeParse = (x) => { try { return JSON.parse(x); } catch { return x; } };

// ------------------------------------------------------------------ Polymarket books
let tokens = {};   // token -> {cond, kind, slug}
async function getJ(u, opt) {
  const r = await fetch(u, Object.assign({ headers: { 'User-Agent': UA, 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(10000) }, opt || {}));
  if (r.status !== 200) throw new Error('HTTP ' + r.status + ' ' + u.slice(0, 80));
  return r.json();
}
async function discover() {
  while (live()) {
    try {
      const smin = new Date(Date.now() - 14 * 86400e3).toISOString().slice(0, 19) + 'Z';
      let evs = [];
      for (let off = 0; off < 1000; off += 100) {
        const p = await getJ(`${GAMMA}/events?series_id=10310&closed=false&start_date_min=${smin}&limit=100&offset=${off}`);
        evs = evs.concat(p || []); if (!p || p.length < 100) break;
      }
      const now = Date.now(); const nt = {};
      for (const ev of evs) {
        const st = Date.parse(ev.startTime || ''); if (!st || st > now + 3600e3 || st < now - 6 * 3600e3) continue;
        const title = (ev.title || '').toLowerCase();
        if (!cfg.tier1_keywords.some((k) => title.includes(k))) continue;
        for (const mk of ev.markets || []) {
          const t = mk.groupItemTitle || '';
          const kind = t === 'Match Winner' ? 'match' : /^Map \d Winner$/.test(t) ? 'map' + t[4] : null;
          if (!kind || mk.closed) continue;
          let ids = mk.clobTokenIds; if (typeof ids === 'string') ids = JSON.parse(ids);
          let outs = mk.outcomes; if (typeof outs === 'string') outs = JSON.parse(outs);
          if (!ids || !ids.length) continue;
          nt[ids[0]] = { cond: mk.conditionId, kind, slug: ev.slug };
          if (!tokens[ids[0]]) app('markets.jsonl', { recv_ms: Date.now(), token: ids[0], token1: ids[1], cond: mk.conditionId, kind,
            slug: ev.slug, title: ev.title, start: ev.startTime, outcomes: outs });
        }
      }
      tokens = nt; log(`discover: ${Object.keys(tokens).length} tokens`);
    } catch (e) { log('discover error ' + e.message); }
    for (let i = 0; i < 300 && live(); i++) await sleep(1000);
  }
}
const lastBook = {};
let bookOk = 0, bookErr = 0;
async function pollBooks() {
  const P = (cfg.book_poll_s || 1) * 1000;
  while (live()) {
    const t0 = Date.now(); const ids = Object.keys(tokens);
    if (ids.length) {
      try {
        const sent = Date.now();
        const arr = await getJ(`${CLOB}/books`, { method: 'POST', body: JSON.stringify(ids.map((t) => ({ token_id: t }))) });
        const recv = Date.now(); bookOk++;
        for (const b of arr || []) {
          const tok = b.asset_id; const meta = tokens[tok] || {};
          const key = JSON.stringify([b.bids, b.asks]);
          if (lastBook[tok] === key) continue; lastBook[tok] = key;
          app('books.jsonl', { recv_ms: recv, sent_ms: sent, token: tok, cond: meta.cond, kind: meta.kind, slug: meta.slug, ts: b.timestamp,
            bids: (b.bids || []).map((x) => [+x.price, +x.size]), asks: (b.asks || []).map((x) => [+x.price, +x.size]) });
        }
      } catch (e) { bookErr++; if (bookErr % 20 === 1) log('books error ' + e.message); }
    }
    await sleep(Math.max(0, P - (Date.now() - t0)));
  }
}

// ------------------------------------------------------------------ main
(async () => {
  try { log('clock NTPSynchronized=' + require('child_process').execSync('timedatectl show -p NTPSynchronized --value 2>/dev/null || echo unknown').toString().trim()); }
  catch { log('clock NTPSynchronized=unknown'); }
  log(`window ${WSTART} .. ${WEND}; matches ${cfg.matches.map((m) => m.hltv_id).join(',')}; node ${process.version}`);
  while (!stop && Date.now() < start) await sleep(5000);
  const tasks = [discover(), pollBooks()];
  for (const m of cfg.matches) { if (!live()) break; await connect(m); await sleep(6000); }   // >= 6 s between HLTV page requests
  const hb = setInterval(() => log(`hb books ok=${bookOk} err=${bookErr} tokens=${Object.keys(tokens).length} scorebot=${JSON.stringify(counts)}`), 60000);
  while (live()) await sleep(1000);
  clearInterval(hb); clearInterval(stopTimer);
  for (const s of Object.values(sockets)) try { s.close(); } catch {}
  await Promise.race([Promise.all(tasks), sleep(15000)]);
  log(`done books ok=${bookOk} err=${bookErr} scorebot=${JSON.stringify(counts)}`);
  process.exit(0);
})();
