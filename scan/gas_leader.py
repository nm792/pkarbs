#!/usr/bin/env python3
"""Kalshi AAA gas: does buying the early favourite pay? (Nick 11 Nov 04:43Z)
For every resolved gas market (whole available history: live API + /historical), at three checkpoints
(first hour after open, 10% and 25% of the market's life) take the FAVOURED side (YES if mid>=50c else NO)
at the ask, hold to settlement. Report: favourite's ask, win rate, gap (win rate - ask - fee), net return per $,
size = $ traded on that market in the following hour x 0.5 (taker-buy share) x PART, and $/day with an
event-clustered bootstrap CI. First half of history by close time = train, second half = TEST (headline).
Run: python3 scan/gas_leader.py [--max-markets 250]"""
import sys, os, time, calendar, random, math, argparse
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v

PART = 0.10
CHECK = [("first hour", None), ("10% of life", 0.10), ("25% of life", 0.25)]


def ts(x): return calendar.timegm(time.strptime(x[:19], "%Y-%m-%dT%H:%M:%S"))


def fam(t):
    import re
    if re.fullmatch(r"KXAAAGASD[A-Z]{2}", t): return "state daily"
    return {"KXAAAGASD": "national daily", "KXAAAGASW": "national weekly", "KXAAAGASM": "national monthly"}.get(t)


def list_markets(series, hist_pages=8):
    out = []
    for base, p0 in ((v.KAL + "/markets", {"status": "settled", "min_close_ts": 0}), (v.KAL + "/historical/markets", {})):
        cur = None
        for _ in range(hist_pages):
            p = dict(p0, series_ticker=series, limit=1000)
            if cur: p["cursor"] = cur
            d = v.get(base, p, sleep=0.35)
            if not d: break
            out += [m for m in d.get("markets", []) if m.get("result") in ("yes", "no")]
            cur = d.get("cursor")
            if not cur: break
    seen, res = set(), []
    for m in out:
        if m["ticker"] not in seen:
            seen.add(m["ticker"]); res.append(m)
    return res


def candles(m, series):
    ot, ct = ts(m["open_time"]), ts(m["close_time"])
    d = v.get(f"{v.KAL}/series/{series}/markets/{m['ticker']}/candlesticks",
              {"start_ts": ot, "end_ts": ct, "period_interval": 60}, sleep=0.3)
    c = (d or {}).get("candlesticks") or []
    if len(c) < 4: return None
    ask, bid, vol, la, lb = [], [], [], None, None
    for x in c:
        a = v.fl((x.get("yes_ask") or {}).get("close_dollars"), -1); b = v.fl((x.get("yes_bid") or {}).get("close_dollars"), -1)
        la = a if a >= 0 else la; lb = b if b >= 0 else lb
        ask.append(np.nan if la is None else la); bid.append(np.nan if lb is None else lb); vol.append(v.fl(x.get("volume_fp")))
    return np.array(ask), np.array(bid), np.array(vol), ot, ct


def obs_for(m, series):
    r = candles(m, series)
    if not r: return []
    ask, bid, vol, ot, ct = r
    n = len(ask); y = int(m["result"] == "yes"); out = []
    for name, fr in CHECK:
        i = 1 if fr is None else max(1, int(n * fr))
        if i >= n - 1 or np.isnan(ask[i]) or np.isnan(bid[i]) or ask[i] <= bid[i]: continue
        mid = (ask[i] + bid[i]) / 2
        side = "Y" if mid >= 0.5 else "N"
        cost = ask[i] if side == "Y" else 1 - bid[i]
        if not (0.5 <= cost <= 0.995): continue
        win = (y == 1) if side == "Y" else (y == 0)
        fee = 0.07 * cost * (1 - cost)
        size = float(vol[i:i + 2].sum()) * 0.5 * cost            # $ traded next hour(s), taker-buy share
        out.append({"cp": name, "cost": cost, "win": float(win), "ret": (win - cost - fee) / cost, "fee": fee,
                    "size": size * PART, "ev": m["event_ticker"], "close": ct})
    return out


def summarize(rows, days, rng):
    if len(rows) < 20: return None
    cost = np.mean([r["cost"] for r in rows]); win = np.mean([r["win"] for r in rows]); fee = np.mean([r["fee"] for r in rows])
    ret = np.mean([r["ret"] for r in rows])
    pnl = defaultdict(float)
    for r in rows: pnl[r["ev"]] += r["size"] * r["ret"]
    keys = list(pnl); vals = np.array([pnl[k] for k in keys])
    bs = rng.integers(0, len(keys), (1000, len(keys)))
    perday = vals.sum() / days; lo = np.percentile(vals[bs].sum(1), 2.5) / days
    # CI on gap by event cluster
    g = defaultdict(list)
    for r in rows: g[r["ev"]].append(r["win"] - r["cost"] - r["fee"])
    gk = list(g); gs = np.array([sum(g[k]) for k in gk]); gc = np.array([len(g[k]) for k in gk])
    gb = rng.integers(0, len(gk), (1000, len(gk))); gm = gs[gb].sum(1) / gc[gb].sum(1)
    return {"n": len(rows), "ev": len(keys), "cost": cost, "win": win, "gap": win - cost - fee,
            "gap_lo": float(np.percentile(gm, 2.5)), "gap_hi": float(np.percentile(gm, 97.5)), "ret": ret,
            "size": float(np.mean([r["size"] for r in rows])), "perday": perday, "perday_lo": float(lo)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max-markets", type=int, default=250)
    ap.add_argument("--out", default="scan/OUT-gas-early-leader-2026-11-11.md"); a = ap.parse_args()
    random.seed(7); rng = np.random.default_rng(7)
    sl = (v.get(v.KAL + "/series", {"limit": 1000}, sleep=0.4) or {}).get("series", [])
    fams = defaultdict(list)
    for s in sl:
        f = fam(s["ticker"])
        if f: fams[f].append(s["ticker"])
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    P("# Kalshi gas: buy the early favourite (favoured side at the ask, hold to settlement)")
    P("Whole available history (live + /historical). TEST = second half by close date. gap = win rate - ask - Kalshi fee (0.07 p(1-p)). "
      f"size = 10% of the $ traded on that market in the 2 hours from the checkpoint (x0.5 taker-buy share). $/day = sum(size x net return)/days, event-clustered 95% CI.\n")
    P("| series | checkpoint | half | markets (events) | favourite ask | win rate | gap net of fee (95% CI) | net/$ | size per market | $/day (lo95) | days |")
    P("|---|---|---|---|---:|---:|---|---:|---:|---|---:|")
    for f in ["national daily", "state daily", "national weekly", "national monthly"]:
        mk = []
        for t in fams.get(f, []):
            mk += [(m, t) for m in list_markets(t)]
        if not mk: continue
        closes = [ts(m["close_time"]) for m, _ in mk]
        random.shuffle(mk); mk = mk[:a.max_markets]
        rows = []
        for m, t in mk: rows += obs_for(m, t)
        if not rows: continue
        rows.sort(key=lambda r: r["close"]); lo_t, hi_t = min(r["close"] for r in rows), max(r["close"] for r in rows)
        mid_t = np.median([r["close"] for r in rows])
        P(f"<!-- {f}: {len(closes)} resolved markets listed, {len(mk)} sampled, history {time.strftime('%Y-%m-%d', time.gmtime(lo_t))} to {time.strftime('%Y-%m-%d', time.gmtime(hi_t))} -->")
        for cp, _ in CHECK:
            for half, sel, d0, d1 in (("train", lambda r: r["close"] <= mid_t, lo_t, mid_t), ("TEST", lambda r: r["close"] > mid_t, mid_t, hi_t)):
                days = max(1.0, (d1 - d0) / 86400)
                # scale sampled $/day up to all listed markets
                sub = [r for r in rows if r["cp"] == cp and sel(r)]
                s = summarize(sub, days, rng)
                if not s: P(f"| {f} | {cp} | {half} | <20 obs | | | | | | | |"); continue
                scale = len(closes) / max(1, len(mk))
                P(f"| {f} | {cp} | {half} | {s['n']} ({s['ev']}) | {s['cost']*100:.1f}c | {s['win']*100:.1f}% | {s['gap']*100:+.2f}c ({s['gap_lo']*100:+.2f}, {s['gap_hi']*100:+.2f}) | "
                  f"{s['ret']*100:+.2f}% | ${s['size']:,.0f} | ${s['perday']*scale:,.0f} (${s['perday_lo']*scale:,.0f}) | {days:.0f} |")
    P("\n$/day is scaled from the sample to all listed resolved markets. Held to settlement; no exits modelled.")
    open(a.out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
