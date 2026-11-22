#!/usr/bin/env python3
"""PandaScore CS2 kills vs each token's OWN book in pmcs2 (spec: reviewer/pandascore/SPEC-ps-kills-vs-pmcs2-own-books-2026-11-22.md).
usage: python3 -I feeds/ps_kills_vs_pmcs2.py SAMPLEDIR PMCS2DIR [--L 0.5] [--plant 0.03] [--nplacebo 200] [--out result.json]
SAMPLEDIR = ps_sample_*.jsonl.gz (one match each); PMCS2DIR = markets.jsonl + books-*.jsonl[.gz]. Offline, read-only, no network.
Events: audit_ps_inround.events/dedup (kills, 15 s). Map N = rank of game_id. Entry = favoured token's OWN best ask in the first row at/after
recv+1 s+L (within 5 s), also reported with book STATE at that time (last row at or before). Markout = own best bid (last row <= entry+15 s / +60 s).
Fees: both 0.03*p*(1-p) and 0.05*p*(1-p) (market fee field is not stored in markets.jsonl). Inference clustered by match."""
import sys, os, re, json, gzip, glob, bisect, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_ps_inround import events, dedup, ordinals, team_map, norm, boot_matches, sign_test_p

DELAY = 1.0; MAXWAIT = 5.0; PLANT_AT = 5.0; PLANT_LEN = 25.0; HS = (15.0, 60.0)


def fee(p, rate): return rate * p * (1 - p)


class Book:
    """own book of ONE token: sorted rows (t seconds, bid, ask). Rows are change-driven, so the book STATE at t is the last row <= t."""
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
    rows = [(x[0], mv(x[1], shift(x[0])), mv(x[2], shift(x[0]))) for x in book.r]
    for t, s in evs:
        for bp in (t + PLANT_AT, t + PLANT_AT + PLANT_LEN):
            b = book.state(bp)
            if b: rows.append((bp, mv(b[1], shift(bp)), mv(b[2], shift(bp))))
    return Book(rows)


def trade_event(book, t, L, rates=(0.03, 0.05)):
    """one decision at PandaScore recv time t for the favoured token. Returns dict or None (skip reason in 'skip')."""
    T = t + DELAY + L
    row = book.first_at_or_after(T)
    sst = book.state(T)
    out = {}
    for tag, r in (("row", row), ("state", sst)):
        if r is None or r[2] is None: out[tag] = None; continue
        ask = r[2]; res = {"ask": ask, "row_delay": r[0] - T}
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
        op = gzip.open if p.endswith(".gz") else open
        try:
            with op(p, "rt") as f:
                for l in f:
                    try: r = json.loads(l)
                    except Exception: continue
                    a = r.get("asset")
                    if a in rows and t0 - 120 <= r["recv_ms"] / 1000 <= t1 + 180: rows[a].append((r["recv_ms"] / 1000, r.get("bid"), r.get("ask")))
        except Exception as e: sys.stderr.write("skip %s: %s\n" % (os.path.basename(p), e))
    return mk, {t: Book(r) for t, r in rows.items() if r}


def load_match(f, mk, books):
    msgs = [json.loads(l) for l in gzip.open(f, "rt")]
    p0 = next((m["payload"] for m in reversed(msgs) if m["payload"].get("home_team") and m["payload"].get("away_team")), None)
    if not p0: return None
    hn, an = p0["home_team"].get("team_name"), p0["away_team"].get("team_name")
    ev = events(msgs); ordn = ordinals([e[3] for e in ev])
    mks = []
    for m in mk:
        q = (m.get("q") or ""); ql = q.lower()
        if not (norm(hn) in norm(q) and norm(an) in norm(q)): continue
        if any(w in ql for w in ("total", "handicap", "o/u", "spread")): continue
        tm = team_map(m.get("outcomes") or [], hn, an)
        if not tm or len(m.get("tokens", [])) != 2 or any(t not in books for t in m["tokens"]): continue
        mn = re.search(r"map (\d+)", ql)
        mks.append(dict(q=q, mapno=int(mn.group(1)) if mn else None, tok={tm[j]: books[m["tokens"][j]] for j in (0, 1)}))
    return dict(mid=msgs[0].get("match_id"), hn=hn, an=an, t0=msgs[0]["recv_ns"] / 1e9, t1=msgs[-1]["recv_ns"] / 1e9, ev=ev, ordn=ordn, mk=mks)


def other(tm): return "away_team" if tm == "home_team" else "home_team"


def run(M, L, mode="real", plant=0.0, rnd=None, nplace=200):
    """returns {match_id: [row dicts]}. mode: real | swap (buy the OTHER token) | shift (events +300 s) | placebo (event-free random times, random side)."""
    out = {}
    for m in M:
        ks = dedup([e for e in m["ev"] if e[1] == "K"]); rows = []
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
                if mode == "shift": evs = [(e[0] + 300,) + e[1:] for e in evs]
            bk = dict(books)
            if plant:
                for tmk in ("home_team", "away_team"):
                    pe = [(e[0], 1 if e[2] == tmk else -1) for e in evs]
                    bk[tmk] = plant_book(books[tmk], pe, plant)
            for e in evs:
                fav = other(e[2]) if mode == "swap" else e[2]
                r = trade_event(bk[fav], e[0], L)
                rows.append(dict(t=e[0], q=mk["q"], **r))
        out[m["mid"]] = rows
    return out


def summ(R, tag="row", h=15.0, key="net03"):
    per = {}; skipped = 0; n = 0
    for mid, rows in R.items():
        v = []
        for r in rows:
            n += 1; x = r.get(tag)
            if not x or not x.get(h): skipped += 1; continue
            v.append(x[h][key])
        if v: per[mid] = v
    allv = [x for v in per.values() for x in v]
    if not allv: return dict(n_events=n, skipped=skipped, matches=0)
    lo, hi = boot_matches(per)
    mm = [st.mean(v) for v in per.values()]
    return dict(n_events=n, skipped=skipped, used=len(allv), matches=len(per), mean_c=100 * st.mean(allv), boot95_c=[100 * lo, 100 * hi],
                matches_positive=sum(x > 0 for x in mm), sign_test_p=sign_test_p(mm))


def main(sd, pd, L=0.5, plant=0.03, nplace=200):
    fs = sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz")))
    t0 = min(json.loads(next(gzip.open(f, "rt")))["recv_ns"] for f in fs) / 1e9; t1 = t0 + 10 * 86400
    mk, books = load_books(pd, t0, t1)
    M = [x for x in (load_match(f, mk, books) for f in fs) if x and x["mk"]]
    res = dict(L=L, matches_with_both_token_books=len(M), match_ids=[m["mid"] for m in M])
    R = run(M, L); res["real_row_15s_net03"] = summ(R, "row", 15.0, "net03"); res["real_row_15s_net05"] = summ(R, "row", 15.0, "net05")
    res["real_state_15s_net03"] = summ(R, "state", 15.0, "net03"); res["real_row_60s_net03"] = summ(R, "row", 60.0, "net03")
    res["real_row_15s_gross"] = summ(R, "row", 15.0, "gross")
    for L2 in (0.0, 1.0): res["sens_L%s_row_15s_net03" % L2] = summ(run(M, L2), "row", 15.0, "net03")
    res["control_swap_15s_gross"] = summ(run(M, L, "swap"), "row", 15.0, "gross")
    res["control_shift300_15s_gross"] = summ(run(M, L, "shift"), "row", 15.0, "gross")
    rnd = random.Random(7); pl = []
    for _ in range(nplace):
        pr = run(M, L, "placebo", rnd=rnd); s = summ(pr, "row", 15.0, "gross")
        if s.get("used"): pl.append(s["mean_c"])
    res["control_placebo_gross_c"] = dict(draws=len(pl), mean=st.mean(pl) if pl else None, sd=st.pstdev(pl) if len(pl) > 1 else None)
    if plant:
        base = summ(R, "row", 15.0, "gross"); pr = summ(run(M, L, plant=plant), "row", 15.0, "gross")
        if base.get("used") and pr.get("used"):
            rec = (pr["mean_c"] - base["mean_c"]) / (100 * plant)
            res["plant"] = dict(plant_c=100 * plant, recovery=rec, in_band_95_105=0.95 <= rec <= 1.05)
    print(json.dumps(res, indent=1, default=str)); return res


if __name__ == "__main__":
    a = sys.argv[1:]; g = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    r = main(a[0], a[1], g("--L", 0.5), g("--plant", 0.03), g("--nplacebo", 200))
    if "--out" in a: json.dump(r, open(a[a.index("--out") + 1], "w"), indent=1, default=str)
