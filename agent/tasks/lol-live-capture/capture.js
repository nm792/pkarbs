// Live LoL capture: Riot livestats frames (every 10 s) and Polymarket CLOB book top-of-book (every 1 s, REST).
// No npm deps (Node 22 global fetch). Usage: node capture.js <config.json> <label> <minutesBefore> <minutesAfter> <outDir>
// Window: scheduled_start_utc - minutesBefore .. + minutesAfter. Exits at the end of the window or on SIGTERM.
// Frames are deduped on rfc460Timestamp; book rows are written only when the top of book changes.
// Clocks: recv_ms (local receive time) is the only clock on the book side. Livestats keeps the feed's own timestamp.
// 3 Nov: book rows keep 15 price levels per side (queue depth at our resting bid). Frames polled every FRAME_POLL_MS (default 2000) for ALL game ids of the series (cfg.game_ids, else game1_id),
// and every poll writes a line to <label>_polls.jsonl {recv_ms, game, status, newest_ts, n} so the feed delay
// (recv_ms - newest frame timestamp) is measured with ~2 s resolution. Host clock must be NTP-synced (logged at start).
const fs = require('fs');
const path = require('path');
const [, , CFG, LABEL, BEFORE = '90', AFTER = '150', OUT = process.env.HOME + '/lolcap/out'] = process.argv;
const cfg = JSON.parse(fs.readFileSync(CFG, 'utf8')).find((m) => m.label === LABEL);
if (!cfg) { console.error('no label ' + LABEL); process.exit(2); }
fs.mkdirSync(OUT, { recursive: true });
const POLLS = path.join(OUT, `${LABEL}_polls.jsonl`), FRAME_POLL_MS = +(process.env.FRAME_POLL_MS || 2000);
const GAMES = cfg.game_ids || [cfg.game1_id];
const FRAMES = path.join(OUT, `${LABEL}_frames.jsonl`), BOOKS = path.join(OUT, `${LABEL}_books.jsonl`), LOG = path.join(OUT, `${LABEL}_capture.log`);
const log = (m) => fs.appendFileSync(LOG, new Date().toISOString() + ' ' + m + '\n');
const start = Date.parse(cfg.scheduled_start_utc) - BEFORE * 60000;
const end = Date.parse(cfg.scheduled_start_utc) + AFTER * 60000;
const UA = 'Mozilla/5.0 (X11; Linux x86_64) pkarbs-lol-capture';
const seenFrame = new Set();
const lastBook = {};
let stop = false;
process.on('SIGTERM', () => { log('SIGTERM'); stop = true; });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pollFrames() {
  while (!stop && Date.now() < end) {
    const t0 = Date.now();
    await Promise.all(GAMES.map(async (gid) => {
      try {
        // Live games: without startingTime the feed returns the FIRST frames of the game. It rejects (400) a startingTime
        // newer than ~50 s, so ask for the newest accepted 10 s boundary (measured 3 Nov: newest frame 50-60 s old).
        let r, st = Math.floor((Date.now() - 50000) / 10000) * 10000;
        for (let k = 0; k < 3; k++, st -= 10000) {
          r = await fetch(`https://feed.lolesports.com/livestats/v1/window/${gid}?startingTime=${new Date(st).toISOString().slice(0, 19)}Z`, { headers: { 'User-Agent': UA } });
          if (r.status !== 400) break;
        }
        const recv = Date.now();
        let newest = null, n = 0;
        if (r.status === 200) {
          const w = await r.json();
          for (const f of w.frames || []) {
            n++; if (!newest || f.rfc460Timestamp > newest) newest = f.rfc460Timestamp;
            const k = gid + f.rfc460Timestamp;
            if (seenFrame.has(k)) continue;
            seenFrame.add(k);
            fs.appendFileSync(FRAMES, JSON.stringify({ recv_ms: recv, game_id: gid, ...f }) + '\n');
          }
        } else if (r.status !== 204 && r.status !== 404) log('frames status ' + r.status + ' ' + gid);
        if (r.status === 200) fs.appendFileSync(POLLS, JSON.stringify({ recv_ms: recv, sent_ms: t0, game: gid, status: r.status, newest_ts: newest, n }) + '\n');
      } catch (e) { log('frames error ' + gid + ' ' + e.message); }
    }));
    await sleep(Math.max(0, FRAME_POLL_MS - (Date.now() - t0)));
  }
}

async function pollBooks() {
  const tokens = cfg.pm_tokens.slice(0, 2);
  let backoff = 0;
  while (!stop && Date.now() < end) {
    const t0 = Date.now();
    for (let i = 0; i < tokens.length; i++) {
      try {
        const r = await fetch(`https://clob.polymarket.com/book?token_id=${tokens[i]}`, { headers: { 'User-Agent': UA } });
        if (r.status === 429) { backoff = Math.min(backoff * 2 + 2000, 30000); log('429 backoff ' + backoff); await sleep(backoff); }
        else if (r.status === 200) {
          backoff = 0;
          const b = await r.json();
          const lv = (a, desc) => (a || []).map((x) => [+x.price, +x.size]).sort((p, q) => desc ? q[0] - p[0] : p[0] - q[0]).slice(0, 15);
          const bids = lv(b.bids, true), asks = lv(b.asks, false);
          const top = { bid: bids[0]?.[0] ?? null, bid_size: bids[0]?.[1] ?? null, ask: asks[0]?.[0] ?? null, ask_size: asks[0]?.[1] ?? null, bids, asks, hash: b.hash ?? null };
          const key = JSON.stringify(top);
          if (lastBook[tokens[i]] !== key) {
            lastBook[tokens[i]] = key;
            fs.appendFileSync(BOOKS, JSON.stringify({ recv_ms: Date.now(), outcome: cfg.pm_outcomes[i], token: tokens[i], ...top }) + '\n');
          }
        } else log('book status ' + r.status + ' ' + tokens[i].slice(0, 10));
      } catch (e) { log('book error ' + e.message); }
    }
    await sleep(Math.max(0, 1000 - (Date.now() - t0)));
  }
}

(async () => {
  const wait = start - Date.now();
  try { log('clock: ' + require('child_process').execSync('timedatectl show -p NTPSynchronized --value 2>/dev/null || echo unknown').toString().trim()); } catch (e) { log('clock: unknown'); }
  log(`games ${GAMES.join(',')} frame poll ${FRAME_POLL_MS} ms`);
  log(`start ${LABEL} window ${new Date(start).toISOString()} .. ${new Date(end).toISOString()}`);
  if (wait > 0) { log(`waiting ${Math.round(wait / 1000)} s`); await sleep(Math.min(wait, 2 * 3600 * 1000)); }
  await Promise.all([pollFrames(), pollBooks()]);
  log('done');
})();
