#!/usr/bin/env python3
"""PandaScore CS2 daily look (sequential): feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md (+ amendment: ONE primary cell, cs2|map|lat0).
Written by the checker thread, to be checked against the PREREG by the PandaScore thread (rule-to-code table: feeds/RULE-TO-CODE-pandascore-cs2-daily-look-2026-11-18.md).
Shape of feeds/goalserve_odds_vs_pm_v2.py; shares its signed helpers (parse_book_row, mid_of, seed_rng, cell_t) and ps_lead_test.py's loaders. Read-only.

Per-event rules are those of ps_lead_test.py (event = score rise between consecutive messages of one game; onset = first book mid in [-60,+60] s of receive time that is >= 2c above the mid at
window start, in the event direction; lead = onset - receive time, positive = feed first; placebo = 10 random event-free times, random token and direction), with the deviations listed in the rule-to-code table (D1-D6).
Statistic: per match d = mean(real leads with an onset) - mean(placebo leads with an onset); cell = t-statistic of the per-match d (n-1 df) -> z_eq; pass if z_eq >= C_BM / sqrt(min(1, n/N_MAX)).
Usage: ps_cs2_daily_look.py --ps RAW_DIR --pm PMDIR [--pm PMDIR..] --evlog events.jsonl.gz --copied-at-utc EPOCH --clock-note TEXT --out result.json
"""
import argparse, bisect, calendar, collections, glob, hashlib, json, math, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ps_lead_test import norm, find, load_pm, mk_index
from goalserve_odds_vs_pm import counted_lines, med
from goalserve_odds_vs_pm_v2 import parse_book_row, mid_of, seed_rng, cell_t

W, THR, SEED = 60.0, 0.02, 20261118
NPLC, MAXTRIES = 10, 400
T_START = 1795046400.0            # 2026-11-19T00:00:00Z: only messages from here on are scored (earlier = exploration)
LOOKS = 12                        # one per complete UTC day: look 1 = 19 Nov data ... look 12 = 30 Nov data
C_BM = 2.60
N_MAX = 60
PRIMARY = "cs2|map|lat0"
MIN_MATCHES, MIN_EVENTS, MIN_DIFF_S, MIN_SHARE = 12, 30, 2.0, 60.0
FREEZE_S = 1800.0                 # a match with any message within 30 min before the cut is NOT counted at this look (counted at the next one, complete)
PRE_S = 8 * 3600.0                # files read from 8 h before T_START to detect matches that straddle the start
PLANT_C, PLANT_DT = 1.0, 10.0           # machinery plant (a level shift far above the 2c threshold so a drifted pre-step mid cannot hide it): checks parse path, window, sign, token; power is checked separately (boundary x SE)
CS2 = ("cs-go", "cs-2", "cs2", "counter-strike")


def lat_of(m):
    try:
        for x in m.get("latency") or []:
            if x.get("field") == "round_score":
                return "lat0" if x.get("delay") == 0 else "lat>0"
    except Exception:
        pass
    return "lat_unknown"


def boundary(n):
    return float("inf") if n < 1 else C_BM / math.sqrt(min(1.0, n / N_MAX))


def onset_from(rows, t0, sign):
    """rows = [(ts, mid)] sorted. ps_lead_test.onset on an explicit row list: base = last mid at or before t0-W; first row in [t0-W, t0+W] with sign*(mid-base) >= THR -> ts - t0; else None. Returns (lead, has_base)."""
    ts = [r[0] for r in rows]
    i = bisect.bisect_right(ts, t0 - W) - 1
    if i < 0:
        return None, False
    base = rows[i][1]
    j = bisect.bisect_left(ts, t0 - W)
    while j < len(rows) and rows[j][0] <= t0 + W:
        if sign * (rows[j][1] - base) >= THR:
            return rows[j][0] - t0, True
        j += 1
    return None, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ps", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--evlog", required=True, help="events.jsonl.gz of ll_capture.py (connected/silent/stopped records)")
    ap.add_argument("--copied-at-utc", type=float, required=True, help="epoch seconds when the files were copied; must be after the end of the look day + 10 min")
    ap.add_argument("--clock-note", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--smoke", action="store_true", help="crash test only: no look/completeness refusals, output marked smoke_not_a_result")
    ap.add_argument("--t-start", type=float, default=None, help="TEST ONLY (self test); refused unless --smoke")
    a = ap.parse_args()
    global T_START
    if a.t_start is not None:
        if not a.smoke:
            raise SystemExit("--t-start is only allowed with --smoke")
        T_START = a.t_start
    files = {}
    for f in glob.glob(os.path.join(a.ps, "pandascore_*.jsonl*")):
        m = re.search(r"pandascore_(\d{10})", os.path.basename(f))
        if m:
            files[calendar.timegm(time.strptime(m.group(1), "%Y%m%d%H"))] = f
    if not files:
        raise SystemExit("no pandascore hour files in --ps")
    if a.smoke and a.t_start is None:
        T_START = 86400.0 * int(min(files) // 86400)
    K = 1 if a.smoke else int(((max(files) + 3600.0) - T_START) // 86400)
    if not a.smoke and not 1 <= K <= LOOKS:
        raise SystemExit("look K=%d outside 1..%d (no complete UTC day since 2026-11-19 or past the last look)" % (K, LOOKS))
    t_hi = T_START + K * 86400.0
    if not a.smoke and a.copied_at_utc < t_hi + 600:
        raise SystemExit("files were copied %.0f s before the end of look day K=%d + 10 min: the last hour may be half written; copy again later" % (t_hi + 600 - a.copied_at_utc, K))
    drops, cnt = collections.Counter(), collections.Counter()
    # ---- capture log: completeness
    evl = []
    for r in counted_lines(a.evlog, cnt, "evlog"):
        try:
            tt = calendar.timegm(time.strptime(str(r.get("t"))[:19], "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            continue
        if T_START - PRE_S <= tt < t_hi:
            evl.append((tt, r))
    if cnt.get("evlog_truncated_files", 0) and not a.smoke:
        raise SystemExit("event log truncated: %s" % dict(cnt))
    stopped = [(tt, r.get("kind"), r.get("reason")) for tt, r in evl if r.get("kind") in ("stopped", "stop_for_match") and tt >= T_START]
    if stopped and not a.smoke:
        raise SystemExit("capture logged stopped/stop_for_match inside the window: %s; this look is not complete" % json.dumps(stopped[:5]))
    silent = collections.defaultdict(list)
    for tt, r in evl:
        if r.get("kind") == "silent":
            silent[str(r.get("match_id"))].append(tt)
    capture_starts = sum(1 for tt, r in evl if r.get("kind") == "start" and tt >= T_START)
    connected = {str(r.get("match_id")) for tt, r in evl if r.get("kind") == "connected" and tt >= T_START and r.get("slug") in CS2}
    # ---- messages
    last, gorder = {}, collections.defaultdict(list)
    first_seen, last_seen = {}, {}
    names, ev, rises = collections.defaultdict(set), [], collections.defaultdict(list)   # rises: every score rise (used for placebo event-free test)
    hours = sorted(h for h in files if T_START - PRE_S <= h < t_hi)
    for h in hours:
        for r in counted_lines(files[h], cnt, "ps_rows"):
            m = r.get("payload") or {}
            mid, slug, kind, rn = r.get("match_id"), r.get("slug"), r.get("kind"), r.get("recv_ns")
            if slug not in CS2 or rn is None or not (T_START - PRE_S <= rn / 1e9 < t_hi):
                continue
            t = rn / 1e9
            first_seen[mid] = min(first_seen.get(mid, t), t)
            last_seen[mid] = max(last_seen.get(mid, t), t)
            if kind == "hello":
                for k in [k for k in last if k[0] == mid]:
                    last.pop(k)
                continue
            gid = m.get("game_id")
            if gid is None:
                continue
            if gid not in gorder[mid]:
                gorder[mid].append(gid)
            for k in ("home_team", "away_team"):
                tm = m.get(k)
                if isinstance(tm, dict) and tm.get("team_name"):
                    names[mid].add(norm(tm["team_name"]))
            cur = {}
            if "round_score" in set(m.get("available_fields") or []):
                for k in ("home_team", "away_team"):
                    tm = m.get(k) or {}
                    if isinstance(tm.get("score"), int):
                        cur[(tm.get("team_id"), tm.get("team_name"))] = tm["score"]
            prev = last.get((mid, gid))
            last[(mid, gid)] = cur
            if prev is None or t < T_START:
                continue
            if prev and not cur:
                drops["baseline_cleared_no_round_score"] += 1
            for k, v in cur.items():
                pv = prev.get(k)
                if pv is not None and v > pv:
                    rises[mid].append(t)
                    if v - pv != 1:
                        drops["events_score_jump_not_1_excluded"] += 1
                        continue
                    ev.append(dict(mid=mid, gid=gid, gord=gorder[mid].index(gid) + 1, t=t, team=norm(k[1]), lat=lat_of(m)))
    if cnt.get("ps_rows_truncated_files", 0) or cnt.get("ps_rows_bad_lines", 0) > 50:
        if not a.smoke:
            raise SystemExit("unreadable or truncated pandascore hour file(s): %s; re-copy and run again" % json.dumps(dict(cnt)))
    lost = sorted(x for x in connected if x not in {str(m) for m in first_seen})
    if lost and not a.smoke:
        raise SystemExit("capture log shows CS2 match(es) connected in the window with no messages in the copied files (lost or unshipped file): %s" % lost[:10])
    # ---- match-level exclusions (counted, never silent)
    excl = collections.Counter()
    ok_match = set()
    for mid in first_seen:
        if first_seen[mid] < T_START:
            excl["match_straddles_start_excluded"] += 1
        elif last_seen[mid] > t_hi - FREEZE_S:
            excl["match_in_progress_at_cut_not_counted_yet"] += 1
        elif str(mid) in silent:
            excl["match_had_silent_gap_gt_300s_excluded"] += 1
        elif len(names[mid]) != 2:
            excl["match_names_not_exactly_2_excluded"] += 1
        else:
            ok_match.add(mid)
    # ---- polymarket markets and books
    idx = mk_index(load_pm(a.pm))
    sel = {}
    mlist = {}
    for (mid, gord) in sorted({(e["mid"], e["gord"]) for e in ev if e["mid"] in ok_match}, key=lambda x: (str(x[0]), x[1])):
        for kind in ("Map %d Winner" % gord, "Match Winner"):
            if (mid, kind) in sel or (mid, kind) in mlist:
                continue
            c = [x for x in (idx.get(frozenset(names[mid])) or []) if x["kind"] == kind]
            mlist[(mid, kind)] = len(c)
            if len(c) == 1:
                sel[(mid, kind)] = c[0]
    for (mid, kind), n in mlist.items():
        if n != 1:
            drops["market_none" if n == 0 else "market_ambiguous_rematch_excluded"] += 1
    need = {tk for m in sel.values() for tk in m["tokens"]}
    book = collections.defaultdict(list)
    for d in a.pm:
        p = find(d, "books")
        if not p:
            continue
        for r in counted_lines(p, drops, "pm_books"):
            if "token" in r and not (r.get("tk") or r.get("asset")):      # layout of feeds/pm_dota_books.js ({recv_ms, token, bids, asks, ...}): same row, token key renamed, counted
                r = dict(r, tk=r["token"])
                drops["pm_book_rows_token_key_layout"] += 1
            if (r.get("tk") or r.get("asset")) not in need:
                continue
            pr = parse_book_row(r, drops)
            if pr and T_START - 400 <= pr[1] < t_hi + 400:
                book[pr[0]].append((pr[1], pr[2], pr[3]))
    if need and not book and not a.smoke:
        raise SystemExit("no usable Polymarket book row for any of the %d needed tokens (wrong --pm dir, unknown row layout, or recorder not running): drops %s" % (len(need), json.dumps(dict(drops))))
    for tk in book:
        book[tk].sort()
    bts = {tk: [x[0] for x in v] for tk, v in book.items()}

    def window_rows(tk, t0, plant=None):
        """book rows of tk from the base row (last at or before t0-W) to t0+W as [(ts, mid)] through the ONE parse path; plant = (step_time, +-c): bid and ask of every row at/after step_time shifted, plus a raw row at step_time carrying the last book shifted."""
        v = book.get(tk, [])
        lo = max(0, bisect.bisect_right(bts.get(tk, []), t0 - W) - 1)      # from the base row (last row at or before t0-W)
        hi = bisect.bisect_right(bts.get(tk, []), t0 + W)
        raw = [(ts, bb, ba) for (ts, bb, ba) in v[lo:hi]]
        if plant:
            st, c = plant
            i = bisect.bisect_right([x[0] for x in raw], st) - 1
            shifted = [(ts, bb + (c if ts >= st else 0.0), ba + (c if ts >= st else 0.0)) for (ts, bb, ba) in raw]
            if i >= 0:
                shifted.append((st, raw[i][1] + c, raw[i][2] + c))
            raw = sorted(shifted)
        out = []
        for (ts, bb, ba) in raw:
            pr = parse_book_row({"ms": ts * 1000.0, "tk": tk, "bids": [{"price": repr(bb)}], "asks": [{"price": repr(ba)}]})
            out.append((pr[1], mid_of(pr[2], pr[3])))
        return out

    def alive(toks, t):
        for tk in toks:
            L = bts.get(tk, [])
            i = bisect.bisect_left(L, t - 300)
            if i < len(L) and L[i] <= t + 300:
                return True
        return False

    # ---- events -> leads
    recs = collections.defaultdict(list)       # (series) -> [event records]
    cellx = collections.defaultdict(collections.Counter)
    plant_viol = collections.Counter()
    plant_n = 0
    evt_all = {m: sorted(v) for m, v in rises.items()}
    for e in sorted(ev, key=lambda x: (x["t"], str(x["mid"]))):
        if e["mid"] not in ok_match:
            continue
        for kind in ("Map %d Winner" % e["gord"], "Match Winner"):
            ser = "match" if kind == "Match Winner" else "map"
            m = sel.get((e["mid"], kind))
            if not m:
                cellx[ser]["events_without_market_or_ambiguous"] += 1
                continue
            outs = [norm(o) for o in m["outcomes"]]
            if e["team"] not in outs:
                cellx[ser]["rising_team_not_a_pm_outcome"] += 1
                continue
            tk = m["tokens"][outs.index(e["team"])]
            otk = [x for x in m["tokens"] if x != tk][0]
            if not alive(m["tokens"], e["t"]):
                cellx[ser]["pm_recorder_silent_pm300s"] += 1
                continue
            real, has_base = onset_from(window_rows(tk, e["t"]), e["t"], +1)
            if not has_base:
                cellx[ser]["no_own_book_mid_at_t_minus_60"] += 1
                continue
            r = dict(m=e["mid"], t=e["t"], team=e["team"], tok=tk, lat=e["lat"], lead=real, ser=ser, kind=kind)
            # end-to-end plant identities through the same row parser and onset function (exact, per event)
            pl_p, _ = onset_from(window_rows(tk, e["t"], (e["t"] + PLANT_DT, PLANT_C)), e["t"], +1)
            pl_m, _ = onset_from(window_rows(tk, e["t"], (e["t"] - PLANT_DT, PLANT_C)), e["t"], +1)
            tmap = dict(zip(outs, m["tokens"]))      # a SEPARATE CODE PATH (name-to-token dictionary) over the same markets file: catches code bugs, not a misordered outcomes/tokens pair in markets.jsonl (V22-style mapping audit still needed)
            exp_p = min(real if real is not None else PLANT_DT, PLANT_DT)
            exp_m = min(real if real is not None else -PLANT_DT, -PLANT_DT)
            plant_n += 1
            if pl_p is None or abs(pl_p - exp_p) > 1e-6:
                plant_viol["plus_step_not_recovered"] += 1
            if pl_m is None or abs(pl_m - exp_m) > 1e-6:
                plant_viol["minus_step_not_recovered"] += 1
            if tmap.get(e["team"]) != tk:
                plant_viol["token_mapping_mismatch"] += 1
            recs[ser].append(r)
    # ---- placebo per (match, market): 10 deterministic draws, event-free vs ALL rises of the match
    plc = collections.defaultdict(list)        # (ser) -> [(match, lead)]
    plc_n = collections.Counter()
    done = set()
    for (mid, kind), m in sorted(sel.items(), key=lambda x: (str(x[0][0]), x[0][1])):
        ser = "match" if kind == "Match Winner" else "map"
        if mid not in ok_match or not any(r["m"] == mid and r["kind"] == kind for r in recs[ser]):
            continue
        times = evt_all.get(mid, [])
        if kind == "Match Winner":
            span = (min(times), max(times))
        else:
            gts = sorted(e["t"] for e in ev if e["mid"] == mid and e["gord"] == int(re.search(r"(\d+)", kind).group(1)))
            span = (gts[0], gts[-1]) if gts else None
        if not span:
            continue
        for k in range(NPLC):
            prng = seed_rng(a.seed, "plc", mid, kind, k)
            got = False
            for _ in range(MAXTRIES):
                t = span[0] + prng.random() * (span[1] - span[0])
                tk, sg = prng.choice(m["tokens"]), prng.choice((-1, 1))
                if any(abs(t - x) <= W for x in times) or not alive(m["tokens"], t):
                    continue
                ld, hb = onset_from(window_rows(tk, t), t, sg)
                plc[ser].append((mid, ld, hb))
                got = True
                break
            plc_n[ser + (":drawn" if got else ":failed_to_draw")] += 1
    # ---- cells
    def mean(x):
        x = list(x)
        return sum(x) / len(x) if x else None

    cells, big = {}, None
    for ser in ("map", "match"):
        for strat in ("lat0", "lat>0", "lat_unknown", "all"):
            R = [r for r in recs[ser] if strat == "all" or r["lat"] == strat]
            cell = "cs2|%s|%s" % (ser, strat)
            first = {}
            for r in R:
                first[r["m"]] = min(first.get(r["m"], r["t"]), r["t"])
            order = sorted(first, key=lambda x: (first[x], str(x)))
            used = set(order[:N_MAX])
            Ru = [r for r in R if r["m"] in used]
            P = [(mm, ld) for (mm, ld, hb) in plc[ser] if mm in used and hb]
            dm, nr0, np0 = {}, 0, 0
            for mm in used:
                rl = [r["lead"] for r in Ru if r["m"] == mm and r["lead"] is not None]
                pl = [ld for (m2, ld) in P if m2 == mm and ld is not None]
                if not rl:
                    nr0 += 1
                    continue
                if not pl:
                    np0 += 1
                    continue
                dm[mm] = mean(rl) - mean(pl)
            means = list(dm.values())
            n_, mu_, se_, t_, z_ = cell_t(means)
            rl_all = [r["lead"] for r in Ru if r["lead"] is not None and r["m"] in dm]
            pl_all = [ld for (m2, ld) in P if ld is not None and m2 in dm]
            medr, medp = med(rl_all), med(pl_all)
            share = 100.0 * sum(1 for x in rl_all if x > 0) / len(rl_all) if rl_all else None
            c = dict(role="primary" if cell == PRIMARY else "informational (cannot be called a pass)", n_matches_used=n_, n_matches_seen=len(order), n_matches_beyond_planned_max=len(order) - len(used),
                     n_matches_without_real_onset=nr0, n_matches_without_placebo_onset=np0, n_events=len(Ru), n_events_with_onset=len(rl_all), n_placebo_with_onset=len(pl_all),
                     information_time=min(1.0, n_ / N_MAX), mean_d_per_match_s=mu_, se=se_, t_stat=t_, z_eq=z_, median_real_lead_s=medr, median_placebo_lead_s=medp,
                     median_diff_s=(medr - medp) if medr is not None and medp is not None else None, pct_price_after_feed=share,
                     per_match_d={str(k_): v_ for k_, v_ in dm.items()}, events_per_match=sorted(collections.Counter(r["m"] for r in Ru).values(), reverse=True)[:10])
            if cell == PRIMARY:
                zb = boundary(n_)
                c["boundary_z"] = zb
                c["min_detectable_mean_d_s"] = (zb * se_) if se_ and math.isfinite(zb) else None
                plants_ok = plant_n > 0 and not plant_viol
                power_ok = bool(se_ and math.isfinite(zb) and zb * se_ <= MIN_DIFF_S)
                closed = n_ >= N_MAX or K == LOOKS
                if not plants_ok:
                    v = "unknown (plant identities violated: %s)" % json.dumps(dict(plant_viol))
                elif n_ < MIN_MATCHES or len(rl_all) < MIN_EVENTS or z_ is None:
                    v = "unknown (%d matches, %d events with onset; needs >= %d and >= %d)" % (n_, len(rl_all), MIN_MATCHES, MIN_EVENTS)
                elif z_ >= zb and c["median_diff_s"] is not None and c["median_diff_s"] >= MIN_DIFF_S and share >= MIN_SHARE:
                    v = "meets bar (needs audit)"
                elif z_ <= -zb and power_ok:
                    v = "PM moved first (needs audit)"
                elif closed and power_ok:
                    v = "no lead detected (needs audit)"
                elif closed:
                    v = "unknown (closed but underpowered: min detectable %.1f s)" % (zb * se_)
                else:
                    v = "no pass yet (not a no-lead)"
                c.update(plants_ok=plants_ok, power_ok=power_ok, closed=closed, verdict=v)
                big = sorted(Ru, key=lambda r: r["t"])[:20]
            else:
                c["verdict"] = "(informational) no boundary"
            cells[cell] = c
    res = dict(smoke_not_a_result=bool(a.smoke), look=K, looks_total=LOOKS, c_bm=C_BM, n_max=N_MAX, primary=PRIMARY, data_from_utc=T_START, data_through_utc=t_hi, seed=a.seed, plant_c=PLANT_C, plant_dt_s=PLANT_DT,
               clock_note=a.clock_note, hour_files_read=len(hours), cs2_events=len(ev), pm_tokens_needed=len(need), pm_tokens_with_rows=len(book), drops=dict(drops), counters=dict(cnt), match_exclusions=dict(excl), capture_silent_matches=sorted(silent)[:20], capture_starts_in_window=capture_starts,
               plant=dict(events_checked=plant_n, violations=dict(plant_viol)), placebo_draws=dict(plc_n), event_exclusions={k: dict(v) for k, v in cellx.items()}, cells=cells,
               wording="Only cs2|map|lat0 can be called a pass. Lead = price onset minus our receive time, positive = feed first; pairs of windows cannot resolve under ~5 s. Round-score latency is relative to the fastest data point in the message, not to the real world. Single-host clock.",
               first20_events_primary=[dict(t=r["t"], match=r["m"], team=r["team"], token=r["tok"], lead=r["lead"], series=r["ser"], market=r["kind"]) for r in (big or [])])
    res["plain_summary"] = ["%s [%s]: look %d of %d (data through %s UTC), %d matches used, info time %.2f, z_eq %s vs boundary %s, plants: %s, verdict: %s" % (
        k_, v_["role"].split(" ")[0], K, LOOKS, time.strftime("%Y-%m-%d", time.gmtime(t_hi - 1)), v_["n_matches_used"], v_["information_time"],
        "%.2f" % v_["z_eq"] if v_["z_eq"] is not None else "n/a", "%.2f" % v_["boundary_z"] if v_.get("boundary_z") is not None and math.isfinite(v_["boundary_z"]) else "n/a",
        ("OK (%d events, 0 violations)" % plant_n) if v_.get("plants_ok") else "n/a", v_["verdict"]) for k_, v_ in cells.items() if k_ == PRIMARY]
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "cells"}, indent=1))
    print(json.dumps(cells.get(PRIMARY), indent=1))


if __name__ == "__main__":
    main()
