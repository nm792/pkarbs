// Live-path test of pm_sport_books.js against a LOCAL fake Gamma + fake Polymarket websocket (R-057/R-058). Run: node test_pm_sport_books_live.js
// PASS or FAIL: ..., exit 1. Checks: preflight PASS with tokens>0 and rows>0; ZERO markets => preflight FAIL (exit 5) and normal run exits 4; second copy refused (exit 2);
// stale pidfile taken over; the socket is NEVER opened with 0 tokens (ws open line says tokens 2, not 0).
const http = require('http'), crypto = require('crypto'), fs = require('fs'), os = require('os'), path = require('path'), { spawnSync, spawn } = require('child_process');
const bad = []; const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'psbl-'));
const frame = (s) => { const b = Buffer.from(s); return Buffer.concat([Buffer.from([0x81, b.length < 126 ? b.length : 126]), ...(b.length < 126 ? [] : [Buffer.from([b.length >> 8, b.length & 255])]), b]); };
function server(markets) {
  const srv = http.createServer((req, res) => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(markets)); });
  srv.on('upgrade', (req, sock) => {
    sock.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + crypto.createHash('sha1').update(req.headers['sec-websocket-key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64') + '\r\n\r\n');
    sock.on('data', (d) => { // client frames are masked; decode first text frame and answer with a book per subscribed asset
      let len = d[1] & 127, off = 2; if (len === 126) { len = d.readUInt16BE(2); off = 4; } const mask = d.slice(off, off + 4); off += 4;
      let txt = Buffer.from(d.slice(off, off + len).map((x, i) => x ^ mask[i % 4])).toString(); if (txt === 'PING') return; let m; try { m = JSON.parse(txt); } catch { return; }
      for (const a of m.assets_ids || []) sock.write(frame(JSON.stringify([{ event_type: 'book', asset_id: a, timestamp: String(Date.now()), bids: [{ price: '0.50', size: '100' }], asks: [{ price: '0.54', size: '80' }] }])));
    });
    sock.on('error', () => {});
  });
  return new Promise((r) => srv.listen(0, '127.0.0.1', () => r(srv)));
}
const ev = () => [{ slug: 'nba-aaa-bbb-2026-11-23', startTime: new Date(Date.now() + 3600e3).toISOString(), markets: [{ sportsMarketType: 'moneyline', clobTokenIds: '["T1","T2"]', outcomes: '["A","B"]', question: 'A vs B', conditionId: 'c1', gameStartTime: new Date(Date.now() + 3600e3).toISOString() }] }];
const run = (srv, out, args, env = {}, ms = 30000) => new Promise((resolve) => { // async (the fake servers live in THIS process; spawnSync would block them)
  const c = spawn('node', [path.join(__dirname, 'pm_sport_books.js'), out, ...args], { env: { ...process.env, GAMMA_URL: 'http://127.0.0.1:' + srv.address().port, PM_WS_URL: 'ws://127.0.0.1:' + srv.address().port, ...env } });
  let so = '', se = ''; c.stdout.on('data', (d) => so += d); c.stderr.on('data', (d) => se += d); const t = setTimeout(() => c.kill('SIGKILL'), ms);
  c.on('exit', (code) => { clearTimeout(t); resolve({ status: code, stdout: so, stderr: se }); }); });
(async () => {
  const s1 = await server(ev()), o1 = path.join(tmp, 'o1'), r1 = await run(s1, o1, ['', '0', 'nba', 'preflight', '4']);
  let j1 = {}; try { j1 = JSON.parse(r1.stdout.trim().split('\n').pop()); } catch {}
  if (r1.status !== 0 || j1.preflight !== 'PASS' || j1.ws_tokens !== 2 || !(j1.rows_written > 0)) bad.push('preflight with 1 market should PASS 2 tokens rows>0: ' + r1.status + ' ' + r1.stdout + r1.stderr);
  const log1 = fs.readFileSync(path.join(o1, 'recorder.log'), 'utf8'); if (/tokens 0\b/.test(log1.replace(/ws_tokens=\d+/g, '')) || !/ws open, tokens 2/.test(log1)) bad.push('ws open must say tokens 2, never 0: ' + log1);
  if (fs.existsSync(path.join(o1, 'recorder.pid'))) bad.push('pidfile not removed at exit');
  const s0 = await server([]), o0 = path.join(tmp, 'o0'), r0 = await run(s0, o0, ['', '0', 'nba', 'preflight', '3']);
  if (r0.status !== 5) bad.push('preflight with 0 markets must exit 5, got ' + r0.status);
  const r4 = await run(s0, path.join(tmp, 'o4'), ['', '0', 'nba'], { NOTOKEN_EXIT_S: '2' }, 20000);
  if (r4.status !== 4) bad.push('normal run with 0 tokens must exit 4, got ' + r4.status);
  // single instance: hold a long run, start a second on the same dir
  const o2 = path.join(tmp, 'o2'), end = new Date(Date.now() + 15000).toISOString();
  const first = spawn('node', [path.join(__dirname, 'pm_sport_books.js'), o2, end, '0', 'nba'], { env: { ...process.env, GAMMA_URL: 'http://127.0.0.1:' + s1.address().port, PM_WS_URL: 'ws://127.0.0.1:' + s1.address().port }, stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 2500));
  const second = await run(s1, o2, [end, '0', 'nba']); if (second.status !== 2) bad.push('second copy must be refused with exit 2, got ' + second.status);
  if (first.exitCode !== null) bad.push('first recorder must still be running after the refused second copy');
  first.kill('SIGTERM'); await new Promise((r) => setTimeout(r, 1500));
  // stale pidfile (dead pid) is taken over
  const o3 = path.join(tmp, 'o3'); fs.mkdirSync(o3); fs.writeFileSync(path.join(o3, 'recorder.pid'), '999999');
  const r3 = await run(s1, o3, ['', '0', 'nba', 'preflight', '3']); if (r3.status !== 0) bad.push('stale pidfile must be taken over, preflight status ' + r3.status);
  console.log(bad.length ? 'FAIL: ' + bad.join(' | ') : 'PASS (live-path: 8 checks incl. preflight, tokens 0, single instance)'); s1.close(); s0.close(); process.exit(bad.length ? 1 : 0);
})();
