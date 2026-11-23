#!/usr/bin/env python3
"""PandaScore CS2 kills vs each token's OWN book in pmcs2 (spec: reviewer/pandascore/SPEC-ps-kills-vs-pmcs2-own-books-2026-11-22.md; checker notes: reviewer/pandascore/CHECK-ps-kills-vs-pmcs2-2026-11-22.md).
usage: python3 -I feeds/ps_kills_vs_pmcs2.py SAMPLEDIR PMCS2DIR [--L 0.5] [--delay 1.0] [--plant 0.03] [--nplacebo 200] [--out result.json]
SAMPLEDIR = ps_sample_*.jsonl.gz (one match each); PMCS2DIR = markets.jsonl + books-*.jsonl[.gz]. Offline, read-only, no network.
Events: audit_ps_inround.events/dedup (kills, 15 s). Map N = rank of game_id (Map-N markets skipped if the capture started mid-game). ONE ROW PER EVENT (markets averaged).
Entry = favoured token's OWN best ask in the first row at/after recv+1 s+L (within 5 s) = PRIMARY ('row'); book STATE at that time (last row <= T) = 'state'.
Markout = own best bid (last row <= entry+15 s / +60 s). Fee on entry only: 0.03 and 0.05 * p*(1-p). Inference clustered by match.
GATE: real numbers are printed only if every control passes (plant recovery 95-105% on ISOLATED events, placebo and shift controls read -spread, label swap below real)."""
import sys, os, re, json, gzip, glob, bisect, random, calendar, time, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_ps_inround import events, dedup, ordinals, team_map, norm, boot_matches, sign_test_p

DELAY = 1.0; MAXWAIT = 5.0; PLANT_AT = 5.0; PLANT_LEN = 25.0; HS = (15.0, 60.0); ISO_BEFORE = 30.0; ISO_AFTER = 15.0


def fee(p, rate): return rate * p * (1 - p)


class Book:
    """own book of ONE token: sorted rows (t seconds, bid, ask, ask_size). Rows are change-driven, so the book STATE at t is the last row <= t."""
    def __init__(self, rows): self.r = sorted(rows, key=lambda x: x[0]); self.t = [x[0] for x in self.r]

    def state(self, t):
        i = bisect.bisect_right(self.t, t)
        return self.r[i - 1] if i else None

    def first_at_or_after(self, t, wait=MAXWAIT):
        i = bisect.bisect_left(self.t, t)
        return self.r[i] if i < len(self.t) and self.r[i][0] - t <= wait else None


def plant_book(book, evs, delta):
    """RAW-ROW plant on a COPY: for each (t, s) shift every row in [t+5, t+30) by s*delta, plus breakpoint rows at t+5 and t+30. Never mutates `book`."""
    def shift(x): return sum(s * delta for t, s in evs if t + PLANT_AT <= x < t + PLANT_AT + PLANT_LEN)
    def mv(v, d): return None if v is None else min(.99, max(.01, v + d))
    rows = [(x[0], mv(x[1], shift(x[0])), mv(x[2], shift(x[0])), x[3] if len(x) > 3 else None) for x in book.r]
    for t, s in evs:
        for bp in (t + PLANT_AT, t + PLANT_AT + PLANT_LEN):
            b = book.state(bp)
            if b: rows.append((bp, mv(b[1], shift(bp)), mv(b[2], shift(bp)), b[3] if len(b) > 3 else None))
    return Book(rows)


def trade_event(book, t, L, rates=(0.03, 0.05)):
    """one decision at PandaScore recv time t for the favoured token."""
    T = t + DELAY + L
    row = book.first_at_or_after(T); sst = book.state(T); out = {}
    for tag, r in (("row", row), ("state", sst)):
        if r is None or r[2] is None: out[tag] = None; continue
        ask = r[2]; res = {"ask": ask, "row_delay": r[0] - T, "asize": r[3] if len(r) > 3 else None, "spread": None if r[1] is None else ask - r[1]}
        for h in HS:
            e = book.state(T + h)
            if e is None or e[1] is None: res[h] = None; continue
            g = e[1] - ask
            res[h] = {"gross": g, "net03": g - fee(ask, rates[0]), "net05": g - fee(ask, rates[1]), "age": T + h - e[0]}
        out[tag] = res
    return out


def load_books(d, t0, t1):
    mk = []
    for l in open(os.path.join(d, "markets.jsonl")):
        try: mk.append(json.loads(l))
        except Exception: pass
    want = {t for m in mk for t in m.get("tokens", [])}; rows = {t: [] for t in want}
    for p in sorted(glob.glob(os.path.join(d, "books-*.jsonl*"))):
        mh = re.match(r"books-(\d{10})\.jsonl", os.path.basename(p))
        if mh:   # hour filter: only hours overlapping [t0-1 h, t1+1 h]; never parse a whole recorder history
            h0 = calendar.timegm(time.strptime(mh.group(1), "%Y%m%d%H"))
            if h0 + 3600 < t0 - 3600 or h0 > t1 + 3600: continue
        op = gzip.open if p.endswith(".gz") else open
        try:
            with op(p, "rt") as f:
                for l in f:
                    try: r = json.loads(l)
                    except Exception: continue
                    a = r.get("asset")
                    if a in rows and t0 - 120 <= r["recv_ms"] / 1000 <= t1 + 420:
                        asks = r.get("asks") or []
                        rows[a].append((r["recv_ms"] / 1000, r.get("bid"), r.get("ask"), asks[0].get("size") if asks and isinstance(asks[0], dict) else None))
        except Exception as e: sys.stderr.write("skip %s: %s\n" % (os.path.basename(p), e))
    return mk, {t: Book(r) for t, r in rows.items() if r}


def series_ordinals(msgs):
    """Map N = order of first appearance of game_id in the capture (all messages, not only those with events). Returns (ordn, mid_game_start)."""
    order = []; first = None
    for m in msgs:
        g = m["payload"].get("game_id")
        if g is not None and g not in order: order.append(g)
        cr = m["payload"].get("current_round") or {}
        if first is None and g is not None and cr: first = (cr.get("round_number") or 0)
    return {g: i + 1 for i, g in enumerate(order)}, bool(first and first > 1)   # capture must open before the first round of the first game seen


def load_match(f, mk, books):
    msgs = [json.loads(l) for l in gzip.open(f, "rt")]
    p0 = next((m["payload"] for m in reversed(msgs) if m["payload"].get("home_team") and m["payload"].get("away_team")), None)
    if not p0: return None
    hn, an = p0["home_team"].get("team_name"), p0["away_team"].get("team_name")
    ev = events(msgs); ordn, midgame = series_ordinals(msgs)
    mks = []
    for m in mk:
        q = (m.get("q") or ""); ql = q.lower()
        if not (norm(hn) in norm(q) and norm(an) in norm(q)): continue
        if any(w in ql for w in ("total", "handicap", "o/u", "spread")): continue
        tm = team_map(m.get("outcomes") or [], hn, an)
        if not tm or len(m.get("tokens", [])) != 2 or any(t not in books for t in m["tokens"]): continue
        mn = re.search(r"map (\d+)", ql)
        if mn and midgame: continue   # capture started mid-game: game rank unreliable, skip Map N markets
        mks.append(dict(q=q, mapno=int(mn.group(1)) if mn else None, tok={tm[j]: books[m["tokens"][j]] for j in (0, 1)}))
    return dict(mid=msgs[0].get("match_id"), hn=hn, an=an, t0=msgs[0]["recv_ns"] / 1e9, t1=msgs[-1]["recv_ns"] / 1e9, ev=ev, ordn=ordn, mk=mks)


def other(tm): return "away_team" if tm == "home_team" else "home_team"


def isolated(ks, e):
    """no other kept kill within ISO_BEFORE s before and ISO_AFTER s after (the plant lasts 25 s and the markout reads +15 s)."""
    return not any(o is not e and e[0] - ISO_BEFORE <= o[0] <= e[0] + ISO_AFTER for o in ks)


def run(M, L, mode="real", plant=0.0, rnd=None, only_isolated=False):
    """returns {match_id: [event rows]}; ONE row per event (markets averaged inside summ via the 'rows' list).
    mode: real | swap (buy the OTHER token) | shift (events +300 s) | placebo (event-free random times, random side)."""
    out = {}
    for m in M:
        ks = dedup([e for e in m["ev"] if e[1] == "K"]); per = {}
        for mk in m["mk"]:
            books = mk["tok"]
            if mode == "placebo":
                ts = sorted(e[0] for e in m["ev"]); evs = []; tries = 0
                while len(evs) < len(ks) and tries < 5000:
                    tries += 1; t = rnd.uniform(m["t0"], m["t1"]); i = bisect.bisect_left(ts, t)
                    if (i < len(ts) and ts[i] - t < 30) or (i and t - ts[i - 1] < 30): continue
                    evs.append((t, "K", rnd.choice(("home_team", "away_team")), None, None))
            else:
                evs = [e for e in ks if mk["mapno"] is None or m["ordn"].get(e[3]) == mk["mapno"]]
                if only_isolated: evs = [e for e in evs if isolated(ks, e)]
                if mode == "shift": evs = [(e[0] + 300,) + e[1:] for e in evs if e[0] + 300 <= m["t1"]]
            bk = dict(books)
            if plant:
                for tmk in ("home_team", "away_team"):
                    bk[tmk] = plant_book(books[tmk], [(e[0], 1 if e[2] == tmk else -1) for e in evs], plant)
            for e in evs:
                fav = other(e[2]) if mode == "swap" else e[2]
                per.setdefault((round(e[0], 3), fav), []).append(trade_event(bk[fav], e[0], L))
        out[m["mid"]] = [dict(t=k[0], rs=v) for k, v in sorted(per.items())]   # one entry per event; v = one result per market
    return out


def _ev_val(ev, tag, h, key):
    xs = [r[tag][h][key] for r in ev["rs"] if r.get(tag) and r[tag].get(h)]
    return st.mean(xs) if xs else None


def summ(R, tag="row", h=15.0, key="net03", ci=0.95):
    per = {}; skipped = 0; n = 0; gaps = []; ages = []; sizes = []
    for mid, evs in R.items():
        v = []
        for ev in evs:
            n += 1; x = _ev_val(ev, tag, h, key)
            if x is None: skipped += 1; continue
            v.append(x)
            for r in ev["rs"]:
                if r.get(tag):
                    gaps.append(r[tag]["row_delay"])
                    if r[tag].get(h): ages.append(r[tag][h]["age"])
                    if r[tag].get("asize") is not None: sizes.append(r[tag]["asize"])
        if v: per[mid] = v
    allv = [x for v in per.values() for x in v]
    if not allv: return dict(n_events=n, skipped=skipped, matches=0)
    lo, hi = boot_matches(per, nb=5000) if ci == 0.95 else _boot(per, ci)
    mm = [st.mean(v) for v in per.values()]
    return dict(n_events=n, skipped=skipped, used=len(allv), matches=len(per), mean_c=100 * st.mean(allv), ci=ci, boot_c=[100 * lo, 100 * hi],
                matches_positive=sum(x > 0 for x in mm), sign_test_p=sign_test_p(mm), median_row_gap_s=st.median(gaps) if gaps else None,
                median_markout_age_s=st.median(ages) if ages else None, median_ask_size=st.median(sizes) if sizes else None)


def _boot(per, ci, nb=5000, seed=11):
    rnd = random.Random(seed); ms = list(per.values()); out = []
    for _ in range(nb):
        smp = [rnd.choice(ms) for _ in ms]; n = sum(len(x) for x in smp); out.append(sum(sum(x) for x in smp) / n if n else 0.0)
    out.sort(); a = (1 - ci) / 2
    return out[int(a * nb)], out[min(nb - 1, int((1 - a) * nb))]


def mean_spread_c(R, tag="row"):
    xs = [r[tag]["spread"] for evs in R.values() for ev in evs for r in ev["rs"] if r.get(tag) and r[tag].get("spread") is not None]
    return 100 * st.mean(xs) if xs else None


def shuffle_p(M, L, nperm=2000, seed=5):
    """within-match BLOCK label shuffle (60 s blocks): each block is scored with its real favoured token or the other token with prob 1/2; p = share of shuffles with mean >= real."""
    real = run(M, L); sw = run(M, L, "swap"); rnd = random.Random(seed); pairs = []
    for mid in real:
        for a, b in zip(real[mid], sw[mid]):
            x, y = _ev_val(a, "row", 15.0, "gross"), _ev_val(b, "row", 15.0, "gross")
            if x is not None and y is not None: pairs.append(((mid, int(a["t"] // 60)), x, y))
    if not pairs: return None
    obs = st.mean(p[1] for p in pairs); c = 0; blocks = sorted({p[0] for p in pairs})
    for _ in range(nperm):
        flip = {b: rnd.random() < .5 for b in blocks}   # BLOCK shuffle: all events of one match within the same 60 s share a label flip (kills inside a round are correlated)
        if st.mean(p[2] if flip[p[0]] else p[1] for p in pairs) >= obs - 1e-12: c += 1
    return c / nperm


def main(sd, pd, L=0.5, plant=0.03, nplace=200):
    fs = sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz")))
    t0 = min(json.loads(next(gzip.open(f, "rt")))["recv_ns"] for f in fs) / 1e9
    t1 = max(json.loads(l)["recv_ns"] for f in fs for l in gzip.open(f, "rt")) / 1e9
    mk, books = load_books(pd, t0, t1)
    M = [x for x in (load_match(f, mk, books) for f in fs) if x and x["mk"]]
    res = dict(L=L, matches_with_both_token_books=len(M), match_ids=[m["mid"] for m in M])
    R = run(M, L); spread = mean_spread_c(R)
    # ---- controls first
    ctl = {}
    swap = summ(run(M, L, "swap"), "row", 15.0, "gross"); real_g = summ(R, "row", 15.0, "gross")
    ctl["swap_gross"] = swap; ctl["swap_below_real"] = bool(swap.get("used") and real_g.get("used") and swap["mean_c"] < real_g["mean_c"])
    sh = summ(run(M, L, "shift"), "row", 15.0, "gross"); ctl["shift300_gross"] = sh
    rnd = random.Random(7); pl = []
    for _ in range(nplace):
        pr_ = run(M, L, "placebo", rnd=rnd); s = summ(pr_, "row", 15.0, "gross"); sp_ = mean_spread_c(pr_)
        if s.get("used") and sp_ is not None: pl.append(s["mean_c"] + sp_)     # deviation of placebo gross from MINUS ITS OWN entry spread; no edge reads 0
    pl.sort()
    if pl:
        ctl["placebo_dev_from_minus_spread_c"] = dict(draws=len(pl), mean=st.mean(pl), p2_5=pl[int(.025 * len(pl))], p97_5=pl[min(len(pl) - 1, int(.975 * len(pl)))])
    shift_run = run(M, L, "shift"); sh_sp = mean_spread_c(shift_run); ctl["expected_gross_if_no_edge_c_real_times"] = None if spread is None else -spread
    ok_pl = bool(pl and ctl["placebo_dev_from_minus_spread_c"]["p2_5"] - 0.05 <= 0 <= ctl["placebo_dev_from_minus_spread_c"]["p97_5"] + 0.05)   # each control compared with its OWN spread
    ok_sh = bool(sh.get("used") and sh_sp is not None and sh["boot_c"][0] - 0.05 <= -sh_sp <= sh["boot_c"][1] + 0.05)
    ctl["placebo_ok"] = ok_pl; ctl["shift_ok"] = ok_sh
    ok_plant = False
    if plant:
        base = summ(run(M, L, only_isolated=True), "row", 15.0, "gross"); pr = summ(run(M, L, plant=plant, only_isolated=True), "row", 15.0, "gross")
        if base.get("used", 0) >= 5 and pr.get("used", 0) >= 5:   # fewer than 5 isolated events: not measurable
            rec = (pr["mean_c"] - base["mean_c"]) / (100 * plant)
            ok_plant = 0.95 <= rec <= 1.05
            ctl["plant"] = dict(plant_c=100 * plant, recovery=rec, in_band_95_105=ok_plant, isolated_events=base["used"], note="events with no other kept kill within -30/+15 s only")
        else: ctl["plant"] = dict(recovery=None, note="no isolated events: plant not measurable, gate FAILS")
    res["controls"] = ctl
    res["gate_pass"] = bool(ok_plant and ok_pl and ok_sh and ctl["swap_below_real"])
    if not res["gate_pass"]:
        res["real"] = "WITHHELD: a control failed (see controls); no real number is reported"
    else:
        res["real"] = {"row_15s_net03_95": summ(R, "row", 15.0, "net03"), "row_15s_net03_99": summ(R, "row", 15.0, "net03", ci=0.99),
                       "row_15s_net05_95": summ(R, "row", 15.0, "net05"), "state_15s_net03_95": summ(R, "state", 15.0, "net03"),
                       "row_60s_net03_95": summ(R, "row", 60.0, "net03"), "row_15s_gross": real_g, "mean_spread_c": spread,
                       "within_match_shuffle_p_gross": shuffle_p(M, L),
                       "sens_L0": summ(run(M, 0.0), "row", 15.0, "net03"), "sens_L1": summ(run(M, 1.0), "row", 15.0, "net03")}
    print(json.dumps(res, indent=1, default=str)); return res


if __name__ == "__main__":
    a = sys.argv[1:]; g = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    DELAY = g("--delay", 1.0)   # R-065: market seconds_delay read from CLOB /markets (1 s on CS2 match markets, 23 Nov 09:00Z); never assume 250 ms
    r = main(a[0], a[1], g("--L", 0.5), g("--plant", 0.03), g("--nplacebo", 200))
    if "--out" in a: json.dump(r, open(a[a.index("--out") + 1], "w"), indent=1, default=str)
