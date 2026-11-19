"""Can-fail tests for Amendment 2 (planted stale prints, fair-priced prints, sign flip, no lookahead, missing perp mark). Run: python3 test_stale.py"""
import random, math, numpy as np
from oclib import *
rng = random.Random(3); S30 = 0.0015; CS = 7000.0; T = 1_800_000_000
def make(n_events=6000, price_offset=0.0, jump_after=False):
    ev = []
    for i in range(n_events):
        x = rng.gauss(0, 0.004); mark = CS * math.exp(x); tau = 120.0; t = T - int(tau * 60)
        pu = Phi(x / s_tau(S30, tau)); up = rng.random() < pu
        r = dict(date=f"d{i}", T=T, up_token="U", dn_token="D", up=up, cs=CS)
        tok = "U" if pu >= 0.5 else "D"; fair = pu if tok == "U" else 1 - pu
        price = min(0.97, max(0.03, fair - price_offset))
        tr = [dict(token_id=tok, side="BUY", price=price, size=100.0, timestamp=t)]
        bars_ts = [(t - 200) * 1000 // 60000 * 60000]; bars_mark = [mark]
        ev.append((r, tr, bars_ts, bars_mark))
    return ev
def run(ev, flip=False, thr=THR):
    allst = []; cnt = collections.Counter()
    for r, tr, bt, bm in ev:
        st, c = stale_prints(r, tr, bt, bm, S30, thr=thr, flip=flip); allst += st; cnt.update(c)
    return allst, cnt
# 1 planted: prints priced 5c below fair -> found, P&L about +5c minus fee
ev = make(price_offset=0.05); st, c = run(ev); m = np.mean([s["pnl"] for s in st]); print("planted stale", len(st), "of", c["buy_prints"], "mean pnl", round(m, 4)); assert len(st) > 4000 and 0.025 < m < 0.055, m
# 2 prints at fair -> no stale prints (edge = -fee < thr)
st0, c0 = run(make(price_offset=0.0)); print("fair-priced stale", len(st0)); assert len(st0) == 0
# 3 sign flip: on the planted case (prints on the model's favoured token, priced 5c below fair) the flipped model believes that token is worth LESS than the print price, so it must find (almost) nothing
stf, cf = run(ev, flip=True); print("flip stale", len(stf), "of", cf["buy_prints"]); assert len(stf) < 0.05 * cf["buy_prints"]
# 4 no lookahead: a jump in the minute that ends after the print must not change the fair used
r, tr, bt, bm = make(1, price_offset=0.0)[0]; t = tr[0]["timestamp"]
bt2 = [t * 1000 - 200000, t * 1000 - 30000]; bm2 = [bm[0], bm[0] * 1.05]   # second bar is stamped within the last 30 s: its minute is not complete at t
assert perp_at(bt2, bm2, t * 1000) == bm[0], "lookahead: used a bar whose minute was not complete"
# a bar stamped exactly t-60 s IS complete (closes at t)
bt3 = [t * 1000 - 60000]; assert perp_at(bt3, [123.0], t * 1000) == 123.0
# 5 missing / old perp mark -> skipped and counted, never filled
r5, tr5, _, _ = make(1)[0]; st5, c5 = stale_prints(r5, tr5, [(tr5[0]["timestamp"] - 900) * 1000], [CS], S30); assert st5 == [] and c5["no_perp_mark"] == 1 and c5["buy_prints"] == 1, c5
st6, c6 = stale_prints(r5, tr5, [], [], S30); assert st6 == [] and c6["no_perp_mark"] == 1
print("STALE TESTS PASS")
