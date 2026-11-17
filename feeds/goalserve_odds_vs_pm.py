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
 R4 event: per (event id, market id) a baseline p_home is set at the first valid row. A later stored row whose p_home differs from the baseline by >= 0.02 is ONE event
    at that row's recv time (first-seen time; resolution = one poll, about 1 s); the team whose probability rose is the direction; baseline := new p_home.
 R5 PM side (STANDARD section 2): direction token = the rising team's outcome token. onset = first book mid inside [t-60,t+60] that is >= 2c above the mid at t-60 in the
    event direction. lead = onset - t (positive = Goalserve first). Placebo = 10 random times per (match, kind), no Goalserve event of that match within +-60 s, random token and direction, same procedure.
 R6 bar per (kind) cell: n_events >= 30, median(real - placebo) >= +2.0 s, match-clustered bootstrap 95% CI excludes 0, price moves after feed (lead > 0) in >= 60% of events with an onset.
    Fewer than 30 events = 'unknown (n<30), preliminary'. If the placebo has no onsets the difference is undefined = 'no lead (undefined placebo)'. Money bar only if this passes.
 R7 seed 20261117. Verdicts are PRELIMINARY until the rule-to-code table is signed by another project thread and an independent audit is done.
Usage: python3 -I feeds/goalserve_odds_vs_pm.py --files '<glob of esports_*.jsonl.gz>' --pm DIR [--pm DIR] --out result.json
Self test (planted edge): python3 -I feeds/test_goalserve_odds_vs_pm.py
"""
import argparse, bisect, collections, glob, gzip, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import lines, norm, find, load_pm, mk_index

W, THR, SEED = 60.0, 0.02, 20261117
MAP_RE = re.compile(r"^(?:map|game) (\d+) winner$")


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
    """-> events [(eid, kind, t_s, rising_team_norm, home_norm, away_norm)], audit counters."""
    A = collections.Counter()
    seen_names, used_names, excl_names, bms = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    base = {}
    ev = []
    for p in sorted(files):
        for r in lines(p):
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
            for eid, e in (d.get("events") or {}).items():
                if not isinstance(e, dict):
                    continue
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
                        ev.append((eid, kind, t / 1e9, h if ph > base[k] else a, h, a))
                        A["events"] += 1
                        base[k] = ph
    audit = dict(counters=dict(A), bm_values=dict(bms), market_names_seen=dict(seen_names.most_common(60)),
                 market_names_used=dict(used_names), market_names_excluded=dict(excl_names.most_common(60)))
    return ev, audit


def med(x):
    x = sorted(x)
    n = len(x)
    return None if not n else (x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rnd = random.Random(SEED)
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    ev, audit = goalserve_events(files)
    idx = mk_index(load_pm(a.pm))
    sel, unmatched = {}, collections.Counter()
    for (eid, kind, t, rise, h, a_) in ev:
        c = idx.get(frozenset((h, a_)))
        m = next((x for x in (c or []) if x["kind"] == kind), None)
        if not m:
            unmatched[(eid, kind)] += 1
            continue
        sel[(eid, kind)] = m
    need = {tk for m in sel.values() for tk in m["tokens"]}
    series = collections.defaultdict(list)
    for d in a.pm:
        p = find(d, "books")
        if not p:
            continue
        for r in lines(p):
            tk = r.get("asset") or r.get("tk")
            tms = r.get("recv_ms") or r.get("ms")
            if tk not in need or tms is None:
                continue
            b = [float(x["price"]) for x in r.get("bids") or []]
            s = [float(x["price"]) for x in r.get("asks") or []]
            if b and s:
                series[tk].append((tms / 1000.0, (max(b) + min(s)) / 2.0))
    ts = {}
    for tk in series:
        series[tk].sort()
        ts[tk] = [x[0] for x in series[tk]]

    def mid_at(tk, t):
        i = bisect.bisect_right(ts.get(tk, []), t) - 1
        return series[tk][i][1] if i >= 0 else None

    def onset(tk, t0, sign):
        if tk not in series:
            return None
        b = mid_at(tk, t0 - W)
        if b is None:
            return None
        i = bisect.bisect_left(ts[tk], t0 - W)
        v = series[tk]
        while i < len(v) and v[i][0] <= t0 + W:
            if sign * (v[i][1] - b) >= THR:
                return v[i][0] - t0
            i += 1
        return None

    rows, by_match_t = [], collections.defaultdict(list)
    for (eid, kind, t, rise, h, a_) in ev:
        by_match_t[eid].append(t)
        m = sel.get((eid, kind))
        if not m:
            continue
        outs = [norm(o) for o in m["outcomes"]]
        if rise not in outs:
            continue
        tk = m["tokens"][outs.index(rise)]
        rows.append(dict(kind=kind, match=eid, t=t, tok=tk, lead=onset(tk, t, +1)))
    plc, done = [], set()
    for r in rows:
        key = (r["match"], r["kind"])
        if key in done:
            continue
        done.add(key)
        et = sorted(by_match_t[r["match"]])
        toks = sorted(sel[key]["tokens"], key=str)
        got = tries = 0
        while got < 10 and tries < 400 and et[0] < et[-1]:
            tries += 1
            t = rnd.uniform(et[0], et[-1])
            if any(abs(t - x) <= W for x in et):
                continue
            plc.append(dict(kind=key[1], match=key[0], lead=onset(rnd.choice(toks), t, rnd.choice((-1, 1)))))
            got += 1

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

    res = dict(seed=SEED, resolution="one poll (about 1 s); onset resolution = PM book snapshot spacing", files=len(files),
               goalserve_events_total=len(ev), events_without_pm_market=sum(unmatched.values()), audit=audit, cells={})
    for grp, test in (("match", lambda k: k == "Match Winner"), ("map", lambda k: k != "Match Winner")):
        R = [r for r in rows if test(r["kind"])]
        P = [r for r in plc if test(r["kind"])]
        rl, pl = [r["lead"] for r in R if r["lead"] is not None], [r["lead"] for r in P if r["lead"] is not None]
        n = len(R)
        c = dict(n_events=n, n_matches=len({r["match"] for r in R}), n_with_onset=len(rl), n_placebo=len(P), n_placebo_with_onset=len(pl),
                 median_real_lead_s=med(rl), median_placebo_lead_s=med(pl), diff_s=(med(rl) - med(pl)) if rl and pl else None,
                 pct_price_after_feed=(100.0 * sum(1 for x in rl if x > 0) / len(rl)) if rl else None,
                 pct_placebo_after=(100.0 * sum(1 for x in pl if x > 0) / len(pl)) if pl else None,
                 ci95_match_boot=boot(R, P) if n and pl else None)
        if n < 30:
            c["verdict"] = "unknown (n=%d < 30), preliminary" % n
        elif c["diff_s"] is None:
            c["verdict"] = "no lead (undefined placebo)"
        else:
            ok = c["diff_s"] >= 2 and c["ci95_match_boot"] and c["ci95_match_boot"][0] > 0 and (c["pct_price_after_feed"] or 0) >= 60
            c["verdict"] = "meets bar (needs audit)" if ok else "no lead (needs audit)"
        c["real_leads_s_first500"] = [round(x, 2) for x in rl[:500]]
        c["placebo_leads_s_first500"] = [round(x, 2) for x in pl[:500]]
        res["cells"][grp] = c
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
