// PM EVENT book recorder for scheduled macro releases (23 Nov 2026, re-audit thread, R-070 D / DISCARDED-AUDIT rank 5).
// Records BOTH tokens' OWN books (YES and NO separate) of every market of the named Gamma events, so a stale-quote pickoff can be scored on own-token asks.
// Window: release time R (ISO, UTC) -> records from R-PRE_MIN to R+POST_MIN (defaults 15 and 15 min), idle outside; WS stays open only inside the window.
// Read-only. Node 22, no deps. Reuses pm_cs2_books.js (book state) and pm_mece_books.js (hourly gzip writer, lock).
// Usage: node pm_event_books.js <outDir> <releaseISO> <slug1,slug2,...> [floorGB=10] [capGB=0.5] [preflight [seconds]]
// Output: markets.jsonl {cond,q,outcomes,tokens,slug,release}; books-YYYYMMDDHH.jsonl.gz rows as pm_cs2_books.js (one row per best bid/ask or size change, top 3 levels).
// Preflight ignores the window (books exist any time): run 60 s live, PASS only if ws_tokens == 2 x markets > 0 and rows > 0; exit 0 PASS, 5 FAIL, 2 second copy, 4 no markets.
const fs = require('fs'), path = require('path');
const { newState, applyMsg, floorBytes } = require('./pm_cs2_books.js');
const { hourWriter, dirBytes, acquireLock } = require('./pm_mece_books.js');
const UA = { 'User-Agent': 'pkarbs-event-recorder', 'Accept-Encoding': 'gzip' };

// events: Gamma event objects -> markets with exactly two tokens (skips closed markets and malformed token lists)
function pickMarkets(events, release) {
  const res = [];
  for (const e of events) {
    for (const m of e.markets || []) {
      if (m.closed === true) continue;
      let toks, oc; try { toks = JSON.parse(m.clobTokenIds); oc = JSON.parse(m.outcomes); } catch { continue; }
      if (!toks || toks.length !== 2 || !oc || oc.length !== 2) continue;
      res.push({ cond: m.conditionId, q: m.question, outcomes: oc, tokens: toks, slug: e.slug, release });
    }
  }
  return res;
}
// inWindow(now, releaseMs, preMin, postMin): true from R-pre to R+post
function inWindow(now, releaseMs, preMin = 15, postMin = 15) { return now >= releaseMs - preMin * 60e3 && now <= releaseMs + postMin * 60e3; }
module.exports = { pickMarkets, inWindow };

async function fetchSlug(slug, log) {
  for (let a = 0; a < 3; a++) {
    try {
      const r = await fetch('https://gamma-api.polymarket.com/events?slug=' + encodeURIComponent(slug), { headers: UA });
      if (r.ok) return await r.json();
      log('gamma ' + slug + ' http ' + r.status);
    } catch (e) { log('gamma ' + slug + ' error ' + e.message); }
    await new Promise((r) => setTimeout(r, 2000 * (a + 1)));
  }
  return [];
}

if (require.main === module) {
  const [OUT, REL, SLUGS] = process.argv.slice(2, 5), FLOOR = floorBytes(process.argv[5]), CAP = (process.argv[6] === undefined ? 0.5 : Number(process.argv[6])) * 1e9;
  const PREFLIGHT = process.argv[7] === 'preflight' ? (parseInt(process.argv[8], 10) || 60) : 0;
  const RMS = Date.parse(REL), PRE = Number(process.env.PRE_MIN) || 15, POST = Number(process.env.POST_MIN) || 15;
  if (!OUT || !SLUGS || isNaN(RMS)) { console.error('usage: node pm_event_books.js <outDir> <releaseISO> <slug1,slug2> [floorGB] [capGB] [preflight [s]]'); process.exit(64); }
  if (!acquireLock(OUT)) { console.error('REFUSED: second copy (pidfile ' + path.join(OUT, 'recorder.pid') + ')'); process.exit(2); }
  const unlock = () => { try { if (parseInt(fs.readFileSync(path.join(OUT, 'recorder.pid'), 'utf8'), 10) === process.pid) fs.unlinkSync(path.join(OUT, 'recorder.pid')); } catch {} };
  process.on('exit', unlock);
  const gw = hourWriter(OUT), st = newState();
  const log = (m) => fs.appendFileSync(path.join(OUT, 'recorder.log'), new Date().toISOString() + ' ' + m + '\n');
  let ws = null, open = false, wsTokens = 0, stop = false, markets = [];
  process.on('SIGTERM', () => { stop = true; gw.flush(); });
  setInterval(() => { try { gw.flush(); } catch (e) { log('flush error ' + e.message); } }, 30000);
  setInterval(() => log(`alive rows=${st.rows} msgs=${st.msgs} markets=${markets.length} ws_tokens=${wsTokens} window=${PREFLIGHT ? 'preflight' : inWindow(Date.now(), RMS, PRE, POST)}`), PREFLIGHT ? 5000 : 300000);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const active = () => PREFLIGHT || inWindow(Date.now(), RMS, PRE, POST);
  (async () => {
    const evs = []; for (const s of SLUGS.split(',')) evs.push(...await fetchSlug(s, log));
    markets = pickMarkets(evs, REL);
    if (!markets.length) { log('FATAL: 0 markets for slugs ' + SLUGS + '; exit 4'); console.error('FATAL: 0 markets'); process.exit(4); }
    for (const m of markets) { fs.appendFileSync(path.join(OUT, 'markets.jsonl'), JSON.stringify(m) + '\n'); m.tokens.forEach((t, i) => { st.meta[t] = { outcome: m.outcomes[i], q: m.q, cond: m.cond }; }); }
    log('start ' + new Date().toISOString() + ' markets=' + markets.length + ' release=' + REL + (PREFLIGHT ? ' PREFLIGHT ' + PREFLIGHT + 's' : ''));
    if (PREFLIGHT) setTimeout(() => {
      gw.flush(); const exp = markets.length * 2, ok = wsTokens > 0 && wsTokens === exp && st.rows > 0;
      const rep = { preflight: ok ? 'PASS' : 'FAIL', markets: markets.length, expected_tokens: exp, ws_tokens: wsTokens, rows_written: st.rows, msgs: st.msgs, seconds: PREFLIGHT, bytes: dirBytes(OUT) };
      log('PREFLIGHT ' + JSON.stringify(rep)); console.log(JSON.stringify(rep)); unlock(); process.exit(ok ? 0 : 5);
    }, PREFLIGHT * 1000);
    while (!stop && (PREFLIGHT || Date.now() < RMS + POST * 60e3)) {
      if (!active()) { await sleep(1000); continue; }
      await new Promise((resolve) => {
        const toks = Object.keys(st.meta); let hb, chk, fin = false;
        const done = () => { if (fin) return; fin = true; open = false; wsTokens = 0; clearInterval(hb); clearInterval(chk); try { ws.close(); } catch {} resolve(); };
        ws = new WebSocket('wss://ws-subscriptions-clob.polymarket.com/ws/market');
        ws.onopen = () => { open = true; wsTokens = toks.length; log('ws open, tokens ' + toks.length); ws.send(JSON.stringify({ assets_ids: toks, type: 'market' })); hb = setInterval(() => { try { ws.send('PING'); } catch {} }, 10000); };
        ws.onmessage = (ev) => { const recv = Date.now(); let d; try { d = JSON.parse(ev.data); } catch { return; } for (const e of Array.isArray(d) ? d : [d]) applyMsg(st, e, recv, (row) => gw.add(row)); };
        ws.onclose = done; ws.onerror = (e) => { log('ws error ' + (e.message || '')); done(); };
        chk = setInterval(() => { if (stop || !active()) done(); try { const s = fs.statfsSync(OUT); if (s.bavail * s.bsize < FLOOR) { log('disk below floor: stopping'); stop = true; } if (CAP > 0 && dirBytes(OUT) > CAP) { log('folder over cap: stopping'); stop = true; } } catch {} }, 1000);
      });
      st.books = {}; st.last = {}; await sleep(2000);
    }
    gw.flush(); log('done'); process.exit(0);
  })();
}
