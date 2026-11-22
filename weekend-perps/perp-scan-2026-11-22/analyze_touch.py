#!/usr/bin/env python3
"""LOCKED run of the weekly-touch vs perp-gap test. Usage: python3 analyze_touch.py RUNDIR   (needs collect_touch.py output). Writes RUNDIR/result_touch.json."""
import datetime, gzip, json, sys
from collections import Counter, defaultdict
from universe import UNDER
from pscanlib import parse_strike
from touchlib import (decision_ts, perp_at, last_close, yes_wins, entry, select, stat, boot_weeks, permutation_p, per_day_floor, gap, FEE_RATE, NY)


def fee_rate(f):
    try:
        f = json.loads(f) if isinstance(f, str) else f
        return float(f["rate"]) if f and "rate" in f else FEE_RATE
    except Exception:
        return FEE_RATE


def build(run):
    ev = json.load(gzip.open(run + "/touch_events.json.gz", "rt"))
    cand = json.load(gzip.open(run + "/touch_candles.json.gz", "rt"))
    closes = json.load(open(run + "/touch_closes.json"))
    ex = Counter(); weeks = {}                       # (tk, monday) -> dict(perp, close, margin, kind, strikes[])
    for e in ev:
        tk, mon = e["tk"], datetime.date.fromisoformat(e["monday"]); kind = UNDER[tk][2]
        if not e.get("found"):
            ex["no_event"] += 1; continue
        if not e.get("trades_complete"):
            ex["trades_incomplete"] += 1
        T = decision_ts(kind, mon)
        perp = perp_at(cand.get("%s|%s" % (tk, mon)), T)
        tdate = datetime.datetime.fromtimestamp(T, NY).date()
        close = last_close(closes.get(tk), tdate)
        if perp is None:
            ex["no_candle"] += 1; continue
        if close is None:
            ex["no_close"] += 1; continue
        strikes = []
        for m in e["markets"]:
            ks = parse_strike(m["q"])
            if not ks:
                ex["strike_unparsed"] += 1; continue
            try:
                outs = json.loads(m["outcomes"]); toks = json.loads(m["tokens"])
                yes_tok = toks[[o.lower() for o in outs].index("yes")]
            except Exception:
                ex["tokens_unreadable"] += 1; continue
            w = yes_wins(m["prices"], m["outcomes"])
            if w is None:
                ex["unresolved"] += 1; continue
            en, why = entry([t for t in e["trades"] if t["c"] == m["cid"]], yes_tok, T)
            if en is None:
                ex[why] += 1; continue
            strikes.append(dict(kind=ks[0], strike=ks[1], price=en["price"], usd=en["usd"], win=w, rate=fee_rate(m.get("fee")), n=en["n"], tk=tk, monday=e["monday"]))
        weeks[(tk, e["monday"])] = dict(perp=perp, close=close, margin=UNDER[tk][3], strikes=strikes, group=("GAS/METALS" if kind in ("METALS", "OIL") else "STOCK"))
    return weeks, ex


def evaluate(weeks, label, n_mondays):
    sel = {k: select(v["strikes"], v["perp"], v["close"], v["margin"]) for k, v in weeks.items()}
    st = stat(sel)
    out = dict(label=label)
    if st is None:
        out.update(n=0, verdict="NO CANDIDATE WITH A PRINT"); return out
    mon = defaultdict(list)
    for (tk, w), v in sel.items(): mon[w].extend(v)
    ci = boot_weeks(mon)
    by_tk = defaultdict(list)
    for (tk, w), v in weeks.items():
        by_tk[tk].append((w, v["perp"], v["close"], v["margin"], v["strikes"]))
    p = permutation_p(by_tk, st["mean_gap"])
    floor = per_day_floor(sel, n_mondays)
    ok = st["n"] >= 60 and st["weeks"] >= 12 and ci[0] > 0 and p is not None and p <= 0.05
    verdict = "PASS-eligible (FLOOR)" if ok else ("UNPROVEN (count)" if (ci[0] > 0 and st["mean_gap"] > 0) else "FAIL (FLOOR)")
    out.update(n=st["n"], mondays=st["weeks"], mean_gap=st["mean_gap"], win=st["win"], price=st["price"], capped_usd=st["usd"], ci=ci, placebo_p=p, floor_usd_per_day=floor, pct_of_200=100 * floor / 200, verdict=verdict)
    out["by_tk"] = {tk: sum(len(sel[(t, w)]) for (t, w) in sel if t == tk) for tk in by_tk}
    return out


def main(run):
    weeks, ex = build(run)
    n_mondays = len({w for (_, w) in weeks})
    print("excluded/counted:", dict(ex), "| (tk,week) cells with perp and close:", len(weeks), "| Mondays:", n_mondays)
    n_strikes = sum(len(v["strikes"]) for v in weeks.values())
    print("strikes with a usable pre-T YES print:", n_strikes)
    res = [evaluate(weeks, "ALL", n_mondays)]
    for g in ("STOCK", "GAS/METALS"):
        res.append(evaluate({k: v for k, v in weeks.items() if v["group"] == g}, g, n_mondays))
    for r in res:
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}))
    json.dump(dict(excluded=dict(ex), cells=len(weeks), mondays=n_mondays, strikes_with_print=n_strikes, results=res), open(run + "/result_touch.json", "w"), default=str)


if __name__ == "__main__":
    main(sys.argv[1])
