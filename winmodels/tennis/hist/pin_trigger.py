"""Tennis backtest with Pinnacle (or bet365) price steps as the TRIGGER (5 Nov 2026).

Nick: "why do we need 5-10 seconds and not 2?"  Test it directly instead of reading it off the delay curve.

  * Book data: OddsPapi /v4/historical-odds (createdAt = OddsPapi ingest time, which already includes
    Pinnacle->OddsPapi delay). Raw: rn1/scores/oddspapi/2026-11-04b.
  * Trigger: a book update where the no-vig prob of player 0 moves >= STEP (default 1.5pp) from the previous
    update. Side = direction of the book move. NOT oracle: the book decides the side.
  * Our bid: from trigger + LAT s (time to receive the update + place the order), bid PM mid x 0.975 on that side
    for W s, only while the PM mid has moved < 50% of the book step (PM hasn't caught up) and mid in [0.05, 0.95].
  * Fills: TRADE-BASED ESTIMATE (no tennis order books recorded): a print selling our side at most 1% below our
    bid fills us, min(size, 500). Queue ignored = optimistic. Hold to result. Same fill code as hist_delay.py.
  * Also reports where the book step sits relative to the PM price onset (hist_delay.events definition).
Usage: python3 pin_trigger.py OP_DIR    (writes out_pin_trigger.json)
"""
import sys, os, json, gzip, glob, re, bisect, datetime as dt, statistics as stx
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import common as C
from common import RAW
import hist_delay as H

OP = sys.argv[1]
STEP = float(os.environ.get('STEP', 0.015))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def toks(s): return [w for w in re.sub(r'[^a-z ]', ' ', s.lower().replace(',', ' ')).split() if len(w) > 2]
def same(a, b):
    A, B = set(toks(a)), set(toks(b))
    return bool(A & B) or any(x[:4] == y[:4] for x in A for y in B if len(x) > 4 and len(y) > 4)

G = [(e, m) for e in json.load(gzip.open(f'{RAW}/tennis/point/gamma_tennis_2026-11-02_on.json.gz'))
     if re.search(r'2026-11-0[45]$', e['slug']) for m in e['markets'] if m.get('sportsMarketType') == 'moneyline']

def book_series(b, flip):
    if '121' not in b['markets']: return []
    ev = sorted((ts(x['createdAt']), oid, x['price'], x['active']) for oid, ov in b['markets']['121']['outcomes'].items() for x in ov['players'].get('0', []))
    cur = {}; out = []
    for t, oid, pr, act in ev:
        if not act: continue
        cur[oid] = pr
        if cur.get('121') and cur.get('122'):
            q = (1 / cur['121']) / (1 / cur['121'] + 1 / cur['122']); out.append((t, 1 - q if flip else q))
    return out

games = []
for f in glob.glob(f'{OP}/hist/*'):
    d = json.load(gzip.open(f)); fx = d['fixture']
    if fx['sportId'] != 12 or '/' in fx['participant1Name'] or '(srl)' in fx['participant1Name'].lower(): continue
    hit = None
    for e, m in G:
        o = json.loads(m['outcomes'])
        if same(fx['participant1Name'], o[0]) and same(fx['participant2Name'], o[1]): hit = (e, m, False); break
        if same(fx['participant1Name'], o[1]) and same(fx['participant2Name'], o[0]): hit = (e, m, True); break
    if not hit: continue
    e, m, flip = hit
    op = json.loads(m.get('outcomePrices') or '[]')
    if sorted(op) != ['0', '1']: continue
    t0 = ts(e.get('startTime') or e.get('startDate'))
    tr = C.pull_trades(m['conditionId'], t0 - 3600, t0 + 8 * 3600, 'tennis/pin/trades')
    pr = C.prints(tr); pr = [p for p in pr if p[0] >= t0 - 600]
    if len(pr) < 30: continue
    fs = m.get('feeSchedule') or {}; reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
    g = dict(slug=e['slug'], pr=pr, M=C.Mid(pr), win0=op[0] == '1', reb=reb, t0=t0, t1=pr[-1][0])
    g['books'] = {bk: book_series(d['hist']['bookmakers'][bk], flip) for bk in ('pinnacle', 'bet365') if bk in d['hist'].get('bookmakers', {})}
    games.append(g)
print('tennis matches with PM trades + book history', len(games), flush=True)

def triggers(bs):
    E = []
    for (t1, q1), (t2, q2) in zip(bs, bs[1:]):
        if abs(q2 - q1) >= STEP and 0.03 < q1 < 0.97: E.append(dict(on=t2, pj=q2 - q1))
    return E

def m0_for(g, E):
    for e in E: e['m0'] = g['M'].at(e['on'] - 2)
    return [e for e in E if e['m0'] is not None and 0.03 < e['m0'] < 0.97]

out = dict(step=STEP, matches=len(games), books={})
for bk in ('pinnacle', 'bet365'):
    gs = [g for g in games if len(g['books'].get(bk, [])) > 20]
    # where do book steps sit vs PM price onsets?
    rel = []
    for g in gs:
        pe = H.events(g); pon = [x['on'] for x in pe]
        for e in triggers(g['books'][bk]):
            i = bisect.bisect_left(pon, e['on'] - 30)
            near = [(abs(pon[j] - e['on']), pon[j], pe[j]['pj']) for j in range(i, min(len(pon), i + 6)) if abs(pon[j] - e['on']) <= 30 and pe[j]['pj'] * e['pj'] > 0]
            if near: rel.append(min(near)[1] - e['on'])     # >0: PM onset AFTER book step (book first)
    res = dict(matches=len(gs), steps=sum(len(triggers(g['books'][bk])) for g in gs),
               steps_with_pm_move_within_30s=len(rel),
               pm_onset_minus_book_s=dict(median=stx.median(rel) if rel else None,
                                          quartiles=[round(x, 1) for x in stx.quantiles(rel, n=4)] if len(rel) > 3 else None,
                                          share_book_first=round(sum(r > 0 for r in rel) / len(rel), 2) if rel else None), curve=[])
    print(bk, {k: v for k, v in res.items() if k != 'curve'}, flush=True)
    for g in gs: g['E'] = m0_for(g, triggers(g['books'][bk]))
    days = (max(g['t0'] for g in gs) - min(g['t0'] for g in gs)) / 86400 + 1
    for W in [int(x) for x in os.environ.get('WS', '10,30').split(',')]:
        for lat in [float(x) for x in os.environ.get('LATS', '0.5,1.5,3,5').split(',')]:
            P = [H.run(g, lat, W) for g in gs]; s = C.summarize(P)
            s = {k: ([float(x) for x in v] if isinstance(v, list) else v) for k, v in s.items()}
            n = len(gs); r = dict(W=W, latency_s=lat, matches_filled=sum(1 for p in P if p[0] > 0),
                                  filled_per_match=round(s['usd'] / n, 1), result_per_match=round(s['net_result_usd'] / n, 2),
                                  result_per_match_ci=[round(x / n, 2) for x in s['ci_result_usd']], m1_pct=s['net_1min_pct'],
                                  result_pct=s['net_result_pct'], ex_top5_result_pct=s['ex_top5_result_pct'])
            res['curve'].append(r)
            print(f"  {bk} W{W} lat {lat}s: {r['matches_filled']}/{n} filled, ${r['filled_per_match']}/match filled, 1min {r['m1_pct']}%, result {r['result_pct']}% = ${r['result_per_match']}/match {r['result_per_match_ci']}, ex-top5 {r['ex_top5_result_pct']}%", flush=True)
    out['books'][bk] = res
json.dump(out, open(f"{HERE}/out_pin_trigger{os.environ.get('SFX', '')}.json", 'w'), indent=1)
