#!/usr/bin/env python3
"""Independent audit of it/ps_inround_test.py (PandaScore CS2 in-round kill lead vs Polymarket).
usage: python3 -I feeds/audit_ps_inround.py SAMPLEDIR CACHEDIR [--plant 0.03]
Network: gamma + data-api v2 (public). Trades are cached as CACHEDIR/trades_<cid>.json so reruns are identical.

What it does that the audited script does not (see feeds/RULE-TO-CODE-ps-inround-audit-2026-11-20.md):
 A1 Map N markets get the events of the N-th map of the series (rank of game_id), not map_id == N (map_id is a map-POOL id).
 A2 Only two-team winner markets (outcomes == the two teams, each matched exactly once) are used.
 A3 Match-clustered inference: per-match means, sign test over matches, bootstrap over matches, and a WITHIN-MATCH sign shuffle.
 A4 Event-level rows (one row per event, markets averaged) and first-kill-per-round rows.
 A5 Placebo as pre-registered: event-free times, random sign, many draws.
 A6 Capturable edge: move from t+1 s (the 1 s taker delay) to t+15 s, timing profile, fresh-price subset.
 A7 Executable proxy from public trades: entry = first BUY print on the favoured token at >= t+1 s, fee 0.05*p*(1-p).
 A8 Plant by shifting real prints in [t+5, t+16) and reading recovery against the share of rows with a print there.
Own-book asks are NOT available here (no pmcs2 books for these hours); A7 is a trades proxy and says so."""
import sys, os, json, gzip, glob, bisect, random, re, statistics as st, urllib.request

H = 15; DELAY = 1.0; PLANT_AT = 5.0
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}


def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def fee(p): return 0.05 * p * (1 - p)


# ---------------------------------------------------------------- events
def events(msgs):
    """list of (t, kind, fav_team, game_id). kind K = kill (opponent alive count drops, same game_id and round), T = round end."""
    out = []; prev = None
    for d in msgs:
        p = d["payload"]; cr = p.get("current_round") or {}; gid = p.get("game_id")
        if gid is None or not cr: continue
        al = {}
        for tm in ("home_team", "away_team"):
            pl = (cr.get(tm) or {}).get("players") or []
            al[tm] = sum(bool(x.get("alive")) for x in pl) if pl else None
        sc = ((p.get("home_team") or {}).get("score"), (p.get("away_team") or {}).get("score"))
        cur = dict(gid=gid, rnd=cr.get("round_number"), al=al, sc=sc, t=d["recv_ns"] / 1e9)
        if prev and prev["gid"] == gid:
            if prev["rnd"] == cur["rnd"]:
                for tm in ("home_team", "away_team"):
                    a, b = prev["al"][tm], cur["al"][tm]
                    if a is not None and b is not None and b < a:
                        out.append((cur["t"], "K", "away_team" if tm == "home_team" else "home_team", gid, cur["rnd"]))
            for i, tm in enumerate(("home_team", "away_team")):
                if None not in prev["sc"] + cur["sc"] and cur["sc"][i] > prev["sc"][i]:
                    out.append((cur["t"], "T", tm, gid, cur["rnd"]))
        prev = cur
    return out


def dedup(ev, gap=H):
    ded = []; last = {}
    for e in ev:
        if e[0] - last.get(e[1], -1e18) >= gap: ded.append(e); last[e[1]] = e[0]
    return ded


def first_per_round(ev):
    seen = set(); out = []
    for e in ev:
        k = (e[1], e[3], e[4])
        if k not in seen: seen.add(k); out.append(e)
    return out


def no_round_end_within(ev_all, evs, gap=H):
    """keep kills with no round-end (score rise) in the same game within [t, t+gap]: the last kill of a round IS the round end, and the
    round-end price move would otherwise be counted as a kill lead."""
    te = sorted((e[0], e[3]) for e in ev_all if e[1] == "T")
    return [e for e in evs if not any(g == e[3] and e[0] <= t <= e[0] + gap for t, g in te)]


def ordinals(ev_all_gids):
    return {g: i + 1 for i, g in enumerate(sorted(set(ev_all_gids)))}


# ---------------------------------------------------------------- price helpers
class Tok:
    """prints of ONE token (outcome index j): sorted arrays of ts, price, side."""
    def __init__(self, tr):
        tr = sorted(tr, key=lambda x: x["timestamp"])
        self.ts = [x["timestamp"] for x in tr]; self.px = [x["price"] for x in tr]; self.sd = [x.get("side") for x in tr]

    def last(self, t):
        i = bisect.bisect_right(self.ts, t)
        return (self.px[i - 1], t - self.ts[i - 1]) if i else (None, None)

    def first_buy(self, t, t_max):
        i = bisect.bisect_left(self.ts, t)
        while i < len(self.ts) and self.ts[i] <= t_max:
            if self.sd[i] == "BUY": return self.px[i], self.ts[i]
            i += 1
        return None, None

    def count(self, a, b): return bisect.bisect_right(self.ts, b) - bisect.bisect_left(self.ts, a)


def plant_tok(tok, ev_times_signs, plant):
    """shift the REAL prints of this token inside [t+PLANT_AT, t+H+1) by s*plant (s=+1 if the event favours this token)."""
    px = list(tok.px)
    for t, s in ev_times_signs:
        lo = bisect.bisect_left(tok.ts, t + PLANT_AT); hi = bisect.bisect_left(tok.ts, t + H + 1)
        for i in range(lo, hi): px[i] = min(.99, max(.01, px[i] + s * plant))
    n = Tok([]); n.ts = tok.ts; n.px = px; n.sd = tok.sd
    return n


# ---------------------------------------------------------------- rows
def rows_for_market(evs, tok0, tok1, s_of_fav, hs=1):
    """one row per event: dict with signed moves, from the outcome-0 token (as the audited script) and from the favoured token."""
    out = []
    for e in evs:
        t, kind, fav = e[0], e[1], e[2]
        s = s_of_fav(fav)
        if s is None: continue
        a, _ = tok0.last(t - H); b, age = tok0.last(t); c, _ = tok0.last(t + H); b1, _ = tok0.last(t + DELAY)
        if None in (a, b, c, b1): continue
        r = dict(t=t, kind=kind, rnd=e[4], gid=e[3], s=s, st=s * hs, rawpost=hs * (c - b), rawpre=hs * (b - a), pre=s * (b - a), post=s * (c - b), post_cap=s * (c - b1), early=s * (b1 - b),
                 age=age, nprint=tok0.count(t, t + H))
        j = 0 if s == 1 else 1
        tk = tok0 if j == 0 else tok1
        if tk is not None and tk.ts:
            pe, te = tk.first_buy(t + DELAY, t + H)
            pm, _ = tk.last(t + H)
            if pe is not None and pm is not None:
                r["entry"] = pe; r["mark"] = pm; r["net"] = pm - pe - fee(pe); r["gross"] = pm - pe
        out.append(r)
    return out


def match_unit(rows): return st.mean(r["post"] for r in rows) if rows else None


def sign_test_p(vals):
    """two-sided exact sign test p over per-match means (zeros dropped)."""
    v = [x for x in vals if x != 0]; n = len(v); k = sum(x > 0 for x in v)
    if n == 0: return 1.0
    from math import comb
    m = max(k, n - k)
    return min(1.0, 2 * sum(comb(n, i) for i in range(m, n + 1)) / 2 ** n)


def boot_matches(per_match, nb=5000, seed=11):
    """bootstrap over MATCHES of the event-weighted pooled mean; returns (lo, hi) 95%."""
    rnd = random.Random(seed); ms = list(per_match.values()); out = []
    for _ in range(nb):
        smp = [rnd.choice(ms) for _ in ms]; n = sum(len(x) for x in smp)
        out.append(sum(sum(x) for x in smp) / n if n else 0.0)
    out.sort(); return out[int(.025 * nb)], out[int(.975 * nb) - 1]


def within_match_shuffle_p(rows_by_match, field="rawpost", nperm=5000, seed=5):
    """null: which team a kill favours (st = +1 home, -1 away) is unrelated to the later HOME-price move INSIDE a match. Shuffle st among
    the events of each match (keeps the match's drift and volatility). NOTE: it treats events as exchangeable, so it ignores that kills inside
    a round are correlated: it is anti-conservative; the match bootstrap below is the cluster-robust number."""
    rnd = random.Random(seed)
    data = [([r[field] for r in rs], [r["st"] for r in rs]) for rs in rows_by_match.values() if rs]
    n = sum(len(a) for a, _ in data)
    obs = sum(s_ * x for raw, ss in data for s_, x in zip(ss, raw)) / n
    cnt = 0
    for _ in range(nperm):
        tot = 0
        for raw, ss in data:
            sh = ss[:]; rnd.shuffle(sh); tot += sum(a * b for a, b in zip(sh, raw))
        if abs(tot / n) >= abs(obs) - 1e-12: cnt += 1
    return obs, cnt / nperm


def iid_perm_p(vals, nperm=5000, seed=3):
    """what the audited script does: flip signs of rows as if independent."""
    rnd = random.Random(seed); obs = st.mean(vals); c = 0
    for _ in range(nperm):
        if abs(st.mean(v * rnd.choice((-1, 1)) for v in vals)) >= abs(obs) - 1e-12: c += 1
    return c / nperm


def placebo_rows(ev_all, tok0, t0, t1, n, rnd, avoid=30.0, sign_pair=None):
    """n random event-free times in [t0,t1] (no PS event within +-avoid s) with random sign."""
    ts = sorted(e[0] for e in ev_all); out = []; tries = 0
    while len(out) < n and tries < 200 * max(n, 1):
        tries += 1; t = rnd.uniform(t0, t1)
        i = bisect.bisect_left(ts, t)
        if (i < len(ts) and ts[i] - t < avoid) or (i and t - ts[i - 1] < avoid): continue
        a, _ = tok0.last(t - H); b, _ = tok0.last(t); c, _ = tok0.last(t + H)
        if None in (a, b, c): continue
        s = rnd.choice((-1, 1)); out.append(s * (c - b))
    return out


def summarise(R_by_match, label):
    allr = [r for rs in R_by_match.values() for r in rs]
    if not allr: return {"label": label, "n": 0}
    out = dict(label=label, n=len(allr), matches=len(R_by_match))
    out["lead_c"] = 100 * st.mean(r["post"] for r in allr)
    out["ant_c"] = 100 * st.mean(r["pre"] for r in allr)
    out["lead_cap_c"] = 100 * st.mean(r["post_cap"] for r in allr)
    out["early_0_1s_c"] = 100 * st.mean(r["early"] for r in allr)
    pm = {m: [r["post"] for r in rs] for m, rs in R_by_match.items() if rs}
    pmm = {m: st.mean(v) for m, v in pm.items()}
    out["pos_matches"] = sum(v > 0 for v in pmm.values()); out["n_matches"] = len(pmm)
    out["mean_of_match_means_c"] = 100 * st.mean(pmm.values())
    out["sign_test_p_matches"] = sign_test_p(list(pmm.values()))
    lo, hi = boot_matches(pm); out["boot95_c"] = (100 * lo, 100 * hi)
    pa = {m: [r["pre"] for r in rs] for m, rs in R_by_match.items() if rs}
    lo, hi = boot_matches(pa); out["ant_boot95_c"] = (100 * lo, 100 * hi)
    pd = {m: [r["post"] - r["pre"] for r in rs] for m, rs in R_by_match.items() if rs}
    lo, hi = boot_matches(pd); out["lead_minus_ant_c"] = 100 * st.mean(x for v in pd.values() for x in v); out["lead_minus_ant_boot95_c"] = (100 * lo, 100 * hi)
    out["iid_perm_p"] = iid_perm_p([r["post"] for r in allr])
    _, out["within_match_shuffle_p"] = within_match_shuffle_p({m: rs for m, rs in R_by_match.items() if rs})
    out["median_price_age_s"] = st.median(r["age"] for r in allr)
    out["share_with_print_in_15s"] = sum(r["nprint"] > 0 for r in allr) / len(allr)
    fresh = [r for r in allr if r["age"] <= 5]
    out["fresh_n"] = len(fresh); out["fresh_lead_c"] = 100 * st.mean(r["post"] for r in fresh) if fresh else None
    ex = [r for r in allr if "net" in r]
    out["exec_fill_rate"] = len(ex) / len(allr)
    if ex:
        out["exec_gross_c"] = 100 * st.mean(r["gross"] for r in ex); out["exec_net_after_fee_c"] = 100 * st.mean(r["net"] for r in ex)
        out["exec_mean_entry"] = st.mean(r["entry"] for r in ex)
    return out


# ---------------------------------------------------------------- network
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30); b = r.read()
    return json.loads(gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b)


def find_markets(h, a):
    out = {}
    for off in range(0, 400, 100):
        for u in (f"https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2&limit=100&offset={off}&closed=false",
                  f"https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2&limit=100&offset={off}&closed=true&order=startDate&ascending=false"):
            for e in get(u):
                ti = norm(e.get("title"))
                if norm(h) in ti and norm(a) in ti:
                    for m in e.get("markets", []): out[m.get("conditionId")] = (m.get("question"), json.loads(m.get("outcomes") or "[]"))
    return [(q, cid, o) for cid, (q, o) in out.items()]


class WrongMarketRows(Exception):
    pass


def check_rows(rows, cid):
    """R-080: data-api v2 /trades silently IGNORES unknown params and then returns OTHER markets' trades. Every row must carry the requested condition_id."""
    bad = [r.get("condition_id") for r in rows if r.get("condition_id") != cid]
    if bad: raise WrongMarketRows("%d of %d rows are not condition_id %s (e.g. %s)" % (len(bad), len(rows), cid, bad[0]))
    return rows


def window_trades(rows, t0, t1, pad=60):
    """R-080 addendum: /v2/trades silently ignores start/end, so the request returns whole-market history. The window is applied HERE, by timestamp."""
    return [x for x in rows if t0 - pad <= x["timestamp"] <= t1 + pad]


def trades(cid, cache, fetch=None):
    fetch = fetch or get
    p = os.path.join(cache, f"trades_{cid}.json")
    if os.path.exists(p): return check_rows(json.load(open(p)), cid)
    r = []; cur = None
    for _ in range(40):
        j = fetch(f"https://data-api.polymarket.com/v2/trades?condition_id={cid}&limit=500" + (f"&cursor={cur}" if cur else ""))
        r += check_rows(j.get("data", []), cid); cur = j.get("next_cursor")
        if not cur or not j.get("data"): break
    os.makedirs(cache, exist_ok=True); json.dump(r, open(p, "w")); return r


def team_map(outs, hn, an):
    """A2: outcomes must be exactly the two teams. returns {0: team, 1: team} or None."""
    if len(outs) != 2: return None
    m = {}
    for j, o in enumerate(outs):
        no = norm(o); ih = no and (no in norm(hn) or norm(hn) in no); ia = no and (no in norm(an) or norm(an) in no)
        if ih == ia: return None
        m[j] = "home_team" if ih else "away_team"
    return m if m[0] != m[1] else None


def load_match(f, cache):
    msgs = [json.loads(l) for l in gzip.open(f, "rt")]
    p0 = next((m["payload"] for m in reversed(msgs) if m["payload"].get("home_team") and m["payload"].get("away_team")), None)
    if not p0: return None
    hn, an = p0["home_team"].get("team_name"), p0["away_team"].get("team_name")
    t0, t1 = msgs[0]["recv_ns"] / 1e9, msgs[-1]["recv_ns"] / 1e9
    ev_all = events(msgs); gids = [e[3] for e in ev_all] or [m["payload"].get("game_id") for m in msgs if m["payload"].get("game_id")]
    ordn = ordinals([g for g in gids if g])
    mk = []
    for q, cid, outs in find_markets(hn, an):
        ql = (q or "").lower()
        if any(w in ql for w in ("total", "handicap", "o/u", "spread")): continue
        tmap = team_map(outs, hn, an)
        if not tmap: continue
        mapno = None
        if "map" in ql:
            m = re.search(r"map (\d+)", ql)
            if not m: continue
            mapno = int(m.group(1))
        tr = window_trades(trades(cid, cache), t0, t1)
        t_0 = Tok([x for x in tr if x.get("outcome_index") == 0]); t_1 = Tok([x for x in tr if x.get("outcome_index") == 1])
        if len(t_0.ts) < 30: continue
        mk.append(dict(q=q, cid=cid, mapno=mapno, tmap=tmap, t0=t_0, t1=t_1))
    return dict(f=os.path.basename(f), mid=msgs[0]["match_id"], hn=hn, an=an, t0=t0, t1=t1, ev=ev_all, ordn=ordn, mk=mk)


def build_rows(M, kinds=("K",), mode="dedup", no_re=False):
    """returns {match_id: [rows]} with ONE row per event: markets for that event averaged (A4)."""
    out = {}
    for m in M:
        ev = [e for e in m["ev"] if e[1] in kinds]
        ev = dedup(ev) if mode == "dedup" else first_per_round(ev)
        if no_re: ev = no_round_end_within(m["ev"], ev)
        per_event = {}
        for mk in m["mk"]:
            evs = [e for e in ev if mk["mapno"] is None or m["ordn"].get(e[3]) == mk["mapno"]]
            inv = {v: k for k, v in mk["tmap"].items()}
            sof = lambda fav, inv=inv: 1 if inv.get(fav) == 0 else (-1 if inv.get(fav) == 1 else None)
            for r in rows_for_market(evs, mk["t0"], mk["t1"], sof, hs=1 if mk["tmap"][0] == "home_team" else -1): per_event.setdefault((r["t"], r["kind"]), []).append(r)
        rows = []
        for k, rs in per_event.items():
            avg = {f: st.mean(r[f] for r in rs) for f in ("pre", "post", "post_cap", "early", "age", "nprint", "rawpost", "rawpre")}
            ex = [r for r in rs if "net" in r]
            if ex: avg.update(entry=st.mean(r["entry"] for r in ex), mark=st.mean(r["mark"] for r in ex), net=st.mean(r["net"] for r in ex), gross=st.mean(r["gross"] for r in ex))
            avg.update(t=k[0], kind=k[1], s=1, st=rs[0]["st"], rnd=rs[0]["rnd"], gid=rs[0]["gid"], nmk=len(rs)); rows.append(avg)
        out[m["mid"]] = rows
    return out


def market_rows(M, kinds=("K",), plant=0.0, no_re=False, only=None):
    """audited-script-comparable table: event x market rows with the corrected map mapping (A1/A2). returns {mid:[rows]}"""
    out = {}
    for m in M:
        ev = dedup([e for e in m["ev"] if e[1] in kinds]); rows = []
        if no_re: ev = no_round_end_within(m["ev"], ev)
        for mk in m["mk"]:
            if only == "moneyline" and mk["mapno"] is not None or only == "map" and mk["mapno"] is None: continue
            evs = [e for e in ev if mk["mapno"] is None or m["ordn"].get(e[3]) == mk["mapno"]]
            inv = {v: k for k, v in mk["tmap"].items()}
            sof = lambda fav, inv=inv: 1 if inv.get(fav) == 0 else (-1 if inv.get(fav) == 1 else None)
            t0 = mk["t0"]
            if plant:
                t0 = plant_tok(t0, [(e[0], sof(e[2])) for e in evs if sof(e[2]) is not None], plant)
            rows += rows_for_market(evs, t0, mk["t1"], sof, hs=1 if mk["tmap"][0] == "home_team" else -1)
        out[m["mid"]] = rows
    return out


def shifted_vals(ev_all, evs, tok0, sof, rnd, lo=40.0, hi=240.0, avoid=20.0):
    """placebo B: keep each event's real sign (and the clustering of the sample) but move it by a random +-[lo,hi] s,
    dropping shifts that land within `avoid` s of a real PS event. A lead that survives is drift or stale prints, not the event."""
    ts = sorted(e[0] for e in ev_all); out = []
    for e in evs:
        s = sof(e[2])
        if s is None: continue
        t = e[0] + rnd.choice((-1, 1)) * rnd.uniform(lo, hi)
        i = bisect.bisect_left(ts, t)
        if (i < len(ts) and ts[i] - t < avoid) or (i and t - ts[i - 1] < avoid): continue
        b, _ = tok0.last(t); c, _ = tok0.last(t + H)
        if None in (b, c): continue
        out.append(s * (c - b))
    return out


def placebo_summary(M, ndraw=200, seed=17):
    rnd = random.Random(seed); A = []; B = []
    for _ in range(ndraw):
        va = []; vb = []
        for m in M:
            ev_k = dedup([e for e in m["ev"] if e[1] == "K"])
            for mk in m["mk"]:
                evs = [e for e in ev_k if mk["mapno"] is None or m["ordn"].get(e[3]) == mk["mapno"]]
                inv = {v: k for k, v in mk["tmap"].items()}
                sof = lambda fav, inv=inv: 1 if inv.get(fav) == 0 else (-1 if inv.get(fav) == 1 else None)
                va += placebo_rows(m["ev"], mk["t0"], m["t0"], m["t1"], len(evs), rnd)
                vb += shifted_vals(m["ev"], evs, mk["t0"], sof, rnd)
        if va: A.append(100 * st.mean(va))
        if vb: B.append(100 * st.mean(vb))
    def q(x): x = sorted(x); return dict(mean_c=st.mean(x), lo=x[int(.025 * len(x))], hi=x[int(.975 * len(x)) - 1], draws=len(x)) if x else None
    return dict(A_random_time_random_sign=q(A), B_shifted_events_real_sign=q(B))


def main(sd, cache, plant=0.0):
    M = [x for x in (load_match(f, cache) for f in sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz")))) if x]
    print("matches loaded:", len(M), "| with >=1 usable market:", sum(1 for m in M if m["mk"]))
    for m in M:
        print(f"  {m['mid']} {m['hn']} v {m['an']}: kills(dedup15)={len(dedup([e for e in m['ev'] if e[1]=='K']))} markets={[(k['q'][-24:], k['mapno']) for k in m['mk']]}")
    for name, rows in (("event x market rows (audited-comparable, corrected map mapping)", market_rows(M, plant=plant)),
                       ("one row per kill (dedup 15 s), markets averaged", build_rows(M, mode="dedup")),
                       ("first kill of each round only", build_rows(M, mode="round")),
                       ("kills with NO round end within 15 s, event x market rows", market_rows(M, no_re=True)),
                       ("  same, moneyline (BO3/BO5 winner) markets only", market_rows(M, no_re=True, only="moneyline")),
                       ("  same, Map N winner markets only", market_rows(M, no_re=True, only="map")),
                       ("all kills, moneyline markets only", market_rows(M, only="moneyline")),
                       ("all kills, Map N winner markets only", market_rows(M, only="map"))):
        print("\n==", name, "| plant", plant)
        print(json.dumps(summarise(rows, name), indent=1, default=str))
    print("\n== placebo (event-free random times, random sign, kill counts per market):", placebo_summary(M))


if __name__ == "__main__":
    a = sys.argv[1:]; pl = float(a[a.index("--plant") + 1]) if "--plant" in a else 0.0
    main(a[0], a[1], pl)
