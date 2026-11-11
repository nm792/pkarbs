#!/usr/bin/env python3
"""Shard worker for scan/LOCKED-gas-follow-entry-exit-rule-2026-11-11.md. Usage: gas_follow_entry_test.py SHARD NSHARDS"""
import sys, os, calendar, time, pickle
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
STATES = "AK AL AR AZ CO CT DE HI IA ID KS KY LA MA MD ME MN MO MS MT ND NE NH NM NV OK OR RI SC SD TN UT VT WV WY".split()
ENTRY = (1, 6, 12)
def fee(p): return 0.07 * p * (1 - p)
def run(st):
    ser = f"KXAAAGASD{st}"; ms = g.list_markets(ser, hist_pages=3); ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {e: float(l[0]["expiration_value"]) for e, l in ev.items() if l[0].get("expiration_value")}
    pd_ = lambda d, k: time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    ds = sorted(byday); rows = []
    for wi, win in (("A", ds[-30:]), ("B", ds[-60:-30])):
        for d in win:
            e = byday[d]; e1, e2 = byday.get(pd_(d, 1)), byday.get(pd_(d, 2))
            if e not in expv or e1 not in expv or e2 not in expv: continue
            prev, chg = expv[e1], expv[e1] - expv[e2]
            if abs(chg) < 0.0005: continue
            up = chg > 0
            for m in ev[e]:
                if abs(float(m["floor_strike"]) - prev) > 0.03: continue
                r = g.candles(m, ser)
                if not r: continue
                ask, bid, vol, ot, ct = r; n = len(ask); y = int(m["result"] == "yes")
                for k in ENTRY:
                    if k + 1 >= n or np.isnan(ask[k]) or np.isnan(bid[k]) or ask[k] <= bid[k]: continue
                    mid = (ask[k] + bid[k]) / 2
                    if not (0.25 <= mid <= 0.75): continue
                    x = min(k + 3, n - 1)
                    def side(is_yes):
                        c = ask[k] if is_yes else 1 - bid[k]
                        if not (0.05 < c < 0.95): return None
                        win = float(y == 1) if is_yes else float(y == 0)
                        gh = win - c - fee(c)
                        if x > k and not (np.isnan(ask[x]) or np.isnan(bid[x])):
                            q = bid[x] if is_yes else 1 - ask[x]
                            ge = q - c - fee(c) - fee(q)
                        else: ge = gh
                        return c, win, gh, ge
                    f, o = side(up), side(not up)
                    if f is None or o is None: continue
                    rows.append({"st": st, "win": wi, "k": k, "ev": e, "close": ct, "cost": f[0], "hit": f[1], "imp": mid if up else 1 - mid,
                                 "spread": float(ask[k] - bid[k]), "gh": f[2], "ge": f[3], "ah": o[2], "ae": o[3],
                                 "size": float(vol[k + 1:k + 3].sum()) * 0.5 * f[0] * 0.10, "dvol": float(vol[k + 1:k + 3].sum()) * mid})
    return rows
if __name__ == "__main__":
    s, n = int(sys.argv[1]), int(sys.argv[2]); rows = []
    for st in STATES[s::n]:
        try: rows += run(st)
        except Exception as e: print(st, "error", e, flush=True)
        print(st, len(rows), flush=True)
    pickle.dump(rows, open(f"/tmp/fe_rows_{s}.pkl", "wb"))
