// Test for feeds/pm_dota_books.js against a local mock gamma + CLOB server (no network, Node 22, no deps).
// Case A: a market first listed with an OLD start (window closed) is RESCHEDULED to now+5 min: both tokens must then be recorded.
// Case B: >100 events: a market on page 2 must be discovered (paging).
// Usage: node test_pm_dota_books.js [path/to/pm_dota_books.js]   (exit 0 = ALL PASS)
const http = require('http'), { spawn } = require('child_process'), fs = require('fs'), os = require('os'), path = require('path');
const script = process.argv[2] || path.join(__dirname, 'pm_dota_books.js');
let polls = 0, tick = 0;
const mkMarket = (id, q, start) => ({ conditionId: id, question: q, outcomes: '["A","B"]', clobTokenIds: JSON.stringify(['tok' + id + 'a', 'tok' + id + 'b']), gameStartTime: start, sportsMarketType: 'moneyline' });
const srv = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x');
  if (u.pathname === '/events') {
    const off = +u.searchParams.get('offset') || 0;
    if (off === 0) polls++;
    const start = polls >= 2 ? new Date(Date.now() + 300000).toISOString() : '2026-11-19 10:00:00+00';
    const evs = [];
    if (off === 0) { evs.push({ markets: [mkMarket('R1', 'Dota 2: X vs Y - Game 1 Winner', start)] }); for (let i = 0; i < 99; i++) evs.push({ markets: [mkMarket('F' + i, 'Dota 2: filler ' + i + ' Winner junk', start)] }); }
    if (off === 100) evs.push({ markets: [mkMarket('P2', 'Dota 2: Page vs Two - Game 1 Winner', new Date(Date.now() + 300000).toISOString())] });
    res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(evs));
  } else if (u.pathname === '/book') {
    tick++; res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify({ bids: [{ price: '0.40', size: String(10 + tick) }], asks: [{ price: '0.60', size: '5' }] }));
  } else { res.statusCode = 404; res.end(); }
});
srv.listen(0, () => {
  const port = srv.address().port, out = fs.mkdtempSync(path.join(os.tmpdir(), 'pmd-'));
  const end = new Date(Date.now() + 9000).toISOString();
  const p = spawn('node', [script, out, end], { env: { ...process.env, GAMMA_URL: 'http://127.0.0.1:' + port, CLOB_URL: 'http://127.0.0.1:' + port, DISC_MS: '1500' }, stdio: 'inherit' });
  p.on('exit', () => {
    srv.close();
    const rows = fs.existsSync(out + '/books.jsonl') ? fs.readFileSync(out + '/books.jsonl', 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
    const log = fs.readFileSync(out + '/recorder.log', 'utf8');
    const toks = (c) => new Set(rows.filter((r) => r.cond === c).map((r) => r.token));
    const fails = [];
    if (!/reschedule .*Game 1 Winner/.test(log)) fails.push('A: no reschedule logged');
    if (toks('R1').size !== 2) fails.push('A: rescheduled market recorded ' + toks('R1').size + ' tokens, need 2');
    if (toks('P2').size !== 2) fails.push('B: page-2 market recorded ' + toks('P2').size + ' tokens, need 2');
    if (toks('F0').size !== 0) fails.push('filler (non-Winner title) must not be recorded');
    if (fails.length) { console.log('FAIL', fails.join('; '), 'rows', rows.length); process.exit(1); }
    console.log('ALL PASS rows', rows.length); process.exit(0);
  });
});
