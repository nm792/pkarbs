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
 V9 (checker signoff 17 Nov 23:00Z) capture outage: --poll-log is REQUIRED; a payload whose preceding poll is more than 10 s earlier (or has none) CLEARS all baselines (counted: baseline_cleared_poll_gap_gt_10s), so the first price after an outage is never an event.
 V10 PRIMARY cells: cs2|Match Winner and dota2|Match Winner (alpha not corrected, 2 cells). All other cells are informational, printed with the prefix '(informational)', and cannot be called a pass. The real run omits --plant-c and --seed (the audit checks plant_c 0.01 and seed 20261118 in the JSON). Hand check: first20_events_biggest_cell is printed.
 V12 (sequential, 18 Nov 01:40Z, Nick: check daily) Only payloads from 2026-11-18T00:00Z (T_START) count. Look number K = number of COMPLETE UTC days between T_START and the end of the last hour file given (read from the file names); data of an incomplete day is ignored. K is never a command-line option; K must be 1..20.
    A look uses ALL complete days so far. Boundary z_K = C_OBF / sqrt(K/LOOKS) with C_OBF = 2.39 (simulated: P(any of 20 looks has Z >= C/sqrt(t)) = 0.0122 under the null, one-sided, per primary cell, so <= 0.025 over the 2 primary cells). Statistic z = cell mean d / SE, SE = standard deviation of the match-clustered bootstrap (5000 draws) of the cell mean.
    'meets bar' needs z >= z_K plus the V6 conditions (12 matches, 60 events, mean d >= 0.005, share >= 55%); 'PM moved first' needs z <= -z_K; the V7 power check becomes z_K * SE < PLANT_C (a 1c edge would pass this look). Early looks therefore pass only on a very large effect. Looks 1..20 are on 19 Nov..8 Dec; no look after 20; a pass at any look is a pass, later looks never overturn it but the audit reads it.
    Daily output for every cell: matches_by_day (matches with at least one usable event that day) and the cumulative count.
 V8 seed 20261118 (--seed only for the self test). Every verdict is UNCHECKED until the rule-to-code table is signed by another thread and an independent audit is done. Bookmaker is not identified (bm empty; vendor docs say bet365): say so with every result.
Usage: python3 -I feeds/goalserve_odds_vs_pm_v2.py --files '<glob of esports_*.jsonl.gz>' --pm DIR [--pm DIR] --poll-log '<glob of goalserve_*.jsonl>' --clock-note 'text' --out result.json
Self test: python3 -I feeds/test_goalserve_odds_vs_pm_v2.py
"""
import argparse, bisect, calendar, collections, glob, json, math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import norm, find, load_pm, mk_index
from goalserve_odds_vs_pm import counted_lines, market_kind, num, med, poll_gaps

THR, SEED, CAP, NPLC = 0.02, 20261118, 40, 10
PLANT_C = 0.01
MIN_MATCHES, MIN_EVENTS, MIN_EFFECT, MIN_SHARE = 12, 60, 0.005, 55.0
OPEN = (0, "0", False, None)
OUTAGE_S = 10.0
T_START = 1794960000.0        # 2026-11-18T00:00:00Z: only data from here on is used (earlier data is already seen)
LOOKS, C_OBF = 20, 2.39       # sequential rule V12: one look per complete UTC day, 20 looks; O'Brien-Fleming boundary z_k = C_OBF / sqrt(k/LOOKS)
PRIMARY = ("cs2|Match Winner", "dota2|Match Winner")


def load_polls(globs, cnt):
    ts = []
    for g in globs:
        for p in sorted(glob.glob(g)):
            for r in counted_lines(p, cnt, "poll_log"):
                e = r.get("esports") or {}
                if e.get("recv_ns") and "err" not in e:
                    ts.append(e["recv_ns"] / 1e9)
    return sorted(ts)


def open_events(files, polls, t_lo, t_hi):
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
            if not (t_lo <= t / 1e9 < t_hi):
                A["payloads_outside_look_window"] += 1
                continue
            A["rows"] += 1
            bms[repr(d.get("bm"))] += 1
            i = bisect.bisect_left(polls, t / 1e9) - 1      # last poll strictly before this payload
            if i < 0 or t / 1e9 - polls[i] > OUTAGE_S:
                A["baseline_cleared_poll_gap_gt_10s"] += len(base)
                A["payloads_after_poll_gap_gt_10s"] += 1
                base.clear()
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
    ap.add_argument("--poll-log", action="append", required=True, help="goalserve_<date>.jsonl poll logs (capture.py): used to detect capture outages (> 10 s between polls)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--plant-c", type=float, default=PLANT_C)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    drops = collections.Counter()
    polls = load_polls(a.poll_log, drops)
    if not polls:
        raise SystemExit("no polls read from --poll-log")
    hrs = []
    for f in files:
        m = re.search(r"esports_(\d{10})", os.path.basename(f))
        if not m:
            raise SystemExit("cannot read the hour from file name %s" % f)
        hrs.append(calendar.timegm(__import__("time").strptime(m.group(1), "%Y%m%d%H")) + 3600.0)
    K = int((max(hrs) - T_START) // 86400)
    if not 1 <= K <= LOOKS:
        raise SystemExit("look K=%d is outside 1..%d (no complete UTC day since 2026-11-18 or past the last look)" % (K, LOOKS))
    t_hi = T_START + K * 86400.0
    zb = C_OBF / math.sqrt(K / LOOKS)
    ev, audit = open_events(files, polls, T_START, t_hi)
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
            if tk not in need:
                continue
            if tms is None:
                drops["book_rows_no_time"] += 1
                continue
            drops["pm_book_rows_time_from_recv_ms" if r.get("recv_ms") is not None else "pm_book_rows_time_from_ms"] += 1
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
            if r0 == mp:
                drops["events_tie_d_zero"] += 1
            cells["%s|%s" % (game, kind)][eid].append((r0 - mp, 1.0 if r0 > mp else 0.0, None, r0, mp, t, eid, rise, tk))

    def mean(x):
        return sum(x) / len(x) if x else None

    def boot(by, pick, n=5000):
        ms = sorted(by)
        pm_ = {k: mean([pick(e) for e in by[k] if pick(e) is not None]) for k in ms}
        ms = [k for k in ms if pm_[k] is not None]
        if len(ms) < 2:
            return None, None
        out = sorted(mean([pm_[rnd.choice(ms)] for _ in ms]) for _ in range(n))
        mu = sum(out) / n
        return [out[int(.025 * n)], out[int(.975 * n)]], (sum((x - mu) ** 2 for x in out) / (n - 1)) ** 0.5

    res = dict(look=K, looks_total=LOOKS, boundary_z=zb, c_obf=C_OBF, data_from_utc=T_START, data_through_utc=t_hi, seed=a.seed, plant_c=a.plant_c, clock_note=a.clock_note, files=len(files), goalserve_events_total=len(ev), drops=dict(drops), audit=audit, cells={},
               poll_interval_measured=poll_gaps(a.poll_log), primary_cells=list(PRIMARY),
               wording="Only primary cells can be called a pass. Say 'odds moved before the price within the 60 s window' or 'did not'; never 'lead of N seconds' (windows cannot resolve under about 5 s). Bookmaker not identified (bm empty; vendor docs say bet365). d is volatility-matched (sign-symmetric placebo), not momentum-matched.",
               match_list=sorted(ml.values(), key=lambda r: (str(r["eid"]), r["kind"])))
    big = (0, None, [])
    for cell, by in sorted(cells.items()):
        evs = [e for k in by for e in by[k]]
        n_m, n_e = len(by), len(evs)
        md = mean([mean([e[0] for e in by[k]]) for k in by])
        ci, se = boot(by, lambda e: e[0])
        share = 100.0 * sum(e[1] for e in evs) / n_e
        zstat = (md / se) if se else None
        ex = [e[0] - md + a.plant_c for e in evs]
        plant_ok = bool(se and zb * se < a.plant_c and a.plant_c >= MIN_EFFECT and 100.0 * sum(1 for x in ex if x > 0) / n_e >= MIN_SHARE)
        days = collections.defaultdict(set)
        for m_, L_ in by.items():
            for e in L_:
                days[int((e[5] - T_START) // 86400) + 1].add(m_)
        seen_m, cum = set(), {}
        for dd in sorted(days):
            seen_m |= days[dd]
            cum[dd] = len(seen_m)
        c = dict(role="primary" if cell in PRIMARY else "informational (cannot be called a pass)", n_matches=n_m, n_events=n_e, mean_d_per_match=md, se_match_boot=se, z=zstat, boundary_z=zb,
                 ci95_match_boot_descriptive=ci, share_events_real_gt_placebo_pct=share,
                 mean_R_real=mean([e[3] for e in evs]), mean_R_placebo=mean([e[4] for e in evs]),
                 plant_c=a.plant_c, plant_detected=plant_ok, min_detectable_effect_at_this_look=(zb * se) if se else None,
                 matches_by_day={str(k_): len(v_) for k_, v_ in sorted(days.items())}, matches_cumulative_by_day={str(k_): v_ for k_, v_ in cum.items()},
                 events_per_match=sorted((len(v) for v in by.values()), reverse=True)[:10])
        if n_m < MIN_MATCHES or n_e < MIN_EVENTS:
            c["verdict"] = "unknown (%d matches, %d events; needs >= %d and >= %d)" % (n_m, n_e, MIN_MATCHES, MIN_EVENTS)
        elif not plant_ok:
            c["verdict"] = "unknown (underpowered at look %d: a %.0fc edge would not pass the boundary)" % (K, 100 * a.plant_c)
        elif zstat is not None and zstat >= zb and md >= MIN_EFFECT and share >= MIN_SHARE:
            c["verdict"] = "meets bar at look %d (needs audit)" % K
        elif zstat is not None and zstat <= -zb:
            c["verdict"] = "PM moved first at look %d (needs audit)" % K
        else:
            c["verdict"] = "no lead detected at look %d (needs audit)" % K
        if cell not in PRIMARY:
            c["verdict"] = "(informational) " + c["verdict"]
        c["ties_d_zero"] = sum(1 for e in evs if e[0] == 0)
        res["cells"][cell] = c
        if n_e > big[0]:
            big = (n_e, cell, sorted(evs, key=lambda e: e[5])[:20])
    res["plain_summary"] = ["%s [%s]: look %d of %d (data through %s UTC), %d matches, z %s vs boundary %.2f, a planted 1c edge %s at this look, verdict: %s" % (
        k_, v_["role"].split(" ")[0], K, LOOKS, __import__("time").strftime("%Y-%m-%d", __import__("time").gmtime(t_hi - 1)), v_["n_matches"], "%.2f" % v_["z"] if v_["z"] is not None else "n/a", zb,
        "WOULD pass (power ok)" if v_["plant_detected"] else "would NOT pass (underpowered)", v_["verdict"]) for k_, v_ in res["cells"].items()]
    res["first20_events_biggest_cell"] = dict(cell=big[1], rows=[dict(t=e[5], match=e[6], rising_team=e[7], token=e[8], R_real=e[3], placebo_mean=e[4], d=e[0]) for e in big[2]])
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "match_list"}, indent=1))
    print("match_list rows:", len(res["match_list"]))


if __name__ == "__main__":
    main()
