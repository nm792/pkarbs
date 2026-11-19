"""Stage 1: screen all Polymarket series on (1) frequency, (2) volume, (3) late moves to the winner,
then run signal IC / walk-forward / BH on the families that pass 1 and 2.

Usage: python3 screen.py --events EVENTS.jsonl --window-days 30 --out OUTDIR [--max-families N --n-events N]
"""
import argparse, concurrent.futures as cf, datetime as dt, gzip, hashlib, json, os, random, statistics, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evalx, families as F, pit_store as P, signals as S

HORIZONS = {"2m": 120, "10m": 600, "1h": 3600, "6h": 21600, "24h": 86400}
CACHE = "/home/user/pk_cache/trades"


def parse_ts(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    try: return dt.datetime.fromisoformat(str(x).replace("Z", "+00:00").replace(" ", "T")).timestamp()
    except Exception: return None


def binary_resolved(m):
    try:
        out = json.loads(m["outcomes"]) if isinstance(m["outcomes"], str) else m["outcomes"]
        op = [float(x) for x in (json.loads(m["outcomePrices"]) if isinstance(m["outcomePrices"], str) else m["outcomePrices"])]
        toks = json.loads(m["clobTokenIds"]) if isinstance(m["clobTokenIds"], str) else m["clobTokenIds"]
    except Exception:
        return None
    if len(out) != 2 or len(op) != 2 or len(toks) != 2 or sorted(op) != [0.0, 1.0]: return None
    return dict(cond=m["conditionId"], tokens=toks, win=op.index(1.0), vol=float(m.get("volumeNum") or 0),
                end=parse_ts(m.get("endDate")), closed=parse_ts(m.get("closedTime")))


def get_trades(cond):
    os.makedirs(CACHE, exist_ok=True)
    p = f"{CACHE}/{cond}.json.gz"
    if os.path.exists(p):
        return json.load(gzip.open(p, "rt"))
    rows, trunc = P.pull_trades(cond)
    json.dump({"rows": rows, "trunc": trunc, "fetched_at": int(time.time())}, gzip.open(p, "wt"))
    return {"rows": rows, "trunc": trunc}


def tapes(mk, rows):
    by = {t: [] for t in mk["tokens"]}
    for ts, side, tok, px, sz, oi in rows:
        if tok in by: by[tok].append((ts, side, px, sz))
    return [S.TokenTape(by[t]) for t in mk["tokens"]]


def late_move(mk, tp):
    """Descriptive (uses hindsight): T* = last print of the WINNING token below 0.95 (own prints only).
    gap(k) = winner's last own-token price before T*-k. Larger gap = winner still far from 1 shortly before the move."""
    w = tp[mk["win"]]
    if not w.ts: return None
    low = [t for t, p in zip(w.ts, w.px) if p < 0.95]
    if not low: return dict(tstar=None)
    tstar = low[-1]
    out = dict(tstar=tstar)
    for k, sec in (("10m", 600), ("1h", 3600)):
        p = w.price_before(tstar - sec)
        out["p_" + k] = p
    return out


def sample_events(evs, n, seed):
    evs = sorted(evs, key=lambda e: parse_ts(e["endDate"]))
    if len(evs) <= n: return evs
    rnd = random.Random(seed); step = len(evs) / n
    return [evs[int(i * step + rnd.random() * step)] for i in range(n)]


def build_family(fam, evs, n_events, seed, workers=8):
    chosen = sample_events(evs, n_events, seed)
    jobs = []
    for e in chosen:
        ms = [binary_resolved(m) for m in e["markets"]]
        ms = sorted([m for m in ms if m], key=lambda m: -m["vol"])[:2]
        for m in ms: jobs.append((e, m))
    with cf.ThreadPoolExecutor(workers) as ex:
        data = list(ex.map(lambda j: get_trades(j[1]["cond"]), jobs))
    lm, rows, ntrunc = [], [], 0
    for (e, m), d in zip(jobs, data):
        if d["trunc"]: ntrunc += 1
        tp = tapes(m, d["rows"])
        r = late_move(m, tp)
        if r and r.get("tstar") is not None: lm.append(r)
        end = m["end"] or parse_ts(e["endDate"])
        for hn, H in HORIZONS.items():
            t = end - H
            if m["closed"] and m["closed"] < t: continue
            for idx in (0, 1):
                s = S.signals_at(tp[idx], t, H)
                if s is None: continue
                f = tp[idx].fill_after(t, max(H // 4, 60))
                if f is None: continue
                px, fts = f
                if px <= 0.01 or px >= 0.99: continue
                ret = (1.0 if idx == m["win"] else 0.0) / px - 1.0
                rows.append(dict(h=hn, event=e["id"], ts=t, day=int(t // 86400), week=int(t // (7 * 86400)),
                                 token=idx, fill=px, ret=ret, edge=(1.0 if idx == m["win"] else 0.0) - px, **s))
    return rows, lm, ntrunc, len(jobs)


def run(args):
    events = P.load_events(args.events)
    ev_by = {}
    for e in events: ev_by.setdefault(F.family_key(e), []).append(e)
    scr = F.screen(events, args.window_days)
    for r in scr:
        r["pass_freq"] = r["events_per_day"] >= 1.0 and r["active_day_share"] >= 0.5
        r["pass_vol"] = r["median_vol"] >= args.min_median_vol
    cand = [r for r in scr if r["pass_freq"] and r["pass_vol"]]
    cand.sort(key=lambda r: -(r["events_per_day"] * r["median_vol"]))
    cand = cand[: args.max_families]
    os.makedirs(args.out, exist_ok=True)
    fam_out, cells = [], []
    for r in cand:
        fam = r["family"]; t0 = time.time()
        rows, lm, ntrunc, nm = build_family(fam, ev_by[fam], args.n_events, args.seed)
        p10 = [x["p_10m"] for x in lm if x.get("p_10m") is not None]; p1h = [x["p_1h"] for x in lm if x.get("p_1h") is not None]
        r.update(n_markets_sampled=nm, n_trunc=ntrunc, n_late=len(lm), n_rows=len(rows),
                 mean_gap_10m=(sum(0.95 - p for p in p10) / len(p10)) if p10 else None,
                 share_winner_below_50_at_10m=(sum(p < 0.5 for p in p10) / len(p10)) if p10 else None,
                 share_winner_below_50_at_1h=(sum(p < 0.5 for p in p1h) / len(p1h)) if p1h else None,
                 seconds=round(time.time() - t0))
        fam_out.append(r); print(fam, r["n_rows"], r["seconds"], flush=True)
        for hn in HORIZONS:
            hr = [x for x in rows if x["h"] == hn]
            if len({x["event"] for x in hr}) < 20: continue
            bucket = "day" if len(hr) / max(1, len({x["day"] for x in hr})) >= 8 else "week"
            for x in hr: x["_b"] = x[bucket]
            m_ret, t_ret, n_ev = evalx.cluster_mean(hr, key="edge")
            for sn in S.SIGNAL_NAMES:
                for x in hr: x["sig"] = x[sn]
                rr = [dict(x, day=x["_b"]) for x in hr]
                ev = evalx.evaluate(rr, ret="edge")
                cells.append(dict(family=fam, h=hn, signal=sn, bucket=bucket, n_events=n_ev, mean_edge=m_ret, edge_t=t_ret, roi=sum(x['ret'] * 0 for x in hr) + (sum(x['edge'] for x in hr) / sum(x['fill'] for x in hr)), **ev))
    # multiple-testing penalty over ALL cells tried
    pv = [c["p_test"] for c in cells]
    keep = evalx.bh_fdr(pv, 0.1)
    for c, k in zip(cells, keep): c["bh_discovery_q10"] = k; c["n_cells_tried"] = len(cells)
    json.dump(dict(families=fam_out, all_screen=scr), open(f"{args.out}/families.json", "w"), indent=1)
    json.dump(cells, open(f"{args.out}/cells.json", "w"), indent=1)
    return scr, fam_out, cells


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True); ap.add_argument("--window-days", type=int, default=30)
    ap.add_argument("--out", required=True); ap.add_argument("--max-families", type=int, default=25)
    ap.add_argument("--n-events", type=int, default=100); ap.add_argument("--min-median-vol", type=float, default=20000)
    ap.add_argument("--seed", type=int, default=2026)
    run(ap.parse_args())
