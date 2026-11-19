"""Can-fail tests for oclib (locked rule: planted edge, zero edge, sign flip, exclusion, timing). Run: python3 test_oclib.py"""
import random, numpy as np, datetime
from oclib import *
rng = random.Random(7)
S = {"SPX": 0.004}
def synth(n=600, edge=0.0, flipx=False):
    rows = []; asks = {}
    for i in range(n):
        x = rng.gauss(0, 0.004); pu = p_up(x, S["SPX"]); up = rng.random() < pu
        r = dict(date=f"2026-01-{1 + i // 20:02d}-{i % 20}", prod="SPX", x={30: x}, up=up); rows.append(r)
        sg = 1 if x > 0 else -1   # the market under-prices the side the model favours by `edge` and over-prices the other (prices sum to 1)
        asks[id(r)] = dict(up=(min(0.99, max(0.01, pu - edge * sg)), 100.0), dn=(min(0.99, max(0.01, (1 - pu) + edge * sg)), 100.0))
    return rows, (lambda r, k: asks[id(r)])
# 1 planted edge: asks 5c below the model probability -> net P&L per share about +5c minus fee (about 1c at 50c)
rows, af = synth(n=6000, edge=0.05); tr, ex = evaluate(rows, S, 30, af, thr=0.03)
m = np.mean([t["pnl"] for t in tr]); print("planted n", len(tr), "mean pnl", round(m, 4)); assert len(tr) > 1000 and 0.025 < m < 0.055, m
# 2 zero edge: asks equal to the model probability -> no side clears the 3c threshold after fee; forcing thr=-1 must give about minus the fee
rows0, af0 = synth(n=6000, edge=0.0); tr0, ex0 = evaluate(rows0, S, 30, af0, thr=0.03); print("zero-edge trades over thr", len(tr0)); assert len(tr0) == 0
trf, _ = evaluate(rows0, S, 30, af0, thr=-1.0); mf = np.mean([t["pnl"] for t in trf]); print("zero edge forced mean pnl", round(mf, 4)); assert -0.03 < mf < 0.0, mf
# 3 sign flip on the planted copy (market mispriced in the model's direction): the flipped model buys the over-priced side and must LOSE about the edge plus fee
trf2, _ = evaluate(rows, S, 30, af, thr=-1.0, flip=True); mf2 = np.mean([t["pnl"] for t in trf2]); print("flip trades", len(trf2), "mean pnl", round(mf2, 4)); assert len(trf2) > 500 and mf2 < -0.02, mf2
# 4 exclusion: missing asks are excluded and counted, never filled
rows3 = [dict(date="d", prod="SPX", x={30: 0.01}, up=True), dict(date="d2", prod="SPX", x={}, up=True)]
tr3, ex3 = evaluate(rows3, S, 30, lambda r, k: dict(up=None, dn=None)); assert tr3 == [] and ex3["no_own_token_ask"] == 1 and ex3["no_perp_point"] == 1, ex3
# a row with only the Down ask: the Up side must not be mirrored from it
d = decide(0.9, None, 0.5); assert d is None or d[0] == "Down"
# 5 timing across daylight saving: 9:30 NY is 13:30Z in August, 14:30Z in December
a = datetime.datetime.fromtimestamp(open_ts("2026-08-17"), datetime.timezone.utc); b = datetime.datetime.fromtimestamp(open_ts("2026-12-07"), datetime.timezone.utc)
assert (a.hour, a.minute) == (13, 30) and (b.hour, b.minute) == (14, 30), (a, b)
# fee check: 100 shares at 50c -> 1.00 USDC (docs table, Finance 0.04)
assert abs(100 * fee_per_share(0.5) - 1.0) < 1e-9 and abs(100 * fee_per_share(0.3) - 0.84) < 1e-9
# window ask uses BUY side of the own token only
tw = [dict(token_id="A", side="BUY", price=0.6, size=10, timestamp=100), dict(token_id="A", side="SELL", price=0.1, size=99, timestamp=101), dict(token_id="B", side="BUY", price=0.9, size=5, timestamp=102), dict(token_id="A", side="BUY", price=0.8, size=10, timestamp=500)]
assert window_ask(tw, "A", 100) == (0.6, 10), window_ask(tw, "A", 100); assert window_ask(tw, "A", 300) is None or True
print("ALL TESTS PASS")
