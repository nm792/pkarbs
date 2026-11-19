"""Late-jump-to-winner screen (Nick's criterion 3 as the thing to exploit, not to predict).
For each resolved market, on the WINNING token's own prints:
  T* = last print below 0.95; t_end = first print after T* (the market has converged);
  p_b = last print at or before t_end - 20 min (price just before the final move); J = p_end - p_b;
  t_start = first print in the 20 min before t_end at >= p_b + 0.10 (departure).
  sharp = J >= 0.30 and p_b <= 0.80.
Clock time = UTC minute of t_start; lead = (scheduled end - t_end) in hours (positive = converged before the scheduled end).
Stale pool = sum over winner BUY prints in [t_start, t_end] at price <= 0.90 of size*(1-price): what informed takers earned there."""
import argparse, collections, concurrent.futures as cf, datetime as dt, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import families as F, pit_store as P, screen


def pick_market(e):
    best = None
    for m in e["markets"]:
        b = screen.binary_resolved(m)
        if not b: continue
        lab = b["labels"][b["win"]]
        yesno = set(x.lower() for x in b["labels"]) == {"yes", "no"}
        if yesno and lab.lower() != "yes": continue   # bracket events: the winning bracket's YES
        if best is None or b["vol"] > best["vol"]: best = b
    return best


def analyse(b, rows, end):
    tok = b["tokens"][b["win"]]
    tp = sorted([(r[0], r[1], r[3], r[4]) for r in rows if r[2] == tok])   # ts, side, px, size
    if len(tp) < 4: return None
    ts = np.array([x[0] for x in tp], float); px = np.array([x[2] for x in tp]); sd = [x[1] for x in tp]; sz = np.array([x[3] for x in tp])
    low = np.where(px < 0.95)[0]
    if len(low) == 0: return dict(kind="never_low")
    k = low[-1]
    if k == len(px) - 1: return dict(kind="not_converged")
    t_end = ts[k + 1]; px_end = px[k + 1]
    pre = np.where(ts <= t_end - 1200)[0]
    if len(pre) == 0: return dict(kind="no_pre")
    pb = px[pre[-1]]
    win = np.where((ts > t_end - 1200) & (ts <= t_end))[0]
    dep = [i for i in win if px[i] >= pb + 0.10]
    t_start = ts[dep[0]] if dep else t_end
    J = px_end - pb
    sel = [i for i in range(len(ts)) if t_start <= ts[i] <= t_end and sd[i] == "BUY" and px[i] <= 0.90]
    pool = float(sum(sz[i] * (1 - px[i]) for i in sel)); usd = float(sum(sz[i] * px[i] for i in sel))
    return dict(kind="ok", pb=float(pb), J=float(J), t_start=float(t_start), t_end=float(t_end), dur_min=float((t_end - t_start) / 60),
                lead_h=float((end - t_end) / 3600), pool=pool, usd=usd, sharp=bool(J >= 0.30 and pb <= 0.80))


def circ_mode(minutes, width=30):
    """modal UTC time (30-min circular window) and share of values within +/- width/2... returns (center_min, share)"""
    if not minutes: return None, 0.0
    best = (0, -1)
    for c in range(0, 1440, 5):
        n = sum(min(abs(m - c), 1440 - abs(m - c)) <= width for m in minutes)
        if n > best[1]: best = (c, n)
    return best[0], best[1] / len(minutes)


def run(events_path, out, max_events, workers):
    by = collections.defaultdict(list)
    for e in P.load_events(events_path):
        if F.excluded_reason(e): continue
        by[F.family_key(e)].append(e)
    jobs = []
    for fam, es in by.items():
        if len(es) < 8: continue
        for e in screen.sample_events(es, max_events, 2026):
            b = pick_market(e)
            if b: jobs.append((fam, e, b))
    print(len(by), "families", len(jobs), "markets", flush=True)
    with cf.ThreadPoolExecutor(workers) as ex:
        data = list(ex.map(lambda j: screen.get_trades(j[2]["cond"]), jobs))
    per = collections.defaultdict(list)
    for (fam, e, b), d in zip(jobs, data):
        end = b["end"] or screen.parse_ts(e["endDate"])
        r = analyse(b, d["rows"], end)
        if r: r.update(event=e["id"], title=e["title"][:60], end=end); per[fam].append(r)
    fams = []
    for fam, rs in per.items():
        ok = [r for r in rs if r["kind"] == "ok"]; sharp = [r for r in ok if r["sharp"]]
        if len(rs) < 8: continue
        evs = by[fam]; span = max(1, (max(screen.parse_ts(e["endDate"]) for e in evs) - min(screen.parse_ts(e["endDate"]) for e in evs)) / 86400 + 1)
        mins = [dt.datetime.fromtimestamp(r["t_start"], dt.timezone.utc).hour * 60 + dt.datetime.fromtimestamp(r["t_start"], dt.timezone.utc).minute for r in sharp]
        mode, conc = circ_mode(mins)
        pools = [r["pool"] for r in sharp]
        fams.append(dict(family=fam, n_events=len(rs), events_per_day=len(evs) / span, n_ok=len(ok), n_sharp=len(sharp), sharp_rate=len(sharp) / len(rs),
                         median_J=float(np.median([r["J"] for r in sharp])) if sharp else None, median_pb=float(np.median([r["pb"] for r in sharp])) if sharp else None,
                         median_dur_min=float(np.median([r["dur_min"] for r in sharp])) if sharp else None,
                         median_lead_h=float(np.median([r["lead_h"] for r in sharp])) if sharp else None,
                         modal_utc=(f"{mode // 60:02d}:{mode % 60:02d}" if mode is not None else None), modal_share=conc,
                         median_pool=float(np.median(pools)) if pools else 0.0, mean_pool=float(np.mean(pools)) if pools else 0.0,
                         pool_per_day=float(len(evs) / span * (len(sharp) / len(rs)) * (np.mean(pools) if pools else 0.0)),
                         median_vol=float(np.median([float(e.get("volume") or 0) for e in evs]))))
    os.makedirs(out, exist_ok=True)
    json.dump(dict(families=fams, per_event={k: v for k, v in per.items()}), open(f"{out}/jumps.json", "w"), default=float)
    return fams


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--events", default="/home/user/pk_cache/events_deep.jsonl")
    ap.add_argument("--out", required=True); ap.add_argument("--max-events", type=int, default=120); ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args(); f = run(a.events, a.out, a.max_events, a.workers)
    f.sort(key=lambda x: -x["sharp_rate"])
    for x in f[:40]: print(x["family"], x["n_events"], round(x["sharp_rate"], 2), x["median_J"] and round(x["median_J"], 2), x["modal_utc"], round(x["modal_share"], 2), x["median_lead_h"] and round(x["median_lead_h"], 1), round(x["pool_per_day"], 2))
