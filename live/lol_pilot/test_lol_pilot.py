"""Offline tests for the LoL pilot (PROTOCOL rule 1): hand-checked cases plus a replay of GEN-LYON game 1
(4-5 Nov 2026: Polymarket sports WS messages from cito-timing/lol_race1, mids from the market's public trades).
Run: python3 test_lol_pilot.py [race.jsonl.gz trades.json]  -> must end with 'N of N tests pass'."""
import asyncio, gzip, json, math, os, sys, tempfile, types
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import lol_pilot as L
B = L.BASE

R = []
def check(name, cond):
    R.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name)

P = L.MD.parse
# ---- event classification
check('kill for home', L.kill_event(P('3-2|1-0|Bo5'), P('4-2|1-0|Bo5')) == ('kill', 2, 1))
check('two kills for away in one tick', L.kill_event(P('3-2|1-0|Bo5'), P('3-4|1-0|Bo5')) == ('kill', 2, -2))
check('2-for-1 nets +1', L.kill_event(P('3-2|0-0|Bo5'), P('5-3|0-0|Bo5')) == ('kill', 1, 1))
check('trade is not traded', L.kill_event(P('3-2|0-0|Bo5'), P('4-3|0-0|Bo5'))[0] == 'trade')
check('game end', L.kill_event(P('20-9|0-0|Bo5'), P('0-0|1-0|Bo5'))[0] == 'game_end')
check('reset', L.kill_event(P('20-9|0-0|Bo5'), P('0-0|0-0|Bo5'))[0] == 'reset')
check('kills going down ignored', L.kill_event(P('5-2|0-0|Bo5'), P('4-2|0-0|Bo5'))[0] is None)
check('glitch jump ignored', L.kill_event(P('0-0|0-0|Bo5'), P('15-0|0-0|Bo5'))[0] is None)
# ---- jump: sig(logit(0.5) + 0.284) - 0.5 = 0.07053 (hand: e^0.284 = 1.3284, 1.3284/2.3284 = 0.57053)
check('jump 1 kill at 50c = +7.05c', abs(L.game_jump(0.5, 1) - 0.07053) < 1e-4)
check('jump symmetric', abs(L.game_jump(0.5, -1) + 0.07053) < 1e-4)
check('jump small at 95c', 0 < L.game_jump(0.95, 1) < 0.02)


# ---- pilot on a fake game market
def mk_game(p, o0_home=True):
    g = B.Game(7, {'title': 'LoL: Home vs Away (BO5) - Worlds Playoffs', 'slug': 's', 'markets': [
        {'groupItemTitle': 'Game 1 Winner', 'conditionId': '0xg1', 'clobTokenIds': json.dumps(['T0', 'T1']),
         'outcomes': json.dumps(['Home Team', 'Away Team'] if o0_home else ['Away Team', 'Home Team']),
         'orderPriceMinTickSize': '0.01', 'orderMinSize': 5},
        {'groupItemTitle': 'Match Winner', 'conditionId': '0xmw', 'clobTokenIds': json.dumps(['M0', 'M1']),
         'outcomes': json.dumps(['Home Team', 'Away Team']), 'orderPriceMinTickSize': '0.01', 'orderMinSize': 5}]})
    p.games[7] = g; return g

def new_pilot():
    a = types.SimpleNamespace(mode='dry', out=tempfile.mkdtemp()); p = L.Pilot(a); p.rows = []; orig = p.log
    def log(typ, **kw): p.rows.append((typ, kw)); orig(typ, **kw)
    p.log = log
    async def noop(g): return None
    p.refresh_markets = noop
    return p

def ws(score, t): return {'gameId': 7, 'leagueAbbreviation': 'lol', 'homeTeam': 'Home Team', 'awayTeam': 'Away Team', 'score': score, 'live': True}

async def scenario(o0_home=True, mid=0.50, mid_now=None, dk_score='1-0|0-0|Bo5'):
    p = new_pilot(); g = mk_game(p, o0_home)
    p.on_score(ws('0-0|0-0|Bo5', 0), 900.0)
    m = g.markets['game1']
    for t in range(900, 1001): m.mids.append((float(t), mid))
    m.book = {0: (mid - 0.01, mid + 0.01, {}), 1: (1 - mid - 0.01, 1 - mid + 0.01, {})}
    p.on_score(ws(dk_score, 0), 1000.0)
    if mid_now is not None:
        m.mids.append((1001.0, mid_now)); mn = mid_now
        m.book = {0: (mn - 0.01, mn + 0.01, {}), 1: (1 - mn - 0.01, 1 - mn + 0.01, {})}
    B.CFG['TRADES_POLL'] = 1e12
    await p.manage(m, 1001.0)
    return p, g, m

async def main_tests():
    p, g, m = await scenario()
    check('only Game k markets attached', set(g.markets) == {'game1'})
    w = [kw for t, kw in p.rows if t == 'window']
    check('home kill opens window on home token (o0=home)', len(w) == 1 and w[0]['tok'] == 0 and abs(w[0]['j'] - 0.0705) < 1e-3)
    o = m.order
    check('bid = 0.50 x 0.975 = 0.4875 rounded up = 0.49', o is not None and abs(o['price'] - 0.49) < 1e-9)
    check('bid below best ask', o['price'] < m.book[0][1])
    check('size = 5 shares (cap)', o['size'] == 5)
    p, g, m = await scenario(o0_home=False)
    w = [kw for t, kw in p.rows if t == 'window']
    check('home kill buys token 1 when outcome 0 is away', w and w[0]['tok'] == 1 and m.order and abs(m.order['price'] - 0.49) < 1e-9)
    p, g, m = await scenario(mid_now=0.58)
    check('no bid when price already moved by the jump', m.order is None and not [1 for t, _ in p.rows if t == 'order_place'])
    p, g, m = await scenario(mid=0.98)
    check('no window at anchor 98c', not [1 for t, _ in p.rows if t == 'window'])
    p, g, m = await scenario(dk_score='1-1|0-0|Bo5')
    check('no window on a trade', not [1 for t, _ in p.rows if t == 'window'] and m.order is None)
    # E rule: fair - bid >= 1c always holds at d=2.5% when jump >= 1c and mid unmoved; check a moved-but-not-fully case
    p, g, m = await scenario(mid_now=0.55)
    o = m.order
    check('partially moved: bid = 0.55 x 0.975 = 0.536 up = 0.54, fair 0.5705 - 0.54 >= E', o and abs(o['price'] - 0.54) < 1e-9)
    # caps: $5 per match
    p, g, m = await scenario()
    p.st['positions']['0xg1'] = dict(gid=7, kind='game1', tokens=['T0', 'T1'], tok={'0': [9.0, 4.5]})
    check('match cap leaves no room for another 5-share order', p.room(7) < 5 * 0.49)


def replay(race, trades):
    """GEN-LYON game 1: WS lol messages + public trades as the mid. Checks the bot opens windows on real kills and never
    quotes at/above mid x 0.975. Prints what it would have done (paper; fills need the live book)."""
    tr = json.load(open(trades)); cond = tr[0]['condition_id']
    tok = {}; outc = {}
    for t in tr: tok[t['outcome_index']] = t['token_id']; outc[t['outcome_index']] = t['outcome']
    msgs = []
    for line in gzip.open(race, 'rt'):
        d = json.loads(line)
        if d.get('src') != 'pm': continue
        m = json.loads(d['m'])
        if m.get('leagueAbbreviation') == 'lol' and 'Gen' in (m.get('homeTeam') or '') + (m.get('awayTeam') or ''):
            msgs.append((d['rt'], m))
    if not msgs: return None
    gid = msgs[0][1]['gameId']
    p = new_pilot()
    g = B.Game(gid, {'title': 'LoL: Gen.G vs LYON (BO5) - Worlds Playoffs', 'slug': 's', 'markets': [
        {'groupItemTitle': 'Game 1 Winner', 'conditionId': cond, 'clobTokenIds': json.dumps([tok[0], tok[1]]),
         'outcomes': json.dumps([outc[0], outc[1]]), 'orderPriceMinTickSize': '0.01', 'orderMinSize': 5}]})
    p.games[gid] = g
    px = sorted((t['timestamp'], t['price'] if t['outcome_index'] == 0 else 1 - t['price']) for t in tr)
    B.CFG['TRADES_POLL'] = 1e12
    loop = asyncio.new_event_loop(); i = 0; j = 0
    t0, t1 = int(max(px[0][0], msgs[0][0])), int(min(px[-1][0], msgs[-1][0]))
    for T in range(t0, t1):
        while j < len(px) and px[j][0] <= T:
            mk = g.markets.get('game1')
            if mk is not None: mk.mids.append((float(px[j][0]), px[j][1]))
            j += 1
        while i < len(msgs) and msgs[i][0] <= T:
            p.on_score(msgs[i][1], msgs[i][0]); i += 1
        mk = g.markets.get('game1')
        if mk is not None and mk.mids:
            md = mk.mid(); mk.book = {0: (md - 0.005, md + 0.005, {}), 1: (1 - md - 0.005, 1 - md + 0.005, {})}
            loop.run_until_complete(p.manage(mk, float(T)))
    return p

loop = asyncio.new_event_loop(); loop.run_until_complete(main_tests())
race = sys.argv[1] if len(sys.argv) > 2 else '/mnt/project-files/cito-timing/lol_race1_2026-11-04.jsonl.gz'
trades = sys.argv[2] if len(sys.argv) > 2 else '/mnt/project-files/cito-timing/lol_trades_g1.json'
if os.path.exists(race) and os.path.exists(trades):
    p = replay(race, trades)
    ev = [kw for t, kw in p.rows if t == 'event']; win = [kw for t, kw in p.rows if t == 'window']
    pl = [kw for t, kw in p.rows if t == 'order_place']; sk = [kw for t, kw in p.rows if t == 'window_skip']
    import collections
    print(f"replay GEN-LYON g1: kill events {len(ev)}, windows {len(win)}, skips {dict(collections.Counter(k['why'] for k in sk))}, "
          f"bids placed {len(pl)}, cancels {dict(collections.Counter(kw['why'] for t, kw in p.rows if t == 'order_cancel'))}")
    for kw in pl[:8]:
        print(f"   bid {kw['outcome']} {kw['price']:.2f} x {kw['size']:.0f}, mid0 {kw['mid0']:.3f}, {kw['lag_since_event']:.0f} s after WS")
    check('replay: kill events seen', len(ev) >= 5)
    check('replay: every bid >= token mid x 0.975 (never lower), < mid + under best ask',
          all(kw['price'] >= (kw['mid0'] if kw['tok'] == 0 else 1 - kw['mid0']) * 0.975 - 1e-9 and kw['price'] < kw['best_ask'] for kw in pl))
else:
    print('replay files not found, replay skipped')
n = sum(ok for _, ok in R); print(f"{n} of {len(R)} tests pass")
