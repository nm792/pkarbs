#!/usr/bin/env python3
"""Cricket feed timing vs the Polymarket PRICE, and the event-only rule delay curve (5 Nov 2026).

Inputs: a capture folder from capture.py (books/markets/espn/sports jsonl), a match map json, and per-token
trades (data-api v2) saved as TRADESDIR/<conditionId>.json.

Match map (one entry per match): {"espn": "1543953", "slug": "...", "teams": {"<ESPN batting abbr>": "<token id>", ...},
                                  "fmt": "T20", "winner": "<ESPN abbr of winner or null>"}

1. Feed lag. Events = ESPN balls whose playType is out / four / six (first poll of a match skipped).
   R = the time our 1 s poll that first returned the ball was SENT (ms). The ball was on ESPN at most 1 s before.
   Price onset = first second, after base time, at which the mid of the batting team's token has moved >= TH in the
   event's direction (boundary up, wicket down) from the base mid. Base = mid at max(R - 60 s, previous ESPN ball + 3 s).
   TH = 1c for boundaries, 2c for wickets. lag = R - onset (positive = ESPN is BEHIND the price).
   The Polymarket sports-WS score change for the same ball gives a second lag (WS - onset).
2. Delay curve. T0 = R - --anchor (0 = the ESPN feed as it is; 30 = ESPN's measured lag behind the price, i.e. a feed at true event time).
   For d in 0/5/10/20/30/60 s, at t = T0 + d, the rule bids on the token the model says should rise >= 1c and has not
   yet risen that far since T0 - 5 s: price = mid x 0.975 rounded UP to the 0.1c/1c tick, never at/above best ask,
   only if fair - bid >= E (1c). The bid rests 30 s. Fill = trades on that token at price <= bid in the 30 s, minus the
   resting size already at our price (queue ahead), capped at CAP shares. Held to resolution.
   Model = evrules.cricket.fair_after (men's T20I logistic, market-anchored). Innings 2 overs 15-20 blocked (PR #32).
Usage: analyze.py CAPDIR MATCHMAP.json TRADESDIR [--cap 500]
"""
import argparse, bisect, gzip, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from evrules import cricket   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('cap'); ap.add_argument('mapf'); ap.add_argument('trades')
ap.add_argument('--cap-shares', type=float, default=500)
ap.add_argument('--out', default='')
ap.add_argument('--anchor', type=float, default=0.0, help='T0 = R - anchor seconds (0 = ESPN receipt; ~30 = estimated true event time from the event-triggered average)')
A = ap.parse_args()
D, E, WIN = 0.025, 0.01, 30.0
DELAYS = [0, 5, 10, 20, 30, 60]


def rd(name):
    for fn in (name + '.jsonl', name + '.jsonl.gz'):
        p = os.path.join(A.cap, fn)
        if os.path.exists(p):
            op = gzip.open if fn.endswith('.gz') else open
            with op(p, 'rt') as f:
                return [json.loads(l) for l in f if l.strip()]
    return []


def parse_score(s):
    s = str(s or '0')
    if '/' in s:
        r, w = s.split('/')[:2]; return int(r), int(w.split()[0])
    try: return int(s.split()[0]), 0
    except Exception: return 0, 0


def balls_of(over):
    if over is None: return None
    o = int(over); b = round((over - o) * 10); return o * 6 + b


class Book:
    def __init__(self):
        self.t, self.mid, self.bb, self.ba, self.bsz = [], [], [], [], []

    def add(self, ms, bids, asks):
        bids = [(float(x['price']), float(x['size'])) for x in bids or []]
        asks = [(float(x['price']), float(x['size'])) for x in asks or []]
        if not bids or not asks: return
        bb = max(bids); ba = min(asks)
        self.t.append(ms / 1000.0); self.bb.append(bb[0]); self.ba.append(ba[0])
        self.mid.append((bb[0] + ba[0]) / 2); self.bsz.append(dict(bids))

    def at(self, t):
        i = bisect.bisect_right(self.t, t) - 1
        return None if i < 0 else i


def tick_up(p, tick):
    return math.ceil(p / tick - 1e-9) * tick


def main():
    M = json.load(open(A.mapf))
    books = {}
    for r in rd('books'):
        books.setdefault(r['tk'], Book()).add(r['ms'], r.get('bids'), r.get('asks'))
    espn = {}
    for r in rd('espn'):
        espn.setdefault(r['ev'], []).append(r)
    sports = rd('sports')
    lagrows, simrows = [], []
    for m in M:
        rows = sorted(espn.get(m['espn'], []), key=lambda r: (r['seq'] or 0))
        teams = m['teams']; inv = {v: k for k, v in teams.items()}
        trades = {}
        for abbr, tk in teams.items():
            p = os.path.join(A.trades, f"{tk}.json")
            if os.path.exists(p):
                tr = json.load(open(p)); tr = tr.get('data', tr) if isinstance(tr, dict) else tr
                trades[tk] = sorted((float(x['timestamp']), float(x['price']), float(x['size'])) for x in tr
                                    if str(x.get('token_id', x.get('asset'))) == tk)
        bat_first = None; first_total = None; prev_R = None; prev_state = {}
        for r in rows:
            inn = r.get('inn')
            if inn == 1 and r.get('bat'): bat_first = bat_first or r['bat']
            if inn == 1: first_total = parse_score(r['home'])[0]
            runs, w = parse_score(r['home'] if inn == 1 else r['away'])
            b = balls_of(r.get('over'))
            if b is None: continue
            st = dict(innings=inn, runs=runs, wkts=w, balls=b,
                      target=(first_total + 1) if inn == 2 and first_total else None, fmt=m.get('fmt', 'T20'))
            before = prev_state.get(inn); prev_state[inn] = st
            R = r['ms'] / 1000.0
            pR, prev_R = prev_R, R
            if r.get('first') or r.get('play') not in ('out', 'four', 'six') or before is None: continue
            bat = r.get('bat'); tk = teams.get(bat)
            if tk is None or tk not in books: continue
            Bk = books[tk]; s = -1 if r['play'] == 'out' else 1; TH = 0.02 if r['play'] == 'out' else 0.01
            t_base = max(R - 60, (pR or 0) + 3)
            ib = Bk.at(t_base)
            if ib is None: continue
            base = Bk.mid[ib]
            onset = None
            j = ib
            while j < len(Bk.t) and Bk.t[j] <= R + 60:
                if s * (Bk.mid[j] - base) >= TH - 1e-9: onset = Bk.t[j]; break
                j += 1
            lagrows.append(dict(match=m['slug'], play=r['play'], inn=inn, over=r.get('over'), R=R, onset=onset,
                                lag=None if onset is None else R - onset, base=base))
            # ---------- delay curve ----------
            T0 = R - A.anchor
            ia = Bk.at(T0 - 5)
            if ia is None: continue
            anc_bat = Bk.mid[ia]
            if not (0.03 < anc_bat < 0.97): continue
            if inn == 2 and b >= 84: continue          # overs 15-20 of the chase blocked (PR #32)
            p_bf_before = anc_bat if bat == bat_first else 1 - anc_bat
            fair_bf = cricket.fair_after(before, st, p_bf_before)
            fair_bat = fair_bf if bat == bat_first else 1 - fair_bf
            jump_bat = fair_bat - anc_bat
            for d in DELAYS:
                tp = T0 + d
                for side_tk, pj, fair, sgn in [(tk, jump_bat, fair_bat, 1)] + \
                        [(t2, -jump_bat, 1 - fair_bat, -1) for a2, t2 in teams.items() if t2 != tk]:
                    if pj < 0.01 or side_tk not in books: continue
                    Bs = books[side_tk]; ip = Bs.at(tp); ia2 = Bs.at(T0 - 5)
                    if ip is None or ia2 is None: continue
                    mk = Bs.mid[ip]; rm = mk - Bs.mid[ia2]
                    if rm >= pj or not (0.05 <= mk <= 0.95): continue
                    tick = 0.001 if mk < 0.04 or mk > 0.96 else 0.01
                    bid = round(tick_up(mk * (1 - D), tick), 3)
                    if bid >= Bs.ba[ip] - 1e-9 or fair - bid < E: continue
                    q_ahead = Bs.bsz[ip].get(bid, 0.0)
                    vol = sum(sz for (ts, px, sz) in trades.get(side_tk, []) if tp <= ts < tp + WIN and px <= bid + 1e-9)
                    q = min(A.cap_shares, max(0.0, vol - q_ahead))
                    win_abbr = m.get('winner'); side_abbr = inv.get(side_tk)
                    out = None if win_abbr is None else (1.0 if side_abbr == win_abbr else 0.0)
                    simrows.append(dict(match=m['slug'], d=d, play=r['play'], inn=inn, over=r.get('over'), bid=bid, mk=mk,
                                        fair=fair, pj=pj, q_ahead=q_ahead, vol=vol, q=q,
                                        pnl=None if out is None else q * (out - bid), traded=bool(trades.get(side_tk))))
    # ---------- WS vs price ----------
    ws = []
    for r in sports:
        try: d = json.loads(r['raw'])
        except Exception: continue
        ws.append((r['ms'] / 1000.0, d))
    # ---------- summary ----------
    out = dict(events=len(lagrows))
    L = np.array([x['lag'] for x in lagrows if x['lag'] is not None])
    if len(L):
        out['espn_lag_vs_price_s'] = dict(n=int(len(L)), no_move=int(sum(x['lag'] is None for x in lagrows)),
                                         median=float(np.median(L)), p25=float(np.percentile(L, 25)),
                                         p75=float(np.percentile(L, 75)), share_price_first=float(np.mean(L > 0)))
        for pl in ('out', 'four', 'six'):
            Lp = np.array([x['lag'] for x in lagrows if x['lag'] is not None and x['play'] == pl])
            if len(Lp): out[f'lag_{pl}'] = dict(n=int(len(Lp)), median=float(np.median(Lp)))
    curve = {}
    for d in DELAYS:
        rs = [x for x in simrows if x['d'] == d]
        f = [x for x in rs if x['q'] > 0]
        curve[d] = dict(bids=len(rs), filled=len(f), shares=float(sum(x['q'] for x in f)),
                        usd_in=float(sum(x['q'] * x['bid'] for x in f)),
                        pnl=float(sum(x['pnl'] for x in f if x['pnl'] is not None)),
                        unresolved=sum(1 for x in f if x['pnl'] is None))
    out['delay_curve'] = curve
    out['ws_msgs'] = len(ws)
    print(json.dumps(out, indent=1))
    if A.out:
        json.dump(dict(summary=out, lag_rows=lagrows, sim_rows=simrows), open(A.out, 'w'))


if __name__ == '__main__':
    main()
