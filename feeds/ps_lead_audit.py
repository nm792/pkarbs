#!/usr/bin/env python3
"""Independent audit of the PandaScore lead test (STANDARD v1 section 4). Read-only, streaming, own code path
(it does NOT import ps_lead_test.py). Three checks, rule locked in
agent/inbox/TO-IT-URGENT-pandascore-lead-AUDIT-locked-rule-2026-11-16-0215Z.md before any data is read.

A. Isolated-event check: event kept only if no other PandaScore event of the same match lies within +-60 s of its
   receive time (nearest-event gap >= 60 s on both sides). Also report % price-after-feed by nearest-gap bucket
   (<10, 10-30, 30-60, >=60 s). Onset/lead/placebo as STANDARD v1 section 2 (seed 20261116).
B. Count reconciliation: per match, per type, increases vs any-change, for the 23 matches in --ps, and which
   match ids appear in the 14 Nov recount JSON (--recount) but not in --ps.
C. Unmatched matches: for each PandaScore match with no exact normalised-name PM market, list the PS names and the
   PM markets sharing at least one normalised name token (information only, never joined into the result).
D. Timestamp and message-lag check (added 16 Nov 02:50Z, before any audit run): the test used OUR receive time
   (`recv_ns` in the capture row, local chrony clock) for the feed and the book row `ms` (same host) for the price;
   PandaScore `updated_at` is logged, never used for lead. D reports recv_ns - updated_at per title and per message
   kind (message that produced a counted event vs other messages), and for CS2 the delay between the first message
   showing all five players of a team dead (current_round.<team>.players[].alive) and the round-score increase that
   follows in the same game. It also reports the PM-side `ms - sent`. Field names are quoted in the output.
Usage: ps_lead_audit.py --ps DIR --pm DIR [--pm DIR ...] [--recount p318-recount-2026-11-14.json] [--vol vol.json] --out out.json
"""
import argparse, bisect, collections, datetime, glob, gzip, json, os, random, re

W, THR, SEED = 60.0, 0.02, 20261116


def lines(p):
    op = gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")
    try:
        with op as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    pass
    except (EOFError, OSError):
        return


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def pick(d, stem):
    for e in (".jsonl", ".jsonl.gz"):
        p = os.path.join(d, stem + e)
        if os.path.exists(p):
            return p


def med(x):
    x = sorted(x)
    n = len(x)
    return None if not n else (x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ps", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--recount")
    ap.add_argument("--vol")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rnd = random.Random(SEED)

    # ---- PS events (own parser): per message state of counters keyed by (match, game)
    events = []  # dict(match, slug, game, t, team, field, order, dirkey)
    both = collections.defaultdict(set)
    last = {}
    gord = collections.defaultdict(list)
    cnt_inc = collections.defaultdict(collections.Counter)   # increases
    cnt_chg = collections.defaultdict(collections.Counter)   # any change (incl. decreases)
    slugs = {}
    lags = collections.defaultdict(list)       # (title, kind) -> recv - updated_at seconds
    elim = {}                                   # (match, game) -> recv time of first all-dead message this round
    elim_delay = []                             # seconds from all-dead message to round-score increase
    fields_seen = collections.Counter()

    def parse_ts(x):
        try:
            return datetime.datetime.fromisoformat(str(x).replace("Z", "+00:00")).timestamp()
        except Exception:
            return None

    for p in sorted(glob.glob(os.path.join(a.ps, "pandascore_*.jsonl*"))):
        for r in lines(p):
            m = r.get("payload") or {}
            mid = r.get("match_id")
            slugs[mid] = r.get("slug")
            if r.get("kind") == "hello":
                for k in [k for k in last if k[0] == mid]:
                    last.pop(k)
                continue
            gid = m.get("game_id")
            if gid is None:
                continue
            if gid not in gord[mid]:
                gord[mid].append(gid)
            af = set(m.get("available_fields") or [])
            cur = {}
            cs = r.get("slug") in ("cs-go", "cs-2", "cs2")
            sides = ("home_team", "away_team") if cs else ("radiant", "dire")
            for sd in sides:
                t = m.get(sd) or {}
                if t.get("team_name"):
                    both[mid].add(norm(t["team_name"]))
                if cs:
                    if "round_score" in af and isinstance(t.get("score"), int):
                        cur[(t.get("team_name"), "round")] = t["score"]
                else:
                    for f in ("kills", "towers", "barracks", "roshans"):
                        if f in af and isinstance(t.get(f), int):
                            cur[(t.get("team_name"), f)] = t[f]
            prev = last.get((mid, gid))
            last[(mid, gid)] = cur
            ua = parse_ts(r.get("updated_at") or m.get("updated_at"))
            lag = (r["recv_ns"] / 1e9 - ua) if ua else None
            title = "cs2" if cs else "dota2"
            fields_seen["recv_ns (capture row)"] += 1
            if ua:
                fields_seen["updated_at (capture row or payload)"] += 1
            produced = False
            if cs and "player_alive" in af:
                cr = m.get("current_round") or {}
                dead = False
                for sd in ("home_team", "away_team"):
                    pl = (cr.get(sd) or {}).get("players") or []
                    if len(pl) >= 1 and all(x.get("alive") is False for x in pl):
                        dead = True
                if dead and (mid, gid) not in elim:
                    elim[(mid, gid)] = r["recv_ns"] / 1e9
            if prev is None:
                if lag is not None:
                    lags[(title, "other")].append(lag)
                continue
            for k, v in cur.items():
                pv = prev.get(k)
                if pv is None or v == pv:
                    continue
                cnt_chg[mid][k[1]] += 1
                if v > pv:
                    produced = True
                    if cs and (mid, gid) in elim:
                        elim_delay.append(r["recv_ns"] / 1e9 - elim.pop((mid, gid)))
                    elif cs:
                        elim.pop((mid, gid), None)
                    cnt_inc[mid][k[1]] += 1
                    events.append(dict(match=mid, title="cs2" if cs else "dota2", game=gord[mid].index(gid) + 1,
                                       t=r["recv_ns"] / 1e9, team=k[0], field=k[1]))
            if lag is not None:
                lags[(title, "event_message" if produced else "other")].append(lag)

    # ---- B reconciliation
    rec = {"per_match": {}, "totals_increases": collections.Counter(), "totals_any_change": collections.Counter()}
    for mid in set(cnt_inc) | set(cnt_chg):
        rec["per_match"][str(mid)] = {"increases": dict(cnt_inc[mid]), "any_change": dict(cnt_chg[mid])}
        rec["totals_increases"].update(cnt_inc[mid])
        rec["totals_any_change"].update(cnt_chg[mid])
    rec["totals_increases"] = dict(rec["totals_increases"])
    rec["totals_any_change"] = dict(rec["totals_any_change"])
    if a.recount:
        rj = json.load(open(a.recount))["pandascore"]["per_match"]
        rec["match_ids_in_recount_not_in_ps_dir"] = sorted(set(rj) - {str(m) for m in cnt_chg} - {str(m) for m in slugs})
        rec["match_ids_in_ps_dir_not_in_recount"] = sorted({str(m) for m in slugs} - set(rj))
        rec["recount_per_match_same_matches"] = collections.Counter()
        for mid, v in rj.items():
            if mid in {str(m) for m in slugs}:
                for k, x in v.get("counts", {}).items():
                    rec["recount_per_match_same_matches"][k] += x
        rec["recount_per_match_same_matches"] = dict(rec["recount_per_match_same_matches"])

    # ---- PM markets
    volmap = json.load(open(a.vol)) if a.vol else {}
    mk, seen = [], set()
    for d in a.pm:
        p = pick(d, "markets")
        for m in (lines(p) if p else []):
            c = m.get("cond")
            if c in seen or not m.get("outcomes") or not m.get("tokens"):
                continue
            seen.add(c)
            q = m.get("q") or m.get("title") or ""
            mm = re.search(r"(?:map|game)\s*(\d+)", q, re.I)
            if mm:
                m["_kind"] = "Map %s Winner" % mm.group(1)
            elif (m.get("smt") or "moneyline") == "moneyline" or re.search(r"match\s*winner", q, re.I):
                m["_kind"] = "Match Winner"
            else:
                continue
            if m.get("vol") is None and c in volmap:
                m["vol"] = volmap[c]
            mk.append(m)
    idx = collections.defaultdict(list)
    for m in mk:
        if len(m["outcomes"]) == 2:
            idx[frozenset(norm(o) for o in m["outcomes"])].append(m)
    sel, unmatched = {}, {}
    for mid, names in both.items():
        c = idx.get(frozenset(names)) if len(names) == 2 else None
        if not c:
            unmatched[mid] = sorted(names)
            continue
        for m in c:
            sel[(mid, m["_kind"])] = m
    # ---- C unmatched (information only)
    toks_by_market = [(set(" ".join(norm(o) for o in m["outcomes"]).split()), m) for m in mk]
    unm = {}
    for mid, names in unmatched.items():
        nt = set(" ".join(names).split()) - {"team", "esports", "gaming", "club", "the", "of", "and"}
        near = [{"outcomes": m["outcomes"], "q": (m.get("q") or m.get("title") or "")[:90], "kind": m["_kind"]}
                for ts, m in toks_by_market if nt & ts][:6]
        unm[str(mid)] = {"ps_names": names, "title": "cs2" if slugs.get(mid) in ("cs-go", "cs-2", "cs2") else "dota2",
                         "ps_events": sum(1 for e in events if e["match"] == mid), "pm_markets_sharing_a_name_token": near}

    # ---- books for needed tokens
    need = {t for m in sel.values() for t in m["tokens"]}
    series = collections.defaultdict(list)
    for d in a.pm:
        p = pick(d, "books")
        for r in (lines(p) if p else []):
            tk = r.get("asset") or r.get("tk")
            if tk not in need:
                continue
            b = [float(x["price"]) for x in r.get("bids") or []]
            s = [float(x["price"]) for x in r.get("asks") or []]
            ms = r.get("recv_ms") or r.get("ms")
            if b and s and ms:
                series[tk].append((ms / 1000.0, (max(b) + min(s)) / 2))
    ts = {}
    for k in series:
        series[k].sort()
        ts[k] = [x[0] for x in series[k]]

    def mid_at(k, t):
        i = bisect.bisect_right(ts[k], t) - 1
        return series[k][i][1] if i >= 0 else None

    def onset(k, t0, sign):
        if k not in series:
            return None
        base = mid_at(k, t0 - W)
        if base is None:
            return None
        i = bisect.bisect_left(ts[k], t0 - W)
        while i < len(series[k]) and series[k][i][0] <= t0 + W:
            if sign * (series[k][i][1] - base) >= THR:
                return series[k][i][0] - t0
            i += 1
        return None

    # nearest-event gap per event (any type, same match)
    by_match = collections.defaultdict(list)
    for e in events:
        by_match[e["match"]].append(e["t"])
    for v in by_match.values():
        v.sort()
    for e in events:
        v = by_match[e["match"]]
        i = bisect.bisect_left(v, e["t"])
        gaps = [abs(e["t"] - v[j]) for j in (i - 1, i + 1) if 0 <= j < len(v)]
        # v contains e itself at index i (or a tie); neighbours are i-1 and i+1
        e["gap"] = min(gaps) if gaps else 1e9

    rows = []
    for e in events:
        for kind in ("Map %d Winner" % e["game"], "Match Winner"):
            m = sel.get((e["match"], kind))
            if not m:
                continue
            names = [norm(o) for o in m["outcomes"]]
            tn = norm(e["team"])
            if tn not in names:
                continue
            tk = m["tokens"][names.index(tn)]
            rows.append(dict(e, series="map" if kind != "Match Winner" else "match", lead=onset(tk, e["t"], +1)))

    def cell(R, P):
        rl = [r["lead"] for r in R if r["lead"] is not None]
        pl = [r["lead"] for r in P if r["lead"] is not None]
        ms = sorted({r["match"] for r in R})
        by = {m: [r["lead"] for r in R if r["match"] == m and r["lead"] is not None] for m in ms}
        pb = {m: [r["lead"] for r in P if r["match"] == m and r["lead"] is not None] for m in ms}
        boots = []
        for _ in range(2000 if ms else 0):
            s = [rnd.choice(ms) for _ in ms]
            x = [v for m in s for v in by[m]]
            y = [v for m in s for v in pb[m]]
            if x and y:
                boots.append(med(x) - med(y))
        boots.sort()
        n = len(R)
        out = dict(n_events=n, n_matches=len(ms), pct_real_with_onset=100 * len(rl) / n if n else None,
                   pct_placebo_with_onset=100 * len(pl) / len(P) if P else None,
                   median_real_lead_s=med(rl), median_placebo_lead_s=med(pl),
                   diff_s=(med(rl) - med(pl)) if rl and pl else None,
                   pct_price_after_feed=100 * sum(1 for x in rl if x > 0) / len(rl) if rl else None,
                   ci95=[boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]] if len(boots) > 20 else None)
        out["audit_word"] = ("unknown (n<30)" if n < 30 else
                             ("not confirmed as no-lead" if (out["diff_s"] is not None and out["diff_s"] >= 2) or
                              (out["pct_price_after_feed"] or 0) >= 60 else "no lead reproduced"))
        return out

    def placebo(R, iso):
        P = []
        for key in {(r["match"], r["series"]) for r in R}:
            ev = by_match[key[0]]
            lo, hi = ev[0], ev[-1]
            toks = list({m["tokens"][i] for (mm, k), m in sel.items() if mm == key[0] for i in (0, 1)})
            got = tries = 0
            while got < 10 and tries < 500 and toks:
                tries += 1
                t = rnd.uniform(lo, hi)
                j = bisect.bisect_left(ev, t)
                near = min([abs(t - ev[x]) for x in (j - 1, j) if 0 <= x < len(ev)] or [1e9])
                if near <= W:
                    continue
                P.append(dict(match=key[0], series=key[1], lead=onset(rnd.choice(toks), t, rnd.choice((-1, 1)))))
                got += 1
        return P

    res = {"seed": SEED, "A_isolated": {}, "A_gap_buckets": {}, "B_reconciliation": rec,
           "C_unmatched": unm, "matched_ps_matches": len(both) - len(unmatched), "unmatched_ps_matches": len(unmatched)}
    for title in ("cs2", "dota2"):
        for sr in ("map", "match"):
            R_all = [r for r in rows if r["title"] == title and r["series"] == sr]
            R_iso = [r for r in R_all if r["gap"] >= W]
            res["A_isolated"]["%s|%s|all_events" % (title, sr)] = cell(R_all, placebo(R_all, False))
            res["A_isolated"]["%s|%s|isolated_gap>=60s" % (title, sr)] = cell(R_iso, placebo(R_all, True))
            for lo, hi in ((0, 10), (10, 30), (30, 60), (60, 1e10)):
                B = [r for r in R_all if lo <= r["gap"] < hi]
                rl = [r["lead"] for r in B if r["lead"] is not None]
                res["A_gap_buckets"]["%s|%s|gap %s-%ss" % (title, sr, lo, "inf" if hi > 1e9 else hi)] = dict(
                    n_events=len(B), n_with_onset=len(rl),
                    pct_price_after_feed=100 * sum(1 for x in rl if x > 0) / len(rl) if rl else None,
                    median_real_lead_s=med(rl))
    def q(x):
        x = sorted(x)
        n = len(x)
        if not n:
            return None
        return {"n": n, "p10": x[int(.1 * (n - 1))], "median": x[n // 2], "p90": x[int(.9 * (n - 1))], "max": x[-1]}
    res["D_timestamps"] = {
        "feed_clock_used_by_test": "recv_ns (our receipt, capture host clock); updated_at NOT used for lead",
        "price_clock_used_by_test": "ms on the PM book row (same host); `sent` is the exchange send time, logged only",
        "fields_seen": dict(fields_seen),
        "recv_minus_updated_at_seconds": {"%s|%s" % k: q(v) for k, v in lags.items()},
        "cs2_all_dead_message_to_round_score_increase_seconds": q(elim_delay),
        "note": "negative recv-updated_at means the two clocks disagree; a large positive median means the delay is "
                "before our socket (PandaScore side) or in our receive path; compare event_message vs other"}
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
