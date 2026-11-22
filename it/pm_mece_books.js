// PM MULTI-LEG (MECE) book recorder, 20 Nov 2026 (sports MECE NO-side thread): BOTH tokens' OWN books (YES and NO are separate books)
// for every leg of 3-way soccer sets (moneyline home/draw/away, halftime result) so the buy-all-YES / buy-all-NO / sell-all sets can be scored on own asks.
// SLIM (pattern of pm_cs2_books.js 20 Nov): live markets only (game start -1 h .. +3.5 h), a row only when best bid/ask price or size changes (deep levels at most once per 10 s),
// top 3 levels, one gzip member per 30 s appended to ONE FILE PER UTC HOUR (books-YYYYMMDDHH.jsonl.gz, crash-safe multi-member gzip). Stops itself under floorGB free or when its folder passes capGB.
// Read-only. Node 22, no deps. Usage: node pm_mece_books.js <outDir> [endISO] [floorGB=10] [capGB=3]
// Output: markets.jsonl {cond,q,outcomes,tokens,smt,start,slug,set,league}  (set = slug|sportsMarketType = the mutually exclusive group); books-*.jsonl.gz rows as pm_cs2_books.js.
// Gamma note: date filters on /events use CREATION date, so discovery is /events/keyset?tag_slug=soccer&end_date_min/max (end = game end) then selection by game start (checked 20 Nov: 350 three-way events in 36 h that way).
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const { newState, applyMsg, floorBytes, hourStr } = require('./pm_cs2_books.js');
const UA = { 'User-Agent': 'pkarbs-mece-recorder', 'Accept-Encoding': 'gzip' };
const SETS = new Set(['moneyline', 'soccer_halftime_result']);   // exactly-three-market neg-risk groups
const LO_MS = -3.5 * 3600e3, HI_MS = (Number(process.env.MECE_HI_H) || 1) * 3600e3;   // keep markets whose game start is within [now-3.5h, now+MECE_HI_H h] (default 1 h)

// events: Gamma event objects -> markets of every complete 3-market group (same event, same sportsMarketType), each with exactly two tokens.
function pickMarkets(events, opts) {
  const res = [];
  for (const e of events) {
    if (e.ended === true || e.closed === true) continue;
    const grp = {};
    for (const m of e.markets || []) { if (SETS.has(m.sportsMarketType) && m.closed !== true) (grp[m.sportsMarketType] = grp[m.sportsMarketType] || []).push(m); }
    for (const [smt, ms] of Object.entries(grp)) {
      if (ms.length !== 3) continue;
      const rows = [];
      for (const m of ms) {
        let toks, oc; try { toks = JSON.parse(m.clobTokenIds); oc = JSON.parse(m.outcomes); } catch { rows.length = 0; break; }
        if (!toks || toks.length !== 2 || !oc || oc.length !== 2) { rows.length = 0; break; }
        const start = Date.parse(m.gameStartTime || e.startTime || '') || null;
        if (start === null || (opts && (start < opts.now + LO_MS || start > opts.now + HI_MS))) { rows.length = 0; break; }
        rows.push({ cond: m.conditionId, q: m.question, outcomes: oc, tokens: toks, smt, start: new Date(start).toISOString(), slug: e.slug, set: e.slug + '|' + smt, league: String(e.slug || '').split('-')[0] });
      }
      res.push(...rows);
    }
  }
  return res;
}
// buffered gzip appender per UTC hour: add(row) buffers by the row's own hour; flush() appends ONE gzip member per hour file touched. Returns bytes written.
function hourWriter(dir) {
  const buf = new Map();
  return {
    add(o) { const h = hourStr(o.recv_ms); (buf.get(h) || buf.set(h, []).get(h)).push(JSON.stringify(o)); },
    flush() { let n = 0; for (const [h, b] of buf) { if (!b.length) continue; const z = zlib.gzipSync(Buffer.from(b.join('\n') + '\n')); fs.appendFileSync(path.join(dir, 'books-' + h + '.jsonl.gz'), z); n += z.length; } buf.clear(); return n; },
    pending() { let n = 0; for (const b of buf.values()) n += b.length; return n; },
  };
}
function dirBytes(dir) { let n = 0; for (const f of fs.readdirSync(dir)) { try { n += fs.statSync(path.join(dir, f)).size; } catch {} } return n; }
async function fetchEvents(tag, lo, hi, log) {
  const out = []; let cur = null;
  for (let i = 0; i < 60; i++) {
    const u = `https://gamma-api.polymarket.com/events/keyset?tag_slug=${tag}&closed=false&limit=100&end_date_min=${lo}&end_date_max=${hi}` + (cur ? `&after_cursor=${encodeURIComponent(cur)}` : '');
    const r = await fetch(u, { headers: UA });
    if (r.status !== 200) { log('gamma status ' + r.status); break; }
    const j = await r.json(), es = Array.isArray(j) ? j : (j.events || []);
    out.push(...es); cur = j.next_cursor || null; if (!cur || !es.length) break;
  }
  return out;
}
module.exports = { pickMarkets, hourWriter, dirBytes, SETS };

if (require.main === module) {
  const OUT = process.argv[2], END = process.argv[3] ? Date.parse(process.argv[3]) : Infinity, FLOOR = floorBytes(process.argv[4]), CAP = (process.argv[5] === undefined ? 3 : Number(process.argv[5])) * 1e9;
  fs.mkdirSync(OUT, { recursive: true });
  const gw = hourWriter(OUT);
  const app = (n, o) => fs.appendFileSync(path.join(OUT, n), JSON.stringify(o) + '\n');
  const log = (m) => fs.appendFileSync(path.join(OUT, 'recorder.log'), new Date().toISOString() + ' ' + m + '\n');
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let stop = false; process.on('SIGTERM', () => { stop = true; gw.flush(); });
  const live = () => !stop && Date.now() < END;
  const st = newState(), known = new Set(); let ws = null, open = false, backoff = 2000;
  setInterval(() => { try { gw.flush(); } catch (e) { log('flush error ' + e.message); } }, 30000);
  const subscribe = (toks) => { if (open && toks.length) ws.send(JSON.stringify({ assets_ids: toks, operation: 'subscribe' })); };
  async function discover() {
    while (live()) {
      try {
        const lo = new Date(Date.now() - 6 * 3600e3).toISOString(), hi = new Date(Date.now() + 12 * 3600e3).toISOString();
        const evs = await fetchEvents('soccer', lo, hi, log);
        const fresh = pickMarkets(evs, { now: Date.now() }), freshSet = new Set(fresh.map((m) => m.cond)), gone = [];
        for (const c of [...known]) if (!freshSet.has(c)) { known.delete(c); for (const t of Object.keys(st.meta)) if (st.meta[t].cond === c) { gone.push(t); delete st.meta[t]; delete st.books[t]; delete st.last[t]; } }
        if (open && gone.length) ws.send(JSON.stringify({ assets_ids: gone, operation: 'unsubscribe' }));
        const newToks = [];
        for (const m of fresh) {
          if (known.has(m.cond)) continue; known.add(m.cond); app('markets.jsonl', m); log('market ' + m.set + ' ' + m.q);
          m.tokens.forEach((t, i) => { st.meta[t] = { outcome: m.outcomes[i], q: m.q, cond: m.cond }; newToks.push(t); });
        }
        subscribe(newToks);
        log(`discover events=${evs.length} live-markets=${known.size}`);
        try {
          const s = fs.statfsSync(OUT), fr = s.bavail * s.bsize;
          if (fr < FLOOR) { log('disk below floor ' + (FLOOR / 1e9) + ' GB (free ' + (fr / 1e9).toFixed(1) + ' GB): stopping'); stop = true; }
          if (CAP > 0 && dirBytes(OUT) > CAP) { log('folder over cap ' + (CAP / 1e9) + ' GB: stopping'); stop = true; }
        } catch (e) { log('statfs error ' + e.message); }
      } catch (e) { log('discover error ' + e.message); }
      for (let i = 0; i < 300 && live(); i++) await sleep(1000);
    }
  }
  async function stream() {
    while (live()) {
      await new Promise((resolve) => {
        const toks = Object.keys(st.meta); let hb, chk, finished = false;
        const done = () => { if (finished) return; finished = true; open = false; clearInterval(hb); clearInterval(chk); try { ws.close(); } catch {} resolve(); };
        ws = new WebSocket('wss://ws-subscriptions-clob.polymarket.com/ws/market');
        ws.onopen = () => { open = true; backoff = 2000; log('ws open, tokens ' + toks.length); ws.send(JSON.stringify({ assets_ids: toks, type: 'market' })); hb = setInterval(() => { try { ws.send('PING'); } catch {} }, 10000); };
        ws.onmessage = (ev) => {
          const recv = Date.now(); let d; try { d = JSON.parse(ev.data); } catch { return; }
          for (const e of Array.isArray(d) ? d : [d]) applyMsg(st, e, recv, (row) => gw.add(row));
        };
        ws.onclose = done; ws.onerror = (e) => { log('ws error ' + (e.message || '')); done(); };
        chk = setInterval(() => { if (!live()) done(); }, 1000);
      });
      st.books = {}; st.last = {}; if (live()) { await sleep(backoff); backoff = Math.min(backoff * 2, 60000); }
    }
  }
  setInterval(() => log(`alive rows=${st.rows} msgs=${st.msgs} markets=${known.size} pending=${gw.pending()}`), 600000);
  log('start ' + new Date().toISOString());
  Promise.all([discover(), stream()]).then(() => { gw.flush(); log('done'); process.exit(0); });
}
