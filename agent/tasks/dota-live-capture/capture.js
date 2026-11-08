// Live Dota 2 capture, 4 Nov 2026. No npm deps (Node 22 fetch + built-in WebSocket).
// Usage: node capture.js <config.json> <outDir> <windowStartISO> <windowEndISO>
// Sources (all free, no key):
//  1. Valve www.dota2.com/webapi/IDOTA2League/GetLiveGames/v001 every 5 s -> live league games (server_steam_id, teams, clock).
//  2. Valve www.dota2.com/webapi/IDOTA2MatchStats/GetRealtimeStats/v001?server_steam_id= every 2 s for every league game
//     with team names (cap 10) -> kills, net worth, buildings, per-player stats. Written only when match.timestamp changes.
//  3. OpenDota api/live every 30 s -> 'delay' tag (spectator delay) per match.
//  4. Polymarket sports WS: all messages whose leagueAbbreviation contains 'dota'.
//  5. Polymarket CLOB /book for the first token of each Game N Winner / match market of series inside their window
//     (scheduled start -15 min .. +240 min), every 2 s, written only on change.
// Every row carries recv_ms (local receive time). Host clock must be NTP-synced (logged at start).
const fs = require('fs'), path = require('path');
const [, , CFG, OUT, WSTART, WEND] = process.argv;
const cfg = JSON.parse(fs.readFileSync(CFG, 'utf8'));
const BASE = process.env.DOTA_BASE || 'https://www.dota2.com';
fs.mkdirSync(OUT, { recursive: true });
const F = (n) => path.join(OUT, n);
const log = (m) => fs.appendFileSync(F('capture.log'), new Date().toISOString() + ' ' + m + '\n');
const app = (n, o) => fs.appendFileSync(F(n), JSON.stringify(o) + '\n');
const start = Date.parse(WSTART), end = Date.parse(WEND);
const UA = 'Mozilla/5.0 (X11; Linux x86_64) pkarbs-dota-capture';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let stop = false; process.on('SIGTERM', () => { log('SIGTERM'); stop = true; });
const live = () => !stop && Date.now() < end;
const get = async (u) => { const r = await fetch(u, { headers: { 'User-Agent': UA } }); return [r.status, r.status === 200 ? await r.json() : null]; };

let games = {};               // server_steam_id -> GetLiveGames row
async function pollLeague() {
  while (live()) {
    const t0 = Date.now();
    try {
      const [s, j] = await get(`${BASE}/webapi/IDOTA2League/GetLiveGames/v001`);
      const recv = Date.now();
      if (s === 200) {
        const g = {}; for (const x of j.games || []) if (x.radiant_name || x.dire_name) g[x.server_steam_id] = x;
        games = g; app('league_games.jsonl', { recv_ms: recv, games: j.games || [] });
      } else log('league status ' + s);
    } catch (e) { log('league error ' + e.message); }
    await sleep(Math.max(0, 5000 - (Date.now() - t0)));
  }
}
const lastTs = {};
async function pollRealtime() {
  while (live()) {
    const t0 = Date.now();
    const ids = Object.keys(games).slice(0, 10);
    await Promise.all(ids.map(async (sid) => {
      try {
        const sent = Date.now();
        const [s, j] = await get(`${BASE}/webapi/IDOTA2MatchStats/GetRealtimeStats/v001?server_steam_id=${sid}`);
        const recv = Date.now();
        if (s !== 200 || !j || !j.match) { if (s !== 200) log('rt status ' + s + ' ' + sid); return; }
        const ts = j.match.timestamp;
        app('rt_polls.jsonl', { recv_ms: recv, sent_ms: sent, sid, match_id: j.match.match_id, ts, game_time: j.match.game_time, live_time: games[sid]?.time });
        if (lastTs[sid] === ts) return; lastTs[sid] = ts;
        const tm = (j.teams || []).map((t) => ({ team: t.team_number, name: t.team_name, score: t.score, nw: t.net_worth,
          players: (t.players || []).map((p) => [p.heroid, p.kill_count, p.death_count, p.assists_count, p.net_worth, p.level]) }));
        const bld = (j.buildings || []).map((b) => [b.team, b.type, b.lane, b.tier, b.destroyed ? 1 : 0]);
        app('realtime.jsonl', { recv_ms: recv, sid, match_id: j.match.match_id, league_id: j.match.league_id, ts, game_time: j.match.game_time,
          game_state: j.match.game_state, teams: tm, buildings: bld, gold: (j.graph_data?.graph_gold || []).slice(-3) });
      } catch (e) { log('rt error ' + sid + ' ' + e.message); }
    }));
    await sleep(Math.max(0, 2000 - (Date.now() - t0)));
  }
}
async function pollOpenDota() {
  while (live()) {
    try {
      const [s, j] = await get('https://api.opendota.com/api/live'); const recv = Date.now();
      if (s === 200) app('opendota_live.jsonl', { recv_ms: recv, games: j.filter((g) => g.league_id).map((g) => ({ match_id: g.match_id, server_steam_id: g.server_steam_id, league_id: g.league_id,
        r: g.team_name_radiant, d: g.team_name_dire, delay: g.delay, game_time: g.game_time, last_update_time: g.last_update_time, rs: g.radiant_score, ds: g.dire_score, lead: g.radiant_lead })) });
      else log('opendota status ' + s);
    } catch (e) { log('opendota error ' + e.message); }
    for (let i = 0; i < 30 && live(); i++) await sleep(1000);
  }
}
const lastBook = {};
async function pollBooks() {
  while (live()) {
    const t0 = Date.now(), now = Date.now();
    const toks = [];
    for (const s of cfg) { const st = Date.parse(s.scheduled_start_utc); if (now >= st - 15 * 60000 && now <= st + 240 * 60000) for (const m of s.markets) toks.push([s.label, m.q, m.tokens[0], m.outcomes[0]]); }
    for (const [label, q, tok, oc] of toks) {
      try {
        const [st, b] = await get(`https://clob.polymarket.com/book?token_id=${tok}`); const recv = Date.now();
        if (st !== 200) { log('book status ' + st); if (st === 429) await sleep(5000); continue; }
        const lv = (a, desc) => (a || []).map((x) => [+x.price, +x.size]).sort((p, q2) => desc ? q2[0] - p[0] : p[0] - q2[0]).slice(0, 10);
        const bids = lv(b.bids, true), asks = lv(b.asks, false), k = JSON.stringify([bids, asks]);
        if (lastBook[tok] === k) continue; lastBook[tok] = k;
        app('books.jsonl', { recv_ms: recv, label, q, outcome: oc, token: tok, bid: bids[0]?.[0] ?? null, ask: asks[0]?.[0] ?? null, bids, asks });
      } catch (e) { log('book error ' + e.message); }
    }
    await sleep(Math.max(0, 2000 - (Date.now() - t0)));
  }
}
function sportsWs() {
  if (!globalThis.WebSocket) { log('sportsws: no WebSocket'); return; }
  const go = () => {
    if (!live()) return;
    const ws = new globalThis.WebSocket('wss://sports-api.polymarket.com/ws');
    ws.addEventListener('open', () => log('sportsws open'));
    ws.addEventListener('message', (ev) => {
      const s = String(ev.data); if (s === 'ping') { ws.send('pong'); return; }
      let g; try { g = JSON.parse(s); } catch { return; }
      if (String(g.leagueAbbreviation || '').toLowerCase().includes('dota')) app('sportsws.jsonl', { recv_ms: Date.now(), ...g });
    });
    ws.addEventListener('close', () => setTimeout(go, 3000));
    ws.addEventListener('error', () => log('sportsws error'));
  };
  go();
}
(async () => {
  try { log('clock NTP: ' + require('child_process').execSync('timedatectl show -p NTPSynchronized --value 2>/dev/null || echo unknown').toString().trim()); } catch (e) { log('clock unknown'); }
  log(`window ${new Date(start).toISOString()} .. ${new Date(end).toISOString()} base ${BASE}`);
  const w = start - Date.now(); if (w > 0) { log(`waiting ${Math.round(w / 1000)} s`); await sleep(w); }
  sportsWs();
  await Promise.all([pollLeague(), pollRealtime(), pollOpenDota(), pollBooks()]);
  log('done'); process.exit(0);
})();
