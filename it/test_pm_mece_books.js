// Test for pm_mece_books.js. Run: node test_pm_mece_books.js (PASS or FAIL: ..., exit 1). Every check can fail.
const fs = require('fs'), os = require('os'), path = require('path'), zlib = require('zlib');
const { pickMarkets, hourWriter, dirBytes, acquireLock } = require('./pm_mece_books.js');
const bad = [], NOW = Date.parse('2026-11-21T15:00:00Z');
const mk = (smt, c, start, toks = '["1","2"]') => ({ sportsMarketType: smt, clobTokenIds: toks, outcomes: '["Yes","No"]', question: 'q' + c, conditionId: c, gameStartTime: start });
const live = '2026-11-21T15:30:00Z', old = '2026-11-21T09:00:00Z', far = '2026-11-22T15:00:00Z';
const ev = [
  { slug: 'epl-a-b-2026-11-21', markets: [mk('moneyline', 'a1', live), mk('moneyline', 'a2', live), mk('moneyline', 'a3', live), mk('totals', 'x', live), mk('soccer_exact_score', 'y', live)] },
  { slug: 'epl-c-d-2026-11-21', markets: [mk('moneyline', 'b1', live), mk('moneyline', 'b2', live)] },               // only 2 legs: skipped
  { slug: 'epl-e-f-2026-11-21', markets: [mk('moneyline', 'c1', live), mk('moneyline', 'c2', live), mk('moneyline', 'c3', live, '["1"]')] }, // bad tokens: skipped whole set
  { slug: 'epl-g-h-2026-11-21', markets: [mk('moneyline', 'd1', old), mk('moneyline', 'd2', old), mk('moneyline', 'd3', old)] },  // started 6 h ago
  { slug: 'epl-i-j-2026-11-22', markets: [mk('moneyline', 'e1', far), mk('moneyline', 'e2', far), mk('moneyline', 'e3', far)] },   // tomorrow
  { slug: 'epl-k-l-2026-11-21', ended: true, markets: [mk('moneyline', 'f1', live), mk('moneyline', 'f2', live), mk('moneyline', 'f3', live)] },
  { slug: 'laliga-m-n-2026-11-21', markets: [mk('moneyline', 'g1', live), mk('moneyline', 'g2', live), mk('moneyline', 'g3', live), mk('soccer_halftime_result', 'h1', live), mk('soccer_halftime_result', 'h2', live), mk('soccer_halftime_result', 'h3', live)] }];
const pk = pickMarkets(ev, { now: NOW }), conds = pk.map((m) => m.cond).join(',');
if (conds !== 'a1,a2,a3,g1,g2,g3,h1,h2,h3') bad.push('pickMarkets wrong: ' + conds);
if (pk[0] && (pk[0].set !== 'epl-a-b-2026-11-21|moneyline' || pk[0].league !== 'epl')) bad.push('set/league wrong ' + JSON.stringify(pk[0]));
if (new Set(pk.map((m) => m.set)).size !== 3) bad.push('expected 3 distinct sets');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'mece-')), w = hourWriter(dir);
if (w.flush() !== 0 || fs.readdirSync(dir).length) bad.push('empty flush wrote');
const h1 = Date.parse('2026-11-21T15:59:59Z'), h2 = Date.parse('2026-11-21T16:00:01Z');
w.add({ recv_ms: h1, asset: 'A', bid: 0.5 }); w.add({ recv_ms: h2, asset: 'B', bid: 0.4 }); w.flush(); w.add({ recv_ms: h1 + 5, asset: 'A', bid: 0.51 }); w.flush();
const files = fs.readdirSync(dir).sort();
if (files.join() !== 'books-2026112115.jsonl.gz,books-2026112116.jsonl.gz') bad.push('hour files wrong: ' + files);
else {
  const r15 = zlib.gunzipSync(fs.readFileSync(path.join(dir, files[0]))).toString().trim().split('\n').map(JSON.parse), r16 = zlib.gunzipSync(fs.readFileSync(path.join(dir, files[1]))).toString().trim().split('\n').map(JSON.parse);
  if (r15.length !== 2 || r15[1].bid !== 0.51 || r16.length !== 1 || r16[0].asset !== 'B') bad.push('multi-member round trip wrong');
}
if (dirBytes(dir) <= 0) bad.push('dirBytes zero');
const ld = fs.mkdtempSync(path.join(os.tmpdir(), 'mece-lock-'));
if (acquireLock(ld, process.pid) !== true) bad.push('first lock not acquired');
if (acquireLock(ld, process.ppid) !== false) bad.push('second copy (live pid) not refused');   // pidfile holds our pid, alive, != ppid
fs.writeFileSync(path.join(ld, 'recorder.pid'), '99999999');
if (acquireLock(ld, process.pid) !== true) bad.push('stale pid not taken over');
console.log(bad.length ? 'FAIL: ' + bad.join('; ') : 'PASS (9 checks, each able to fail)'); process.exit(bad.length ? 1 : 0);
