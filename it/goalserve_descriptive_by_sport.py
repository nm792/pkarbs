#!/usr/bin/env python3
"""EXPLORATORY / INTERIM descriptive table, NOT the signed test and NOT a result (Goalserve thread, 20 Nov 2026).

Per sport: Goalserve events (a >=2c move of the normalised home win probability = v2's own event, imported unchanged from the
hash-pinned feeds/goalserve_odds_vs_pm_v2.py), then for each event on the RISING team's own Polymarket token (never NO = 1 - YES):
  pm_before = mid(t) - mid(t-60)   pm_after = mid(t+60) - mid(t)   net = pm_after - pm_before   (cents; same windows as v2, no 5 s guard)
  ask depth at t = shares resting at the best ask of that token's last book row at or before t, and within +2c of it (and USD).
Also a placebo (random token, random sign, 10 draws, same windows) so a net is not read in isolation.
net is NOT a lead in seconds: say 'odds moved before the price within 60 s' or 'did not'. It reads no hour file twice, writes only --out.
Never reports a pass. Tennis: open-market moves only; a tennis 'no pass' is NOT 'Goalserve has no tennis lead'.
Hockey/basketball: if the PM recorder folder holds no book for those markets the table says so (events_no_pm_market), it does not guess.
Usage: FEEDS_DIR=<exported feeds dir> python3 -I goalserve_descriptive_by_sport.py --sport esports|tennis|hockey_nhl|basketball \
   --files 'GLOB' [--files ...] --poll-log 'GLOB' --pm <dir with markets.jsonl and books.jsonl> --out result.json [--t-from EPOCH --t-to EPOCH]
"""
import argparse, bisect, collections, glob, json, os, random, statistics, sys

FEEDS = os.environ.get("FEEDS_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feeds")
sys.path.insert(0, FEEDS)
import goalserve_odds_vs_pm_v2 as v2
from ps_lead_test import norm, find, load_pm, mk_index
from goalserve_odds_vs_pm import counted_lines

SEED, NPLC, NEAR = 20261120, 10, 0.02


def depth(asks, near=NEAR):
    """-> (best_ask, shares at best, shares within +near of best, usd within +near). Asks need not be sorted."""
    a = sorted((float(x["price"]), float(x.get("size") or 0)) for x in asks or [])
    if not a:
        return None
    b = a[0][0]
    at = sum(s for p, s in a if abs(p - b) < 1e-9)
    nr = [(p, s) for p, s in a if p <= b + near + 1e-9]
    return b, at, sum(s for p, s in nr), sum(p * s for p, s in nr)


def build_series(pm_dirs, need, drops):
    series = collections.defaultdict(list)
    for d in pm_dirs:
        p = find(d, "books")
        if not p:
            continue
        for r in counted_lines(p, drops, "pm_books"):
            if (r.get("tk") or r.get("asset")) not in need:
                continue
            pr = v2.parse_book_row(r, drops)
            if pr:
                series[pr[0]].append((pr[1], pr[2], pr[3], depth(r.get("asks"))))
    for tk in series:
        series[tk].sort(key=lambda x: x[0])
    return series


def run(a):
    sport = a.sport
    v2.SPORT = sport                      # poll-log key and tennis kind rule; no other v2 global is touched
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    polls = v2.load_polls(a.poll_log, collections.Counter())
    if not polls:
        raise SystemExit("no polls read from --poll-log (key %r)" % sport)
    t_from = a.t_from if a.t_from is not None else polls[0]
    t_to = a.t_to if a.t_to is not None else polls[-1] + 1
    ev, audit = v2.open_events(files, polls, t_from, t_to)
    drops = collections.Counter()
    idx = mk_index(load_pm(a.pm))
    sel, ml = {}, {}
    for (eid, kind, t, rise, h, a_, game) in ev:
        key = (eid, kind)
        if key not in ml:
            c = [x for x in (idx.get(frozenset((h, a_))) or []) if x["kind"] == kind]
            ml[key] = len(c)
            if len(c) == 1:
                sel[key] = c[0]
    need = {tk for m in sel.values() for tk in m["tokens"]}
    series = build_series(a.pm, need, drops)
    ts = {tk: [x[0] for x in series[tk]] for tk in series}

    def row_at(tk, x):
        i = bisect.bisect_right(ts.get(tk, []), x) - 1
        return series[tk][i] if i >= 0 else None

    def mid(tk, x):
        r = row_at(tk, x)
        return None if r is None else (r[1] + r[2]) / 2.0

    def R(tk, t):
        m = [mid(tk, t + dt) for dt in (60, 0, -60)]
        if None in m:
            return None
        return m[0] - m[1], m[1] - m[2]          # after, before

    def alive(toks, t):
        for tk in toks:
            L = ts.get(tk, [])
            i = bisect.bisect_left(L, t - 300)
            if i < len(L) and L[i] <= t + 300:
                return True
        return False

    rows = []
    for (eid, kind, t, rise, h, a_, game) in ev:
        m = sel.get((eid, kind))
        if not m:
            drops["events_no_pm_market_or_ambiguous"] += 1
            continue
        outs = [norm(o) for o in m["outcomes"]]
        if rise not in outs:
            drops["events_rising_team_not_a_pm_outcome"] += 1
            continue
        tk = dict(zip(outs, m["tokens"]))[rise]
        if not alive(m["tokens"], t):
            drops["events_pm_recorder_silent_pm300s"] += 1
            continue
        r0 = R(tk, t)
        if r0 is None:
            drops["events_no_own_book_mid_at_t_minus_60"] += 1
            continue
        prng = random.Random("%s|%s|%r" % (SEED, eid, t))
        pl = []
        for _ in range(NPLC):
            ptk, sg = prng.choice(m["tokens"]), prng.choice((-1, 1))
            x = R(ptk, t)
            if x is not None:
                pl.append(sg * (x[0] - x[1]))
        br = row_at(tk, t)
        dp = br[3] if br else None
        rows.append(dict(match=eid, kind=kind, game=game, t=t, after=r0[0], before=r0[1], net=r0[0] - r0[1],
                         placebo_net=(sum(pl) / len(pl)) if pl else None, best_ask=dp[0] if dp else None,
                         ask_shares_at_best=dp[1] if dp else None, ask_shares_within_2c=dp[2] if dp else None,
                         ask_usd_within_2c=dp[3] if dp else None))
    cells = {}
    byc = collections.defaultdict(list)
    for r in rows:
        byc["%s|%s" % (r["game"], r["kind"])].append(r)
    gs_events = collections.Counter("%s|%s" % (e[6], e[1]) for e in ev)

    def med(x):
        x = [y for y in x if y is not None]
        return statistics.median(x) if x else None

    def avg(x):
        x = [y for y in x if y is not None]
        return sum(x) / len(x) if x else None

    for c, R_ in sorted(byc.items()):
        pm = collections.defaultdict(list)
        for r in R_:
            pm[r["match"]].append(r["net"])
        pn = [r["placebo_net"] for r in R_ if r["placebo_net"] is not None]
        cells[c] = dict(goalserve_events_total=gs_events[c], events_usable=len(R_), matches_usable=len(pm),
                        mean_pm_before_c=100 * avg(r["before"] for r in R_), mean_pm_after_c=100 * avg(r["after"] for r in R_),
                        mean_net_c=100 * avg(r["net"] for r in R_), mean_net_per_match_c=100 * avg(avg(v) for v in pm.values()),
                        placebo_mean_net_c=100 * avg(pn) if pn else None,
                        share_net_gt_placebo_pct=100.0 * sum(1 for r in R_ if r["placebo_net"] is not None and r["net"] > r["placebo_net"]) / max(1, len(pn)),
                        median_best_ask=med(r["best_ask"] for r in R_), median_ask_shares_at_best=med(r["ask_shares_at_best"] for r in R_),
                        median_ask_shares_within_2c=med(r["ask_shares_within_2c"] for r in R_), median_ask_usd_within_2c=med(r["ask_usd_within_2c"] for r in R_),
                        share_events_ask_shares_within_2c_ge_100_pct=100.0 * sum(1 for r in R_ if (r["ask_shares_within_2c"] or 0) >= 100) / len(R_))
    for c, n in gs_events.items():
        cells.setdefault(c, dict(goalserve_events_total=n, events_usable=0, matches_usable=0))
    return dict(label="EXPLORATORY/INTERIM descriptive table; NOT the signed v2 test, no verdict, no pass; UNCHECKED until an independent checker signs",
                sport=sport, files=len(files), t_from=t_from, t_to=t_to, goalserve_events_total=len(ev),
                events_with_unique_pm_market=sum(1 for r in ml.values() if r == 1), match_markets_seen=len(ml),
                unmatched_markets=sum(1 for r in ml.values() if r == 0), ambiguous_markets=sum(1 for r in ml.values() if r > 1),
                drops=dict(drops), audit=audit, cells=cells, rows=rows[:200],
                tennis_note="open-market moves only; a tennis 'no pass' is NOT 'Goalserve has no tennis lead'" if sport == "tennis" else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sport", required=True, choices=("esports", "tennis", "hockey_nhl", "basketball"))
    ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--poll-log", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--t-from", type=float)
    ap.add_argument("--t-to", type=float)
    a = ap.parse_args()
    res = run(a)
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    print(res["label"])
    for k in ("sport", "files", "goalserve_events_total", "match_markets_seen", "unmatched_markets", "ambiguous_markets", "drops"):
        print(k, json.dumps(res[k]))
    for c, v in res["cells"].items():
        print("CELL", c, json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()}))
    if res["tennis_note"]:
        print("WORDING:", res["tennis_note"])


if __name__ == "__main__":
    main()
