// Fake local Polymarket websocket; planted cases: both tokens print -> PASS; only one token acknowledged -> exit 5; acknowledged but no prints -> exit 6; no server -> exit 4.
const http = require('http'), crypto = require('crypto'), path = require('path'), { spawn } = require('child_process');
const frame = (s) => { const b = Buffer.from(s); return Buffer.concat([Buffer.from([0x81, b.length < 126 ? b.length : 126]), ...(b.length < 126 ? [] : [Buffer.from([b.length >> 8, b.length & 255])]), b]); };
function server(mode) {
  const srv = http.createServer((q, r) => r.end('x'));
  srv.on('upgrade', (req, sock) => {
    sock.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + crypto.createHash('sha1').update(req.headers['sec-websocket-key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64') + '\r\n\r\n');
    sock.on('data', (d) => {
      let len = d[1] & 127, off = 2; if (len === 126) { len = d.readUInt16BE(2); off = 4; } const mask = d.slice(off, off + 4); off += 4;
      let txt; try { txt = Buffer.from(d.slice(off, off + len).map((x, i) => x ^ mask[i % 4])).toString(); const m = JSON.parse(txt);
        const toks = m.assets_ids || []; const ack = mode === 'oneack' ? toks.slice(0, 1) : toks;
        for (const a of ack) sock.write(frame(JSON.stringify([{ event_type: 'book', asset_id: a, bids: [], asks: [] }])));
        if (mode === 'ok') { sock.write(frame(JSON.stringify({ event_type: 'last_trade_price', asset_id: toks[0], price: '0.48', size: '40', side: 'SELL', timestamp: '1' }))); sock.write(frame(JSON.stringify({ event_type: 'last_trade_price', asset_id: toks[1], price: '0.52', size: '40', side: 'BUY', timestamp: '1' }))); }
      } catch {} });
    sock.on('error', () => {});
  });
  return new Promise((r) => srv.listen(0, '127.0.0.1', () => r(srv)));
}
const run = (port, secs) => new Promise((res) => { const c = spawn('node', [path.join(__dirname, 'trade_feed_probe.js'), 'TA', 'TB', String(secs)], { env: { ...process.env, PM_WS_URL: 'ws://127.0.0.1:' + port } }); let o = ''; c.stdout.on('data', (d) => o += d); c.on('exit', (code) => res({ code, o })); });
(async () => {
  const bad = [];
  for (const [mode, want] of [['ok', 0], ['oneack', 5], ['noprints', 6]]) { const s = await server(mode); const r = await run(s.address().port, 2); if (r.code !== want) bad.push(`${mode}: exit ${r.code} want ${want} ${r.o}`); if (mode === 'ok') { const j = JSON.parse(r.o.split('\n')[0]); if (j.tokens.TA.trades !== 1 || j.tokens.TB.trades !== 1) bad.push('ok: per-token trade counts wrong ' + r.o); } s.close(); }
  const r4 = await run(1, 2); if (r4.code !== 4) bad.push('no server: exit ' + r4.code + ' want 4');
  console.log(bad.length ? 'FAIL: ' + bad.join(' | ') : 'PASS (feed probe: both tokens print, one token unacked, no prints, no server)'); process.exit(bad.length ? 1 : 0);
})();
