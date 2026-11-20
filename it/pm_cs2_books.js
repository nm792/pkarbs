// PM CS2 book recorder: BOTH tokens' OWN books (YES and NO are separate books) for every Counter-Strike moneyline market
// (Map N Winner and match winner), TICK-LEVEL from Polymarket's market websocket, one local clock (Date.now() at receive).
// No deps (Node 22 global WebSocket/fetch). Read-only. Usage: node pm_cs2_books.js <outDir> [endISO]
// Usage: node pm_cs2_books.js <outDir> [endISO] [floorGB=10]  (stops itself only if free disk falls below floorGB; 0 disables the check)
// Output (format read by feeds/ps_lead_test.py and feeds/ps_cs2_daily_look.py):
//   markets.jsonl {cond,q,outcomes,tokens,smt,start}; books.jsonl {recv_ms,asset,outcome,q,cond,bid,ask,bids:[{price,size}],asks:[...],ts,ev}
// A row is written on every book snapshot and every price_change that changes the local book (top 5 levels each side).
const fs = require('fs'), path = require('path');
const UA = { 'User-Agent': 'pkarbs-cs2-recorder', 'Accept-Encoding': 'gzip' };

function newState() { return { books: {}, meta: {}, rows: 0, msgs: 0, silentTokens: new Set() }; }
const lv = (m, desc) => [...m.entries()].map(([p, s]) => [+p, s]).filter((x) => x[1] > 0).sort((a, b) => desc ? b[0] - a[0] : a[0] - b[0]).slice(0, 5).map(([price, size]) => ({ price, size }));
function emit(st, tok, recv, ts, ev, out) {
  const b = st.books[tok], m = st.meta[tok]; if (!b || !m) return;
  const bids = lv(b.bids, true), asks = lv(b.asks, false);
  out({ recv_ms: recv, asset: tok, outcome: m.outcome, q: m.q, cond: m.cond, bid: bids[0] ? bids[0].price : null, ask: asks[0] ? asks[0].price : null, bids, asks, ts, ev });
  st.rows++;
}
// msg: one decoded Polymarket event object; out(row) writes a row. Returns number of rows written.
function applyMsg(st, e, recv, out) {
  const before = st.rows; st.msgs++;
  const ts = e.timestamp ? +e.timestamp : null;
  if (e.event_type === 'book' && st.meta[e.asset_id]) {
    const b = { bids: new Map(), asks: new Map() };
    for (const x of e.bids || []) b.bids.set(String(+x.price), +x.size);
    for (const x of e.asks || []) b.asks.set(String(+x.price), +x.size);
    st.books[e.asset_id] = b; emit(st, e.asset_id, recv, ts, 'book', out);
  } else if (e.event_type === 'price_change') {
    const touched = new Set();
    for (const c of e.price_changes || []) {
      const b = st.books[c.asset_id]; if (!b) continue;   // no snapshot yet: wait for the book message
      const side = c.side === 'BUY' ? b.bids : b.asks, k = String(+c.price);
      if (+c.size > 0) side.set(k, +c.size); else side.delete(k);
      touched.add(c.asset_id);
    }
    for (const t of touched) emit(st, t, recv, ts, 'price_change', out);
  }
  return st.rows - before;
}
// Choose the Counter-Strike moneyline markets (Map N Winner, match winner) with exactly two tokens and two outcomes.
// opts {now, loMs, hiMs}: keep only markets whose game start is within [now+loMs, now+hiMs] (FIX 20 Nov: gamma date filters use event CREATION date; CS2 events are created a median 17 h before the match, so selection must be by game start).
function pickMarkets(events, opts) {
  const res = [];
  for (const e of events) {
    if (!/counter-strike/i.test(e.title || '')) continue;
    for (const m of e.markets || []) {
      if (!['moneyline', 'child_moneyline'].includes(m.sportsMarketType)) continue;
      let toks, oc; try { toks = JSON.parse(m.clobTokenIds); oc = JSON.parse(m.outcomes); } catch { continue; }
      if (!toks || toks.length !== 2 || !oc || oc.length !== 2) continue;
      const start = Date.parse(m.gameStartTime || e.startTime || '') || null;
      if (opts && start !== null && (start < opts.now + opts.loMs || start > opts.now + opts.hiMs)) continue;
      res.push({ cond: m.conditionId, q: m.question, outcomes: oc, tokens: toks, smt: m.sportsMarketType, start: start && new Date(start).toISOString() });
    }
  }
  return res;
}
const floorBytes = (arg) => { const g = arg === undefined ? 10 : Number(arg); return (Number.isFinite(g) && g >= 0 ? g : 10) * 1e9; };
module.exports = { newState, applyMsg, pickMarkets, floorBytes };

if (require.main === module) {
  const OUT = process.argv[2], END = process.argv[3] ? Date.parse(process.argv[3]) : Infinity, FLOOR = floorBytes(process.argv[4]);
  fs.mkdirSync(OUT, { recursive: true });
  const app = (n, o) => fs.appendFileSync(path.join(OUT, n), JSON.stringify(o) + '\n');
  const log = (m) => fs.appendFileSync(path.join(OUT, 'recorder.log'), new Date().toISOString() + ' ' + m + '\n');
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let stop = false; process.on('SIGTERM', () => { stop = true; });
  const live = () => !stop && Date.now() < END;
  const st = newState(), known = new Set(); let ws = null, open = false, backoff = 2000;
  const subscribe = (toks) => { if (open && toks.length) ws.send(JSON.stringify({ assets_ids: toks, operation: 'subscribe' })); };
  async function discover() {
    while (live()) {
      try {
        const lo = new Date(Date.now() - 8 * 3600e3).toISOString(), hi = new Date(Date.now() + 36 * 3600e3).toISOString();
        const fresh = [];
        const win = { now: Date.now(), loMs: -8 * 3600e3, hiMs: 36 * 3600e3 };
        for (const base of [`https://gamma-api.polymarket.com/events?closed=false&active=true&limit=100&tag_slug=counter-strike-2`,
                            `https://gamma-api.polymarket.com/events?closed=false&active=true&limit=100&start_date_min=${lo}&start_date_max=${hi}`]) {
          for (let off = 0; off < 2000; off += 100) {
            const r = await fetch(`${base}&offset=${off}`, { headers: UA });
            if (r.status !== 200) { log('gamma status ' + r.status); break; }
            const evs = await r.json(); fresh.push(...pickMarkets(evs, win)); if (evs.length < 100) break;
          }
        }
        const newToks = [];
        for (const m of fresh) {
          if (known.has(m.cond)) continue; known.add(m.cond); app('markets.jsonl', m); log('market ' + m.q);
          m.tokens.forEach((t, i) => { st.meta[t] = { outcome: m.outcomes[i], q: m.q, cond: m.cond }; newToks.push(t); });
        }
        subscribe(newToks);
        try { const fr = fs.statfsSync(OUT).bavail * fs.statfsSync(OUT).bsize; if (fr < FLOOR) { log('disk below floor ' + (FLOOR / 1e9) + ' GB (free ' + (fr / 1e9).toFixed(1) + ' GB): stopping'); stop = true; } } catch {}
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
          for (const e of Array.isArray(d) ? d : [d]) applyMsg(st, e, recv, (row) => app('books.jsonl', row));
        };
        ws.onclose = done; ws.onerror = (e) => { log('ws error ' + (e.message || '')); done(); };
        chk = setInterval(() => { if (!live()) done(); }, 1000);
      });
      // a reconnect resends a fresh snapshot (book messages), so local books are rebuilt from the new snapshot
      st.books = {}; if (live()) { await sleep(backoff); backoff = Math.min(backoff * 2, 60000); }
    }
  }
  setInterval(() => log(`alive rows=${st.rows} msgs=${st.msgs} markets=${known.size}`), 600000);
  log('start ' + new Date().toISOString());
  Promise.all([discover(), stream()]).then(() => { log('done'); process.exit(0); });
}
