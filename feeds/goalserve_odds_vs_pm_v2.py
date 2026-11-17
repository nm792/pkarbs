#!/usr/bin/env python3
"""Goalserve esports in-play odds vs Polymarket price, locked rerun v2 (non-onset, time-aligned). Read-only. Pre-registration: feeds/PREREG-goalserve-odds-vs-pm-v2-2026-11-18.md.
Why v2: the v1 run (agent/status/goalserve-odds-vs-pm-result-2026-11-17-shift*.json, audit reviews/AUDIT-goalserve-odds-vs-pm-result-2026-11-17.md) returned 'unknown' everywhere (30-match placebo gate unreachable, placebo not like-for-like, planted lead not recovered, 54% of rows suspended so reopen prices read as late events).
Input A: hour files esports_<hour>.jsonl.gz of {"recv_ns","body"} (live/goalserve/capture.py). Input B: --pm DIR (repeatable) with markets.jsonl(.gz) and books.jsonl(.gz) of the PM recorder (live/thesports/capture.py; row time = `ms`, rows only on change).
Rules (locked before any new data is read):
 V1 event = a move of the vig-removed home probability >= 0.02 between TWO CONSECUTIVE stored payloads in which the market is valid and open in both (market and both participants not suspended, 2 participants, value_eu > 1). Any payload in which the (event, market) is
    missing, suspended or invalid CLEARS the baseline, so a reopen price is never an event (v1 fault). Markets: exactly the v1 names ('Home/Away' = Match Winner, 'Home/Away (map N)' = Map N Winner); all others excluded and counted. Cells = league prefix (cs2, dota2, ...) x kind.
 V2 per (match, kind) at most CAP=40 events, kept by seeded random choice; the number dropped is reported.
 V3 PM side: rising team's outcome token, own book (never the other token). mid(x) = last book mid at or before x. For event time t: R = (mid(t+60) - mid(t)) - (mid(t-5) - mid(t-60)). Needs a mid at t-60, and at least one book row of either market token within +-300 s of t (recorder alive); else dropped and counted.
    Positive R beyond placebo = PM moved after the odds did. A PM move before the odds (PM first) lowers R.
 V4 placebo = SAME event times, 10 draws per event, token random of the two, sign random (+-1), R computed the same way (direction shuffled, like cs2model/lead3.py). d = R_real - mean(R_placebo draws).
 V5 cell statistic = mean over matches of the per-match mean d (matches equal weight). CI = match-clustered bootstrap (2000, seed) 95%.
 V6 bar: >= 12 matches and >= 60 usable events in the cell; mean d >= 0.005 (0.5c) and CI lower bound > 0 and (share of events with R_real > mean placebo R) >= 55%. Else, with enough data, 'no lead detected'. If CI upper bound < 0: 'PM moved first (price ahead of the odds)'.
 V7 power check on the REAL series, same run (replaces v1's time-shift plant, which cannot move a fixed-window statistic): a planted edge of PLANT_C = 0.01 (1c, injected at t+10 s on the rising token, which adds exactly +0.01 to every R_real) is added on top of this cell's own noise,
    d_plant = d - (cell mean d) + 0.01. The plant is DETECTED if the V6 bar is met on d_plant (CI lower > 0, mean >= 0.005, share >= 55%). If not detected the cell verdict is capped at 'unknown (underpowered: a 1c edge would not be detected)'. min_detectable_effect = cell mean d - CI lower bound is reported.
 V8 seed 20261118 (--seed only for the self test). Every verdict is UNCHECKED until the rule-to-code table is signed by another thread and an independent audit is done. Bookmaker is not identified (bm empty; vendor docs say bet365): say so with every result.
Usage: python3 -I feeds/goalserve_odds_vs_pm_v2.py --files '<glob of esports_*.jsonl.gz>' --pm DIR [--pm DIR] --clock-note 'text' --out result.json
Self test: python3 -I feeds/test_goalserve_odds_vs_pm_v2.py
"""
import argparse, bisect, collections, glob, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import norm, find, load_pm, mk_index
from goalserve_odds_vs_pm import counted_lines, market_kind, num, med

THR, SEED, CAP, NPLC = 0.02, 20261118, 40, 10
PLANT_C = 0.01
MIN_MATCHES, MIN_EVENTS, MIN_EFFECT, MIN_SHARE = 12, 60, 0.005, 55.0
OPEN = (0, "0", False, None)


def open_events(files):
    """-> events [(eid, kind, t_s, rising_team_norm, home, away, game)], audit counters. Baseline cleared whenever the market is not valid+open in a payload."""
    A = collections.Counter()
    seen, used, excl, bms, prefixes = (collections.Counter() for _ in range(5))
    base, ev = {}, []
    for p in sorted(files):
        for r in counted_lines(p, A, "goalserve_rows"):
            body, t = r.get("body"), r.get("recv_ns")
            if not isinstance(body, str) or t is None:
                A["rows_unusable"] += 1
                continue
            try:
                d = json.loads(body)
            except Exception:
                A["rows_bad_json"] += 1
                continue
            A["rows"] += 1
            bms[repr(d.get("bm"))] += 1
            valid = set()
            for eid, e in (d.get("events") or {}).items():
                if not isinstance(e, dict):
                    continue
                lg = str((e.get("info") or {}).get("league") or "")
                game = norm(lg.split(" - ", 1)[0]) if " - " in lg else "unparsed"
                prefixes[game] += 1
                ti = e.get("team_info") or {}
                h, a = norm((ti.get("home") or {}).get("name")), norm((ti.get("away") or {}).get("name"))
                for mid, m in (e.get("odds") or {}).items():
                    if not isinstance(m, dict):
                        continue
                    name = m.get("name") or "?"
                    seen[name] += 1
                    kind = market_kind(name)
                    if not kind:
                        excl[name] += 1
                        continue
                    used[name] += 1
                    parts = [x for x in (m.get("participants") or {}).values() if isinstance(x, dict)]
                    if len(parts) != 2:
                        A["skip_not_2_participants"] += 1
                        continue
                    if m.get("suspend") not in OPEN or any(x.get("suspend") not in OPEN for x in parts):
                        A["skip_suspended"] += 1
                        continue
                    o = [num(x.get("value_eu")) for x in parts]
                    if None in o:
                        A["skip_bad_odds"] += 1
                        continue
                    side = []
                    for x in parts:
                        n = norm(x.get("name"))
                        side.append("h" if n == h and h else "a" if n == a and a else "h" if n in ("1", "home") else "a" if n in ("2", "away") else None)
                    if sorted(side, key=str) != ["a", "h"] or not h or not a:
                        A["excluded_participant_mapping"] += 1
                        continue
                    ph = (1 / o[side.index("h")]) / (1 / o[0] + 1 / o[1])
                    k = (eid, str(mid))
                    valid.add(k)
                    if k in base and abs(ph - base[k]) >= THR:
                        ev.append((eid, kind, t / 1e9, h if ph > base[k] else a, h, a, game))
                        A["events"] += 1
                    base[k] = ph
            for k in [k for k in base if k not in valid]:
                del base[k]
                A["baseline_cleared_not_valid_open"] += 1
    return ev, dict(counters=dict(A), bm_values=dict(bms), market_names_used=dict(used), market_names_excluded=dict(excl.most_common(60)), league_prefixes_seen=dict(prefixes.most_common(40)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--clock-note", required=True)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--plant-c", type=float, default=PLANT_C)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    ev, audit = open_events(files)
    drops = collections.Counter()
    idx = mk_index(load_pm(a.pm))
    sel, ml = {}, {}
    for (eid, kind, t, rise, h, a_, game) in ev:
        key = (eid, kind)
        if key in ml:
            ml[key]["n_events"] += 1
            continue
        c = [x for x in (idx.get(frozenset((h, a_))) or []) if x["kind"] == kind]
        ml[key] = dict(eid=eid, game=game, kind=kind, home=h, away=a_, n_pm_candidates=len(c), n_events=1)
        if len(c) == 1:
            sel[key] = c[0]
        else:
            ml[key]["excluded"] = "no PM market with these exact names and kind" if not c else "more than one PM market (rematch), excluded"
    for r in ml.values():
        if "excluded" in r:
            drops["events_no_pm_market" if r["n_pm_candidates"] == 0 else "events_ambiguous_rematch_excluded"] += r["n_events"]
    need = {tk for m in sel.values() for tk in m["tokens"]}
    series = collections.defaultdict(list)
    for d in a.pm:
        p = find(d, "books")
        if not p:
            continue
        for r in counted_lines(p, drops, "pm_books"):
            tk, tms = r.get("tk") or r.get("asset"), r.get("recv_ms") if r.get("recv_ms") is not None else r.get("ms")
            if tk not in need or tms is None:
                continue
            b = [float(x["price"]) for x in r.get("bids") or []]
            s = [float(x["price"]) for x in r.get("asks") or []]
            if not b or not s:
                drops["book_rows_one_sided"] += 1
                continue
            series[tk].append((tms / 1000.0, (max(b) + min(s)) / 2.0))
    ts = {}
    for tk in series:
        series[tk].sort()
        ts[tk] = [x[0] for x in series[tk]]

    def mid_at(tk, x):
        i = bisect.bisect_right(ts.get(tk, []), x) - 1
        return series[tk][i][1] if i >= 0 else None

    def alive(toks, t):
        for tk in toks:
            L = ts.get(tk, [])
            i = bisect.bisect_left(L, t - 300)
            if i < len(L) and L[i] <= t + 300:
                return True
        return False

    def R(tk, t):
        m = [mid_at(tk, t + dt) for dt in (60, 0, -5, -60)]
        return None if None in m else (m[0] - m[1]) - (m[2] - m[3])

    per = collections.defaultdict(list)   # (game, kind, match) -> list of events
    for (eid, kind, t, rise, h, a_, game) in ev:
        per[(game, kind, eid)].append((t, rise))
    cells = collections.defaultdict(lambda: collections.defaultdict(list))   # cell -> match -> [(d, share_flag, plant_gain)]
    for (game, kind, eid), L in sorted(per.items()):
        m = sel.get((eid, kind))
        if not m:
            continue
        if len(L) > CAP:
            drops["events_dropped_by_match_cap"] += len(L) - CAP
            L = sorted(rnd.sample(L, CAP))
        outs = [norm(o) for o in m["outcomes"]]
        for (t, rise) in L:
            if rise not in outs:
                drops["events_rising_team_not_a_pm_outcome"] += 1
                continue
            tk = m["tokens"][outs.index(rise)]
            if not alive(m["tokens"], t):
                drops["events_pm_recorder_silent_pm300s"] += 1
                continue
            r0 = R(tk, t)
            if r0 is None:
                drops["events_no_pm_baseline_at_t_minus_60"] += 1
                continue
            pl = []
            for _ in range(NPLC):
                x = R(rnd.choice(m["tokens"]), t)
                if x is not None:
                    pl.append(rnd.choice((-1, 1)) * x)
            if not pl:
                drops["events_no_placebo"] += 1
                continue
            mp = sum(pl) / len(pl)
            cells["%s|%s" % (game, kind)][eid].append((r0 - mp, 1.0 if r0 > mp else 0.0, None, r0, mp))

    def mean(x):
        return sum(x) / len(x) if x else None

    def boot(by, pick, n=2000):
        ms = sorted(by)
        pm_ = {k: mean([pick(e) for e in by[k] if pick(e) is not None]) for k in ms}
        ms = [k for k in ms if pm_[k] is not None]
        if len(ms) < 2:
            return None
        out = sorted(mean([pm_[rnd.choice(ms)] for _ in ms]) for _ in range(n))
        return [out[int(.025 * n)], out[int(.975 * n)]]

    res = dict(seed=a.seed, plant_c=a.plant_c, clock_note=a.clock_note, files=len(files), goalserve_events_total=len(ev), drops=dict(drops), audit=audit, cells={},
               match_list=sorted(ml.values(), key=lambda r: (str(r["eid"]), r["kind"])))
    for cell, by in sorted(cells.items()):
        evs = [e for k in by for e in by[k]]
        n_m, n_e = len(by), len(evs)
        md = mean([mean([e[0] for e in by[k]]) for k in by])
        ci = boot(by, lambda e: e[0])
        share = 100.0 * sum(e[1] for e in evs) / n_e
        ex = [e[0] - md + a.plant_c for e in evs]
        plant_ok = bool(ci and ci[0] - md + a.plant_c > 0 and a.plant_c >= MIN_EFFECT and 100.0 * sum(1 for x in ex if x > 0) / n_e >= MIN_SHARE)
        c = dict(n_matches=n_m, n_events=n_e, mean_d_per_match=md, ci95_match_boot=ci, share_events_real_gt_placebo_pct=share,
                 mean_R_real=mean([e[3] for e in evs]), mean_R_placebo=mean([e[4] for e in evs]),
                 plant_c=a.plant_c, plant_detected=plant_ok, min_detectable_effect=(md - ci[0]) if ci else None,
                 events_per_match=sorted((len(v) for v in by.values()), reverse=True)[:10])
        if n_m < MIN_MATCHES or n_e < MIN_EVENTS:
            c["verdict"] = "unknown (%d matches, %d events; needs >= %d and >= %d)" % (n_m, n_e, MIN_MATCHES, MIN_EVENTS)
        elif not plant_ok:
            c["verdict"] = "unknown (underpowered: a %.0fc edge would not be detected)" % (100 * a.plant_c)
        elif ci and ci[0] > 0 and md >= MIN_EFFECT and share >= MIN_SHARE:
            c["verdict"] = "meets bar (needs audit)"
        elif ci and ci[1] < 0:
            c["verdict"] = "PM moved first (needs audit)"
        else:
            c["verdict"] = "no lead detected (needs audit)"
        res["cells"][cell] = c
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "match_list"}, indent=1))
    print("match_list rows:", len(res["match_list"]))


if __name__ == "__main__":
    main()
