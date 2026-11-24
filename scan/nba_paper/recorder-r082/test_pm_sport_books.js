// Test for pm_sport_books.js. Run: node test_pm_sport_books.js  (PASS or FAIL: ..., exit 1). Every check can fail.
const fs = require('fs'), os = require('os'), path = require('path'), zlib = require('zlib');
const { pickMarkets, gzWriter } = require('./pm_sport_books.js');
const bad = [];
const mk = (smt, c, toks = '["1","2"]') => ({ sportsMarketType: smt, clobTokenIds: toks, outcomes: '["A","B"]', question: 'q' + c, conditionId: c, gameStartTime: '2026-11-21T18:00:00Z' });
const ev = [
  { slug: 'nhl-edm-car-2026-11-21', startTime: '2026-11-21T18:00:00Z', markets: [mk('moneyline', 'a'), mk('totals', 'b'), mk('moneyline', 'bad', '["1"]')] },
  { slug: 'nba-cha-atl-2026-11-20', markets: [mk('moneyline', 'c')] },
  { slug: 'nba-gsw-mem-2026-11-19-exact-margin', markets: [mk('moneyline', 'd')] },
  { slug: 'nhl-utah-nsh-2026-11-27', markets: [mk('moneyline', 'e')] },
  { slug: 'nhl-lak-tor-2026-11-19', ended: true, markets: [mk('moneyline', 'g')] },
  { slug: 'cs2-a-b-2026-11-21', markets: [mk('moneyline', 'f')] }];
const pk = pickMarkets(ev), conds = pk.map((m) => m.cond).join(',');
if (conds !== 'a,e') bad.push('pickMarkets wrong: ' + conds);
if (pk[0] && (pk[0].league !== 'nhl' || pk[0].start !== '2026-11-21T18:00:00.000Z')) bad.push('league/start wrong ' + JSON.stringify(pk[0]));
// NBA mode (R-029): only nba game slugs, league field 'nba', exact-margin sub-event slug excluded, nhl never picked
const nb = pickMarkets(ev, 'nba');
if (nb.map((m) => m.cond).join(',') !== 'c') bad.push('nba pick wrong: ' + nb.map((m) => m.cond).join(','));
if (nb[0] && nb[0].league !== 'nba') bad.push('nba league field wrong');
if (!/'nba'/.test(require('fs').readFileSync(path.join(__dirname, 'pm_sport_books.js'), 'utf8').match(/if \(!\['nhl'.*/)[0])) bad.push('CLI does not accept nba');
// R-082 leagues
{
  const { LEAGUES } = require('./pm_sport_books.js');
  const mk = (slug, n) => ({ slug, startTime: '2026-11-28T15:00:00Z', markets: Array.from({ length: n }, (_, i) => ({ sportsMarketType: 'moneyline', conditionId: slug + i, question: 'q' + i, clobTokenIds: JSON.stringify(['t' + slug + i + 'y', 't' + slug + i + 'n']), outcomes: '["Yes","No"]' })) });
  const evs = [mk('epl-lee-cov-2026-11-28', 3), mk('epl-lee-cov-2026-11-28-exact-score', 3), mk('fl1-ang-rcl-2026-11-28', 3), mk('atp-pham-bolt-2026-11-24', 1), mk('nfl-den-pit-2026-11-27', 1), mk('nfl-den-pit-2026-11-27-player-props', 1)];
  const e = pickMarkets(evs, 'epl'); if (e.length !== 3 || !e.every((m) => m.league === 'epl' && m.tokens.length === 2)) bad.push('epl: want 3 moneylines x 2 tokens, no suffix events, got ' + e.length);
  if (pickMarkets(evs, 'fl1').length !== 3 || pickMarkets(evs, 'atp').length !== 1 || pickMarkets(evs, 'nfl').length !== 1) bad.push('fl1/atp/nfl picks wrong');
  if (pickMarkets(evs, 'lal').length !== 0 || pickMarkets(evs, 'sea').length !== 0) bad.push('league leak: lal/sea picked another league');
  if (pickMarkets(evs, 'nba').length !== 0) bad.push('nba picked a soccer/other slug');
  for (const k of ['epl', 'fl1', 'lal', 'sea', 'atp', 'nfl', 'cfb']) if (!LEAGUES[k] || !LEAGUES[k].series || !(LEAGUES[k].durH > 0)) bad.push('LEAGUES.' + k + ' incomplete');
  const r = require('child_process').spawnSync('node', [path.join(__dirname, 'pm_sport_books.js'), require('os').tmpdir() + '/lg-bogus', '', '10', 'bogus'], { encoding: 'utf8' });
  if (r.status !== 3) bad.push('unknown league must exit 3, got ' + r.status);
}
// tennis mode: any slug, but the event must carry the tennis tag; only the 2-outcome moneyline is picked
const tv = [{ slug: 'atp-mayot-gaston-2026-11-19', tags: [{ slug: 'sports' }, { slug: 'tennis' }], markets: [mk('moneyline', 't1'), mk('totals', 't2')] },
  { slug: 'itf-x-y-2026-11-19', tags: [{ slug: 'tennis' }], ended: true, markets: [mk('moneyline', 't3')] },
  { slug: 'nhl-edm-car-2026-11-21', tags: [{ slug: 'nhl' }], markets: [mk('moneyline', 't4')] }];
const tp = pickMarkets(tv, 'tennis').map((m) => m.cond).join(',');
if (tp !== 't1') bad.push('tennis pick wrong: ' + tp);
if (pickMarkets(tv).map((m) => m.cond).join(',') !== 't4') bad.push('nhl mode must pick only the nhl slug');
// gz writer: two flushes make a two-member gzip file that decompresses to all rows in order; empty flush writes nothing
const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'psb-')), 'books.jsonl.gz'), w = gzWriter(f);
if (w.flush() !== 0 || fs.existsSync(f)) bad.push('empty flush wrote');
w.add({ recv_ms: 1, asset: 'A', bids: [{ price: 0.5, size: 10 }], asks: [{ price: 0.54, size: 5 }] }); w.add({ recv_ms: 2, asset: 'B' }); w.flush();
w.add({ recv_ms: 3, asset: 'A' }); w.flush();
const rows = zlib.gunzipSync(fs.readFileSync(f)).toString().trim().split('\n').map(JSON.parse);
if (rows.length !== 3 || rows.map((r) => r.recv_ms).join() !== '1,2,3' || rows[0].asks[0].size !== 5) bad.push('gz round trip wrong ' + JSON.stringify(rows));
// disk-light: 5000 realistic rows compress to under 15% of raw
const w2 = gzWriter(f + '2'); let raw = 0;
for (let i = 0; i < 5000; i++) { const r = { recv_ms: 1795000000000 + i * 137, asset: '7'.repeat(70), outcome: 'Edmonton Oilers', q: 'Oilers vs. Hurricanes', cond: '0x' + 'a'.repeat(64), bid: 0.5 + (i % 5) / 100, ask: 0.54, bids: [{ price: 0.5, size: 100 + i }, { price: 0.49, size: 300 }, { price: 0.48, size: 50 }], asks: [{ price: 0.54, size: 80 }, { price: 0.55, size: 120 }], ts: 1795000000000 + i * 137, ev: 'price_change' }; raw += JSON.stringify(r).length + 1; w2.add(r); }
const gzb = w2.flush(); if (!(gzb < 0.15 * raw)) bad.push('compression ' + gzb + ' of ' + raw);
console.log(bad.length ? 'FAIL: ' + bad.join('; ') : 'PASS (12 original + 7 R-082 league checks, each able to fail)'); process.exit(bad.length ? 1 : 0);
