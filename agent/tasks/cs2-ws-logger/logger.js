// Log Polymarket sports WS CS2 frames. Emits a change record when a match's score string changes.
// Receive time is the only clock (no server timestamp per update). Reconnects on close, error, or 60 s silence.
const fs = require('fs');
const WebSocket = require('ws');
const HOURS = parseFloat(process.env.HOURS || '2');
const OUT = process.env.OUT || (process.env.HOME + '/cs2logger/out');
fs.mkdirSync(OUT, { recursive: true });
const RAW = OUT + '/cs2_frames.jsonl', CHG = OUT + '/cs2_changes.jsonl', LOG = OUT + '/logger.log';
const end = Date.now() + HOURS * 3600 * 1000;
const last = {};            // gameId -> last score string
const log = (m) => fs.appendFileSync(LOG, new Date().toISOString() + ' ' + m + '\n');
let ws, watchdog, reconnects = 0;
function connect() {
  if (Date.now() > end) { log('done'); process.exit(0); }
  ws = new WebSocket('wss://sports-api.polymarket.com/ws', { headers: { 'User-Agent': 'Mozilla/5.0 pkarbs-cs2-logger' } });
  const bump = () => { clearTimeout(watchdog); watchdog = setTimeout(() => { log('silence 60s, reconnect'); ws.terminate(); }, 60000); };
  ws.on('open', () => { log('open #' + reconnects); bump(); });
  ws.on('message', (d) => {
    bump();
    const s = d.toString();
    if (s === 'ping') { ws.send('pong'); return; }
    const now = Date.now();
    let g; try { g = JSON.parse(s); } catch { return; }
    if (g.leagueAbbreviation !== 'cs2') return;
    fs.appendFileSync(RAW, JSON.stringify({ recv_ms: now, recv_iso: new Date(now).toISOString(), ...g }) + '\n');
    const key = String(g.gameId), prev = last[key];
    if (prev !== g.score) {
      fs.appendFileSync(CHG, JSON.stringify({ recv_ms: now, recv_iso: new Date(now).toISOString(), gameId: g.gameId,
        home: g.homeTeam, away: g.awayTeam, prev: prev ?? null, score: g.score, period: g.period, status: g.status, live: g.live, ended: g.ended }) + '\n');
      last[key] = g.score;
    }
  });
  const again = () => { clearTimeout(watchdog); reconnects++; setTimeout(connect, 5000); };
  ws.on('close', (c, r) => { log('close ' + c + ' ' + String(r)); again(); });
  ws.on('error', (e) => { log('error ' + e.message); });
}
process.on('SIGTERM', () => { log('SIGTERM'); process.exit(0); });
connect();
