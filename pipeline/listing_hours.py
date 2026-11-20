"""Series screen for gas-like dynamics with LESS obvious certainty at listing (Nick 01:01Z 20 Nov).
Per resolved event: winner token's own prints by hours after listing (event startDate), winner price at +1/+3/+6/+12/+24 h, when it durably crosses 0.95
(last print < 0.95, cross = next print), and the discount pool = size x (1 - price) over winner BUY prints priced <= 0.90 (executed, a floor).
NOTE gamma volumeNum is SHARES (checked: gas market volumeNum 553 = trade shares 553, trade USD 482); every dollar figure here is sum(price x size)."""
import collections, concurrent.futures as cf, datetime as dt, json, math, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import families as F, pit_store as P, screen, jumps
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
MINEV = int(os.environ.get("MINEV", 12)); MINRATE = float(os.environ.get("MINRATE", 0.4))
OFFS = [(0, 1), (1, 3), (3, 6), (6, 12), (12, 24), (24, 10 ** 6)]


def one(e, b):
    ls = screen.parse_ts(e["startDate"]); end = screen.parse_ts(e["endDate"])
    d = screen.get_trades(b["cond"]); rows = d["rows"]; tok = b["tokens"][b["win"]]
    w = sorted((r[0], r[1], r[3], r[4]) for r in rows if r[2] == tok)
    if len(w) < 2: return None
    ts = np.array([x[0] for x in w], float); px = np.array([x[2] for x in w]); sz = np.array([x[3] for x in w]); sd = [x[1] for x in w]
    h = (ts - ls) / 3600
    out = dict(first_print_h=float(h[0]), ev_usd=float((px * sz).sum()), ev_shares=float(sz.sum()))
    for off in (0.25, 1, 3, 6, 12, 24):
        i = np.where(ts <= ls + off * 3600)[0]; out[f"px{off}"] = float(px[i[-1]]) if len(i) else np.nan
    for a, z in OFFS:
        m = (h >= a) & (h < z); out[f"usd_{a}_{z}"] = float((px[m] * sz[m]).sum())
    out["ge89_first_hour"] = bool(((h < 1) & (px >= 0.89)).any()); out["has_first_hour"] = bool((h < 1).any())
    low = np.where(px < 0.95)[0]
    if len(low) == 0: tc = ts[0]; kind = "never_low"
    elif low[-1] == len(px) - 1: tc = np.nan; kind = "not_converged"
    else: tc = ts[low[-1] + 1]; kind = "ok"
    out["kind"] = kind; out["cross_h"] = float((tc - ls) / 3600) if tc == tc else np.nan; out["cross_lead_h"] = float((end - tc) / 3600) if tc == tc else np.nan
    if tc == tc:
        c = dt.datetime.fromtimestamp(tc, ET); out["cross_et_min"] = c.hour * 60 + c.minute
    sel = [i for i in range(len(px)) if sd[i] == "BUY" and px[i] <= 0.90]
    out["pool90"] = float(sum(sz[i] * (1 - px[i]) for i in sel)); out["usd90"] = float(sum(sz[i] * px[i] for i in sel))
    sel2 = [i for i in sel if tc != tc or ts[i] <= tc]; out["pool90_pre"] = float(sum(sz[i] * (1 - px[i]) for i in sel2))
    return out


def main(days=75, nmax=40, workers=12, outdir="out/listing1"):
    events = [e for e in P.load_events("/home/user/pk_cache/events.jsonl") + P.load_events("/home/user/pk_cache/events_deep.jsonl") if not F.excluded_reason(e)]
    by = collections.defaultdict(dict)
    for e in events: by[F.family_key(e)][e["id"]] = e
    now = max(screen.parse_ts(e["endDate"]) for e in events if screen.parse_ts(e["endDate"]) < dt.datetime.now().timestamp() + 1)
    jobs = []; fam_meta = {}
    for fam, es in by.items():
        es = sorted([e for e in es.values() if e.get("startDate") and screen.parse_ts(e["endDate"]) >= now - days * 86400 and screen.parse_ts(e["endDate"]) <= now], key=lambda e: e["endDate"])
        if len(es) < MINEV: continue
        span = max((screen.parse_ts(es[-1]["endDate"]) - screen.parse_ts(es[0]["endDate"])) / 86400, 1.0); rate = len(es) / span
        if rate < MINRATE: continue
        rec = (es[0].get("series") or [{}])[0].get("recurrence")
        fam_meta[fam] = dict(rate=rate, recurrence=rec, n_win=len(es))
        for e in es[-nmax:]:
            b = jumps.pick_market(e)
            if b: jobs.append((fam, e, b))
    print(len(fam_meta), "families", len(jobs), "markets", flush=True)
    def work(j):
        try: return one(j[1], j[2])
        except Exception as ex: return None
    with cf.ThreadPoolExecutor(workers) as ex: res = list(ex.map(work, jobs))
    rows = []
    for (fam, e, b), r in zip(jobs, res):
        if r: rows.append(dict(fam=fam, date=e["endDate"][:10], title=e["title"], **r))
    df = pd.DataFrame(rows); df.to_csv(f"{outdir}/listing_hours_events.csv", index=False); json.dump(fam_meta, open(f"{outdir}/listing_hours_fam.json", "w"))
    print(len(df), "events analysed")


if __name__ == "__main__": main()
