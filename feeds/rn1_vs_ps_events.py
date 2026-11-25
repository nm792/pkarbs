#!/usr/bin/env python3
"""R-093: do RN1's CS2 fills cluster BEFORE or AFTER public PandaScore kill / round-end messages? Public data, read-only, paper only.
usage: python3 -I feeds/rn1_vs_ps_events.py SAMPLEDIR CACHEDIR [--user 0x2005d16a84ceefa912d4e380cd32e7ff827875ea] [--out result.json]
For every PS sample match: markets from gamma (audit_ps_inround.find_markets, moneyline + Map N), his fills per market from data-api v2 /trades?user=..&condition_id=.. (taker_only=true = TAKER fills; taker_only=false = taker+maker, maker = false minus true by tx hash+size),
every row asserted: proxy_wallet == user AND condition_id == request. Events = audit_ps_inround.events (K kills, T round ends) at PS recv_ns. Per fill: signed time to nearest earlier / later event. delta = fill_time - event_time over all events within +-60 s, 1 s bins.
Placebos: (a) his MAKER fills, (b) random times uniformly inside the same match span, same count as his taker fills, 200 draws. Fill timestamps are whole seconds (data-api) so the test cannot resolve below ~1 s."""
import sys, os, re, json, gzip, glob, bisect, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_ps_inround as A

W = 60

def user_fills(cid, user, cache, taker_only, fetch=None):
    fetch = fetch or A.get
    p = os.path.join(cache, "fills_%s_%s_%s.json" % (user[:8], cid, "t" if taker_only else "all"))
    if os.path.exists(p): return check(json.load(open(p)), user, cid)
    out = []; cur = None
    for _ in range(40):
        j = fetch("https://data-api.polymarket.com/v2/trades?user=%s&condition_id=%s&limit=500&taker_only=%s" % (user, cid, "true" if taker_only else "false") + ("&cursor=%s" % cur if cur else ""))
        out += check(j.get("data", []), user, cid); cur = j.get("next_cursor")
        if not cur or not j.get("data"): break
    os.makedirs(cache, exist_ok=True); json.dump(out, open(p, "w")); return out

def check(rows, user, cid):
    bad = [r for r in rows if r.get("proxy_wallet") != user or r.get("condition_id") != cid]
    if bad: raise A.WrongMarketRows("%d rows are not user %s / condition %s" % (len(bad), user, cid))
    return rows

def maker_of(all_rows, taker_rows):
    t = {(r["transaction_hash"], r["size"], r["price"]) for r in taker_rows}
    return [r for r in all_rows if (r["transaction_hash"], r["size"], r["price"]) not in t]

def hist(fill_ts, ev_ts):
    """counts of (fill - event) in 1 s bins [-W, W); ev_ts sorted."""
    h = [0] * (2 * W)
    for f in fill_ts:
        lo = bisect.bisect_left(ev_ts, f - W); hi = bisect.bisect_right(ev_ts, f + W)
        for e in ev_ts[lo:hi]:
            d = int(f - e + W) if (f - e) >= -W and (f - e) < W else None
            if d is not None and 0 <= d < 2 * W: h[d] += 1
    return h

def nearest(f, ev_ts):
    i = bisect.bisect_left(ev_ts, f)
    before = f - ev_ts[i - 1] if i else None; after = ev_ts[i] - f if i < len(ev_ts) else None
    return before, after   # seconds since the last event; seconds until the next

def summarize(fills, ev_ts):
    nb = [nearest(f, ev_ts) for f in fills]
    sb = [b for b, a in nb if b is not None]; sa = [a for b, a in nb if a is not None]
    h = hist(fills, ev_ts); pre = sum(h[W - 10:W]); post = sum(h[W:W + 10])
    return dict(n=len(fills), median_since_last_event_s=st.median(sb) if sb else None, median_until_next_event_s=st.median(sa) if sa else None,
                pre10=pre, post10=post, pre5=sum(h[W - 5:W]), post5=sum(h[W:W + 5]), hist=h)

def main(sd, cache, user, out=None):
    ms = [x for x in (A.load_match(f, cache) for f in sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz")))) if x]
    res = dict(user=user, matches=len(ms), per_match=[]); allT = []; allM = []; ev_by = {}
    pl_pre = []; rnd = random.Random(9)
    for m in ms:
        ev_ts = sorted(e[0] for e in m["ev"] if e[1] in ("K", "T")); t0, t1 = m["t0"], m["t1"]
        T = []; Mk = []
        for mk in m["mk"]:
            t_rows = user_fills(mk["cid"], user, cache, True); a_rows = user_fills(mk["cid"], user, cache, False)
            T += [r["timestamp"] for r in t_rows if t0 - W <= r["timestamp"] <= t1 + W]
            Mk += [r["timestamp"] for r in maker_of(a_rows, t_rows) if t0 - W <= r["timestamp"] <= t1 + W]
        res["per_match"].append(dict(match_id=m["mid"], label="%s v %s" % (m["hn"], m["an"]), taker_fills_in_window=len(T), maker_fills_in_window=len(Mk), events=len(ev_ts)))
        allT += [(m["mid"], x) for x in T]; allM += [(m["mid"], x) for x in Mk]; ev_by[m["mid"]] = (ev_ts, t0, t1)
    res["overlap_taker_fills"] = len(allT); res["overlap_maker_fills"] = len(allM)
    if not allT:
        res["verdict"] = "OVERLAP COUNT 0: no taker fills by this user in any sample match market (any time) / window"
        if allM:   # maker fills (placebo class) against the same events, with a random-time placebo of the same count
            H = [0] * (2 * W)
            for mid, f in allM: H = [a + b for a, b in zip(H, hist([f], ev_by[mid][0]))]
            pls = []
            for _ in range(200):
                HH = [0] * (2 * W)
                for mid, _f in allM: HH = [a + b for a, b in zip(HH, hist([random.Random(rnd.random()).uniform(ev_by[mid][1], ev_by[mid][2])], ev_by[mid][0]))]
                pls.append((sum(HH[W - 10:W]), sum(HH[W:W + 10])))
            res["maker"] = dict(n=len(allM), pre10=sum(H[W - 10:W]), post10=sum(H[W:W + 10]), hist=H)
            res["maker_placebo_random_times"] = dict(draws=200, pre10_mean=st.mean(p[0] for p in pls), post10_mean=st.mean(p[1] for p in pls), pre10_sd=st.pstdev(p[0] for p in pls), post10_sd=st.pstdev(p[1] for p in pls))
        print(json.dumps(res, indent=1, default=str)); 
        if out: json.dump(res, open(out, "w"), indent=1, default=str)
        return res
    def agg(pairs):
        H = [0] * (2 * W); nb = []
        for mid, f in pairs:
            ev_ts = ev_by[mid][0]; hh = hist([f], ev_ts); H = [a + b for a, b in zip(H, hh)]; nb.append(nearest(f, ev_ts))
        return H, nb
    HT, nbT = agg(allT); HM, nbM = agg(allM)
    res["taker"] = dict(summarize([f for _, f in allT][:0] or [], [0]) if False else {})
    res["taker"] = dict(n=len(allT), pre10=sum(HT[W - 10:W]), post10=sum(HT[W:W + 10]), pre5=sum(HT[W - 5:W]), post5=sum(HT[W:W + 5]), hist=HT)
    res["maker"] = dict(n=len(allM), pre10=sum(HM[W - 10:W]), post10=sum(HM[W:W + 10]), hist=HM)
    pls = []
    for _ in range(200):
        pairs = []
        for mid, _f in allT:
            ev_ts, t0, t1 = ev_by[mid]; pairs.append((mid, rnd.uniform(t0, t1)))
        H, _nb = agg(pairs); pls.append((sum(H[W - 10:W]), sum(H[W:W + 10])))
    pre = [p[0] for p in pls]; post = [p[1] for p in pls]
    res["placebo_random_times"] = dict(draws=200, pre10_mean=st.mean(pre), post10_mean=st.mean(post), pre10_sd=st.pstdev(pre), post10_sd=st.pstdev(post))
    z = lambda x, xs: (x - st.mean(xs)) / (st.pstdev(xs) or 1)
    res["taker_pre10_z_vs_random"] = z(res["taker"]["pre10"], pre); res["taker_post10_z_vs_random"] = z(res["taker"]["post10"], post)
    print(json.dumps(res, indent=1, default=str))
    if out: json.dump(res, open(out, "w"), indent=1, default=str)
    return res

if __name__ == "__main__":
    a = sys.argv[1:]; g = lambda k, d: a[a.index(k) + 1] if k in a else d
    main(a[0], a[1], g("--user", "0x2005d16a84ceefa912d4e380cd32e7ff827875ea"), g("--out", None))
