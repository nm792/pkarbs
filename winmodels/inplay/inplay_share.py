"""In-play share of Polymarket volume per league, from data-api v2 trades (4 Nov 2026).

Sample: per league, N events stratified by volume (every k-th event by volume rank). Per event, the top M
markets by volume (always incl. the moneyline). For each market, ALL v2 trades are pulled (cached in
raw/inplay/trades/<cond>.json.gz) and split by gameStartTime:
  pre      = before gameStartTime
  inplay   = gameStartTime .. closedTime
  inplay_mid = in-play with price in [0.05, 0.95] (where a bid at market - 2.5% can matter)
Notional = size x price (taker trade notional; gamma 'volume' is ~2x this, checked on one NFL market).
Output: inplay/inplay_share_2026-10-20_11-04.json (per-league share, volume-weighted over sampled markets).
"""
import sys, os, json, gzip, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
LEAGUES = sys.argv[1].split(',') if len(sys.argv) > 1 else \
    'nba,nfl,atp,wta,ucl,epl,cfb,lal,sea,nhl,bun,mls,mlb,uel,fl1,ufc,mex,crint,val,afcl,itf,wnba,spl'.split(',')
N = int(os.environ.get('NEV', 10)); M = int(os.environ.get('NMK', 3))
E = json.load(gzip.open(f'{RAW}/inplay/events_2026-10-20_11-04.json.gz'))
TD = f'{RAW}/inplay/trades'; os.makedirs(TD, exist_ok=True)

def ts(s):
    if not s: return None
    s = s.replace(' ', 'T').replace('+00', '+00:00') if '+00' in s and '+00:' not in s else s.replace(' ', 'T')
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

def trades(cond):
    fn = f'{TD}/{cond}.json.gz'
    if os.path.exists(fn): return json.load(gzip.open(fn))
    p = {'condition': cond, 'limit': 500}; out = []; cur = None
    for _ in range(1500):
        if cur: p['cursor'] = cur
        c, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if c != 200 or not d: break
        out += [(z['timestamp'], z['price'], z['size'], z['outcome_index'], z['side']) for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(out, gzip.open(fn, 'wt'))
    return out

def sample(lg):
    ev = sorted([e for e in E if e['league'] == lg and e['volume'] > 0 and any(m.get('gameStartTime') for m in e['markets'])],
                key=lambda e: -e['volume'])
    if not ev: return []
    k = max(1, -(-len(ev) // N))
    out = []
    for i in range(0, len(ev), k):          # stratum = k consecutive events by volume rank; sample its largest
        e = dict(ev[i]); e['stratum_vol'] = sum(x['volume'] for x in ev[i:i + k]); e['stratum_n'] = len(ev[i:i + k]); out.append(e)
    return out

def market_split(m):
    t0 = ts(m['gameStartTime']); t1 = ts(m.get('closedTime')) or (t0 + 6 * 3600)
    tr = trades(m['conditionId'])
    r = collections.Counter()
    for t, p, s, oi, sd in tr:
        x = p * s
        if t < t0: r['pre'] += x
        elif t <= t1:
            r['inplay'] += x
            if 0.05 <= p <= 0.95: r['inplay_mid'] += x
        else: r['post'] += x
    r['n'] = len(tr); r['last_trade_age_h'] = 0
    if tr: r['span_h'] = (max(t for t, *_ in tr) - min(t for t, *_ in tr)) / 3600
    return dict(r)

jobs = []
for lg in LEAGUES:
    for e in sample(lg):
        mk = sorted([m for m in e['markets'] if m.get('gameStartTime') and m.get('conditionId')], key=lambda m: -float(m.get('volumeNum') or 0))
        ml = [m for m in mk if m.get('sportsMarketType') == 'moneyline'][:1]
        top = (ml + [m for m in mk if m not in ml])[:M]
        evm = sum(float(m.get('volumeNum') or 0) for m in e['markets'])
        for m in top: jobs.append((lg, e['slug'], e['volume'], (e['stratum_vol'], e['stratum_n']), m))
print(len(jobs), 'markets', flush=True)
with ThreadPoolExecutor(10) as ex: res = list(ex.map(lambda j: market_split(j[4]), jobs))

rows = collections.defaultdict(lambda: collections.Counter()); per_ev = collections.defaultdict(dict)
for (lg, slug, ev_vol, strat, m), r in zip(jobs, res):
    typ = 'ml' if m.get('sportsMarketType') == 'moneyline' else 'other'
    R = rows[lg]
    for k in ('pre', 'inplay', 'inplay_mid', 'post'): R[k] += r.get(k, 0); R[f'{typ}_{k}'] += r.get(k, 0)
    R['gamma_sampled'] += float(m.get('volumeNum') or 0)
    per_ev[lg].setdefault(slug, dict(ev_vol=ev_vol, stratum_vol=strat[0], stratum_n=strat[1], mk=[]))['mk'].append(dict(q=m['question'], typ=m.get('sportsMarketType'), gamma=float(m.get('volumeNum') or 0), **r))
LV = collections.Counter(); LN = collections.Counter()
for e in E: LV[e['league']] += e['volume']; LN[e['league']] += 1
out = {}
for lg, R in rows.items():
    # stratified estimate: each sampled event's in-play share (over its sampled markets) x its stratum's gamma volume
    est = collections.Counter()
    for slug, v in per_ev[lg].items():
        t = sum(m.get('pre', 0) + m.get('inplay', 0) + m.get('post', 0) for m in v['mk'])
        if t <= 0: continue
        for k in ('inplay', 'inplay_mid'): est[k] += v['stratum_vol'] * sum(m.get(k, 0) for m in v['mk']) / t
        est['vol'] += v['stratum_vol']
    tot = R['pre'] + R['inplay'] + R['post']
    mlt = R['ml_pre'] + R['ml_inplay'] + R['ml_post']
    out[lg] = dict(events=len(per_ev[lg]), markets=sum(len(v['mk']) for v in per_ev[lg].values()), trade_notional=round(tot),
                   gamma_sampled=round(R['gamma_sampled']), notional_over_gamma=round(tot / max(1, R['gamma_sampled']), 3),
                   inplay_share=round(R['inplay'] / max(1, tot), 3), inplay_mid_share=round(R['inplay_mid'] / max(1, tot), 3),
                   ml_inplay_share=round(R['ml_inplay'] / max(1, mlt), 3), ml_inplay_mid_share=round(R['ml_inplay_mid'] / max(1, mlt), 3),
                   league_gamma_vol_15d=round(LV[lg]), league_events_15d=LN[lg],
                   strat_inplay_share=round(est['inplay'] / max(1, est['vol']), 3), strat_inplay_mid_share=round(est['inplay_mid'] / max(1, est['vol']), 3),
                   inplay_gamma_per_day=round(est['inplay'] / 15), inplay_mid_gamma_per_day=round(est['inplay_mid'] / 15))
fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inplay_share_" + os.environ.get("TAG", "_".join(LEAGUES) if len(LEAGUES) < 4 else "2026-10-20_11-04") + ".json")
json.dump(dict(summary=out, events=per_ev), open(fn, 'w'), indent=1)
for lg, o in sorted(out.items(), key=lambda x: -x[1]['inplay_gamma_per_day']): print(lg, o)
