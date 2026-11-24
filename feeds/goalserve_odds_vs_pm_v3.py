#!/usr/bin/env python3
"""Goalserve in-play odds vs Polymarket OWN-token book, v3 (spec: reviewer/goalserve/SPEC-v3-pm-inputs-and-controls-2026-11-22.md). READ-ONLY, offline on files.
NOT SIGNED: every verdict is UNCHECKED until another thread signs the rule-to-code table and an independent audit is done (R-021, R-023).
Cells: esports (CS2 'Match Winner' + 'Map N Winner', Dota 2), tennis, hockey_nhl. One run = one sport, one explicit window [--start-iso, --end-iso).
Inputs: Goalserve hour files <sport>_<YYYYMMDDHH>.jsonl.gz ({"recv_ns","body"}), poll log goalserve_*.jsonl, PM recorder dir(s) with markets.jsonl[.gz] and books*.jsonl[.gz] (rows: recv_ms, asset, bids, asks).
Rules:
 E1 event = move >= 0.02 of the vig-removed home probability between two CONSECUTIVE stored payloads where market + both participants are open (v2 rule); a poll gap > 10 s clears baselines.
 E2 per event, on the rising team's OWN token, mid(x) = last book row mid at or before x:  d_w = [mid(t+w)-mid(t)] - [mid(t)-mid(t-w)], w = 10 (PRIMARY), 2, 60. d10 > 0: price moved with the odds after the odds moved.
 E3 recorder alive: every 30 s bucket in [t-w-30, t+w] holds >= 1 row of ANY token of the recorder, else the event is excluded (counted).
 E4 placebo: 10 draws per event, time in the same match with no Goalserve move >= 0.01 within +-120 s, random token, random sign, same d_w. |mean placebo d10| must be <= 0.002 (0.2c) else 'placebo drift', no verdict.
 E5 plants: from t+5 s the last real raw book row of the rising token is shifted +-PLANT_C (bid and ask) and re-parsed by the same parse path (as v2 V18; persistent shift); recovery of d10 (per-match mean of d10_plant - d10_base) must be 95-105% of +-PLANT_C for both signs, else no number.
 E6 label-swap: the OTHER token read as rising: mean d10 must be within 0.002 of the NEGATED real mean (complementary books), else 'swap null failed'. Time-shift: events moved +600 s: |mean d10| <= 0.002 else 'shift null failed'.
 E7 per match mean of d10 (cap 40 events per match, seeded); the FIRST 12 matches of a cell by first usable event time are the SIZING BLOCK (used only for sigma and N_MAX, never scored):
    N_MAX = min(100, ceil(6.185 * sigma_c^2 / 0.5^2)) with sigma_c in cents; scored matches = the rest. Success: z_eq*sqrt(min(1,n/N_MAX)) >= 2.60 and mean >= 0.005 and events >= 60.
    Futility (n >= 30 scored): 95% one-sided upper bound of mean d10 < 0.002 -> 'no lead at 0.2c or more, closed'; upper bound < 0 or z_eq <= -boundary -> 'price moves first, closed'.
 E8 join: Goalserve team names to PM outcome names by exact or whole-word containment ('NJ Devils' ~ 'Devils'); both teams must map to different outcomes, ONE market only (else ambiguous, counted), PM start within 36 h of the event when given.
 E9 completeness: poll log must reach --end-iso + 60 s; any hour file missing while polls show capture running -> STOP (no result).
Usage: python3 -I feeds/goalserve_odds_vs_pm_v3.py --sport esports|tennis|hockey_nhl --files '<glob>' --pm DIR [--pm DIR] --poll-log '<glob>' --start-iso ISO --end-iso ISO --clock-note TXT --out result.json
"""
import argparse, bisect, calendar, collections, glob, gzip, hashlib, json, math, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import norm, load_pm
from goalserve_odds_vs_pm import counted_lines, market_kind, num
from goalserve_odds_vs_pm_v2 import parse_book_row, mid_of, seed_rng, cell_t, t_sf, z_from_p, C_BM

THR, MOVE_FREE, FREE_S, CAP, NPLC = 0.02, 0.01, 120.0, 40, 10
PLANT_C, PLANT_AT, W_PRIMARY, WINDOWS = 0.01, 5.0, 10, (10, 2, 60)
SIZING_BLOCK, MIN_EVENTS, MIN_EFFECT, DRIFT_TOL, FUTILITY_MIN = 12, 60, 0.005, 0.002, 30
SHIFT_S, OUTAGE_S, HB_BUCKET = 600.0, 10.0, 30.0
OPEN = (0, "0", False, None)
HOCKEY_NAMES = {"home away", "money line", "moneyline", "match winner", "to win", "who will win"}


def kind_of(sport, name):
    n = norm(name)
    if sport == "esports":
        return market_kind(name)
    if sport == "tennis":
        return "Match Winner" if n == "to win" else None
    return "Match Winner" if n in HOCKEY_NAMES else None


def contains(x, o):
    return bool(x) and bool(o) and (x == o or (len(o) >= 3 and (" %s " % o) in (" %s " % x)) or (len(x) >= 3 and (" %s " % x) in (" %s " % o)))


def map_teams(h, a, outs):
    """-> (index of home outcome, index of away outcome) or None. Both must map, to different outcomes, each to exactly one."""
    ih = [i for i, o in enumerate(outs) if contains(h, o)]
    ia = [i for i, o in enumerate(outs) if contains(a, o)]
    if len(ih) == 1 and len(ia) == 1 and ih[0] != ia[0]:
        return ih[0], ia[0]
    return None


def iso(s):
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))


def gs_events(files, polls, t_lo, t_hi, sport):
    """-> events [(eid, kind, t, rising_norm, h, a, game)], moves {eid: [t of any >= 0.01 move]}, span {(eid,kind): (t0,t1)}, audit."""
    A = collections.Counter()
    base, ev, moves, span, used, excl = {}, [], collections.defaultdict(list), {}, collections.Counter(), collections.Counter()
    for p in sorted(files):
        for r in counted_lines(p, A, "goalserve_rows"):
            body, t = r.get("body"), r.get("recv_ns")
            if not isinstance(body, str) or t is None:
                A["rows_unusable"] += 1
                continue
            ts = t / 1e9
            if not (t_lo <= ts < t_hi):
                A["payloads_outside_window"] += 1
                continue
            try:
                d = json.loads(body)
            except Exception:
                A["rows_bad_json"] += 1
                continue
            A["rows"] += 1
            i = bisect.bisect_left(polls, ts) - 1
            if i < 0 or ts - polls[i] > OUTAGE_S:
                A["baseline_cleared_poll_gap_gt_10s"] += len(base)
                A["payloads_after_poll_gap_gt_10s"] += 1
                base.clear()
            valid = set()
            for eid, e in (d.get("events") or {}).items():
                if not isinstance(e, dict):
                    continue
                lg = str((e.get("info") or {}).get("league") or "")
                game = sport if sport != "esports" else (norm(lg.split(" - ", 1)[0]) if " - " in lg else "unparsed")
                ti = e.get("team_info") or {}
                h, a = norm((ti.get("home") or {}).get("name")), norm((ti.get("away") or {}).get("name"))
                for mid, m in (e.get("odds") or {}).items():
                    if not isinstance(m, dict):
                        continue
                    name = m.get("name") or "?"
                    kind = kind_of(sport, name)
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
                    s0 = span.get((eid, kind), (ts, ts))
                    span[(eid, kind)] = (s0[0], ts)
                    if k in base:
                        dlt = ph - base[k]
                        if abs(dlt) >= MOVE_FREE:
                            moves[eid].append(ts)
                        if abs(dlt) >= THR:
                            ev.append((eid, kind, ts, h if dlt > 0 else a, h, a, game))
                            A["events"] += 1
                    base[k] = ph
            for k in [k for k in base if k not in valid]:
                del base[k]
                A["baseline_cleared_not_valid_open"] += 1
    return ev, moves, span, dict(counters=dict(A), market_names_used=dict(used), market_names_excluded=dict(excl.most_common(40)))


class Books:
    """PM recorder rows as per-token step functions + a recorder heartbeat (any token)."""

    def __init__(self, dirs, need, drops, t_lo=0.0, t_hi=1e18):
        self.s, hb = collections.defaultdict(list), set()
        for d in dirs:
            for p in sorted(glob.glob(os.path.join(d, "books*.jsonl")) + glob.glob(os.path.join(d, "books*.jsonl.gz"))):
                mh = re.search(r"books-(\d{10})", os.path.basename(p))
                if mh and not (t_lo - 7200 <= calendar.timegm(time.strptime(mh.group(1), "%Y%m%d%H")) < t_hi + 3600):
                    drops["pm_book_files_skipped_outside_window"] += 1
                    continue
                for r in counted_lines(p, drops, "pm_books"):
                    ms = r.get("recv_ms") if r.get("recv_ms") is not None else r.get("ms")
                    if ms is None or not (t_lo - 3600 <= ms / 1000.0 < t_hi + 3600):
                        continue
                    pr = parse_book_row(r, drops)
                    tk = r.get("tk") or r.get("asset")
                    if ms is not None:
                        hb.add(int(ms // 1000))
                    if pr and tk in need:
                        self.s[pr[0]].append((pr[1], pr[2], pr[3]))
        self.ts = {}
        for tk in self.s:
            self.s[tk].sort()
            self.ts[tk] = [x[0] for x in self.s[tk]]
        self.hb = sorted(hb)

    def mid(self, tk, x, plant=None):
        """last real row at or before x; plant=(t_p, c): from t_p on, that raw row is shifted by c (bid and ask) and re-parsed by the SAME parse path as every real row."""
        i = bisect.bisect_right(self.ts.get(tk, []), x) - 1
        if i < 0:
            return None
        tt, bb, ba = self.s[tk][i]
        if plant and x >= plant[0]:
            pr = parse_book_row({"ms": tt * 1000.0, "tk": tk, "bids": [{"price": repr(bb + plant[1])}], "asks": [{"price": repr(ba + plant[1])}]})
            return mid_of(pr[2], pr[3])
        return mid_of(bb, ba)

    def alive(self, lo, hi):
        b = lo
        while b <= hi:
            j = bisect.bisect_left(self.hb, int(b))
            if j >= len(self.hb) or self.hb[j] > b + HB_BUCKET:
                return False
            b += HB_BUCKET
        return True

    def d(self, tk, t, w, plant=None):
        m = [self.mid(tk, t + dt, plant) for dt in (w, 0, -w)]
        return None if None in m else (m[0] - m[1]) - (m[1] - m[2])


def mean(x):
    x = list(x)
    return sum(x) / len(x) if x else None


def t_upper(n, conf=0.95):
    lo, hi = 0.0, 50.0
    for _ in range(100):
        m = (lo + hi) / 2
        if t_sf(m, n - 1) > 1 - conf:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def n_max_from_sigma(sigma_c):
    return int(min(100, max(SIZING_BLOCK + 1, math.ceil(6.185 * sigma_c ** 2 / 0.25))))


def decide(means, events, n_max, ok):
    """per-match mean d10 list (scored matches only) -> verdict dict. ok = dict(placebo, plants, swap, shift) booleans."""
    n, mu, se, t, z = cell_t(means)
    out = dict(n=n, mean=mu, se=se, t=t, z_eq=z, n_max=n_max)
    bad = [k for k, v in ok.items() if not v]
    if bad:
        out["verdict"] = "unknown (control failed: %s; no number)" % ", ".join(bad)
        out["mean"] = out["se"] = out["t"] = out["z_eq"] = None
        return out
    if n < FUTILITY_MIN and (n < 2 or events < MIN_EVENTS):
        out["verdict"] = "unknown (%d scored matches, %d events)" % (n, events)
        return out
    if z is None:
        out["verdict"] = "unknown (no variance)"
        return out
    zb = float("inf") if n < 1 else C_BM / math.sqrt(min(1.0, n / n_max))
    ub = mu + t_upper(n) * se if n >= 2 else None
    out.update(boundary_z=zb, upper95=ub)
    if events >= MIN_EVENTS and z >= zb and mu >= MIN_EFFECT:
        out["verdict"] = "meets bar (needs audit)"
    elif z <= -zb or (n >= FUTILITY_MIN and ub is not None and ub < 0):
        out["verdict"] = "price moves first, closed (needs audit)"
    elif n >= FUTILITY_MIN and ub is not None and ub < DRIFT_TOL:
        out["verdict"] = "no lead at 0.2c or more, closed (needs audit)"
    else:
        out["verdict"] = "no pass yet (not a no-lead)"
    return out


def score(ev, moves, span, pm_markets, books, seed, c, drops):
    """-> per cell dict of per-match results + control tallies."""
    idx = collections.defaultdict(list)
    for m in pm_markets:
        idx[m["kind"]].append(m)
    sel, ml = {}, {}
    for (eid, kind, t, rise, h, a, game) in ev:
        key = (eid, kind)
        if key not in ml:
            cands = []
            for m in idx.get(kind, []):
                outs = [norm(o) for o in m["outcomes"]]
                mp = map_teams(h, a, outs) if len(outs) == 2 else None
                st = m.get("start")
                if mp and (not st or abs(iso(st) - t) < 36 * 3600):
                    cands.append((m, mp, outs))
            ml[key] = cands
            if len(cands) == 1:
                sel[key] = cands[0]
        if len(ml[key]) != 1:
            drops["events_no_pm_market" if not ml[key] else "events_ambiguous_market_excluded"] += 1
    per = collections.defaultdict(list)
    for (eid, kind, t, rise, h, a, game) in ev:
        if (eid, kind) in sel:
            per[(game, kind, eid)].append((t, rise, h, a))
    cells = collections.defaultdict(list)
    for (game, kind, eid), L in sorted(per.items()):
        m, (ih, ia), outs = sel[(eid, kind)]
        if len(L) > CAP:
            drops["events_dropped_by_match_cap"] += len(L) - CAP
            L = sorted(sorted(L, key=lambda x: hashlib.sha256(("%s|cap|%s|%r" % (seed, eid, x[0])).encode()).hexdigest())[:CAP])
        rec = collections.defaultdict(list)
        s0, s1 = span.get((eid, kind), (None, None))
        for (t, rise, h, a) in L:
            i = ih if rise == h else ia
            tk, otk = m["tokens"][i], m["tokens"][1 - i]
            wmax = max(WINDOWS)
            if not books.alive(t - wmax - HB_BUCKET, t + wmax):
                drops["events_pm_recorder_silent"] += 1
                continue
            real = {w: books.d(tk, t, w) for w in WINDOWS}
            if real[W_PRIMARY] is None:
                drops["events_no_own_book_mid"] += 1
                continue
            prng = seed_rng(seed, "plc", eid, repr(t))
            pl = {w: [] for w in WINDOWS}
            for _ in range(NPLC):
                for _try in range(50):
                    if s0 is None or s1 - s0 < 4 * FREE_S:
                        break
                    tp = prng.uniform(s0 + FREE_S, s1 - FREE_S)
                    if all(abs(tp - x) > FREE_S for x in moves.get(eid, [])):
                        ptk, sg = prng.choice(m["tokens"]), prng.choice((-1, 1))
                        for w in WINDOWS:
                            x = books.d(ptk, tp, w)
                            if x is not None:
                                pl[w].append(sg * x)
                        break
            if not pl[W_PRIMARY]:
                drops["events_no_event_free_placebo_time"] += 1
                continue
            row = {w: real[w] for w in WINDOWS if real[w] is not None}
            row["placebo"] = mean(pl[W_PRIMARY])
            row["swap"] = books.d(otk, t, W_PRIMARY)
            row["shift"] = books.d(tk, t + SHIFT_S, W_PRIMARY)
            for sgn, nm in ((1, "plus"), (-1, "minus")):
                row[nm] = books.d(tk, t, W_PRIMARY, (t + PLANT_AT, sgn * c))
            for k, v in row.items():
                if v is not None:
                    rec[k].append(v)
            rec["_t"].append(t)
            rec["_base10"].append(real[W_PRIMARY])
            rec["_plus_delta"].append(None if row.get("plus") is None else row["plus"] - real[W_PRIMARY])
            rec["_minus_delta"].append(None if row.get("minus") is None else row["minus"] - real[W_PRIMARY])
        if rec[W_PRIMARY]:
            cells["%s|%s" % (game, kind)].append(dict(eid=eid, t0=min(rec["_t"]), n=len(rec[W_PRIMARY]),
                                                      means={k: mean(v) for k, v in rec.items() if not str(k).startswith("_") and v},
                                                      plus_d=mean(x for x in rec["_plus_delta"] if x is not None),
                                                      minus_d=mean(x for x in rec["_minus_delta"] if x is not None)))
    return cells


def cell_report(ms, c):
    ms = sorted(ms, key=lambda r: r["t0"])
    block, scored = ms[:SIZING_BLOCK], ms[SIZING_BLOCK:]
    out = dict(matches_total=len(ms), sizing_block=len(block), scored=len(scored))
    if len(block) < SIZING_BLOCK:
        out["verdict"] = "unknown (sizing block incomplete: %d of %d matches; nothing scored)" % (len(block), SIZING_BLOCK)
        return out
    bm = [r["means"][W_PRIMARY] for r in block]
    sig = (sum((x - mean(bm)) ** 2 for x in bm) / (len(bm) - 1)) ** 0.5 * 100.0
    nmax = n_max_from_sigma(sig)
    out.update(sigma_cents=sig, n_max=nmax)
    allm = ms  # control checks use every usable match (the controls are not the test)
    ev = sum(r["n"] for r in scored)
    pm = mean(r["means"].get("placebo") for r in allm if r["means"].get("placebo") is not None)
    rm = mean(r["means"][W_PRIMARY] for r in allm)
    sw = mean(r["means"]["swap"] for r in allm if r["means"].get("swap") is not None)
    sh = mean(r["means"]["shift"] for r in allm if r["means"].get("shift") is not None)
    pp = mean(r["plus_d"] for r in allm if r["plus_d"] is not None)
    mp = mean(r["minus_d"] for r in allm if r["minus_d"] is not None)
    ok = dict(placebo=pm is not None and abs(pm) <= DRIFT_TOL,
              plants=pp is not None and mp is not None and 0.95 <= pp / c <= 1.05 and 0.95 <= mp / -c <= 1.05,
              swap=sw is not None and abs(sw + rm) <= DRIFT_TOL,
              shift=sh is not None and abs(sh) <= DRIFT_TOL)
    out.update(controls=dict(placebo_mean_d10=pm, plant_plus_recovery=None if pp is None else pp / c, plant_minus_recovery=None if mp is None else mp / -c,
                             swap_mean_d10=sw, real_mean_d10_all=rm, shift_mean_d10=sh, ok=ok), events_scored=ev)
    out["d10"] = decide([r["means"][W_PRIMARY] for r in scored], ev, nmax, ok)
    out["verdict"] = out["d10"]["verdict"]
    out["secondary"] = {("d%d" % w): dict(zip(("n", "mean", "se", "t", "z_eq"), cell_t([r["means"][w] for r in scored if w in r["means"]]))) for w in (2, 60)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sport", choices=("esports", "tennis", "hockey_nhl"), required=True)
    ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--poll-log", action="append", required=True)
    ap.add_argument("--start-iso", required=True)
    ap.add_argument("--end-iso", required=True)
    ap.add_argument("--clock-note", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261124)
    ap.add_argument("--plant-c", type=float, default=PLANT_C)
    a = ap.parse_args()
    t_lo, t_hi = iso(a.start_iso), iso(a.end_iso)
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no goalserve files matched")
    drops, polls = collections.Counter(), []
    for g in a.poll_log:
        for p in sorted(glob.glob(g)):
            for r in counted_lines(p, drops, "poll_log"):
                e = r.get(a.sport) or {}
                if e.get("recv_ns") and "err" not in e:
                    polls.append(e["recv_ns"] / 1e9)
    polls.sort()
    if not polls:
        raise SystemExit("no polls read from --poll-log")
    if polls[-1] < t_hi + 60:
        raise SystemExit("poll log ends %.0f s before --end-iso + 60 s: run again later" % (t_hi + 60 - polls[-1]))
    have = set()
    for f in files:
        m = re.search(r"%s_(\d{10})" % a.sport, os.path.basename(f))
        if not m:
            raise SystemExit("cannot read the hour from file name %s" % f)
        have.add(calendar.timegm(time.strptime(m.group(1), "%Y%m%d%H")))
    polled = {3600 * int(x // 3600) for x in polls if t_lo <= x < t_hi}
    miss = sorted(h for h in polled if h not in have)
    if miss:
        raise SystemExit("hour file(s) missing although polls show capture running: %s" % ", ".join(time.strftime("%Y%m%d%H", time.gmtime(h)) for h in miss))
    ev, moves, span, audit = gs_events(files, polls, t_lo, t_hi, a.sport)
    if audit["counters"].get("goalserve_rows_truncated_files", 0) or audit["counters"].get("goalserve_rows_bad_lines", 0) > 50:
        raise SystemExit("unreadable or truncated hour file(s): %s" % json.dumps(audit["counters"]))
    pm_markets = load_pm(a.pm)
    need = {tk for m in pm_markets for tk in m["tokens"]}
    books = Books(a.pm, need, drops, t_lo, t_hi)
    cells = score(ev, moves, span, pm_markets, books, a.seed, a.plant_c, drops)
    res = dict(version="v3 UNSIGNED", sport=a.sport, window=[a.start_iso, a.end_iso], clock_note=a.clock_note, seed=a.seed, goalserve_audit=audit, drops=dict(drops),
               pm_markets=len(pm_markets), cells={k: cell_report(v, a.plant_c) for k, v in sorted(cells.items())})
    res["plain_summary"] = "; ".join("%s: %s" % (k, v["verdict"]) for k, v in res["cells"].items()) or "no cell had a usable event"
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    print(res["plain_summary"])


if __name__ == "__main__":
    main()
