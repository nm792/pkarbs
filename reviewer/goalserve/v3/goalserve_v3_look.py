#!/usr/bin/env python3
"""Goalserve in-play odds vs Polymarket own-token books, SPEC v3 (reviewer/goalserve/SPEC-v3-pm-inputs-and-controls-2026-11-22.md).
Written by the Reviewer 24 Nov 2026 (coordinator order 14:50Z). Read-only: reads files, writes one JSON. Stdlib only. Not yet signed by a checker.

Inputs
  --sport esports|hockey_nhl|tennis
  --gs-files GLOB   hour files <sport>_<YYYYMMDDHH>.jsonl.gz of {"recv_ns", "body"} (live/goalserve/capture_store_all.py, locked build ffe21ca1)
  --poll-log GLOB   goalserve_<date>.jsonl poll logs (same capture); a payload whose preceding poll is > 10 s earlier clears every baseline
  --pm DIR          Polymarket recorder dir: markets.jsonl + books-*.jsonl[.gz] (pm_cs2_books.js slim) and/or books.jsonl[.gz] (pm_sport_books.js)
  --t-start ISO     first payload time used (default 2026-11-23T17:00:11Z = start of the locked capture PID 753838; SPEC 7.2 makes earlier capture invalid)
  --t-end ISO       optional; default = last whole UTC hour at least 60 s before the last poll

Rules (SPEC v3 sections in brackets)
  Event [3]: vig-removed home probability moves >= 2c between two consecutive stored payloads in which the market is valid and open in both
     (as v2 V1; a payload where the market is missing, suspended or invalid clears the baseline, so a reopen price is never an event).
     Markets: esports 'Home/Away' (Match Winner) and 'Home/Away (map N)' (Map N Winner); hockey_nhl 'Home/Away' with league exactly NHL; tennis 'To Win'.
  Join [1]: Goalserve (home, away) to a Polymarket market of the same kind whose two outcomes each match one team by whole-word containment
     ('NJ Devils' ~ 'Devils'); a market start time, when present, within 12 h of the first payload. Zero candidates or more than one: dropped, counted.
  Statistic [3], on the rising team's OWN token mid (never inferred from the other token): dW = [mid(t+W) - mid(t)] - [mid(t) - mid(t-W)], W = 10 (primary),
     2 and 60 (reported). mid(x) = last book row at or before x; a one-sided row makes the mid undefined until the next two-sided row.
     Needs an own-token row within +-300 s of t. d10 > 0 = the price moved with the odds AFTER the odds moved, relative to before.
  Cap: at most 40 events per (match, kind), chosen by a hash of the event (reproducible on later looks).
  Placebo [4]: per event 10 times in the same (match, kind) span with no Goalserve move of 1c or more within +-120 s; random token, random sign; same d10.
     Cell placebo mean outside +-0.2c -> 'placebo drift', no verdict.
  Plants [4]: raw book rows (recorder format) through the same parse path: +c and -c at t+5 s on the rising token; swap = +c at t+5 s on the other token
     read as rising. Recovery 95-105% of c in the per-match mean for all three, else 'plant not recovered', no verdict.
  Nulls [4]: label swap (other token read as rising) must give the negated mean within 0.2c; time shift (+600 s) must give 0 within 0.2c. Else no verdict.
  Power [5]: matches ordered by first usable event time. The first 12 are a SIZING BLOCK (never tested): sigma = sd of their per-match mean d10,
     N_MAX = min(100, max(12, ceil(6.185 sigma^2 / 0.005^2))). The test uses matches 13 .. 12 + N_MAX.
  Stops [6]: success z_eq * sqrt(n_test / N_MAX) >= 2.60 (one-sided alpha 0.0093 per cell). At n_test >= min(30, N_MAX): if the one-sided 95% upper bound of the
     mean d10 < 0 -> 'price moves first, closed'; else if < 0.2c -> 'no lead at 0.2c or more, closed'. Primary cells: cs2|Match Winner,
     nhl|Match Winner, tennis|Match Winner; others informational.
  Completeness: STOP (exit 2, no result) if an hour file is missing for an hour in which the poll log shows the capture polling, or a file is truncated.
  Resolution [2]: Goalserve event times carry about 2 s of receive delay (poll cycle 1.8 s), so d2 cannot be read and no lead finer than about 2 s is claimed.
Usage: python3 -I goalserve_v3_look.py --sport esports --gs-files '/V/pkarbs/goalserve/esports_payloads/esports_2026112*.jsonl.gz' \
         --poll-log '/V/pkarbs/goalserve/goalserve_2026112*.jsonl' --pm /V/pkarbs/pmcs2 --out result.json
Self test: python3 -I test_goalserve_v3_look.py
"""
import argparse, bisect, calendar, collections, glob, gzip, hashlib, json, math, os, random, re, sys, time

THR, MOVE1, CAP, NPLC, PLC_EXCL_S = 0.02, 0.01, 40, 10, 120.0
OUTAGE_S, ALIVE_S, JOIN_H = 10.0, 300.0, 12.0
PLANT_C, PLANT_DT, SHIFT_S = 0.01, 5.0, 600.0
TOL_NULL, MIN_LEAD, DELTA, C_BM, SIZING, N_CAP, N_FLOOR, FUT_N = 0.002, 0.002, 0.005, 2.60, 12, 100, 12, 30
WINDOWS = (2, 10, 60)
OPEN = (0, "0", False, None)
DEFAULT_T_START = "2026-11-23T17:00:11Z"
PRIMARY = ("cs2|Match Winner", "nhl|Match Winner", "tennis|Match Winner")
MAP_RE = re.compile(r"^home away map (\d+)$")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def iso(s):
    return calendar.timegm(time.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M:%S"))


def opn(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def counted_lines(p, cnt, key):
    try:
        with opn(p) as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    cnt[key + "_bad_lines"] += 1
    except (EOFError, OSError):
        cnt[key + "_truncated_files"] += 1


def num(x):
    try:
        v = float(x)
        return v if v > 1.0 else None
    except (TypeError, ValueError):
        return None


def kind_of(sport, name):
    n = norm(name)
    if sport == "tennis":
        return "Match Winner" if n == "to win" else None
    if n == "home away":
        return "Match Winner"
    m = MAP_RE.match(n)
    return "Map %s Winner" % m.group(1) if (m and sport == "esports") else None


def game_of(sport, league):
    if sport == "tennis":
        return "tennis"
    if sport == "hockey_nhl":
        return "nhl" if norm(league) == "nhl" else None      # the hockey feed also carries college and other leagues
    return norm(league.split(" - ", 1)[0]) if " - " in league else None


def name_match(gs, pm):
    """whole-word containment either way; the shorter side must have >= 2 characters (esports names such as G2, B8, 9z)."""
    a, b = norm(gs), norm(pm)
    if not a or not b:
        return False
    if a == b:
        return True
    s, l = (a, b) if len(a) <= len(b) else (b, a)
    return len(s) >= 2 and (" %s " % s) in (" %s " % l)


def pm_kind(m):
    if m.get("kind"):
        return m["kind"]
    q = m.get("q") or m.get("title") or ""
    mm = re.search(r"(?:map|game)\s*(\d+)", q, re.I)
    if mm:
        return "Map %s Winner" % mm.group(1)
    if (m.get("smt") or "moneyline") == "moneyline" or re.search(r"match\s*winner", q, re.I):
        return "Match Winner"
    return None


def load_markets(dirs, cnt):
    out, seen = [], set()
    for d in dirs:
        for p in (os.path.join(d, "markets.jsonl"), os.path.join(d, "markets.jsonl.gz")):
            if not os.path.exists(p):
                continue
            for m in counted_lines(p, cnt, "pm_markets"):
                o, tk = m.get("outcomes") or [], m.get("tokens") or []
                if len(o) != 2 or len(tk) != 2 or m.get("cond") in seen:
                    continue
                k = pm_kind(m)
                if not k:
                    cnt["pm_markets_kind_unknown"] += 1
                    continue
                seen.add(m.get("cond"))
                st = None
                try:
                    st = iso(str(m["start"])[:19]) if m.get("start") else None
                except Exception:
                    st = None
                out.append(dict(cond=m.get("cond"), kind=k, outcomes=list(o), tokens=list(tk), start=st, q=m.get("q")))
    return out


def join(markets, kind, h, a, t_first):
    c = []
    for m in markets:
        if m["kind"] != kind:
            continue
        if m["start"] is not None and abs(m["start"] - t_first) > JOIN_H * 3600:
            continue
        o0h, o0a, o1h, o1a = (name_match(h, m["outcomes"][0]), name_match(a, m["outcomes"][0]), name_match(h, m["outcomes"][1]), name_match(a, m["outcomes"][1]))
        if o0h and o1a and not o0a and not o1h:
            c.append((m, {"h": m["tokens"][0], "a": m["tokens"][1]}))
        elif o0a and o1h and not o0h and not o1a:
            c.append((m, {"h": m["tokens"][1], "a": m["tokens"][0]}))
    return c


def parse_book_row(r, cnt=None):
    """ONE parse path for every book row, real or planted -> (token, t_s, best_bid or None, best_ask or None) or None."""
    tk = r.get("asset") or r.get("tk") or r.get("token")
    tms = r.get("recv_ms") if r.get("recv_ms") is not None else r.get("ms")
    if tk is None or tms is None:
        if cnt is not None:
            cnt["book_rows_no_token_or_time"] += 1
        return None

    def px(L):
        v = []
        for x in L or []:
            try:
                v.append(float(x["price"] if isinstance(x, dict) else x[0]))
            except Exception:
                pass
        return v
    b, s = px(r.get("bids")), px(r.get("asks"))
    if (not b or not s) and cnt is not None:
        cnt["book_rows_one_sided"] += 1
    return tk, float(tms) / 1000.0, (max(b) if b else None), (min(s) if s else None)


def seed_rng(*parts):
    return random.Random(int.from_bytes(hashlib.sha256("|".join(str(x) for x in parts).encode()).digest()[:8], "big"))


def phi_sf(x):
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def z_from_p(p):
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
        d = 1.0 / ((1.0 + aa * d) if abs(1.0 + aa * d) > 1e-300 else 1e-300)
        c = (1.0 + aa / c) if abs(1.0 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 / ((1.0 + aa * d) if abs(1.0 + aa * d) > 1e-300 else 1e-300)
        c = (1.0 + aa / c) if abs(1.0 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        if abs(d * c - 1.0) < 3e-16:
            break
    return h


def t_sf(t, df):
    if t == 0:
        return 0.5
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    ib = front * _betacf(a, b, x) / a if x < (a + 1.0) / (a + b + 2.0) else 1.0 - front * _betacf(b, a, 1.0 - x) / b
    return 0.5 * ib if t > 0 else 1.0 - 0.5 * ib


def t_q95(df):
    lo, hi = 0.0, 50.0
    for _ in range(100):
        m = (lo + hi) / 2
        if t_sf(m, df) > 0.05:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def stats(x):
    n = len(x)
    if n == 0:
        return dict(n=0, mean=None, sd=None, se=None)
    mu = sum(x) / n
    sd = (sum((v - mu) ** 2 for v in x) / (n - 1)) ** 0.5 if n > 1 else None
    return dict(n=n, mean=mu, sd=sd, se=(sd / math.sqrt(n)) if sd is not None else None)


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def load_polls(globs, sport, cnt):
    ts = []
    for g in globs:
        for p in sorted(glob.glob(g)):
            for r in counted_lines(p, cnt, "poll_log"):
                e = r.get(sport) or {}
                if e.get("recv_ns") and "err" not in e:
                    ts.append(e["recv_ns"] / 1e9)
    return sorted(ts)


def gs_events(sport, files, polls, t_lo, t_hi):
    """-> events [(eid, kind, t, rising 'h'|'a', home, away, game)], moves {(eid,kind): [t of every >= 1c move]}, span {(eid,kind): [t_first, t_last]}, audit."""
    A, prefixes, names = collections.Counter(), collections.Counter(), collections.Counter()
    base, ev = {}, []
    moves, span = collections.defaultdict(list), {}
    for p in sorted(files):
        for r in counted_lines(p, A, "goalserve_rows"):
            body, tn = r.get("body"), r.get("recv_ns")
            if not isinstance(body, str) or tn is None:
                A["rows_unusable"] += 1
                continue
            t = tn / 1e9
            if not (t_lo <= t < t_hi):
                A["payloads_outside_window"] += 1
                continue
            try:
                d = json.loads(body)
            except Exception:
                A["rows_bad_json"] += 1
                continue
            A["payloads"] += 1
            i = bisect.bisect_left(polls, t) - 1
            if i < 0 or t - polls[i] > OUTAGE_S:
                A["payloads_after_poll_gap_gt_10s"] += 1
                A["baselines_cleared_poll_gap"] += len(base)
                base.clear()
            valid = set()
            for eid, e in (d.get("events") or {}).items():
                if not isinstance(e, dict):
                    continue
                lg = str((e.get("info") or {}).get("league") or "")
                game = game_of(sport, lg)
                prefixes[game or ("excluded:" + norm(lg)[:30])] += 1
                if not game:
                    continue
                ti = e.get("team_info") or {}
                h, a = (ti.get("home") or {}).get("name") or "", (ti.get("away") or {}).get("name") or ""
                if not norm(h) or not norm(a):
                    A["skip_no_team_names"] += 1
                    continue
                for mid, m in (e.get("odds") or {}).items():
                    if not isinstance(m, dict):
                        continue
                    kind = kind_of(sport, m.get("name"))
                    if not kind:
                        continue
                    names[m.get("name")] += 1
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
                        side.append("h" if n in ("home", "1", norm(h)) else "a" if n in ("away", "2", norm(a)) else None)
                    if sorted(side, key=str) != ["a", "h"]:
                        A["skip_participant_mapping"] += 1
                        continue
                    ph = (1 / o[side.index("h")]) / (1 / o[0] + 1 / o[1])
                    k = (eid, str(mid))
                    key = (eid, kind)
                    valid.add(k)
                    sp = span.setdefault(key, [t, t])
                    sp[1] = t
                    if k in base:
                        dlt = ph - base[k][0]
                        if abs(dlt) >= MOVE1:
                            moves[key].append(t)
                        if abs(dlt) >= THR:
                            ev.append((eid, kind, t, "h" if dlt > 0 else "a", h, a, game))
                            A["events"] += 1
                    base[k] = (ph, kind)
            for k in [k for k in base if k not in valid]:
                del base[k]
                A["baselines_cleared_not_valid_open"] += 1
    for k in moves:
        moves[k].sort()
    return ev, moves, span, dict(counters=dict(A), league_prefixes=dict(prefixes.most_common(40)), market_names_used=dict(names))


class Books:
    def __init__(self):
        self.rows = collections.defaultdict(list)
        self.ts = {}

    def load(self, dirs, need, t_lo, t_hi, cnt):
        files = []
        for d in dirs:
            for pat in ("books-*.jsonl", "books-*.jsonl.gz", "books.jsonl", "books.jsonl.gz"):
                files += sorted(glob.glob(os.path.join(d, pat)))
        for p in files:
            for r in counted_lines(p, cnt, "pm_books"):
                tk = r.get("asset") or r.get("tk") or r.get("token")
                if tk not in need:
                    continue
                pr = parse_book_row(r, cnt)
                if pr and t_lo - 900 <= pr[1] <= t_hi + 900:
                    self.rows[tk].append(pr[1:])
                    cnt["pm_book_rows_used"] += 1
        for tk in self.rows:
            self.rows[tk].sort(key=lambda x: x[0])
            self.ts[tk] = [x[0] for x in self.rows[tk]]
        return [os.path.basename(f) for f in files]

    def mid(self, tk, x, plants=()):
        L = self.ts.get(tk)
        if not L:
            return None
        i = bisect.bisect_right(L, x) - 1
        if i < 0:
            return None
        t0, bb, ba = self.rows[tk][i]
        dl = sum(c for (tt, c, tok) in plants if tok == tk and x >= tt)
        if dl:
            # plant = a raw row in the recorder's format, shifted by dl, through the SAME parse path as every real row
            if bb is None or ba is None:
                return None
            pr = parse_book_row({"recv_ms": t0 * 1000.0, "asset": tk, "bids": [{"price": repr(bb + dl)}], "asks": [{"price": repr(ba + dl)}]})
            bb, ba = pr[2], pr[3]
        if bb is None or ba is None:
            return None
        return (bb + ba) / 2.0

    def alive(self, tk, t):
        L = self.ts.get(tk, [])
        i = bisect.bisect_left(L, t - ALIVE_S)
        return i < len(L) and L[i] <= t + ALIVE_S

    def d(self, tk, t, W, plants=()):
        m = [self.mid(tk, t + W, plants), self.mid(tk, t, plants), self.mid(tk, t - W, plants)]
        if None in m:
            return None
        return (m[0] - m[1]) - (m[1] - m[2])


def score_cell(cell, recs, n_floor=N_FLOOR):
    """recs: per-event dicts with m (match key), t, d10, d2, d60, plc, pP, pM, pS, sw, ts. -> cell result."""
    first = {}
    for e in recs:
        first[e["m"]] = min(first.get(e["m"], e["t"]), e["t"])
    order = sorted(first, key=lambda k: (first[k], str(k)))
    by = collections.defaultdict(list)
    for e in recs:
        by[e["m"]].append(e)

    def pm(key, ms):
        return [mean(e[key] for e in by[m]) for m in ms if mean(e[key] for e in by[m]) is not None]

    def pdiff(k1, k0, ms):
        return [mean((e[k1] - e[k0]) for e in by[m] if e[k1] is not None and e[k0] is not None) for m in ms]

    allm = order
    res = dict(cell=cell, role="primary" if cell in PRIMARY else "informational (cannot be called a pass)", n_matches=len(allm), n_events=len(recs),
               matches_by_day=dict(collections.Counter(time.strftime("%Y-%m-%d", time.gmtime(first[m])) for m in allm)))
    # controls over every match in the cell (plants, placebo, nulls are pipeline checks, not tests)
    plc = stats(pm("plc", allm))
    rec = {}
    for nm, k1, k0, exp in (("plus", "pP", "d10", PLANT_C), ("minus", "pM", "d10", -PLANT_C), ("swap", "pS", "sw", PLANT_C)):
        v = [x for x in pdiff(k1, k0, allm) if x is not None]
        r = (mean(v) / exp) if v else None
        rec[nm] = dict(mean_shift=mean(v), recovery=r, ok=r is not None and 0.95 <= r <= 1.05)
    main_mean = mean(pm("d10", allm))
    swap_mean = mean(pm("sw", allm))
    shift_mean = mean(pm("ts", allm))
    ctrl = dict(placebo_mean=plc["mean"], placebo_ok=plc["mean"] is not None and abs(plc["mean"]) <= TOL_NULL, plants=rec,
                label_swap_mean=swap_mean, label_swap_ok=None if (swap_mean is None or main_mean is None) else abs(swap_mean + main_mean) <= TOL_NULL,
                time_shift_mean=shift_mean, time_shift_ok=None if shift_mean is None else abs(shift_mean) <= TOL_NULL)
    res["controls"] = ctrl
    controls_ok = bool(ctrl["placebo_ok"] and all(v["ok"] for v in rec.values()) and ctrl["label_swap_ok"] and ctrl["time_shift_ok"])
    res["controls_ok"] = controls_ok
    sz = order[:SIZING]
    szs = stats(pm("d10", sz))
    res["sizing_block"] = dict(matches=len(sz), mean_d10=szs["mean"], sigma_d10=szs["sd"], mean_d2=mean(pm("d2", sz)), mean_d60=mean(pm("d60", sz)),
                               note="sizing block only: sets N_MAX, is never tested (SPEC v3 section 5)")
    if len(sz) < SIZING or szs["sd"] is None:
        res["verdict"] = "sizing block incomplete (%d of %d matches); no test read" % (len(sz), SIZING)
        return res
    nmax = min(N_CAP, max(n_floor, int(math.ceil(6.185 * szs["sd"] ** 2 / DELTA ** 2))))
    tm = order[SIZING:SIZING + nmax]
    res["n_max"] = nmax
    res["matches_beyond_n_max"] = max(0, len(order) - SIZING - nmax)
    s = stats(pm("d10", tm))
    res["test"] = dict(n_matches=s["n"], mean_d10=s["mean"], se=s["se"], mean_d2=mean(pm("d2", tm)), mean_d60=mean(pm("d60", tm)),
                       share_events_d10_pos=(100.0 * sum(1 for m in tm for e in by[m] if e["d10"] > 0) / max(1, sum(len(by[m]) for m in tm))))
    if s["n"] < 2 or not s["se"]:
        res["verdict"] = "test block has %d matches; no test read yet" % s["n"]
        return res
    tstat = s["mean"] / s["se"]
    z = z_from_p(min(max(t_sf(tstat, s["n"] - 1), 1e-300), 1 - 1e-16))
    info = min(1.0, s["n"] / nmax)
    ub = s["mean"] + t_q95(s["n"] - 1) * s["se"]
    res["test"].update(t_stat=tstat, z_eq=z, information_time=info, z_times_sqrt_t=z * math.sqrt(info), boundary=C_BM, upper95=ub)
    if not controls_ok:
        res["verdict"] = "no verdict: controls failed (%s)" % ", ".join(k for k, v in (("placebo drift", ctrl["placebo_ok"]), ("plant not recovered", all(v["ok"] for v in rec.values())),
                                                                                       ("label swap", ctrl["label_swap_ok"]), ("time shift", ctrl["time_shift_ok"])) if not v)
    elif z * math.sqrt(info) >= C_BM:
        v = "lead: odds move before the price (z_eq x sqrt(t) %.2f >= %.2f)" % (z * math.sqrt(info), C_BM)
        res["verdict"] = v if cell in PRIMARY else "(informational) " + v
    elif s["n"] >= min(FUT_N, nmax) and ub < 0:
        res["verdict"] = "price moves first, closed (upper95 %.4f < 0)" % ub
    elif s["n"] >= min(FUT_N, nmax) and ub < MIN_LEAD:
        res["verdict"] = "no lead at 0.2c or more, closed (upper95 %.4f)" % ub
    elif s["n"] >= nmax:
        res["verdict"] = "N_MAX reached without a pass: closed, no lead detected"
    else:
        res["verdict"] = "no pass yet (not a no-lead): %d of %d test matches" % (s["n"], nmax)
    return res


def run(a):
    t_lo = iso(a.t_start)
    files = sorted({f for g in a.gs_files for f in glob.glob(g)})
    if not files:
        raise SystemExit("STOP: no Goalserve hour files matched")
    cnt = collections.Counter()
    polls = load_polls(a.poll_log, a.sport, cnt)
    if not polls:
        raise SystemExit("STOP: no polls for %s in --poll-log" % a.sport)
    t_hi = iso(a.t_end) if a.t_end else 3600.0 * math.floor((polls[-1] - 60) / 3600.0)
    if t_hi <= t_lo:
        raise SystemExit("STOP: window empty (t_end <= t_start)")
    have = set()
    for f in files:
        m = re.search(r"_(\d{10})\.jsonl", os.path.basename(f))
        if m:
            have.add(calendar.timegm(time.strptime(m.group(1), "%Y%m%d%H")))
    polled = {3600.0 * math.floor(x / 3600.0) for x in polls if t_lo <= x < t_hi}
    missing = sorted(h for h in polled if h not in have)
    if missing and not a.allow_missing:
        raise SystemExit("STOP: hour file(s) missing while the poll log shows the capture polling: %s" % ", ".join(time.strftime("%Y%m%d%H", time.gmtime(h)) for h in missing))
    ev, moves, span, audit = gs_events(a.sport, files, polls, t_lo, t_hi)
    if audit["counters"].get("goalserve_rows_truncated_files"):
        raise SystemExit("STOP: truncated Goalserve hour file(s): %s" % json.dumps(audit["counters"]))
    markets = load_markets(a.pm, cnt)
    sel, mlist = {}, {}
    for (eid, kind, t, rise, h, aw, game) in ev:
        key = (eid, kind)
        if key in mlist:
            mlist[key]["n_events"] += 1
            continue
        c = join(markets, kind, h, aw, span.get(key, [t])[0])
        mlist[key] = dict(eid=eid, kind=kind, game=game, home=h, away=aw, n_pm_candidates=len(c), n_events=1)
        if len(c) == 1:
            sel[key] = c[0]
            mlist[key]["pm_q"] = c[0][0]["q"]
    for r in mlist.values():
        if r["n_pm_candidates"] != 1:
            cnt["events_no_pm_market" if r["n_pm_candidates"] == 0 else "events_ambiguous_pm_market"] += r["n_events"]
    need = {tk for (m, tm) in sel.values() for tk in tm.values()}
    bk = Books()
    book_files = bk.load(a.pm, need, t_lo, t_hi, cnt)
    per = collections.defaultdict(list)
    for (eid, kind, t, rise, h, aw, game) in ev:
        per[(game, kind, eid)].append((t, rise))
    recs = collections.defaultdict(list)
    for (game, kind, eid), L in sorted(per.items()):
        key = (eid, kind)
        if key not in sel:
            continue
        cell = "%s|%s" % (game, kind)
        if len(L) > CAP:
            cnt["events_dropped_by_cap"] += len(L) - CAP
            L = sorted(sorted(L, key=lambda x: hashlib.sha256(("%s|cap|%s|%r" % (a.seed, eid, x[0])).encode()).hexdigest())[:CAP])
        tmap = sel[key][1]
        mv = moves.get(key, [])
        sp = span[key]
        for (t, rise) in L:
            tk, otk = tmap[rise], tmap["a" if rise == "h" else "h"]
            if not bk.alive(tk, t):
                cnt["events_own_book_silent_pm300s"] += 1
                continue
            dd = {W: bk.d(tk, t, W) for W in WINDOWS}
            if dd[10] is None:
                cnt["events_no_own_mid_d10"] += 1
                continue
            rng = seed_rng(a.seed, "plc", eid, kind, repr(t))
            pl, tries = [], 0
            while len(pl) < NPLC and tries < 400:
                tries += 1
                u = rng.uniform(sp[0], sp[1])
                j = bisect.bisect_left(mv, u - PLC_EXCL_S)
                if j < len(mv) and mv[j] <= u + PLC_EXCL_S:
                    continue
                ptk, sg = rng.choice((tk, otk)), rng.choice((-1, 1))
                x = bk.d(ptk, u, 10)
                if x is not None:
                    pl.append(sg * x)
            if len(pl) < NPLC:
                cnt["events_placebo_short_%d_of_%d" % (len(pl) // 5 * 5, NPLC)] += 1
            sw = bk.d(otk, t, 10)
            recs[cell].append(dict(m=key, t=t, rise=rise, tok=tk, d10=dd[10], d2=dd[2], d60=dd[60], plc=mean(pl),
                                   pP=bk.d(tk, t, 10, ((t + PLANT_DT, PLANT_C, tk),)), pM=bk.d(tk, t, 10, ((t + PLANT_DT, -PLANT_C, tk),)),
                                   sw=sw, pS=bk.d(otk, t, 10, ((t + PLANT_DT, PLANT_C, otk),)) if sw is not None else None, ts=bk.d(tk, t + SHIFT_S, 10)))
    me = os.path.abspath(__file__)
    res = dict(spec="reviewer/goalserve/SPEC-v3-pm-inputs-and-controls-2026-11-22.md", code_sha256=hashlib.sha256(open(me, "rb").read()).hexdigest(),
               sport=a.sport, window_utc=[time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_lo)), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_hi))],
               gs_hour_files=len(files), missing_polled_hours=[time.strftime("%Y%m%d%H", time.gmtime(h)) for h in missing], polls=len(polls),
               pm_dirs=a.pm, pm_book_files=len(book_files), pm_markets=len(markets), goalserve_events=len(ev), counters=dict(cnt), audit=audit,
               resolution_note="Goalserve event time is our receive time, about 2 s after Goalserve's own update (poll cycle 1.8 s); d2 cannot be read; never 'lead of N seconds'.",
               sign_note="d10 > 0: price moved with the odds after the odds moved (odds first). d10 < 0: price moved before the Goalserve receive time.",
               cells={}, match_list=sorted(mlist.values(), key=lambda r: (r["kind"], str(r["eid"]))))
    for cell in sorted(recs):
        res["cells"][cell] = score_cell(cell, recs[cell], a.n_floor)
    big = max(recs, key=lambda c: len(recs[c])) if recs else None
    res["first20_events_biggest_cell"] = dict(cell=big, rows=[{k: e[k] for k in ("t", "rise", "tok", "d10", "d2", "d60", "plc")} | {"match": list(e["m"])}
                                                             for e in sorted(recs[big], key=lambda e: e["t"])[:20]] if big else [])
    res["plain_summary"] = ["%s [%s]: %d matches, %d events; sizing mean d10 %s sigma %s; controls %s; verdict: %s" % (
        c, v["role"].split(" ")[0], v["n_matches"], v["n_events"], _f(v["sizing_block"]["mean_d10"]), _f(v["sizing_block"]["sigma_d10"]),
        "OK" if v["controls_ok"] else "FAILED " + json.dumps(v["controls"]), v["verdict"]) for c, v in res["cells"].items()]
    return res


def _f(x):
    return "n/a" if x is None else "%.4f" % x


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sport", required=True, choices=("esports", "hockey_nhl", "tennis"))
    ap.add_argument("--gs-files", action="append", required=True)
    ap.add_argument("--poll-log", action="append", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--t-start", default=DEFAULT_T_START)
    ap.add_argument("--t-end")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261124)
    ap.add_argument("--n-floor", type=int, default=N_FLOOR)
    ap.add_argument("--allow-missing", action="store_true", help="report instead of STOP on missing polled hours (never for a real look)")
    a = ap.parse_args(argv)
    res = run(a)
    json.dump(res, open(a.out, "w"), indent=1)
    for l in res["plain_summary"]:
        print(l)
    print("counters", json.dumps(res["counters"]))
    print("audit", json.dumps(res["audit"]["counters"]))
    return res


if __name__ == "__main__":
    main()
