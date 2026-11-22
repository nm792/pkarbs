// PM NHL moneyline book recorder (Goalserve thread, 20 Nov 2026): BOTH tokens' OWN books (YES and NO are separate books), tick level,
// one local clock (Date.now() at receive). Reuses newState/applyMsg/floorBytes from pm_cs2_books.js (same dir). Read-only; Node 22, no deps.
// Disk-light: rows are buffered and appended as one gzip member every 30 s to books.jsonl.gz (multi-member gzip, crash-safe, readable by
// Python gzip and by feeds/ps_lead_test.py find(d,'books')). Only the moneyline market of an NHL or NBA game event (slug nhl|nba-xxx-yyy-YYYY-MM-DD; NBA re-enabled 22 Nov by R-029/R-054, was cut 20 Nov).
// Usage: node pm_sport_books.js <outDir> [endISO] [floorGB=10] [league=nhl|nba|tennis]   (stops itself below floorGB free; 0 disables). league default nhl; nba = NBA game moneylines, same code path; tennis = every tennis moneyline (match winner).
// Output: markets.jsonl {cond,q,outcomes,tokens,smt,start,slug,league}; books.jsonl.gz rows as pm_cs2_books.js (recv_ms, asset, outcome, bids, asks ...).
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const { newState, applyMsg, floorBytes } = require('./pm_cs2_books.js');
const UA = { 'User-Agent': 'pkarbs-sport-recorder', 'Accept-Encoding': 'gzip' };
const SLUG = /^(nhl|nba)-[a-z0-9]+-[a-z0-9]+-\d{4}-\d\d-\d\d$/;

// events: Gamma event objects. -> NHL/NBA game-event moneyline markets with exactly two tokens and two outcomes.
function pickMarkets(events, league = 'nhl') {
  const res = [];
  for (const e of events) {
    let mt = league === 'tennis' ? [null, 'tennis'] : SLUG.exec(e.slug || ''); if (!mt || e.ended === true) continue;
    if (league !== 'tennis' && mt[1] !== league) continue; // league filter: nhl mode never records NBA and vice versa
    if (league === 'tennis' && !(e.tags || []).some((t) => t && t.slug === 'tennis')) continue;
    for (const m of e.markets || []) {
      if (m.sportsMarketType !== 'moneyline') continue;
      let toks, oc; try { toks = JSON.parse(m.clobTokenIds); oc = JSON.parse(m.outcomes); } catch { continue; }
      if (!toks || toks.length !== 2 || !oc || oc.length !== 2) continue;
      const start = Date.parse(m.gameStartTime || e.startTime || '') || null;
      res.push({ cond: m.conditionId, q: m.question, outcomes: oc, tokens: toks, smt: m.sportsMarketType, start: start && new Date(start).toISOString(), slug: e.slug, league: mt[1] });
    }
  }
  return res;
}
// buffered gzip appender: add(row) buffers a JSON line; flush() appends ONE gzip member (no-op when empty). Returns bytes written.
function gzWriter(file) {
  let buf = [];
  return {
    add(o) { buf.push(JSON.stringify(o)); },
    flush() { if (!buf.length) return 0; const z = zlib.gzipSync(Buffer.from(buf.join('\n') + '\n')); buf = []; fs.appendFileSync(file, z); return z.length; },
    pending() { return buf.length; },
  };
}
module.exports = { pickMarkets, gzWriter, SLUG };

if (require.main === module) {
  const OUT = process.argv[2], END = process.argv[3] ? Date.parse(process.argv[3]) : Infinity, FLOOR = floorBytes(process.argv[4]), LEAGUE = ['tennis', 'nba'].includes(process.argv[5]) ? process.argv[5] : 'nhl';
  fs.mkdirSync(OUT, { recursive: true });
  const gw = gzWriter(path.join(OUT, 'books.jsonl.gz'));
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
        const lo = new Date(Date.now() - 8 * 3600e3).toISOString(), hi = new Date(Date.now() + 36 * 3600e3).toISOString();
        const fresh = [];
        for (const tag of [LEAGUE]) {
          for (let off = 0; off < 1000; off += 100) {
            const r = await fetch(`https://gamma-api.polymarket.com/events?tag_slug=${tag}&closed=false&limit=100&offset=${off}`, { headers: UA });
            if (r.status !== 200) { log('gamma status ' + r.status); break; }
            const evs = await r.json(); fresh.push(...pickMarkets(evs, LEAGUE).filter((m) => m.start && m.start >= lo && m.start <= hi)); if (evs.length < 100) break;
          }
        }
        const newToks = [];
        for (const m of fresh) {
          if (known.has(m.cond)) continue; known.add(m.cond); app('markets.jsonl', m); log('market ' + m.slug + ' ' + m.q);
          m.tokens.forEach((t, i) => { st.meta[t] = { outcome: m.outcomes[i], q: m.q, cond: m.cond }; newToks.push(t); });
        }
        subscribe(newToks);
        try { const s = fs.statfsSync(OUT), fr = s.bavail * s.bsize; if (fr < FLOOR) { log('disk below floor ' + (FLOOR / 1e9) + ' GB (free ' + (fr / 1e9).toFixed(1) + ' GB): stopping'); stop = true; } } catch (e) { log('statfs error ' + e.message); }
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
      st.books = {}; if (live()) { await sleep(backoff); backoff = Math.min(backoff * 2, 60000); }
    }
  }
  setInterval(() => log(`alive rows=${st.rows} msgs=${st.msgs} markets=${known.size} pending=${gw.pending()}`), 600000);
  log('start ' + new Date().toISOString());
  Promise.all([discover(), stream()]).then(() => { gw.flush(); log('done'); process.exit(0); });
}
