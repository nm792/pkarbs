#!/usr/bin/env python3
"""Kalshi AAA gas sizing, LOCKED in reviewer/REPLY-2026-11-19-gas-and-perp-open.md (89a146df).
Analysis only: public Kalshi market data, no orders, no keys (SETTLED A6, A7).

Signal: follow rule (sign of print D-1 minus print D-2). Qualifying strike: |strike - print D-1| <= 0.03, mid in [0.25, 0.75] at entry
candle, ask > bid, followed-side cost in (0.05, 0.95).
Routes: R1 taker at the ask; R2 resting bid at the followed side's mid rounded down to the cent, filled only if a trade print in the
next 2 candles is at or below that price (UPPER BOUND: queue position unknown, no historical book depth).
Size: SHARE x contracts traded in the next 2 candles.
Usage: gas_sizing.py --out DIR [--days 60] [--series KXAAAGASD,...] [--workers 4] [--rps 6]
"""
import sys, os, json, time, calendar, math, argparse, threading, urllib.request, urllib.error, urllib.parse
from collections import defaultdict
import numpy as np

KAL = "https://api.elections.kalshi.com/trade-api/v2"
CACHED = "CA TX FL NY IL NJ WA NC OH PA GA VA".split()
FRESH = ("AK AL AR AZ CO CT DE HI IA ID KS KY LA MA MD ME MN MO MS MT ND NE NH NM NV OK OR RI SC SD TN UT VT WV WY").split()
ENTRY = (1, 6, 12)
SHARE = 0.05          # 10% of the volume window x 0.5 taker share
WINDOW = 2            # candles after entry used for volume and fills
STRIKE_TOL = 0.03
MAKER_FEE_SENS = 0.0175   # sensitivity only; ASSUMED until the Kalshi maker schedule is cited


def taker_fee(p): return 0.07 * p * (1 - p)
def maker_fee(p, k=0.0): return k * p * (1 - p)
def ts(x): return calendar.timegm(time.strptime(x[:19], "%Y-%m-%dT%H:%M:%S"))
def fl(x, d=0.0):
    try: return float(x)
    except Exception: return d


class Client:
    """Rate-limited Kalshi GET with 429 backoff."""
    def __init__(self, rps=6.0):
        self.min_gap = 1.0 / rps; self.lock = threading.Lock(); self.t = 0.0
        self.calls = 0; self.fail = 0; self.n429 = 0

    def get(self, path, params=None, tries=8):
        url = KAL + path + ("?" + urllib.parse.urlencode(params) if params else "")
        for i in range(tries):
            with self.lock:
                w = self.t + self.min_gap - time.time()
                if w > 0: time.sleep(w)
                self.t = time.time()
            self.calls += 1
            try:
                with urllib.request.urlopen(url, timeout=40) as r: return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 429: self.n429 += 1; time.sleep(2 * (i + 1)); continue
                if e.code in (404, 400): self.fail += 1; return None
                time.sleep(1 + i)
            except Exception:
                time.sleep(1 + i)
        self.fail += 1
        return None

    def list_markets(self, series, since_ts):
        out, seen = [], set()
        for base, p0 in (("/markets", {"status": "settled", "min_close_ts": since_ts}), ("/historical/markets", {})):
            cur = None
            for _ in range(10):
                p = dict(p0, series_ticker=series, limit=1000)
                if cur: p["cursor"] = cur
                d = self.get(base, p)
                if not d: break
                for m in d.get("markets", []):
                    if m.get("result") in ("yes", "no") and m["ticker"] not in seen and ts(m["close_time"]) >= since_ts:
                        seen.add(m["ticker"]); out.append(m)
                cur = d.get("cursor")
                if not cur: break
        return out

    def candles(self, m, series):
        d = self.get(f"/series/{series}/markets/{m['ticker']}/candlesticks",
                     {"start_ts": ts(m["open_time"]), "end_ts": ts(m["close_time"]), "period_interval": 60})
        return (d or {}).get("candlesticks")


def parse_candles(cs):
    """-> dict of np arrays: ask, bid (forward-filled closes), vol, plo, phi (trade price low/high, nan if no trade), mid."""
    if not cs or len(cs) < 4: return None
    ask, bid, vol, plo, phi = [], [], [], [], []
    la = lb = None
    for x in cs:
        a = fl((x.get("yes_ask") or {}).get("close_dollars"), -1); b = fl((x.get("yes_bid") or {}).get("close_dollars"), -1)
        if a >= 0: la = a
        if b >= 0: lb = b
        ask.append(np.nan if la is None else la); bid.append(np.nan if lb is None else lb)
        vol.append(fl(x.get("volume_fp")))
        pr = x.get("price") or {}
        lo, hi = pr.get("low_dollars"), pr.get("high_dollars")
        plo.append(fl(lo, np.nan) if lo not in (None, "") else np.nan); phi.append(fl(hi, np.nan) if hi not in (None, "") else np.nan)
    return {"ask": np.array(ask), "bid": np.array(bid), "vol": np.array(vol), "plo": np.array(plo), "phi": np.array(phi)}


def eval_side(c, k, yes_side, result_yes):
    """One side (YES or NO) at entry candle k. Returns dict with R1 and R2 gaps, or None (dead / unusable). The NO book is taken
    from Kalshi's own structure (NO bid = 1 - YES ask, NO ask = 1 - YES bid); the API publishes YES bid/ask only."""
    ask, bid = c["ask"][k], c["bid"][k]
    if np.isnan(ask) or np.isnan(bid) or ask <= bid: return None
    mid = (ask + bid) / 2
    if not (0.25 <= mid <= 0.75): return "OUT_OF_BAND"
    cost1 = ask if yes_side else 1 - bid                    # R1 taker: own ask
    if not (0.05 < cost1 < 0.95): return "DEAD"
    win = float(result_yes) if yes_side else float(not result_yes)
    own_mid = mid if yes_side else 1 - mid
    bidp = math.floor(own_mid * 100 + 1e-9) / 100.0         # R2 resting bid price on the own token, 1c tick
    lo, hi = k + 1, min(k + 1 + WINDOW, len(c["ask"]))
    plo = c["plo"][lo:hi]; phi = c["phi"][lo:hi]
    if yes_side: filled = bool(np.any(~np.isnan(plo) & (plo <= bidp + 1e-9)))
    else: filled = bool(np.any(~np.isnan(phi) & (phi >= (1 - bidp) - 1e-9)))   # NO bid at p fills when YES prints at >= 1-p
    contracts = float(c["vol"][lo:hi].sum())
    return {"cost1": cost1, "win": win, "imp": own_mid, "bidp": bidp, "filled": filled, "contracts": contracts,
            "spread": float(ask - bid), "gap1": win - cost1 - taker_fee(cost1),
            "gap2_0": win - bidp - maker_fee(bidp), "gap2_s": win - bidp - maker_fee(bidp, MAKER_FEE_SENS)}


def day_of(m): return time.strftime("%Y-%m-%d", time.gmtime(ts(m["close_time"]) + 3600))
def shift(d, k): return time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))


def process_series(client, series, since_ts, stats):
    """All qualifying observations for one series. Events with no qualifying strike are still returned (zero rows) so per-day
    denominators and clusters are complete."""
    ms = client.list_markets(series, since_ts)
    ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    byday = {day_of(l[0]): e for e, l in ev.items()}
    expv = {e: fl(l[0].get("expiration_value"), None) for e, l in ev.items() if l[0].get("expiration_value") not in (None, "")}
    rows, events, svols = [], [], []
    allvol = sum(fl(m.get("volume_fp")) for m in ms)
    stats["markets_listed"] += len(ms); stats["events_listed"] += len(ev)
    for d, e in sorted(byday.items()):
        e1, e2 = byday.get(shift(d, 1)), byday.get(shift(d, 2))
        events.append(e)
        if e not in expv or e1 not in expv or e2 not in expv: stats["events_no_prints"] += 1; continue
        chg = expv[e1] - expv[e2]
        if abs(chg) < 0.0005: stats["events_no_signal"] += 1; continue
        up = chg > 0; prev = expv[e1]
        for m in ev[e]:
            if m.get("floor_strike") is None or abs(fl(m["floor_strike"]) - prev) > STRIKE_TOL: continue
            stats["strikes_near_print"] += 1
            c = parse_candles(client.candles(m, series))
            if c is None: stats["strikes_no_candles"] += 1; continue
            y = m["result"] == "yes"; n = len(c["ask"])
            svols.append({"series": series, "ev": e, "contracts": float(c["vol"].sum()),
                          "dollars": float(np.nansum(c["vol"] * (c["ask"] + c["bid"]) / 2))})   # whole-life volume, near-print strike (point 1)
            for k in ENTRY:
                if k + 1 >= n: stats["entry_beyond_life"] += 1; continue
                f = eval_side(c, k, up, y); o = eval_side(c, k, not up, y)
                if f is None or o is None: stats["entry_unusable"] += 1; continue
                if f == "OUT_OF_BAND" or o == "OUT_OF_BAND": stats["entry_out_of_band"] += 1; continue
                if f == "DEAD" or o == "DEAD": stats["entry_dead_excluded"] += 1; continue
                rows.append({"series": series, "ev": e, "day": d, "k": k, "f": f, "o": o})
    return rows, events, allvol, svols


def cluster_ci(ev_vals, ev_counts, rng, draws=2000):
    """Event-cluster bootstrap CI of mean per-observation value: sum(vals)/sum(counts)."""
    v = np.asarray(ev_vals, float); n = np.asarray(ev_counts, float)
    if len(v) == 0 or n.sum() == 0: return (float("nan"),) * 3
    idx = rng.integers(0, len(v), (draws, len(v)))
    m = v[idx].sum(1) / np.maximum(n[idx].sum(1), 1)
    return v.sum() / n.sum(), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def perday_ci(ev_pnls, days, rng, draws=2000):
    p = np.asarray(ev_pnls, float)
    if len(p) == 0: return (float("nan"),) * 3
    idx = rng.integers(0, len(p), (draws, len(p)))
    s = p[idx].sum(1) / days
    return float(p.sum() / days), float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def summarize(rows, events, days, rng, route, fee_key=None):
    """route 'R1' (taker, always fills) or 'R2' (resting bid, fills only if filled). fee_key for R2 'gap2_0' | 'gap2_s'."""
    by = defaultdict(lambda: {"g": 0.0, "n": 0, "ga": 0.0, "pnl": 0.0, "cap": 0.0, "shares": 0.0})
    for r in rows:
        f, o = r["f"], r["o"]
        if route == "R1": use, gf, go, cost = True, f["gap1"], o["gap1"], f["cost1"]
        else: use, gf, go, cost = f["filled"], f[fee_key], o[fee_key], f["bidp"]
        if not use: continue
        sh = SHARE * f["contracts"]
        b = by[r["ev"]]; b["g"] += gf; b["ga"] += go; b["n"] += 1; b["pnl"] += sh * gf; b["cap"] += sh * cost; b["shares"] += sh
    evs = sorted(set(events))
    vals = [by[e]["g"] if e in by else 0.0 for e in evs]; cnt = [by[e]["n"] if e in by else 0 for e in evs]
    alts = [by[e]["ga"] if e in by else 0.0 for e in evs]
    pnls = [by[e]["pnl"] if e in by else 0.0 for e in evs]
    nobs = int(sum(cnt)); nev = int(sum(1 for c in cnt if c))
    out = {"obs": nobs, "events_with_obs": nev, "events_total": len(evs)}
    if nobs == 0: return out
    mean, lo, hi = cluster_ci(vals, cnt, rng)
    # sign-flip placebo: each event keeps the followed side or swaps to the opposite side
    v = np.array(vals); a = np.array(alts); n = np.array(cnt, float)
    fl_ = rng.random((2000, len(v))) < 0.5
    sims = np.where(fl_, a, v).sum(1) / n.sum()
    z = float((mean - sims.mean()) / (sims.std() + 1e-12))
    pd_m, pd_lo, pd_hi = perday_ci(pnls, days, rng)
    out.update({"gap_mean": float(mean), "gap_lo": lo, "gap_hi": hi, "placebo_z": z,
                "hit": float(np.mean([r["f"]["win"] for r in rows if (route == "R1" or r["f"]["filled"])])),
                "implied": float(np.mean([r["f"]["imp"] for r in rows if (route == "R1" or r["f"]["filled"])])),
                "perday": pd_m, "perday_lo": pd_lo, "perday_hi": pd_hi,
                "capital_per_day": float(sum(b["cap"] for b in by.values()) / days),
                "mean_spread": float(np.mean([r["f"]["spread"] for r in rows])),
                "fill_rate": float(np.mean([r["f"]["filled"] for r in rows])) if route == "R2" else 1.0})
    daily = defaultdict(float)
    for r in rows:
        f = r["f"]
        if route == "R1": daily[r["day"]] += SHARE * f["contracts"] * f["gap1"]
        elif f["filled"]: daily[r["day"]] += SHARE * f["contracts"] * f[fee_key]
    out["worst_day"] = float(min(daily.values())) if daily else 0.0
    out["best_day"] = float(max(daily.values())) if daily else 0.0
    out["pass"] = bool(out["gap_lo"] > 0 and out["placebo_z"] >= 2 and nobs >= 100 and nev >= 40 and out["perday_lo"] >= 200)
    return out


def run(client, series_list, now_ts, days, out_dir, workers=4):
    since = now_ts - days * 86400
    stats = defaultdict(int); allrows, allevents, famvol, allsv = [], [], defaultdict(float), []
    fam_of = lambda s: "national" if s == "KXAAAGASD" else ("cached12" if s[-2:] in CACHED else "fresh35")
    lock = threading.Lock(); done = [0]
    def work(s):
        st = defaultdict(int)
        try: r, e, av, sv = process_series(client, s, since, st)
        except Exception as ex: r, e, av, sv = [], [], 0.0, []; st["series_errors"] += 1; print("ERR", s, ex, flush=True)
        with lock:
            for k, v in st.items(): stats[k] += v
            for x in r: x["fam"] = fam_of(s)
            for x in sv: x["fam"] = fam_of(s)
            allsv.extend(sv); allrows.extend(r); allevents.extend([(fam_of(s), s, ev_) for ev_ in e]); famvol[fam_of(s)] += av
            done[0] += 1
            print(f"{done[0]}/{len(series_list)} {s} rows={len(r)} events={len(e)} calls={client.calls} 429={client.n429} fail={client.fail}", flush=True)
    ths = []
    it = iter(series_list); itl = threading.Lock()
    def loop():
        while True:
            with itl:
                s = next(it, None)
            if s is None: return
            work(s)
    for _ in range(workers): t = threading.Thread(target=loop); t.start(); ths.append(t)
    for t in ths: t.join()
    return allrows, allevents, famvol, allsv, dict(stats)


def report(rows, events, famvol, svols, stats, days, run_id, sha):
    rng = np.random.default_rng(20261119)
    L = []
    P = lambda s="": (print(s, flush=True), L.append(s))
    P(f"# Kalshi AAA gas sizing, run {run_id} (code {sha})\nSim on real Kalshi data (public API, analysis only). Window: last {days} days to run time. Share = {SHARE} x contracts traded in the 2 candles after entry.")
    P(f"Counters: {json.dumps(stats)}\n")
    P("## Point 1: volume\n| family | all-strike contracts listed (life, window) | per day | near-print-strike contracts (life) per day | near-print $ (contracts x candle mid) per day |\n|---|---:|---:|---:|---:|")
    for fam in ("national", "cached12", "fresh35"):
        q = [x for x in svols if x["fam"] == fam]
        P(f"| {fam} | {famvol[fam]:,.0f} | {famvol[fam]/days:,.0f} | {sum(x['contracts'] for x in q)/days:,.0f} | {sum(x['dollars'] for x in q)/days:,.0f} |")
    P("\n## Points 3-5: by route, entry, family\nR1 = taker (control); R2 = resting bid, UPPER BOUND (queue unknown); maker fee 0 (assumed) and 0.0175 p(1-p) sensitivity (assumed).\n")
    P("| family | entry candle | route | obs (events) | hit vs implied | spread | gap (95% CI) | placebo z | fill rate | $/day (95% CI) | capital/day | worst day | pass |\n|---|---|---|---|---|---:|---|---:|---:|---|---:|---:|---|")
    res = {}
    for fam in ("national", "cached12", "fresh35", "ALL"):
        for k in list(ENTRY) + ["all"]:
            sub = [r for r in rows if (fam == "ALL" or r["fam"] == fam) and (k == "all" or r["k"] == k)]
            evs = [e for (f_, s_, e) in events if fam == "ALL" or f_ == fam]
            for route, fk, lab in (("R1", None, "R1 taker"), ("R2", "gap2_0", "R2 bid, maker fee 0"), ("R2", "gap2_s", "R2 bid, maker fee 0.0175")):
                s = summarize(sub, evs, days, rng, route, fk)
                res[(fam, str(k), lab)] = s
                if s["obs"] == 0: P(f"| {fam} | {k} | {lab} | 0 | | | | | | | | | |"); continue
                P(f"| {fam} | {k} | {lab} | {s['obs']} ({s['events_with_obs']}) | {s['hit']*100:.1f}% vs {s['implied']*100:.1f}% | {s['mean_spread']*100:.0f}c | "
                  f"{s['gap_mean']*100:+.2f}c ({s['gap_lo']*100:+.2f}, {s['gap_hi']*100:+.2f}) | {s['placebo_z']:+.1f} | {s['fill_rate']*100:.0f}% | "
                  f"${s['perday']:,.0f} (${s['perday_lo']:,.0f}, ${s['perday_hi']:,.0f}) | ${s['capital_per_day']:,.0f} | ${s['worst_day']:,.0f} | {'PASS' if s['pass'] else 'FAIL/UNPROVEN'} |")
    P("\nDepth at decision time: UNKNOWN (no historical book; see locked rule). Rebates: none modelled. Daily-P&L correlation with other candidates: UNKNOWN until they exist.")
    return L, res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--series", default=""); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--rps", type=float, default=6.0)
    ap.add_argument("--sha", default="unknown")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    sl = a.series.split(",") if a.series else ["KXAAAGASD"] + [f"KXAAAGASD{s}" for s in CACHED + FRESH]
    now = int(time.time()); run_id = time.strftime("gas-sizing-%Y%m%dT%H%MZ", time.gmtime(now))
    cl = Client(a.rps)
    rows, events, famvol, svols, stats = run(cl, sl, now, a.days, a.out, a.workers)
    stats.update({"api_calls": cl.calls, "api_429": cl.n429, "api_fail": cl.fail, "series_requested": len(sl)})
    L, res = report(rows, events, famvol, svols, stats, a.days, run_id, a.sha)
    open(os.path.join(a.out, f"OUT-{run_id}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"run_id": run_id, "stats": stats, "n_rows": len(rows)}, open(os.path.join(a.out, f"{run_id}.json"), "w"))
    print("DONE", run_id)
