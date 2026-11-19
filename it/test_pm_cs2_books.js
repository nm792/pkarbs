// Test for pm_cs2_books.js. Run: node test_pm_cs2_books.js  (prints PASS or FAIL: ..., exit code 1 on failure). Every check can fail.
const { newState, applyMsg, pickMarkets, floorBytes } = require('./pm_cs2_books.js');
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
console.log(bad.length ? 'FAIL: ' + bad.join('; ') : 'PASS (9 checks, each able to fail)'); process.exit(bad.length ? 1 : 0);
