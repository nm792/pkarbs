// Test for pm_cs2_books.js. Run: node test_pm_cs2_books.js  (prints PASS or FAIL: ..., exit code 1 on failure). Every check can fail.
const { newState, applyMsg, pickMarkets, floorBytes, hourStr, compactOldHours } = require('./pm_cs2_books.js');
const fs = require('fs'), os = require('os'), path = require('path'), zlib = require('zlib');
const bad = [], rows = [], out = (r) => rows.push(r);
const st = newState(); st.meta.A = { outcome: 'Alpha', q: 'Counter-Strike: Alpha vs Beta - Map 1 Winner', cond: 'c1' }; st.meta.B = { outcome: 'Beta', q: 'q', cond: 'c1' };
// price_change before any snapshot writes nothing
if (applyMsg(st, { event_type: 'price_change', timestamp: '1', price_changes: [{ asset_id: 'A', side: 'BUY', price: '0.5', size: '10' }] }, 1000, out) !== 0) bad.push('row written without snapshot');
// snapshots: each token is its OWN book (A bid .50 ask .54; B bid .44 ask .48: NOT 1 - A)
applyMsg(st, { event_type: 'book', asset_id: 'A', timestamp: '2', bids: [{ price: '0.50', size: '10' }], asks: [{ price: '0.54', size: '5' }] }, 2000, out);
applyMsg(st, { event_type: 'book', asset_id: 'B', timestamp: '2', bids: [{ price: '0.44', size: '9' }], asks: [{ price: '0.48', size: '5' }] }, 2000, out);
if (rows.length !== 2 || rows[1].bid !== 0.44 || rows[1].ask !== 0.48 || rows[1].asset !== 'B') bad.push('own-book snapshot wrong ' + JSON.stringify(rows[1]));
// planted: A best bid rises to .56 (new bid level above the ask -> mid moves); recv time carried
applyMsg(st, { event_type: 'price_change', timestamp: '3', price_changes: [{ asset_id: 'A', side: 'BUY', price: '0.53', size: '4' }] }, 3500, out);
const r3 = rows[2]; if (!r3 || r3.recv_ms !== 3500 || r3.bid !== 0.53 || r3.ask !== 0.54 || r3.bids.length !== 2) bad.push('price_change not applied ' + JSON.stringify(r3));
// removal (size 0) drops the level
applyMsg(st, { event_type: 'price_change', timestamp: '4', price_changes: [{ asset_id: 'A', side: 'BUY', price: '0.53', size: '0' }] }, 4000, out);
if (rows[3].bid !== 0.50) bad.push('level removal failed ' + JSON.stringify(rows[3]));
// unknown token ignored
if (applyMsg(st, { event_type: 'book', asset_id: 'Z', bids: [], asks: [] }, 5, out) !== 0) bad.push('unknown token recorded');
// output is readable the way ps_lead_test reads it: mid = (max bid + min ask)/2 from {price} lists
const mid = (r) => (Math.max(...r.bids.map((x) => +x.price)) + Math.min(...r.asks.map((x) => +x.price))) / 2;
if (Math.abs(mid(rows[1]) - 0.46) > 1e-9) bad.push('mid wrong');
// market pick: only Counter-Strike moneyline/child_moneyline with 2 tokens; totals and other games dropped
const ev = [{ title: 'Counter-Strike: A vs B (BO3)', startTime: '2026-11-19T09:00:00Z', markets: [
  { sportsMarketType: 'child_moneyline', clobTokenIds: '["1","2"]', outcomes: '["A","B"]', question: 'Map 1 Winner', conditionId: 'x' },
  { sportsMarketType: 'totals', clobTokenIds: '["3","4"]', outcomes: '["Over","Under"]', question: 'O/U', conditionId: 'y' }] },
  { title: 'Dota 2: C vs D', markets: [{ sportsMarketType: 'moneyline', clobTokenIds: '["5","6"]', outcomes: '["C","D"]', conditionId: 'z' }] }];
const pk = pickMarkets(ev); if (pk.length !== 1 || pk[0].cond !== 'x') bad.push('pickMarkets wrong ' + JSON.stringify(pk));
if (floorBytes(undefined) !== 10e9 || floorBytes('7') !== 7e9 || floorBytes('0') !== 0 || floorBytes('x') !== 10e9) bad.push('floor parse');
// FIX 20 Nov: selection by game start, not creation: a market whose match starts in 20 h is kept, one 3 days away or 10 h ago is dropped; no opts keeps the old behaviour
const nowT = 1_800_000_000_000, mk = (id, off) => ({ title: 'Counter-Strike: A vs B', markets: [{ sportsMarketType: 'moneyline', clobTokenIds: '["1","2"]', outcomes: '["A","B"]', conditionId: id, question: 'q', gameStartTime: new Date(nowT + off).toISOString() }] });
const pw = pickMarkets([mk('soon', 20 * 3600e3), mk('far', 72 * 3600e3), mk('old', -10 * 3600e3)], { now: nowT, loMs: -8 * 3600e3, hiMs: 36 * 3600e3 }).map((x) => x.cond).join(',');
if (pw !== 'soon') bad.push('game-start window wrong: ' + pw);
if (pickMarkets([mk('far', 72 * 3600e3)]).length !== 1) bad.push('no-opts must keep every market');

// SLIM 20 Nov: (a) a change only at level 2 within 10 s of the last row is NOT written; (b) after 10 s it is; (c) a best-price change is always written;
// (d) levels beyond 3 never stored and a change only beyond level 3 is not written; (e) rows carry no q; (f) closed hours are gzipped and removed, current hour untouched.
{
  const s2 = newState(), r2 = [], o2 = (r) => r2.push(r); s2.meta.T = { outcome: 'T', q: 'long question text', cond: 'c' };
  applyMsg(s2, { event_type: 'book', asset_id: 'T', timestamp: '1', bids: [{ price: '0.50', size: '10' }, { price: '0.49', size: '5' }, { price: '0.48', size: '5' }, { price: '0.47', size: '5' }], asks: [{ price: '0.52', size: '8' }] }, 1000, o2);
  if (r2.length !== 1 || r2[0].bids.length !== 3 || 'q' in r2[0]) bad.push('slim row shape ' + JSON.stringify(r2[0]));
  applyMsg(s2, { event_type: 'price_change', timestamp: '2', price_changes: [{ asset_id: 'T', side: 'BUY', price: '0.49', size: '9' }] }, 3000, o2);
  if (r2.length !== 1) bad.push('level-2 change inside 10 s was written');
  applyMsg(s2, { event_type: 'price_change', timestamp: '3', price_changes: [{ asset_id: 'T', side: 'BUY', price: '0.49', size: '11' }] }, 12000, o2);
  if (r2.length !== 2) bad.push('level-2 change after 10 s not written');
  applyMsg(s2, { event_type: 'price_change', timestamp: '4', price_changes: [{ asset_id: 'T', side: 'BUY', price: '0.46', size: '9' }] }, 13000, o2);
  if (r2.length !== 2) bad.push('change beyond level 3 was written');
  applyMsg(s2, { event_type: 'price_change', timestamp: '5', price_changes: [{ asset_id: 'T', side: 'SELL', price: '0.51', size: '3' }] }, 13500, o2);
  if (r2.length !== 3 || r2[2].ask !== 0.51) bad.push('best-price change not written immediately');
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'pmb-')), t0 = Date.parse('2026-11-20T05:30:00Z');
  fs.writeFileSync(path.join(d, 'books-' + hourStr(t0 - 3600e3) + '.jsonl'), '{"a":1}\n{"a":2}\n'); fs.writeFileSync(path.join(d, 'books-' + hourStr(t0) + '.jsonl'), '{"a":3}\n');
  const n = compactOldHours(d, t0), fl = fs.readdirSync(d).sort();
  if (n !== 1 || fl.join() !== 'books-2026112004.jsonl.gz,books-2026112005.jsonl' || zlib.gunzipSync(fs.readFileSync(path.join(d, fl[0]))).toString() !== '{"a":1}\n{"a":2}\n') bad.push('hourly gzip wrong ' + fl.join());
}
console.log(bad.length ? 'FAIL: ' + bad.join('; ') : 'PASS (17 checks, each able to fail)'); process.exit(bad.length ? 1 : 0);
