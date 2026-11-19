#!/usr/bin/env python3
"""Follow-the-last-AAA-change nowcast on the Polymarket daily gas ladder (us-gas-price-daily). Analysis only.

AAA history comes from the resolutions themselves: each day's winning bucket gives the print as an interval
(interior bucket: [lo, lo+1c); bottom "<$X": (-inf, X); top "$X+": [X, inf)).
Sign of the last change (day D-1 vs D-2) is known when the two intervals do not overlap; otherwise the day is skipped.
Rule (fixed before scoring): last change down -> buy YES on the bottom bucket; up -> buy YES on the top bucket.
Model probability = walk-forward hit rate of that bucket on earlier events with the same sign (Laplace prior 1/2),
so day D uses only days before D. Buy at a taker-BUY print (own ask existed at that price/size) only if
  print time < CUTOFF before the event end (pre-print), price + fee <= p_model - MARGIN, 0.05 <= price < 0.95.
Placebo: the reverse rule (down -> top bucket, up -> bottom), same filter.
Usage: python3 nowcast.py raw/events_trades-<stamp>.json.gz [--cutoff-h 11] [--margin 0.05]
"""
import gzip, json, sys, argparse, datetime
from collections import defaultdict
import numpy as np
import size

def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def bounds(title):
    t = title.replace("$", "").replace(",", "")
    if t.startswith("<"): return (-9.0, float(t[1:]))
    if t.endswith("+"): return (float(t[:-1]), 99.0)
    lo, hi = t.split("-"); return (float(lo), float(hi) + 0.0001)

def daily(events):
    out = []
    for e in sorted((e for e in events.values() if e["_series"] == "us-gas-price-daily"), key=lambda e: e["endDate"]):
        mk = e["markets"]; ti = [m.get("groupItemTitle") for m in mk]
        res = [size.resolved_yes(m) for m in mk]
        bot = min(range(len(mk)), key=lambda i: bounds(ti[i])[0]); top = max(range(len(mk)), key=lambda i: bounds(ti[i])[0])
        w = [i for i, r in enumerate(res) if r == 1]
        out.append({"slug": e["slug"], "end": ts(e["endDate"]), "start": ts(e["startDate"]), "mk": mk, "bot": bot, "top": top,
                    "win": w[0] if len(w) == 1 else None, "iv": bounds(ti[w[0]]) if len(w) == 1 else None})
    return out

def sign(a, b):
    """sign of print(a) - print(b) from intervals; 0 if unknown."""
    if a is None or b is None: return 0
    if a[1] <= b[0]: return -1
    if a[0] >= b[1]: return 1
    return 0

def run(events, cutoff_h=11.0, margin=0.05, reverse=False, rng=None):
    rng = rng or np.random.default_rng(0)
    ds = daily(events); hist = defaultdict(lambda: [1, 2])   # Laplace: hits, n
    rows = []; days = []
    for k in range(2, len(ds)):
        d, d1, d2 = ds[k], ds[k - 1], ds[k - 2]
        s = sign(d1["iv"], d2["iv"])
        if s == 0 or d["win"] is None: continue
        side = "bot" if (s < 0) != reverse else "top"
        i = d[side]; key = (s, side)
        p_model = hist[key][0] / hist[key][1]
        m = d["mk"]; y = 1 if d["win"] == i else 0
        days.append((d["slug"], s, side, round(p_model, 2), y))
        for t in m[i]["_trades"]:
            if t["side"] != "BUY" or t["outcome_index"] != 0: continue
            if t["timestamp"] > d["end"] - cutoff_h * 3600: continue
            p = t["price"]
            if not (size.LO <= p < size.HI): continue
            f = size.fee_per_share(m[i], p)
            if p + f > p_model - margin: continue
            rows.append((d["slug"], (p + f) * t["size"], (y - p - f) * t["size"], np.nan))
        hist[key][0] += y; hist[key][1] += 1
    return rows, days, ds

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("snapshot"); ap.add_argument("--cutoff-h", type=float, default=11.0)
    ap.add_argument("--margin", type=float, default=0.05); a = ap.parse_args(argv)
    ev = json.load(gzip.open(a.snapshot, "rt")); rng = np.random.default_rng(7)
    L = []; P = lambda s="": (print(s), L.append(s))
    for rev in (False, True):
        rows, days, ds = run(ev, a.cutoff_h, a.margin, rev, rng)
        span = (ds[-1]["end"] - ds[0]["start"]) / 86400
        hits = sum(x[4] for x in days)
        P(f"## {'PLACEBO reverse rule' if rev else 'Follow rule'} (cutoff {a.cutoff_h:.0f} h before end, margin {a.margin*100:.0f}c)")
        P(f"signal days {len(days)}; chosen bucket won {hits}/{len(days)}")
        st = size.clustered(rows, rng)
        if not st: P("no qualifying prints"); continue
        fd, md, ld, v = size.verdict(st, span)
        P(f"events traded {st['events']}, prints {st['prints']}, $ bought {st['cost']:,.0f} over {span:.0f} d = ${fd:,.0f}/day; "
          f"return {st['ret']*100:+.1f}c per $ (95% CI {st['lo']*100:+.1f}, {st['hi']*100:+.1f}); P&L ${st['pnl']:,.0f}; "
          f"100% of these prints ${st['pnl']/span:,.1f}/day; 10% slice ${md:,.1f}/day (CI low ${ld:,.1f}) -> {v}")
        P("")
    return L

if __name__ == "__main__" and "--v2" not in sys.argv:
    main()


# ---------------- v2: full nowcast with AAA history read from the ladders ----------------
# Fact measured on all 16 interior-resolved days: the next day's bottom threshold X_D = cent(y_{D-1}) - 1c or - 2c.
# So y_{D-1} lies in [X_D + 1c, X_D + 3c), intersected with day D-1's winning interval. Midpoint = estimate.
from math import erf, sqrt
def ncdf(x): return 0.5 * (1 + erf(x / sqrt(2)))

def aaa_series(ds):
    y = {}
    for k in range(len(ds)):
        lo, hi = -9.0, 99.0
        if ds[k]["iv"]: lo, hi = ds[k]["iv"]
        if k + 1 < len(ds):
            X = bounds(ds[k + 1]["mk"][ds[k + 1]["bot"]]["groupItemTitle"])[1]
            lo, hi = max(lo, X + 0.01), min(hi, X + 0.03)
        if lo < hi and hi - lo <= 0.03: y[k] = (lo + hi) / 2
    return y

def run2(events, cutoff_h=10.0, margin=0.05, model="follow", rng=None):
    ds = daily(events); y = aaa_series(ds); res = []; rows = []; info = []
    for k in range(2, len(ds)):
        d = ds[k]
        if d["win"] is None or (k - 1) not in y or (k - 2) not in y: continue
        dlt = y[k - 1] - y[k - 2]
        mu = y[k - 1] + {"follow": dlt, "reverse": -dlt, "flat": 0.0}[model]
        sd = max(0.01, sqrt(np.mean(np.square(res))) if len(res) >= 3 else 0.02)
        for i, m in enumerate(d["mk"]):
            lo, hi = bounds(m["groupItemTitle"])
            pY = ncdf((hi - mu) / sd) - ncdf((lo - mu) / sd)
            yv = 1 if d["win"] == i else 0
            for t in m["_trades"]:
                if t["side"] != "BUY" or t["timestamp"] > d["end"] - cutoff_h * 3600: continue
                p = t["price"]; pm = pY if t["outcome_index"] == 0 else 1 - pY; w = yv if t["outcome_index"] == 0 else 1 - yv
                if not (size.LO <= p < size.HI): continue
                f = size.fee_per_share(m, p)
                if p + f > pm - margin: continue
                rows.append((d["slug"], (p + f) * t["size"], (w - p - f) * t["size"], np.nan))
        if k in y: res.append(y[k] - mu)   # update sigma only after the day resolves (walk-forward)
        info.append((d["slug"], round(mu, 3), round(sd, 3)))
    return rows, info, ds

def main2(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("snapshot"); ap.add_argument("--cutoff-h", type=float, default=10.0)
    ap.add_argument("--margin", type=float, default=0.05); a = ap.parse_args(argv)
    ev = json.load(gzip.open(a.snapshot, "rt")); rng = np.random.default_rng(7)
    for model in ("follow", "flat", "reverse"):
        rows, info, ds = run2(ev, a.cutoff_h, a.margin, model, rng)
        span = (ds[-1]["end"] - ds[0]["start"]) / 86400
        st = size.clustered(rows, rng)
        if not st: print(model, "days", len(info), "no prints"); continue
        fd, md, ld, v = size.verdict(st, span)
        print(f"{model:8s} cutoff {a.cutoff_h:.0f}h: days {len(info)}, events traded {st['events']}, prints {st['prints']}, ${fd:,.0f}/day bought; "
              f"return {st['ret']*100:+.1f}c/$ (CI {st['lo']*100:+.1f}, {st['hi']*100:+.1f}); P&L ${st['pnl']:,.0f} = ${st['pnl']/span:,.1f}/day at 100%; "
              f"10% ${md:,.1f}/day (CI low ${ld:,.1f}) {v}")

if __name__ == "__main__" and "--v2" in sys.argv:
    sys.argv.remove("--v2"); main2()
