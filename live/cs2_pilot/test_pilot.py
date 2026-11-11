"""Offline tests for the CS2 pilot (PROTOCOL rule 1: synthetic cases with hand-checked answers, plus a replay of a
logged WS match). Run: python3 test_pilot.py  -> must end with 'N of N tests pass'."""
import asyncio, gzip, json, os, sys, tempfile, types
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import model as MD
import pilot as P
P.CFG.update(SHARE_CAP=1000, MATCH_CAP_USD=250.0, LOSS_LIMIT_USD=500.0)   # cap-logic tests use $250/$500; the $50 sizing has its own tests

R = []
def check(name, cond):
    R.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name)


# ---- model
check('pmap 0-0 at q=0.5 is 0.5', abs(MD.pmap(0, 0, 0.5) - 0.5) < 1e-9)
check('pmap 12-0 near 1', MD.pmap(12, 0, 0.5) > 0.99)
check('q_from inverts pmap', abs(MD.pmap(0, 0, MD.q_from(0.7)) - 0.7) < 0.01)
check('series 1-0 with map at 0.5 is 0.75', abs(MD.series(1, 0, 0.5) - 0.75) < 1e-9)
check('parse score', MD.parse('7-4|1-0|Bo3') == dict(ra=7, rb=4, ma=1, mb=0, bo=3))
check('parse 000-000', MD.parse('000-000|1-0|Bo3')['ra'] == 0)
a, b = MD.parse('7-4|1-0|Bo3'), MD.parse('8-4|1-0|Bo3')
check('round event', MD.round_event(a, b) == ('round', 2))
check('reset event', MD.round_event(MD.parse('12-6|0-0|Bo3'), MD.parse('000-000|0-0|Bo3')) == ('reset', 1))
check('map end event', MD.round_event(MD.parse('12-6|0-0|Bo3'), MD.parse('000-000|1-0|Bo3')) == ('map_end', 1))
check('round win moves home map prob up', MD.map_move(a, b, 0.5) > 0)
check('round win moves home match prob up', MD.match_move(a, b) > 0)
check('team match', MD.same_team('Team Liquid', 'Liquid') and not MD.same_team('MOUZ', 'PARIVISION'))


# ---- strategy on a fake market
def mk_market(o0_home=True):
    m = {'conditionId': '0xabc', 'clobTokenIds': json.dumps(['T0', 'T1']), 'outcomes': json.dumps(['Home', 'Away']),
         'orderPriceMinTickSize': '0.01', 'orderMinSize': 5, 'feeSchedule': {'rate': 0.05, 'rebateRate': 0.15}}
    return P.Market(1, 'match', m, 'Home' if o0_home else 'Away')

def pilot():
    d = tempfile.mkdtemp(); a = types.SimpleNamespace(mode='dry', out=d)
    p = P.Pilot(a); g = P.Game(1, {'title': 't', 'slug': 's'}); g.home = 'Home'; p.games[1] = g
    p.log_rows = []; orig = p.log
    def log(typ, **kw): p.log_rows.append((typ, kw)); orig(typ, **kw)
    p.log = log
    async def nofill(m, o, T): return None
    p.paper_fills = nofill
    return p, g

def set_book(m, bb, ba, t, lvl0=None, lvl1=None):
    m.book[0] = (bb, ba, lvl0 or {bb: 100.0}); m.book[1] = (round(1 - ba, 2), round(1 - bb, 2), lvl1 or {round(1 - ba, 2): 50.0})
    m.mids.append((t, (bb + ba) / 2))

p, g = pilot(); m = mk_market(); g.markets['match'] = m
set_book(m, 0.49, 0.51, 100.0)
m.window = dict(eid='e1', R=130.0, j=0.04, base=0.50, end=160.0, tok=0)
asyncio.run(p.manage(m, 131.0))
o = m.order
check('bid placed on token0 at mid*0.975 rounded up (0.4875 -> 0.49)', o is not None and abs(o['price'] - 0.49) < 1e-9)
check('bid below best ask (never cross)', o['price'] < 0.51)
check('size capped by $250 per match', o['size'] == 510 and o['size'] * o['price'] <= 250)
check('queue ahead = level size at our price (100 at 0.49 here)', o['ahead0'] == 100.0)
# mid moves by >= j: cancel
set_book(m, 0.54, 0.56, 132.0)
asyncio.run(p.manage(m, 132.0))
check('cancel once price already moved by j', m.order is None and any(k == 'order_cancel' and kw['why'] == 'already moved' for k, kw in p.log_rows))
# window end
set_book(m, 0.49, 0.51, 133.0); asyncio.run(p.manage(m, 133.0))
check('re-placed while still inside window', m.order is not None)
asyncio.run(p.manage(m, 161.0))
check('cancel at window end', m.order is None and m.window is None)

# token1 side with negative jump
p, g = pilot(); m = mk_market(); g.markets['match'] = m
set_book(m, 0.59, 0.61, 100.0)
m.window = dict(eid='e2', R=130.0, j=-0.03, base=0.60, end=160.0, tok=1)
asyncio.run(p.manage(m, 131.0))
check('token1 bid = (1-mid)*0.975 = 0.39 exactly', m.order is not None and abs(m.order['price'] - 0.39) < 1e-9 and m.order['tok'] == 1)

# global loss limit: realized -400 leaves $100 of room
p, g = pilot(); m = mk_market(); g.markets['match'] = m; p.st['realized'] = -400.0
set_book(m, 0.49, 0.51, 100.0)
m.window = dict(eid='e3', R=130.0, j=0.04, base=0.50, end=160.0, tok=0)
asyncio.run(p.manage(m, 131.0))
check('loss limit caps size (room $100)', m.order is not None and m.order['size'] * m.order['price'] <= 100.0 + 1e-6)
p.st['realized'] = -499.5; m.order = None
asyncio.run(p.manage(m, 132.0))
check('no order when room < $1', m.order is None)

# open exposure: existing unresolved position of $240 in this match leaves $10
p, g = pilot(); m = mk_market(); g.markets['match'] = m
p.st['positions']['0xold'] = dict(gid=1, kind='map1', tokens=['a', 'b'], tok={'0': [400.0, 240.0]})
set_book(m, 0.49, 0.51, 100.0); m.window = dict(eid='e4', R=130.0, j=0.04, base=0.50, end=160.0, tok=0)
asyncio.run(p.manage(m, 131.0))
check('per-match cap counts open positions', m.order is not None and m.order['size'] * m.order['price'] <= 10.0 + 1e-6)

# E rule: fair - bid < E -> no bid  (tiny jump that still passes minj is handled by window; force E large)
p, g = pilot(); m = mk_market(); g.markets['match'] = m; P.CFG['E'] = 0.10
set_book(m, 0.49, 0.51, 100.0); m.window = dict(eid='e5', R=130.0, j=0.04, base=0.50, end=160.0, tok=0)
asyncio.run(p.manage(m, 131.0)); P.CFG['E'] = 0.01
check('E rule blocks bid when fair - bid < E', m.order is None)

# paper fill queue logic
p, g = pilot(); m = mk_market(); g.markets['match'] = m
o = dict(id='x', eid='e', tok=0, token='T0', price=0.48, size=100.0, filled=0.0, paper_naive=0.0, paper_queue=0.0,
         ahead0=150.0, ahead=150.0, placed=100.0)
trades = {'data': [dict(timestamp=101, token_id='T0', price=0.48, size=120.0, side='SELL', transaction_hash='a', proxy_wallet='w'),
                   dict(timestamp=102, token_id='T1', price=0.52, size=80.0, side='BUY', transaction_hash='b', proxy_wallet='w'),
                   dict(timestamp=103, token_id='T0', price=0.49, size=500.0, side='SELL', transaction_hash='c', proxy_wallet='w')]}
async def fake_aget(url, body=None): return trades
P.aget = fake_aget
asyncio.run(P.Pilot.paper_fills(p, m, o, 104.0))
check('paper naive fill = 100 (first two prints, capped at size)', abs(o['paper_naive'] - 100.0) < 1e-9)
check('paper queue fill = 50 (150 ahead eaten first)', abs(o['paper_queue'] - 50.0) < 1e-9)
check('print above our bid does not fill', all(not (k == 'paper_fill' and kw['print_px'] > 0.48) for k, kw in p.log_rows))


# $50 pilot sizing: 5-share orders, $5 per match, $40 total
p, g = pilot(); m = mk_market(); g.markets['match'] = m
P.CFG.update(SHARE_CAP=5, MATCH_CAP_USD=5.0, LOSS_LIMIT_USD=40.0)
set_book(m, 0.49, 0.51, 100.0); m.window = dict(eid='e6', R=130.0, j=0.04, base=0.50, end=160.0, tok=0)
asyncio.run(p.manage(m, 131.0))
check('$50 pilot: order is 5 shares ($2.40)', m.order is not None and m.order['size'] == 5)
p.st['positions']['0xold'] = dict(gid=1, kind='map1', tokens=['a', 'b'], tok={'0': [5.0, 2.7]}); m.order = None
asyncio.run(p.manage(m, 132.0))
check('$50 pilot: per-match $5 cap blocks a second $2.40 order', m.order is None)
P.CFG.update(SHARE_CAP=1000, MATCH_CAP_USD=250.0, LOSS_LIMIT_USD=500.0)

# replay a logged match through on_score: no crash, events only on within-map rounds
fn = os.path.join(HERE, '..', '..', 'rn1', 'scores', 'cs2', 'server-2026-11', 'cs2_changes.jsonl.gz')
if os.path.exists(fn):
    rows = [json.loads(l) for l in gzip.open(fn, 'rt')]
    by = {}
    for r in rows:
        if '|Bo' in (r.get('score') or ''): by.setdefault(r['gameId'], []).append(r)
    gid = max(by, key=lambda k: len({x['score'].split('|')[0] for x in by[k]}))
    p, g = pilot(); p.games = {}; gg = P.Game(gid, {'title': 'replay', 'slug': 'r', 'markets': []}); p.games[gid] = gg
    for r in by[gid]:
        d = dict(gameId=gid, homeTeam=r['home'], awayTeam=r['away'], score=r['score'], period=r['period'], status=r['status'], live=r['live'])
        p.on_score(d, r['recv_ms'] / 1000)
    ev = [kw for k, kw in p.log_rows if k == 'event']; sk = [kw for k, kw in p.log_rows if k == 'event_skip']
    check(f'replay game {gid}: round events found ({len(ev)}) and map ends skipped ({len(sk)})', len(ev) > 20 and all(e['new']['ma'] + e['new']['mb'] == e['prev']['ma'] + e['prev']['mb'] for e in ev))

n = sum(ok for _, ok in R); print(f'{n} of {len(R)} tests pass')
sys.exit(0 if n == len(R) else 1)
