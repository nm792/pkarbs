#!/usr/bin/env python3
"""Goalserve bet365 esports in-play odds vs Polymarket price: lead test per feeds/STANDARD-feed-latency-test.md v1 (sections 2-3).
Read-only. Bookmaker = whatever Goalserve sends (docs: bet365 only); this script never assumes a bookmaker name and reports the `bm` values seen.
Input A: hour files esports_<hour>.jsonl.gz of {"recv_ns","body"} (live/goalserve/capture.py store_payload; body = whole in-play file, changed polls only).
Input B: --pm DIR (repeatable) with markets.jsonl(.gz) and books.jsonl(.gz), same format as feeds/ps_lead_test.py.
Rules (pre-registered 17 Nov, locked; code mirrors ps_lead_test.py, which supplies lines/norm/find/load_pm/mk_index):
 R1 winner market names, after norm(): exactly 'match winner' -> kind Match Winner; '(map|game) N winner' -> kind Map N Winner. Every other market name is EXCLUDED
    and printed with counts (seen/used/excluded). No fuzzy name logic.
 R2 market must have exactly 2 participants, not suspended, both value_eu numeric > 1. p_i = (1/o_i) / sum(1/o). Rows failing this are skipped and COUNTED.
 R3 team mapping: Goalserve team_info home/away names -> PM market by EXACT normalised outcome names (frozenset of the two). Participant -> team by exact norm name
    equal to home or away; participant names '1'/'home' = home, '2'/'away' = away; anything else is EXCLUDED and counted. No match found = EXCLUDED and counted.
 R4 event: per (event id, market id) compare p_home with the previous valid stored payload (consecutive payloads, v2). A move of >= 0.02 is ONE event at that row's recv time
    (first-seen time; resolution = one poll, measured with --poll-log); the team whose probability rose is the direction. Slow drift below 2c per payload makes no event (known, by design).
    Cells are per title (info.sport) x bookmaker (bm) x market kind (Match Winner, Map N Winner separately).
 R5 PM side (STANDARD section 2): direction token = the rising team's outcome token. onset = first book mid inside [t-60,t+60] that is >= 2c above the mid at t-60 in the
    event direction. lead = onset - t (positive = Goalserve first). Placebo = 10 random times per (match, kind), no Goalserve event of that match within +-60 s, random token and direction, same procedure.
 R6 bar per cell: n_events >= 30, median(real - placebo) >= +2.0 s, match-clustered bootstrap 95% CI excludes 0, and lead >= 1.0 s (resolved, price after feed) in >= 60% of ALL events.
    Fewer than 30 events = 'unknown (n<30), preliminary'. Fewer than 30 placebo onsets or placebo onsets in fewer than 30 matches = 'unknown (placebo too thin)'. Placebo excludes +-2W (120 s) around any event of the match.
    Money bar only if this passes.
 R7 seed 20261117 (--seed only for the self test). Verdicts are PRELIMINARY until the rule-to-code table is signed by another project thread and an independent audit is done.
Usage: python3 -I feeds/goalserve_odds_vs_pm.py --files '<glob of esports_*.jsonl.gz>' --pm DIR [--pm DIR] --poll-log '<glob of goalserve_*.jsonl>' --clock-note 'PM recorder host X, Goalserve capture host Y, same chrony' --out result.json
Self test (planted edge): python3 -I feeds/test_goalserve_odds_vs_pm.py
"""
import argparse, bisect, collections, glob, gzip, json, os, random, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import lines, norm, find, load_pm, mk_index, opn

W, THR, SEED, RES = 60.0, 0.02, 20261117, 1.0
MAP_RE = re.compile(r"^(?:map|game) (\d+) winner$")


def counted_lines(p, cnt, key):
    """Like ps_lead_test.lines() but COUNTS unparsable lines (key_bad_lines) and truncated/unreadable files (key_truncated_files)."""
    try:
        with opn(p) as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    cnt[key + "_bad_lines"] += 1
    except (EOFError, OSError):
        cnt[key + "_truncated_files"] += 1


def market_kind(name):
    n = norm(name)
    if n == "match winner":
        return "Match Winner"
    m = MAP_RE.match(n)
    return "Map %s Winner" % m.group(1) if m else None


def num(x):
    try:
        v = float(x)
        return v if v > 1.0 else None
    except (TypeError, ValueError):
        return None


def goalserve_events(files):
    """-> events [(eid, kind, t_s, rising_team_norm, home_norm, away_norm, title, bm)], audit counters."""
    A = collections.Counter()
    seen_names, used_names, excl_names, bms = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    base = {}
    ev = []
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
            bm = repr(d.get("bm"))
            bms[bm] += 1
            for eid, e in (d.get("events") or {}).items():
                if not isinstance(e, dict):
                    continue
                title = (e.get("info") or {}).get("sport") or "?"
                ti = e.get("team_info") or {}
                h, a = norm((ti.get("home") or {}).get("name")), norm((ti.get("away") or {}).get("name"))
                for mid, m in (e.get("odds") or {}).items():
                    if not isinstance(m, dict):
                        continue
                    name = m.get("name") or "?"
                    seen_names[name] += 1
                    kind = market_kind(name)
                    if not kind:
                        excl_names[name] += 1
                        continue
                    used_names[name] += 1
                    parts = [x for x in (m.get("participants") or {}).values() if isinstance(x, dict)]
                    if len(parts) != 2:
                        A["skip_not_2_participants"] += 1
                        continue
                    if m.get("suspend") not in (0, "0", False, None) or any(x.get("suspend") not in (0, "0", False, None) for x in parts):
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
                    if k not in base:
                        base[k] = ph
                        continue
                    if abs(ph - base[k]) >= THR:
                        ev.append((eid, kind, t / 1e9, h if ph > base[k] else a, h, a, title, bm))
                        A["events"] += 1
                    base[k] = ph
    audit = dict(counters=dict(A), bm_values=dict(bms), market_names_seen=dict(seen_names.most_common(60)),
                 market_names_used=dict(used_names), market_names_excluded=dict(excl_names.most_common(60)))
    return ev, audit


def med(x):
    x = sorted(x)
    n = len(x)
    return None if not n else (x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2)


def poll_gaps(globs):
    """Measured Goalserve esports poll interval from capture.py logs (goalserve_<date>.jsonl rows, row['esports']['recv_ns'])."""
    ts, errs, cnt = [], 0, collections.Counter()
    for g in globs:
        for p in sorted(glob.glob(g)):
            for r in counted_lines(p, cnt, "poll_log"):
                e = r.get("esports") or {}
                if "err" in e:
                    errs += 1
                elif e.get("recv_ns"):
                    ts.append(e["recv_ns"] / 1e9)
    ts.sort()
    gaps = sorted(b - a for a, b in zip(ts, ts[1:]))
    if not gaps:
        return dict(n_polls=len(ts), poll_errors=errs, skipped=dict(cnt), note="no polls read")
    return dict(n_polls=len(ts), poll_errors=errs, skipped=dict(cnt), median_gap_s=statistics.median(gaps), p90_gap_s=gaps[int(.9 * len(gaps))],
                p99_gap_s=gaps[min(len(gaps) - 1, int(.99 * len(gaps)))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--poll-log", action="append", default=[])
    ap.add_argument("--clock-note", required=True, help="text: PM recorder host, Goalserve capture host, same chrony clock?")
    ap.add_argument("--seed", type=int, default=SEED, help="locked default; only the self test changes it")
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    ev, audit = goalserve_events(files)
    drops = collections.Counter()
    pmlist = load_pm(a.pm)
    for d in a.pm:
        mp = find(d, "markets")
        if mp:
            for _ in counted_lines(mp, drops, "pm_markets"):
                pass
    idx = mk_index(pmlist)
    sel, matchlist = {}, {}
    for (eid, kind, t, rise, h, a_, title, bm) in ev:
        key = (eid, kind)
        if key in matchlist:
            matchlist[key]["n_events"] += 1
            continue
        c = [x for x in (idx.get(frozenset((h, a_))) or []) if x["kind"] == kind]
        rec = dict(eid=eid, title=title, bm=bm, kind=kind, home=h, away=a_, n_pm_candidates=len(c), n_events=1)
        if len(c) == 1:
            sel[key] = c[0]
            rec["pm_cond"] = c[0].get("cond")
        else:
            drops["events_no_pm_market" if not c else "events_ambiguous_rematch_excluded"] += 0
            rec["excluded"] = "no PM market with these exact names and kind" if not c else "more than one PM market (rematch); start time not available, excluded"
        matchlist[key] = rec
    for rec in matchlist.values():
        if "excluded" in rec:
            drops["events_no_pm_market" if rec["n_pm_candidates"] == 0 else "events_ambiguous_rematch_excluded"] += rec["n_events"]
    need = {tk for m in sel.values() for tk in m["tokens"]}
    series = collections.defaultdict(list)
    for d in a.pm:
        p = find(d, "books")
        if not p:
            continue
        for r in counted_lines(p, drops, "pm_books"):
            tk = r.get("asset") or r.get("tk")
            if tk not in need:
                continue
            tms = r.get("recv_ms")
            if tms is None:
                drops["book_rows_no_recv_ms"] += 1
                continue
            b = [float(x["price"]) for x in r.get("bids") or []]
            s = [float(x["price"]) for x in r.get("asks") or []]
            if not b or not s:
                drops["book_rows_one_sided"] += 1
                continue
            series[tk].append((tms / 1000.0, (max(b) + min(s)) / 2.0))
    ts = {}
    bgaps = []
    for tk in series:
        series[tk].sort()
        ts[tk] = [x[0] for x in series[tk]]
        bgaps.extend(y - x for x, y in zip(ts[tk], ts[tk][1:]))
    bgaps.sort()
    book_gap = dict(n_gaps=len(bgaps), median_s=statistics.median(bgaps), p90_s=bgaps[int(.9 * len(bgaps))]) if bgaps else dict(n_gaps=0)
    res_eff = max(RES, book_gap.get("p90_s", RES))

    def mid_at(tk, t):
        i = bisect.bisect_right(ts.get(tk, []), t) - 1
        return series[tk][i][1] if i >= 0 else None

    def onset(tk, t0, sign):
        """-> (status, lead): status 'ok' (lead set), 'none' (price did not move), 'nobase' (no mid at t-60)."""
        if tk not in series:
            return "nobase", None
        b = mid_at(tk, t0 - W)
        if b is None:
            return "nobase", None
        i = bisect.bisect_left(ts[tk], t0 - W)
        v = series[tk]
        while i < len(v) and v[i][0] <= t0 + W:
            if sign * (v[i][1] - b) >= THR:
                return "ok", v[i][0] - t0
            i += 1
        return "none", None

    rows, by_match_t = [], collections.defaultdict(list)
    for (eid, kind, t, rise, h, a_, title, bm) in ev:
        by_match_t[eid].append(t)
        m = sel.get((eid, kind))
        if not m:
            continue
        outs = [norm(o) for o in m["outcomes"]]
        if rise not in outs:
            drops["events_rising_team_not_a_pm_outcome"] += 1
            continue
        tk = m["tokens"][outs.index(rise)]
        st, ld = onset(tk, t, +1)
        if st == "nobase":
            drops["real_events_no_pm_baseline_at_t_minus_60"] += 1
        rows.append(dict(cell="%s|%s|%s" % (title, bm, kind), match=eid, t=t, tok=tk, lead=ld, status=st))
    plc, done = [], set()
    for r in rows:
        key = (r["match"], r["cell"])
        if key in done:
            continue
        done.add(key)
        et = sorted(by_match_t[r["match"]])
        mkey = (r["match"], r["cell"].split("|")[2])
        toks = sorted(sel[mkey]["tokens"], key=str)
        got = tries = 0
        while got < 10 and tries < 400 and et[0] < et[-1]:
            tries += 1
            t = rnd.uniform(et[0], et[-1])
            if any(abs(t - x) <= 2 * W for x in et):
                continue
            st, ld = onset(rnd.choice(toks), t, rnd.choice((-1, 1)))
            if st == "nobase":
                drops["placebo_draws_no_pm_baseline"] += 1
            plc.append(dict(cell=r["cell"], match=r["match"], lead=ld, status=st))
            got += 1
        if got < 10:
            drops["placebo_shortfall_matches"] += 1
            drops["placebo_draws_missing"] += 10 - got

    def boot(R, P, n=2000):
        ms = sorted({r["match"] for r in R})
        by = {m: [r["lead"] for r in R if r["match"] == m and r["lead"] is not None] for m in ms}
        pb = {m: [r["lead"] for r in P if r["match"] == m and r["lead"] is not None] for m in ms}
        out = []
        for _ in range(n):
            s = [rnd.choice(ms) for _ in ms]
            r_, p_ = [x for m in s for x in by[m]], [x for m in s for x in pb[m]]
            if r_ and p_:
                out.append(med(r_) - med(p_))
        out.sort()
        return [out[int(.025 * len(out))], out[int(.975 * len(out))]] if len(out) > 20 else None

    res = dict(seed=a.seed, clock_note=a.clock_note, poll_interval_measured=poll_gaps(a.poll_log) if a.poll_log else "NOT MEASURED (no --poll-log)",
               book_row_spacing_measured=book_gap, resolution_used_in_bar4_s=res_eff, files=len(files), goalserve_events_total=len(ev), drops=dict(drops), audit=audit, cells={},
               match_list=sorted(matchlist.values(), key=lambda r: (str(r["eid"]), r["kind"])))
    for cell in sorted({r["cell"] for r in rows}):
        R = [r for r in rows if r["cell"] == cell]
        P = [r for r in plc if r["cell"] == cell]
        rl, pl = [r["lead"] for r in R if r["lead"] is not None], [r["lead"] for r in P if r["lead"] is not None]
        n = len(R)
        pm_on = len({r["match"] for r in P if r["lead"] is not None})
        c = dict(n_events=n, n_matches=len({r["match"] for r in R}), n_with_onset=len(rl), n_placebo=len(P), n_placebo_with_onset=len(pl),
                 n_matches_with_placebo_onset=pm_on, placebo_onset_rate=(len(pl) / len(P)) if P else None,
                 median_real_lead_s=med(rl), median_placebo_lead_s=med(pl), diff_s=(med(rl) - med(pl)) if rl and pl else None,
                 pct_all_events_lead_ge_res=100.0 * sum(1 for x in rl if x >= res_eff) / n,
                 pct_all_events_lead_gt0=100.0 * sum(1 for x in rl if x > 0) / n,
                 pct_with_onset_lead_gt0=(100.0 * sum(1 for x in rl if x > 0) / len(rl)) if rl else None,
                 pct_placebo_lead_gt0=(100.0 * sum(1 for x in pl if x > 0) / len(pl)) if pl else None,
                 ci95_match_boot=boot(R, P) if n and pl else None)
        if n < 30:
            c["verdict"] = "unknown (n=%d < 30), preliminary" % n
        elif len(pl) < 30 or pm_on < 30:
            c["verdict"] = "unknown (placebo too thin: %d onsets in %d matches)" % (len(pl), pm_on)
        else:
            ok = c["diff_s"] >= 2 and c["ci95_match_boot"] and c["ci95_match_boot"][0] > 0 and c["pct_all_events_lead_ge_res"] >= 60
            c["verdict"] = "meets bar (needs audit)" if ok else "no lead (needs audit)"
        c["real_leads_s_first500"] = [round(x, 2) for x in rl[:500]]
        c["placebo_leads_s_first500"] = [round(x, 2) for x in pl[:500]]
        res["cells"][cell] = c
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "match_list"}, indent=1))
    print("match_list rows:", len(res["match_list"]), "(full list in the JSON)")


if __name__ == "__main__":
    main()
