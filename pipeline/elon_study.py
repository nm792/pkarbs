"""Elon 48h tweet-count series: listing path and count nowcast (xtracker hourly counts) + boundary-distance rule vs the market.
Counts: xtracker hourly 'daily' stats (fetched via TinyFish; cached /home/user/pk_cache/elon_hourly.json). Brackets parsed from market questions.
Nowcast at time T: count so far in [start, T) + sum over remaining hours of the mean count for that UTC hour-of-day over the previous 21 days (hours before T only).
Spread: sd = k * remaining, k fitted on the chronologically FIRST half of events (relative sd of actual remaining vs predicted); evaluated on the SECOND half.
Boundary distance d = min(mu - lo, hi - mu) / sd of the picked bracket; trade if d >= DMIN. Market = own YES-token last print at/before T (+1 / +10 min for the market's later pick).
Fill = earliest BUY print of the picked YES token at or after T+1 min (or T+10 min) within 20 min; edge = win - fill. No fees."""
import bisect, collections, concurrent.futures as cf, datetime as dt, json, math, os, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen
HOURS = json.load(open("/home/user/pk_cache/elon_hourly.json"))
HK = sorted(HOURS); HT = np.array([dt.datetime.fromisoformat(k.replace("Z", "+00:00")).timestamp() for k in HK]); HC = np.array([HOURS[k] for k in HK], float)
DMIN = 0.5
Hs = (None, 36, 24, 12, 6, 3)   # None = at listing (+1/+10 min)


def cnt(a, b):
    return float(HC[(HT >= a) & (HT < b)].sum())


def profile(t, days=21):
    m = (HT >= t - days * 86400) & (HT < t); c = collections.defaultdict(list)
    for ts, v in zip(HT[m], HC[m]): c[int((ts % 86400) // 3600)].append(v)
    return [float(np.mean(c[h])) if c[h] else 0.0 for h in range(24)]


def remaining(t, end, prof):
    s = 0.0; x = t
    while x < end:
        nx = min(end, (x // 3600 + 1) * 3600); s += prof[int((x % 86400) // 3600)] * (nx - x) / 3600; x = nx
    return s


def parse_bracket(q):
    m = re.search(r"post (<?\d+\+?|\d+-\d+) tweets", q)
    if not m: return None
    s = m.group(1)
    if s.startswith("<"): return (0, int(s[1:]) - 1)
    if s.endswith("+"): return (int(s[:-1]), 10 ** 9)
    a, b = s.split("-"); return (int(a), int(b))


def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bprob(lo, hi, mu, sd):
    return Phi((hi + 0.5 - mu) / sd) - Phi((lo - 0.5 - mu) / sd)


def load():
    out = {}
    for p in ("/home/user/pk_cache/events.jsonl", "/home/user/pk_cache/events_deep.jsonl"):
        for l in open(p):
            e = json.loads(l)
            if e.get("seriesSlug") == "elon-tweets-48h": out[e["id"]] = e
    return sorted(out.values(), key=lambda e: e["endDate"])


def last_px(rows, t, max_age=7200):
    p = [(r[0], r[3]) for r in rows if r[0] <= t]
    if not p: return None
    ts, px = max(p); return px if t - ts <= max_age else None


def main():
    evs = []
    for e in load():
        end = screen.parse_ts(e["endDate"]); start = end - 172800; ls = screen.parse_ts(e["startDate"])
        if start < HT[0] + 22 * 86400 or end > HT[-1]: continue
        bk = []
        for m in e["markets"]:
            b = screen.binary_resolved(m); br = parse_bracket(m.get("question") or "")
            if not b or not br: bk = None; break
            lab = [x.lower() for x in b["labels"]]; iy = lab.index("yes")
            bk.append(dict(lo=br[0], hi=br[1], tok=b["tokens"][iy], cond=b["cond"], win=(b["win"] == iy)))
        if not bk or sum(x["win"] for x in bk) != 1: continue
        evs.append(dict(e=e, start=start, end=end, ls=ls, bk=bk))
    print(len(evs), "events with brackets+counts", flush=True)
    jobs = [(i, j) for i, ev in enumerate(evs) for j in range(len(ev["bk"]))]
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda ij: screen.get_trades(evs[ij[0]]["bk"][ij[1]]["cond"]), jobs))
    for (i, j), d in zip(jobs, res): evs[i]["bk"][j]["rows"] = [tuple(r) for r in d["rows"] if r[2] == evs[i]["bk"][j]["tok"]]; evs[i]["bk"][j]["trunc"] = bool(d.get("trunc"))
    chk = []
    for ev in evs:
        fin = cnt(ev["start"], ev["end"]); ev["final"] = fin
        w = [b for b in ev["bk"] if b["win"]][0]; chk.append(w["lo"] <= fin <= w["hi"])
    print("count inside winning bracket:", sum(chk), "/", len(chk), "; truncated markets:", sum(b["trunc"] for ev in evs for b in ev["bk"]), flush=True)
    # LISTING PATH
    lst = []
    for ev in evs:
        allr = [r for b in ev["bk"] for r in b["rows"] if r[0] >= ev["ls"]]; allr.sort()
        w = [b for b in ev["bk"] if b["win"]][0]
        def px_at(b, off): return last_px(b["rows"], ev["ls"] + off, 1800)
        pk = {off: max([(px_at(b, off) or 0, b is w) for b in ev["bk"]])[1] if any(px_at(b, off) for b in ev["bk"]) else None for off in (60, 600, 1800)}
        lst.append(dict(date=ev["e"]["endDate"][:10], ls_to_start_h=(ev["start"] - ev["ls"]) / 3600, first_print_s=(allr[0][0] - ev["ls"]) if allr else None,
                        usd5=sum(r[3] * r[4] for r in allr if r[0] <= ev["ls"] + 300), usd30=sum(r[3] * r[4] for r in allr if r[0] <= ev["ls"] + 1800),
                        buy_usd30=sum(r[3] * r[4] for r in allr if r[0] <= ev["ls"] + 1800 and r[1] == "BUY"), fav1=pk[60], fav10=pk[600], fav30=pk[1800],
                        win_px30=px_at(w, 1800), vol=float(ev["e"].get("volume") or 0)))
    pd.DataFrame(lst).to_csv("out/listing1/elon_listing.csv", index=False)
    # NOWCAST
    half = len(evs) // 2; rows = []
    for H in Hs:
        ks = []
        for ev in evs[:half]:
            T = ev["start"] - 0 if H is None else ev["end"] - H * 3600
            if H is None: T = ev["start"]
            so = cnt(ev["start"], T); rp = remaining(T, ev["end"], profile(T))
            if rp > 5: ks.append((ev["final"] - so - rp) / rp)
        bias = float(np.mean(ks)); k = float(np.std(ks))
        for n, ev in enumerate(evs):
            tdec = ev["ls"] + 60 if H is None else ev["end"] - H * 3600
            Tn = ev["start"] if H is None else tdec          # count/rate evaluated at the window start for the listing case (count 0)
            if H is None: Tn = ev["ls"]                      # at listing: forecast the whole window from rates known at listing
            so = cnt(ev["start"], Tn) if Tn > ev["start"] else 0.0; rp = remaining(max(Tn, ev["start"]), ev["end"], profile(Tn))
            mu = so + rp * (1 + bias); sd = max(k * rp, math.sqrt(max(rp, 1)))
            pr = [(bprob(b["lo"], b["hi"], mu, sd), b) for b in ev["bk"]]; p, pick = max(pr, key=lambda x: x[0])
            dist = min(mu - pick["lo"], pick["hi"] - mu) / sd if pick["hi"] < 10 ** 9 and pick["lo"] > 0 else (pick["hi"] - mu) / sd if pick["lo"] == 0 else (mu - pick["lo"]) / sd
            mk = [(last_px(b["rows"], tdec) or 0, b) for b in ev["bk"]]; mkt_pick = max(mk, key=lambda x: x[0]); mkt_ok = mkt_pick[0] > 0
            def fbuy(off):
                w2 = [r for r in pick["rows"] if r[1] == "BUY" and tdec + off <= r[0] <= tdec + off + 1200]
                if not w2: return None, 0.0
                r = min(w2); return r[3], r[4]
            f1, s1 = fbuy(0); f10, s10 = fbuy(600)
            dep = sum(r[3] * r[4] for r in pick["rows"] if r[1] == "BUY" and tdec <= r[0] <= tdec + 600)
            extra = {}
            if H is None:
                for X, nm in ((1800, "30m"), (7200, "2h"), (21600, "6h"), (86400, "24h"), (172800, "48h")):
                    w3 = [r for r in pick["rows"] if r[1] == "BUY" and tdec <= r[0] <= ev["ls"] + X]
                    extra["pnl_" + nm] = float(sum((float(pick["win"]) - r[3]) * r[4] for r in w3)); extra["stake_" + nm] = float(sum(r[3] * r[4] for r in w3)); extra["n_" + nm] = len(w3)
            rows.append(dict(**extra, H=("listing" if H is None else H), half=("train" if n < half else "test"), date=ev["e"]["endDate"][:10], mu=mu, sd=sd, p=p, d=dist, hit=pick["win"],
                             mkt_hit=(mkt_pick[1]["win"] if mkt_ok else None), mkt_px=mkt_pick[0] if mkt_ok else None, fill1=f1, size1=s1, fill10=f10, size10=s10, depth10=dep,
                             price_pick_at_t=last_px(pick["rows"], tdec), k=k, bias=bias))
    df = pd.DataFrame(rows); df.to_csv("out/listing1/elon_rows.csv", index=False); print(len(df), "rows")


if __name__ == "__main__": main()
