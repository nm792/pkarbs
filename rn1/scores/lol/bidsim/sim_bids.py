"""Backtest resting bids (rn1-style maker) on the 6 Worlds 2026 Game-1 markets we hold.

Data: ../lag-study-worlds-2026-10/out/<match>/{frames,trades}.json.gz
  trades = Polymarket data-api /trades (taker prints, 1 s timestamps).
Rules (all simulated, not traded):
  * In-play only (first in_game frame to 'finished'), mid in [0.05, 0.95].
  * We rest a bid on BOTH tokens. Reference price = trade-derived mid seen
    QDELAY s before the print (avg of last bid-side and ask-side print).
    Variant 'mkt': bid = ref*(1-d). Variant 'fair': ref replaced by the
    LoL event model fair (evrules, leave-one-game-out beta) for 60 s after
    each livestats event, detected DET_LAG s after the frame time.
  * Fill: a sell-direction print (SELL token0 or BUY token1) at price <= our
    token0 bid fills us at OUR bid, min(print size, Q) shares; same for token1.
    Queue position ignored (we are assumed first at our price): optimistic.
  * Optional cancel: no bids from event+CANCEL_LAG to event+30 s.
  * Hold to result. Rebate (ESTIMATE) = 0.15 * 0.05 * p(1-p) per share.
Components per fill (per share): entry = ref_true - bid; m1 = mid(t+60) - ref_true;
rest = outcome - mid(t+60); sum = outcome - bid.  ref_true uses prints before t, no delay.
"""
import json, gzip, os, sys, math, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'lag-study-worlds-2026-10')
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from evrules import fit_lol as F, fit_lol_events as FE
F.D = D
Q = 100.0; QDELAY = 1; DET_LAG = 2; REB = 0.15 * 0.05
KEYS = ['kills', 'towers', 'dragons', 'barons', 'inhibs', 'gold']

def load(x):
    fr = json.load(gzip.open(f"{D}/out/{x['match_id']}/frames.json.gz"))
    tr = json.load(gzip.open(f"{D}/out/{x['match_id']}/trades.json.gz"))
    o0 = x['outcomes'][0]
    pr = []
    for k, t in enumerate(tr):
        is0 = t['outcome'] == o0
        ph = t['price'] if is0 else 1 - t['price']
        sell0 = (is0 and t['side'] == 'SELL') or ((not is0) and t['side'] == 'BUY')
        pr.append((t['timestamp'], -k, ph, sell0, t['size']))   # -k: data-api is newest first
    pr.sort()
    g = F.load_game(x['match_id'], o0)
    fin = [f for f in fr if f['gameState'] == 'finished']
    ing = [f for f in fr if f['gameState'] == 'in_game']
    t0, t1 = F.ts(ing[0]['rfc460Timestamp']), F.ts(fin[0]['rfc460Timestamp'])
    win0 = g['blue_won'] == g['blue_is_outcome0']
    # event clusters (state changes, merged within 10 s)
    evs = []; prev = None; start = None; sb = None; last = None
    for f in ing:
        s = F.state(f); T = F.ts(f['rfc460Timestamp'])
        if prev is not None and any(s[c] != prev[c] for c in KEYS[:5]):
            if start is None: start, sb = T, prev
            last = T
        if start is not None and T - last > 10:
            evs.append((start, last, sb, s)); start = None
        prev = s
    fst = [(F.ts(f['rfc460Timestamp']), F.state(f)) for f in ing]
    return dict(pr=pr, t0=t0, t1=t1, win0=win0, evs=evs, blue0=g['blue_is_outcome0'], fst=fst)

class Mid:
    def __init__(s, pr):
        s.t = [p[0] for p in pr]; s.pr = pr
        lb = None; la = None; s.m = []
        for p in pr:
            if p[3]: lb = p
            else: la = p
            if lb and la and abs(lb[0] - la[0]) <= 120 and lb[2] <= la[2] + 0.005 and la[2] - lb[2] < 0.10:
                s.m.append((lb[2] + la[2]) / 2)
            else:
                s.m.append(p[2])
    def at(s, T):  # mid using prints with timestamp < T
        i = bisect.bisect_left(s.t, T) - 1
        return s.m[i] if i >= 0 else None

def beta_logo():
    m = json.load(open(f'{D}/matched.json'))
    xs = [x for x in m if os.path.exists(f"{D}/out/{x['match_id']}/frames.json.gz")]
    ev = [FE.game_events(x, F.load_game(x['match_id'], x['outcomes'][0])) for x in xs]
    out = {}
    for k, x in enumerate(xs):
        es = [e for j, g in enumerate(ev) if j != k for e in g]
        X = np.array([e['dx'] for e in es]); y = np.array([F.logit(e['post']) - F.logit(e['pre']) for e in es])
        out[x['match_id']] = dict(zip(KEYS, FE.signed_ridge(X, y)))
    return xs, out

def fair_fn(G, M, beta):
    """returns f(T) -> model fair of token0 or None (outside event windows)."""
    win = []
    for (st, en, sb, sa) in G['evs']:
        anc = M.at(st - 1)
        if anc is None or not (0.02 < anc < 0.98): continue
        a = anc if G['blue0'] else 1 - anc
        z = math.log(a / (1 - a)) + sum(beta[k] * (sa[k] - sb[k]) / (1000.0 if k == 'gold' else 1) for k in KEYS)
        fb = 1 / (1 + math.exp(-z)); f0 = fb if G['blue0'] else 1 - fb
        win.append((st + DET_LAG, st + 60, f0))
    def f(T):
        for a, b, v in win:
            if a <= T < b: return v
        return None
    return f

def fair_fn2(G, M, beta, max_win=10, caught=0.7, k=1.0):
    """Corrected use of the jump model (v2, 3 Nov). fair = pre-event mid + model jump,
    using only the state seen DET_LAG s earlier (no lookahead inside a cluster),
    and only until the market has made `caught` of the predicted move or
    max_win s after the event. Outside those windows fair = None (use mid)."""
    ft = [a for a, _ in G['fst']]
    def st_at(T):
        i = bisect.bisect_right(ft, T) - 1
        return G['fst'][max(i, 0)][1]
    W = []
    for (st, en, sb, sa) in G['evs']:
        anc = M.at(st - 1)
        if anc is None or not (0.02 < anc < 0.98): continue
        W.append((st, sb, anc))
    def f(T):
        for st, sb, anc in W:
            if st + DET_LAG <= T < st + max_win:
                s = st_at(T - DET_LAG)
                a = anc if G['blue0'] else 1 - anc
                z = math.log(a / (1 - a)) + sum(beta[k] * (s[k] - sb[k]) / (1000.0 if k == 'gold' else 1) for k in KEYS)
                fb = 1 / (1 + math.exp(-z)); f0 = fb if G['blue0'] else 1 - fb
                m = M.at(T - QDELAY)
                pred = f0 - anc
                if abs(pred) < 0.01 or m is None: return None
                if (m - anc) / pred >= caught: return None   # market has caught up
                return (anc + k * pred, 1 if pred > 0 else -1)   # bid part of the jump on the side it favours; other side pulled
        return None
    return f

def sim(G, M, d, mode='mkt', cancel=None, strict=False, fairf=None, pull_hurt=False):
    fills = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        ref = M.at(T - QDELAY)
        if ref is None or not (0.05 <= ref <= 0.95): continue
        r1 = 1 - ref; inwin = False
        if mode in ('fair', 'min'):
            fv = fairf(T)
            if isinstance(fv, tuple) and mode == 'min':
                # RULE: never above market. Model may only lower (or pull) bids.
                inwin = True
                fk = min(max(fv[0], 0.01), 0.99)
                if pull_hurt:
                    ref, r1 = (ref, None) if fv[1] > 0 else (None, r1)
                else:
                    ref, r1 = min(ref, fk), min(r1, 1 - fk)
                fv = None
            elif isinstance(fv, tuple):
                inwin = True
                fk, sg = fv; fk = min(max(fk, 0.01), 0.99)
                ref, r1 = (fk, None) if sg > 0 else (None, 1 - fk)
                fv = None
            if fv is not None:
                inwin = True
                fv = min(max(fv, 0.01), 0.99)
                if mode == 'fair': ref, r1 = fv, 1 - fv
                else: ref, r1 = min(ref, fv), min(1 - ref, 1 - fv)   # model may only LOWER our bids
        if cancel is not None and not inwin and any(st + cancel <= T < st + 30 for (st, _, _, _) in G['evs']): continue
        mk = M.at(T - QDELAY)
        if sell0:
            if ref is None: continue
            b = ref * (1 - d)
            if mode in ('mkt', 'min'): assert b <= mk * (1 - d) + 1e-9; hit = ph < b - 1e-9 if strict else ph <= b + 1e-9
            if hit: fills.append((T, 0, b, min(sz, Q), inwin))
        else:
            if r1 is None: continue
            b = r1 * (1 - d); p1 = 1 - ph
            if mode in ('mkt', 'min'): assert b <= (1 - mk) * (1 - d) + 1e-9
            hit = p1 < b - 1e-9 if strict else p1 <= b + 1e-9
            if hit: fills.append((T, 1, b, min(sz, Q), inwin))
    rows = []
    for (T, tok, b, q, inwin) in fills:
        rt = M.at(T); m60 = M.at(T + 60); m300 = M.at(T + 300)
        if tok == 1: rt, m60, m300 = 1 - rt, 1 - m60, 1 - m300
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append(dict(win=inwin, q=q, usd=q * b, entry=q * (rt - b), m1=q * (m60 - rt), m5=q * (m300 - m60), rest=q * (out - m300),
                         pnl=q * (out - b), reb=q * REB * b * (1 - b)))
    return rows

def agg(rows):
    s = {k: sum(r[k] for r in rows) for k in ['usd', 'entry', 'm1', 'm5', 'rest', 'pnl', 'reb']}
    s['n'] = len(rows); s['net'] = s['pnl'] + s['reb']
    return s

def main():
    xs, betas = beta_logo()
    games = {}
    for x in xs:
        G = load(x); M = Mid(G['pr']); games[x['match_id']] = (G, M, fair_fn(G, M, betas[x['match_id']]), '-'.join(x['teams']))
    res = []
    configs = []
    for d in [0.0, 0.01, 0.02, 0.025, 0.03, 0.04, 0.05, 0.08]:
        configs.append(('mkt', None, False, d)); configs.append(('mkt', None, True, d))
        configs.append(('mkt', 0, True, d)); configs.append(('mkt', 3, True, d))
        configs.append(('fair', None, True, d)); configs.append(('fair', 3, True, d))
        configs.append(('min', None, True, d)); configs.append(('min', 0, True, d))
    for mode, cancel, strict, d in configs:
        per = {}
        allr = []
        for mid, (G, M, ff, name) in games.items():
            r = sim(G, M, d, mode, cancel, strict, ff); allr += r
            a = agg(r); per[name] = round(a['net'], 0)
        a = agg(allr)
        res.append(dict(mode=mode, cancel=cancel, strict=strict, d=d, **{k: round(v, 1) for k, v in a.items()}, per_game_net=per))
    json.dump(res, open(os.path.join(HERE, 'out_bidsim.json'), 'w'), indent=1)
    print(f"{'mode':5}{'canc':>5}{'strict':>7}{'d':>6}{'fills':>7}{'$fill':>9}{'entry%':>8}{'m1%':>7}{'1-5m%':>7}{'rest%':>7}{'pnl%':>7}{'reb%':>6}{'net$':>8}  per-game net")
    for r in res:
        u = r['usd'] or 1
        print(f"{r['mode']:5}{str(r['cancel']):>5}{str(r['strict']):>7}{r['d']:>6}{r['n']:>7}{r['usd']:>9.0f}{100*r['entry']/u:>8.2f}{100*r['m1']/u:>7.2f}{100*r['m5']/u:>7.2f}{100*r['rest']/u:>7.2f}{100*r['pnl']/u:>7.2f}{100*r['reb']/u:>6.2f}{r['net']:>8.0f}  {list(r['per_game_net'].values())}")

if __name__ == '__main__':
    main()
