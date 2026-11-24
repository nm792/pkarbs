// Test for pm_event_books.js. Run: node test_pm_event_books.js (PASS or FAIL: ..., exit 1). Every check can fail.
const { pickMarkets, inWindow } = require('./pm_event_books.js');
const bad = [];
const mk = (c, toks = '["1","2"]', closed = false) => ({ conditionId: c, question: 'q' + c, clobTokenIds: toks, outcomes: '["Yes","No"]', closed });
const pk = pickMarkets([{ slug: 'core-pce', markets: [mk('a'), mk('b', '["1"]'), mk('c', '["1","2"]', true), mk('d', 'notjson'), mk('e')] }], '2026-11-25T13:30:00Z');
if (pk.map((m) => m.cond).join() !== 'a,e') bad.push('pickMarkets wrong: ' + pk.map((m) => m.cond));
if (pk[0] && pk[0].seconds_delay !== null) bad.push('seconds_delay must start null');
if (pk[0] && (pk[0].slug !== 'core-pce' || pk[0].tokens.length !== 2)) bad.push('market row wrong');
const R = Date.parse('2026-11-25T13:30:00Z');
if (inWindow(R - 31 * 60e3, R)) bad.push('31 min before must be outside');
if (!inWindow(R - 29 * 60e3, R)) bad.push('29 min before must be inside');
if (!inWindow(R + 29 * 60e3, R)) bad.push('29 min after must be inside');
if (inWindow(R + 31 * 60e3, R)) bad.push('31 min after must be outside');
if (inWindow(R - 5 * 60e3, R, 3, 3)) bad.push('custom pre window ignored');
console.log(bad.length ? 'FAIL: ' + bad.join('; ') : 'PASS (7 checks, each able to fail)'); process.exit(bad.length ? 1 : 0);
