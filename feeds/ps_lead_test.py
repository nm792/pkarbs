#!/usr/bin/env python3
"""PandaScore low-latency feed vs Polymarket price: lead test per feeds/STANDARD-feed-latency-test.md v1.
Read-only, streaming. Sections 2-3 of the STANDARD are implemented as follows (no deviation intended):
 - event = increase of a counter between consecutive status messages of the same game_id
   (CS2: home/away score; Dota 2: kills, towers, barracks, roshans per side). First message after a
   hello/reconnect only sets the baseline. Receive time = our recv_ns (never updated_at).
 - direction: the team whose counter rose; its PM outcome token must rise >= 2c (mid).
 - onset: first book mid, inside [-60 s,+60 s] of receive time, that is >= 2c above the mid at window start
   (event-direction). lead = onset - recv time. Positive = feed first.
 - placebo: 10 random event-free times per match (no event within +-60 s), random direction, same procedure.
 - bar: n>=30 events per title, median(real-placebo) >= 2 s, match-clustered bootstrap CI excludes 0,
   price moves after the feed (lead>0) in >=60% of events with an onset.
Matching of team names is EXACT after normalisation (no fuzzy match: 'X Gaming' != 'X Academy').
Usage: ps_lead_test.py --ps DIR_OF_pandascore_*.jsonl.gz --pm DIR [--pm DIR ...] --out result.json
 each --pm DIR holds markets.jsonl(.gz) and books.jsonl(.gz) (recorder format: full book snapshots).
"""
import argparse, bisect, collections, glob, gzip, json, os, random, re, sys

W = 60.0
THR = 0.02
SEED = 20261115


def opn(p):
    return gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")


def lines(p):
    """tolerant reader: yields parsed rows, stops quietly at truncated gzip tails."""
    try:
        with opn(p) as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    continue
    except (EOFError, OSError):
        return


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def find(d, stem):
    for e in (".jsonl", ".jsonl.gz"):
        if os.path.exists(os.path.join(d, stem + e)):
            return os.path.join(d, stem + e)


def counters(msg, slug):
    """-> {(side, field): value}; side keys are team ids."""
    out = {}
    af = set(msg.get("available_fields") or [])
    if slug in ("cs-go", "cs-2", "cs2", "counter-strike"):
        if "round_score" in af:
            for k in ("home_team", "away_team"):
                t = msg.get(k) or {}
                if isinstance(t.get("score"), int):
                    out[(t.get("team_id"), t.get("team_name"), "round")] = t["score"]
    else:
        for k in ("radiant", "dire"):
            t = msg.get(k) or {}
            for f in ("kills", "towers", "barracks", "roshans"):
                if f in af and isinstance(t.get(f), int):
                    out[(t.get("team_id"), t.get("team_name"), f)] = t[f]
    return out


def load_ps(psdir):
    ev = []  # (match_id, slug, game_id, recv_s, team_name, field, game_order)
    stats = collections.Counter()
    last = {}
    gorder = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(psdir, "pandascore_*.jsonl*"))):
        for r in lines(p):
            m = r.get("payload") or {}
            mid, slug, kind = r.get("match_id"), r.get("slug"), r.get("kind")
            if kind == "hello":
                for k in [k for k in last if k[0] == mid]:
                    last.pop(k)
                continue
            gid = m.get("game_id")
            if gid is None:
                continue
            if gid not in gorder[mid]:
                gorder[mid].append(gid)
            cur = counters(m, slug)
            key = (mid, gid)
            prev = last.get(key)
            last[key] = cur
            stats["messages"] += 1
            if prev is None:
                continue
            for k, v in cur.items():
                pv = prev.get(k)
                if pv is not None and v > pv:
                    ev.append((mid, slug, gid, r["recv_ns"] / 1e9, k[1], k[2], gorder[mid].index(gid) + 1))
    return ev, stats


def load_pm(dirs):
    mk = []
    for d in dirs:
        p = find(d, "markets")
        if p:
            mk += list(lines(p))
    return mk


def mk_index(mk):
    """(frozenset of normalised outcome names) -> list of markets."""
    idx = collections.defaultdict(list)
    for m in mk:
        o = m.get("outcomes") or []
        if len(o) == 2:
            idx[frozenset(norm(x) for x in o)].append(m)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ps", required=True)
    ap.add_argument("--pm", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rnd = random.Random(SEED)
    ev, stats = load_ps(a.ps)
    idx = mk_index(load_pm(a.pm))
    # team names per match from events
    teams = collections.defaultdict(set)
    for e in ev:
        teams[e[0]].add(norm(e[4]))
    # need both teams: take from counters' names (event teams only show scorers) -> use opponents seen in all rows
    # second pass gets both names cheaply
    both = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(a.ps, "pandascore_*.jsonl*"))):
        for r in lines(p):
            m = r.get("payload") or {}
            for k in ("home_team", "away_team", "radiant", "dire"):
                t = m.get(k)
                if isinstance(t, dict) and t.get("team_name"):
                    both[r.get("match_id")].add(norm(t["team_name"]))
    # pick market per (match, game order)
    sel = {}  # (match, game_order) -> (market, kind)
    unmatched = collections.Counter()
    for mid, names in both.items():
        c = idx.get(frozenset(names)) if len(names) == 2 else None
        if not c:
            unmatched[mid] += 1
            continue
        for m in c:
            sel[(mid, m["kind"])] = m
    need_tokens = set()
    for m in sel.values():
        need_tokens.update(m["tokens"])
    # books
    series = collections.defaultdict(list)
    for d in a.pm:
        p = find(d, "books")
        if not p:
            continue
        for r in lines(p):
            t = r.get("asset")
            if t not in need_tokens:
                continue
            b = [float(x["price"]) for x in r.get("bids") or []]
            s = [float(x["price"]) for x in r.get("asks") or []]
            if not b or not s:
                continue
            series[t].append((r["recv_ms"] / 1000.0, (max(b) + min(s)) / 2.0))
    for t in series:
        series[t].sort()
    ts_cache = {t: [x[0] for x in v] for t, v in series.items()}

    def mid_at(tok, t):
        v = series.get(tok)
        if not v:
            return None
        i = bisect.bisect_right(ts_cache[tok], t) - 1
        return v[i][1] if i >= 0 else None

    def onset(tok, t0, sign):
        v = series.get(tok)
        if not v:
            return None
        base = mid_at(tok, t0 - W)
        if base is None:
            return None
        i = bisect.bisect_left(ts_cache[tok], t0 - W)
        while i < len(v) and v[i][0] <= t0 + W:
            if sign * (v[i][1] - base) >= THR:
                return v[i][0] - t0
            i += 1
        return None

    def vol_stratum(m):
        return ">=25k" if (m.get("vol") or 0) >= 25000 else "<25k"

    rows = []  # per event: title, match, stratum, series, real lead, placebo leads
    evt_times = collections.defaultdict(list)
    for e in ev:
        evt_times[e[0]].append(e[3])
    nev_no_market = collections.Counter()
    for (mid, slug, gid, t, team, fld, gord) in ev:
        title = "cs2" if slug in ("cs-go", "cs-2", "cs2") else "dota2"
        for kind in ("Map %d Winner" % gord, "Match Winner"):
            m = sel.get((mid, kind))
            if not m:
                nev_no_market[(title, kind)] += 1
                continue
            tn = norm(team)
            try:
                k = [norm(o) for o in m["outcomes"]].index(tn)
            except ValueError:
                nev_no_market[(title, kind + " (team name not an outcome)")] += 1
                continue
            tok = m["tokens"][k]
            rows.append(dict(title=title, match=mid, series="map" if kind != "Match Winner" else "match",
                             stratum=vol_stratum(m), field=fld, t=t, tok=tok, lead=onset(tok, t, +1)))
    # placebo per (match, series): 10 random event-free times within the match's event span
    plc = []
    seen = set()
    for r in rows:
        key = (r["match"], r["series"], r["title"])
        if key in seen:
            continue
        seen.add(key)
        et = sorted(evt_times[r["match"]])
        lo, hi = et[0], et[-1]
        ms = [x for x in rows if (x["match"], x["series"]) == key[:2]]
        toks = list({x["tok"] for x in ms})
        got = 0
        tries = 0
        while got < 10 and tries < 400:
            tries += 1
            t = rnd.uniform(lo, hi)
            if any(abs(t - x) <= W for x in et):
                continue
            tok = rnd.choice(toks)
            plc.append(dict(title=r["title"], match=r["match"], series=r["series"], stratum=r["stratum"],
                            lead=onset(tok, t, rnd.choice((-1, 1)))))
            got += 1

    def med(x):
        x = sorted(x)
        n = len(x)
        return None if not n else (x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2)

    def boot(real, pl, n=2000):
        ms = sorted({r["match"] for r in real})
        if not ms:
            return None
        by = {m: [r["lead"] for r in real if r["match"] == m and r["lead"] is not None] for m in ms}
        pb = {m: [r["lead"] for r in pl if r["match"] == m and r["lead"] is not None] for m in ms}
        out = []
        for _ in range(n):
            s = [rnd.choice(ms) for _ in ms]
            r_ = [x for m in s for x in by[m]]
            p_ = [x for m in s for x in pb[m]]
            if r_ and p_:
                out.append(med(r_) - med(p_))
        out.sort()
        return [out[int(.025 * len(out))], out[int(.975 * len(out))]] if len(out) > 20 else None

    res = {"seed": SEED, "ps_messages": stats["messages"], "ps_events_total": len(ev),
           "ps_matches_seen": len(both), "ps_matches_unmatched_to_pm": len(unmatched),
           "events_without_market": {str(k): v for k, v in nev_no_market.items()}, "cells": {}}
    for title in ("cs2", "dota2"):
        for series_ in ("map", "match"):
            for strat in ("all", "<25k", ">=25k"):
                R = [r for r in rows if r["title"] == title and r["series"] == series_ and (strat == "all" or r["stratum"] == strat)]
                P = [r for r in plc if r["title"] == title and r["series"] == series_ and (strat == "all" or r["stratum"] == strat)]
                rl = [r["lead"] for r in R if r["lead"] is not None]
                pl = [r["lead"] for r in P if r["lead"] is not None]
                n = len(R)
                c = dict(n_events=n, n_matches=len({r["match"] for r in R}), n_with_onset=len(rl),
                         n_placebo=len(P), n_placebo_with_onset=len(pl),
                         pct_real_with_onset=(100.0*len(rl)/n) if n else None,
                         pct_placebo_with_onset=(100.0*len(pl)/len(P)) if P else None,
                         median_real_lead_s=med(rl), median_placebo_lead_s=med(pl),
                         diff_s=(med(rl) - med(pl)) if rl and pl else None,
                         pct_price_after_feed=(100.0 * sum(1 for x in rl if x > 0) / len(rl)) if rl else None,
                         pct_placebo_after=(100.0 * sum(1 for x in pl if x > 0) / len(pl)) if pl else None,
                         ci95_match_boot=boot(R, P) if n else None)
                if n < 30:
                    c["verdict"] = "unknown (n=%d < 30), preliminary" % n
                else:
                    ok = (c["diff_s"] is not None and c["diff_s"] >= 2 and c["ci95_match_boot"] and
                          c["ci95_match_boot"][0] > 0 and (c["pct_price_after_feed"] or 0) >= 60)
                    c["verdict"] = "meets bar (needs audit)" if ok else "no lead (needs audit)"
                res["cells"]["%s|%s|%s" % (title, series_, strat)] = c
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
