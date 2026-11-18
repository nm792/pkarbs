#!/usr/bin/env python3
"""Goalserve esports in-play odds vs Polymarket price, locked rerun v2, SEQUENTIAL (daily looks), amended 18 Nov after the Reviewer's response
(reviewer/REVIEW-RESPONSE-2026-11-18-goalserve-plan.md). Read-only. Pre-registration: feeds/PREREG-goalserve-odds-vs-pm-v2-2026-11-18.md (amendment V12-V20 is the authority).
Input A: hour files esports_<hour>.jsonl.gz of {"recv_ns","body"} (live/goalserve/capture.py). Input B: --pm DIR (repeatable) with markets.jsonl(.gz) and books.jsonl(.gz) of the PM recorder (live/thesports/capture.py; row time = `ms`, rows only on change). Input C: --poll-log (required).
Rules (locked before any new data is read):
 V1 event = a move of the vig-removed home probability >= 0.02 between TWO CONSECUTIVE stored payloads in which the market is valid and open in both (market and both participants not suspended, 2 participants, value_eu > 1). Any payload in which the (event, market) is
    missing, suspended or invalid CLEARS the baseline, so a reopen price is never an event. Markets: exactly 'Home/Away' (Match Winner) and 'Home/Away (map N)' (Map N Winner); all others excluded and counted. Cells = league prefix (cs2, dota2, ...) x kind.
 V2 per (match, kind) at most CAP=40 events, kept by seeded random choice; the number dropped is reported.
 V3 R = (mid(t+60) - mid(t)) - (mid(t-5) - mid(t-60)) on the rising team's OWN token (never inferred from the other token; a row with no own-book mid is excluded and counted per cell). mid(x) = last book mid at or before x. Needs a mid at t-60 and a book row of either token within +-300 s of t; else dropped and counted.
 V4 placebo = SAME event times, 10 draws per event, token random of the two, sign random; d = R_real - mean placebo R. The post term and the pre term are reported separately, real and placebo, per cell.
 V9 capture outage: --poll-log required; a payload whose preceding poll is more than 10 s earlier clears all baselines (counted).
 V10 PRIMARY cells: cs2|Match Winner and dota2|Match Winner, each with its own alpha; all other cells are informational and cannot be called a pass. The real run omits --plant-c and --seed.
 V12 Only payloads from 2026-11-18T00:00Z (T_START) count. Look K = complete UTC days between T_START and the end of the last hour file (read from file names); K must be 1..20; never an option.
 V17 (Reviewer E1(b)/(c)) Statistic: per match, mean d over its usable events; the cell uses the FIRST N_MAX matches by first usable event time (cs2 100, dota2 50: projected from the v1 accrual of 25 and 12 matches in 4 days; later matches are reported, not used), so adding data never changes earlier matches.
    t-statistic of the per-match means, n-1 degrees of freedom, converted to z_eq (same one-sided p). Information time t = n_eff / N_MAX. Boundary (Brownian scale, valid for ANY look schedule by the reflection principle, continuous monitoring): pass if z_eq * sqrt(t) >= C_BM = 2.60, i.e. z_eq >= 2.60 / sqrt(t); one-sided alpha 2(1 - Phi(2.60)) = 0.0093 per primary cell, <= 0.019 over the two (raised from 2.50 on 18 Nov: the checker's 18-scenario grid gave 1.20% worst at 2.50, too close to 1.25%).
    'meets bar' also needs the V6 conditions (>= 12 matches, >= 60 events, mean d >= 0.005, share of events with R_real > placebo mean >= 55%). 'PM moved first' needs z_eq <= -boundary. 'no lead detected' is decided ONLY when the cell is closed (n_eff reached N_MAX, or look 20) and the plants below were recovered; before that the verdict is 'no pass yet (not a no-lead)'.
 V18 (Reviewer E1(a)) End-to-end plants on each look's real data, per event and alone, as RAW BOOK ROWS (a row in the recorder's format with bid and ask shifted by +-PLANT_C from the last real row) parsed by the same parse_book_row and mid formula as every real row, then through the same token lookup and window code (so events do not contaminate each other's windows): (P+) +PLANT_C step at t+10 s on the rising token and -PLANT_C on the other token; (P-) the same step at t-10 s; (S) directions negated (the other token is read as 'rising'); (SP) S plus P+.
    Required: mean over matches of d(P+) - d(base) within 5% of +PLANT_C; d(P-) - d(base) within 5% of -PLANT_C; d(SP) - d(S) within 5% of -PLANT_C; and power: zb * SE < PLANT_C where SE = s / sqrt(n_eff) at this look. If any fails every verdict except 'unknown' is withheld: 'unknown (plant not recovered / underpowered)'.
 V21 (checker, 18 Nov) Completeness: the run STOPS (no result) unless the poll log reaches at least 60 s past the end of day K, every hour file of days 1..K is present for every hour in which the poll log shows capture running (hours without any poll are capture outages, listed in audit.hour_files), and no hour file is truncated. The cap and the placebo draws of an event are seeded from the event itself, so earlier looks reproduce on later looks.
 V19 Output per look: look, n_eff per cell, t, boundary, z_eq, pre and post terms (real, placebo), matches_by_day and cumulative, excluded counts per cell, plain_summary, first20_events_biggest_cell (hand check by another thread), ties, outage counters.
 V8 seed 20261118 (--seed only for the self test). Every verdict is UNCHECKED until the rule-to-code table is signed by another thread and an independent audit is done. Bookmaker is not identified (bm empty; vendor docs say bet365): say so with every result. Say 'odds moved before the price within the 60 s window' or 'did not'; never 'lead of N seconds'.
Usage: python3 -I feeds/goalserve_odds_vs_pm_v2.py --files '<glob of esports_*.jsonl.gz>' [--files ...] --pm DIR [--pm DIR] --poll-log '<glob of goalserve_*.jsonl>' [--poll-log ...] --clock-note 'text' --out result.json
Self test: python3 -I feeds/test_goalserve_odds_vs_pm_v2.py   (includes the null simulation of the whole look schedule)
"""
import argparse, bisect, calendar, collections, glob, hashlib, json, math, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import norm, find, load_pm, mk_index
from goalserve_odds_vs_pm import counted_lines, market_kind, num, med, poll_gaps

THR, SEED, CAP, NPLC = 0.02, 20261118, 40, 10
PLANT_C = 0.01
MIN_MATCHES, MIN_EVENTS, MIN_EFFECT, MIN_SHARE = 12, 60, 0.005, 55.0
OPEN = (0, "0", False, None)
OUTAGE_S = 10.0
T_START = 1794960000.0        # 2026-11-18T00:00:00Z: only data from here on is used (earlier data is already seen)
LOOKS = 20
C_BM = 2.60                   # boundary on the Brownian scale: pass if z_eq * sqrt(t) >= C_BM (2(1-Phi(2.6)) = 0.0093 one-sided per cell, any look schedule; margin over the 1.25% target)
N_MAX = {"cs2|Match Winner": 100, "dota2|Match Winner": 50}
PRIMARY = tuple(N_MAX)


def parse_book_row(r, drops=None):
    """ONE parse path for every Polymarket book row, real or planted: -> (token, time_s, best_bid, best_ask) or None (counted)."""
    tk, tms = r.get("tk") or r.get("asset"), r.get("recv_ms") if r.get("recv_ms") is not None else r.get("ms")
    if tms is None:
        if drops is not None:
            drops["book_rows_no_time"] += 1
        return None
    b = [float(x["price"]) for x in r.get("bids") or []]
    s = [float(x["price"]) for x in r.get("asks") or []]
    if not b or not s:
        if drops is not None:
            drops["book_rows_one_sided"] += 1
        return None
    if drops is not None:
        drops["pm_book_rows_time_from_recv_ms" if r.get("recv_ms") is not None else "pm_book_rows_time_from_ms"] += 1
    return tk, tms / 1000.0, max(b), min(s)


def mid_of(bb, ba):
    return (bb + ba) / 2.0


def seed_rng(*parts):
    """deterministic per-event generator: the same event gets the same cap rank and placebo draws on every later look."""
    return random.Random(int.from_bytes(hashlib.sha256("|".join(str(x) for x in parts).encode()).digest()[:8], "big"))


def phi_sf(x):
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def z_from_p(p):
    """upper-tail normal quantile by bisection (stdlib only); p in (0, 1)."""
    lo, hi = -40.0, 40.0
    for _ in range(200):
        m = (lo + hi) / 2
        if phi_sf(m) > p:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < 3e-16:
            break
    return h


def t_sf(t, df):
    """P(T > t), Student t with df degrees of freedom (regularised incomplete beta; stdlib only)."""
    if t == 0:
        return 0.5
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5
    # I_x(a,b) with the standard prefactor
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    ib = front * _betacf(a, b, x) / a if x < (a + 1.0) / (a + b + 2.0) else 1.0 - front * _betacf(b, a, 1.0 - x) / b
    return 0.5 * ib if t > 0 else 1.0 - 0.5 * ib


def cell_t(means):
    """per-match means -> (n, mean, se, t, z_eq): z_eq has the same one-sided p as the t statistic with n-1 df."""
    n = len(means)
    if n < 2:
        return n, (means[0] if n else None), None, None, None
    mu = sum(means) / n
    se = (sum((x - mu) ** 2 for x in means) / (n - 1)) ** 0.5 / math.sqrt(n)
    if se == 0:
        return n, mu, 0.0, None, None
    t = mu / se
    p = min(max(t_sf(t, n - 1), 1e-300), 1 - 1e-16)
    return n, mu, se, t, z_from_p(p)


def boundary(n_eff, cell):
    return float("inf") if n_eff < 1 else C_BM / math.sqrt(min(1.0, n_eff / N_MAX[cell]))


def decide(means_by_match, n_events, share, plants_ok, closed, cell, md_ok=True):
    """The whole per-cell decision from per-match means (used by main() and by the null simulation in the self test)."""
    n, mu, se, t, z = cell_t(means_by_match)
    if cell not in N_MAX:
        return dict(n=n, mean=mu, se=se, t=t, z_eq=z, boundary_z=None, verdict="(informational) no boundary")
    zb = boundary(n, cell)
    if n < MIN_MATCHES or n_events < MIN_EVENTS or z is None:
        v = "unknown (%d matches, %d events; needs >= %d and >= %d)" % (n, n_events, MIN_MATCHES, MIN_EVENTS)
    elif not plants_ok:
        v = "unknown (plant not recovered / underpowered at this look)"
    elif z >= zb and mu >= MIN_EFFECT and share >= MIN_SHARE:
        v = "meets bar (needs audit)"
    elif z <= -zb:
        v = "PM moved first (needs audit)"
    elif closed:
        v = "no lead detected (needs audit)"
    else:
        v = "no pass yet (not a no-lead)"
    return dict(n=n, mean=mu, se=se, t=t, z_eq=z, boundary_z=zb, verdict=v)


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
    ap.add_argument("--smoke", action="store_true", help="crash test on old files only: counts the first UTC day of the files, skips look/completeness refusals, output is marked smoke_not_a_result; never used for a real look")
    a = ap.parse_args()
    global T_START
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    hrs, hour_names = [], set()
    for f in files:
        m = re.search(r"esports_(\d{10})", os.path.basename(f))
        if not m:
            raise SystemExit("cannot read the hour from file name %s" % f)
        hrs.append(calendar.timegm(time.strptime(m.group(1), "%Y%m%d%H")) + 3600.0)
        hour_names.add(hrs[-1] - 3600.0)
    if a.smoke:
        T_START = 86400.0 * int((min(hrs) - 3600.0) // 86400)   # smoke only: first UTC day of the given files
        K = 1
    else:
        K = int((max(hrs) - T_START) // 86400)
    if not a.smoke and not 1 <= K <= LOOKS:
        raise SystemExit("look K=%d is outside 1..%d (no complete UTC day since 2026-11-18 or past the last look)" % (K, LOOKS))
    t_hi = T_START + K * 86400.0
    drops = collections.Counter()
    polls = load_polls(a.poll_log, drops)
    if not polls:
        raise SystemExit("no polls read from --poll-log")
    if not a.smoke and polls[-1] < t_hi + 60:
        raise SystemExit("poll log ends %.0f s before the end of look day K=%d + 60 s: the last hour may be half written; run again later" % (t_hi + 60 - polls[-1], K))
    expected_hours = [T_START + 3600.0 * h for h in range(24 * K)]
    polled_hours = {T_START + 3600.0 * int((x - T_START) // 3600) for x in polls}
    missing = [h for h in expected_hours if h not in hour_names]
    missing_polled = [h for h in missing if h in polled_hours]
    if missing_polled and not a.smoke:
        raise SystemExit("hour file(s) missing although the poll log shows capture running: %s (a lost or unshipped file would count as a quiet hour); fix the copy and run again" % ", ".join(time.strftime("%Y%m%d%H", time.gmtime(h)) for h in missing_polled))
    ev, audit = open_events(files, polls, T_START, t_hi)
    if audit["counters"].get("goalserve_rows_truncated_files", 0) or audit["counters"].get("goalserve_rows_bad_lines", 0) > 50:
        raise SystemExit("unreadable or truncated hour file(s): %s; re-copy and run again" % json.dumps(audit["counters"]))
    audit["hour_files"] = dict(expected=len(expected_hours), present=len(expected_hours) - len(missing), missing_hours_utc=[time.strftime("%Y%m%d%H", time.gmtime(h)) for h in missing], missing_hours_without_polls_are_capture_outages=True)
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
            if (r.get("tk") or r.get("asset")) not in need:
                continue
            pr = parse_book_row(r, drops)
            if pr:
                series[pr[0]].append((pr[1], pr[2], pr[3]))
    ts = {}
    for tk in series:
        series[tk].sort()
        ts[tk] = [x[0] for x in series[tk]]

    def mid_at(tk, x, steps=()):
        i = bisect.bisect_right(ts.get(tk, []), x) - 1
        if i < 0:
            return None
        tt0, bb, ba = series[tk][i]
        delta = sum(c for (tt, c, tok) in steps if tok == tk and x >= tt)
        if delta:
            # plant: a raw book row (same format as the recorder's) with bid and ask shifted by delta, run through the SAME parse path and mid formula as every real row
            pr = parse_book_row({"ms": tt0 * 1000.0, "tk": tk, "bids": [{"price": repr(bb + delta)}], "asks": [{"price": repr(ba + delta)}]})
            return mid_of(pr[2], pr[3])
        return mid_of(bb, ba)

    def alive(toks, t):
        for tk in toks:
            L = ts.get(tk, [])
            i = bisect.bisect_left(L, t - 300)
            if i < len(L) and L[i] <= t + 300:
                return True
        return False

    def R(tk, t, steps=()):
        m = [mid_at(tk, t + dt, steps) for dt in (60, 0, -5, -60)]
        if None in m:
            return None
        return (m[0] - m[1]) - (m[2] - m[3]), m[0] - m[1], m[2] - m[3]

    def mean(x):
        x = list(x)
        return sum(x) / len(x) if x else None

    per = collections.defaultdict(list)
    for (eid, kind, t, rise, h, a_, game) in ev:
        per[(game, kind, eid)].append((t, rise))
    recs = collections.defaultdict(list)
    cellx = collections.defaultdict(collections.Counter)
    c_ = a.plant_c
    for (game, kind, eid), L in sorted(per.items()):
        m = sel.get((eid, kind))
        if not m:
            continue
        cell = "%s|%s" % (game, kind)
        if len(L) > CAP:
            drops["events_dropped_by_match_cap"] += len(L) - CAP
            cellx[cell]["events_dropped_by_match_cap"] += len(L) - CAP
            L = sorted(sorted(L, key=lambda x_: hashlib.sha256(("%s|cap|%s|%r" % (a.seed, eid, x_[0])).encode()).hexdigest())[:CAP])
        outs = [norm(o) for o in m["outcomes"]]
        for (t, rise) in L:
            if rise not in outs:
                drops["events_rising_team_not_a_pm_outcome"] += 1
                cellx[cell]["rising_team_not_a_pm_outcome"] += 1
                continue
            i = outs.index(rise)
            tk, otk = m["tokens"][i], m["tokens"][1 - i]
            if not alive(m["tokens"], t):
                drops["events_pm_recorder_silent_pm300s"] += 1
                cellx[cell]["pm_recorder_silent_pm300s"] += 1
                continue
            r0 = R(tk, t)
            if r0 is None:
                drops["events_no_own_book_mid_at_t_minus_60"] += 1
                cellx[cell]["no_own_book_mid_at_t_minus_60"] += 1
                continue
            prng = seed_rng(a.seed, "plc", eid, repr(t))
            pl, ppo, ppr = [], [], []
            for _ in range(NPLC):
                ptk, sg = prng.choice(m["tokens"]), prng.choice((-1, 1))
                x = R(ptk, t)
                if x is not None:
                    pl.append(sg * x[0]); ppo.append(sg * x[1]); ppr.append(sg * x[2])
            if not pl:
                drops["events_no_placebo"] += 1
                cellx[cell]["no_placebo"] += 1
                continue
            mp = mean(pl)
            if r0[0] == mp:
                drops["events_tie_d_zero"] += 1

            tmap = dict(zip(outs, m["tokens"]))       # a SEPARATE CODE PATH (name-to-token dictionary) over the same markets file: catches code bugs, not a misordered outcomes/tokens pair in markets.jsonl (V22)
            ttk = tmap[rise]
            ottk = [x for x in m["tokens"] if x != ttk][0]

            def stp(dt):
                return ((t + dt, c_, ttk), (t + dt, -c_, ottk))
            rP, rM = R(tk, t, stp(10)), R(tk, t, stp(-10))
            rS, rSP = R(otk, t), R(otk, t, stp(10))
            recs[cell].append(dict(m=eid, t=t, rise=rise, tok=tk, d=r0[0] - mp, share=1.0 if r0[0] > mp else 0.0, R=r0[0], mp=mp, post=r0[1], pre=r0[2], ppost=mean(ppo), ppre=mean(ppr),
                                   dP=(rP[0] - mp) if rP else None, dM=(rM[0] - mp) if rM else None, dS=(rS[0] - mp) if rS else None, dSP=(rSP[0] - mp) if rS and rSP else None))

    def per_match(evs, key, need=None):
        by = collections.defaultdict(list)
        for e in evs:
            if e[key] is not None and (need is None or all(e[k] is not None for k in need)):
                by[e["m"]].append(e)
        return by

    res = dict(smoke_not_a_result=bool(a.smoke), look=K, looks_total=LOOKS, c_bm=C_BM, n_max=N_MAX, data_from_utc=T_START, data_through_utc=t_hi, seed=a.seed, plant_c=a.plant_c, clock_note=a.clock_note, files=len(files),
               goalserve_events_total=len(ev), drops=dict(drops), audit=audit, poll_interval_measured=poll_gaps(a.poll_log), primary_cells=list(PRIMARY), cells={},
               wording="Only primary cells can be called a pass. Say 'odds moved before the price within the 60 s window' or 'did not'; never 'lead of N seconds' (windows cannot resolve under about 5 s). Bookmaker not identified (bm empty; vendor docs say bet365). d is volatility-matched (sign-symmetric placebo), not momentum-matched.",
               match_list=sorted(ml.values(), key=lambda r: (str(r["eid"]), r["kind"])))
    big = (0, None, [])
    for cell, evs in sorted(recs.items()):
        first = {}
        for e in evs:
            first[e["m"]] = min(first.get(e["m"], e["t"]), e["t"])
        order = sorted(first, key=first.get)
        used = set(order[:N_MAX.get(cell, len(order))])
        ue = [e for e in evs if e["m"] in used]
        by = per_match(ue, "d")
        means = [mean(e["d"] for e in L) for L in by.values()]
        n_e = len(ue)
        share = 100.0 * sum(e["share"] for e in ue) / n_e
        md = mean(means)

        def delta(k1, k2, sign_c):
            """mean over matches of the paired difference (variant k1 minus k2) and the expected value sign_c * c."""
            b = per_match(ue, k1, need=(k1, k2))
            x = mean(mean(e[k1] - e[k2] for e in L) for L in b.values())
            return x
        dP, dM, dSw = delta("dP", "d", +1), delta("dM", "d", -1), delta("dSP", "dS", -1)
        tol = 0.05 * c_
        recovered = dict(plus_step=dP, minus_step=dM, label_swap_plus_step=dSw,
                         plus_ok=dP is not None and abs(dP - c_) <= tol, minus_ok=dM is not None and abs(dM + c_) <= tol, swap_ok=dSw is not None and abs(dSw + c_) <= tol)
        n_, mu_, se_, t_, z_ = cell_t(means)
        zb = boundary(n_, cell) if cell in N_MAX else None
        power_ok = bool(se_ and zb is not None and zb * se_ < c_)
        plants_ok = recovered["plus_ok"] and recovered["minus_ok"] and recovered["swap_ok"] and power_ok
        closed = cell in N_MAX and (n_ >= N_MAX[cell] or K == LOOKS)
        dec = decide(means, n_e, share, plants_ok, closed, cell)
        days = collections.defaultdict(set)
        for e in ue:
            days[int((e["t"] - T_START) // 86400) + 1].add(e["m"])
        seen_m, cum = set(), {}
        for dd in sorted(days):
            seen_m |= days[dd]
            cum[str(dd)] = len(seen_m)
        c = dict(role="primary" if cell in PRIMARY else "informational (cannot be called a pass)", n_matches_used=n_, n_matches_seen=len(order), n_matches_beyond_planned_max=len(order) - len(used), n_events=n_e,
                 information_time=(min(1.0, n_ / N_MAX[cell]) if cell in N_MAX else None), mean_d_per_match=md, se=se_, t_stat=t_, z_eq=z_, boundary_z=zb,
                 share_events_real_gt_placebo_pct=share, ties_d_zero=sum(1 for e in ue if e["d"] == 0),
                 post_real=mean(mean(e["post"] for e in L) for L in by.values()), pre_real=mean(mean(e["pre"] for e in L) for L in by.values()),
                 post_placebo=mean(mean(e["ppost"] for e in L) for L in by.values()), pre_placebo=mean(mean(e["ppre"] for e in L) for L in by.values()),
                 plant_c=c_, plant_recovery=recovered, power_ok=power_ok, plants_ok=plants_ok, min_detectable_effect_at_this_look=(zb * se_) if (se_ and zb) else None, closed=closed,
                 excluded_counts=dict(cellx.get(cell, {})), matches_by_day={str(k_): len(v_) for k_, v_ in sorted(days.items())}, matches_cumulative_by_day=cum,
                 events_per_match=sorted((len(v) for v in by.values()), reverse=True)[:10], per_match_mean_d={str(k_): mean(e["d"] for e in L_) for k_, L_ in by.items()}, verdict=dec["verdict"])
        if cell not in PRIMARY:
            c["verdict"] = "(informational) " + c["verdict"]
        res["cells"][cell] = c
        if n_e > big[0]:
            big = (n_e, cell, sorted(ue, key=lambda e: e["t"])[:20])
    res["plain_summary"] = ["%s [%s]: look %d of %d (data through %s UTC), %d matches used, info time %s, z_eq %s vs boundary %s, planted 1c edge: %s, verdict: %s" % (
        k_, v_["role"].split(" ")[0], K, LOOKS, time.strftime("%Y-%m-%d", time.gmtime(t_hi - 1)), v_["n_matches_used"],
        "%.2f" % v_["information_time"] if v_["information_time"] is not None else "n/a", "%.2f" % v_["z_eq"] if v_["z_eq"] is not None else "n/a",
        "%.2f" % v_["boundary_z"] if v_["boundary_z"] is not None else "n/a", "RECOVERED and powered" if v_["plants_ok"] else "NOT recovered or underpowered (%s)" % json.dumps(v_["plant_recovery"]), v_["verdict"])
        for k_, v_ in res["cells"].items()]
    res["first20_events_biggest_cell"] = dict(cell=big[1], rows=[dict(t=e["t"], match=e["m"], rising_team=e["rise"], token=e["tok"], R_real=e["R"], placebo_mean=e["mp"], d=e["d"]) for e in big[2]])
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "match_list"}, indent=1))
    print("match_list rows:", len(res["match_list"]))


if __name__ == "__main__":
    main()
