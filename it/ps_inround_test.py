#!/usr/bin/env python3
"""In-round sign + placebo test. usage: python3 -I ps_inround_test.py SAMPLEDIR [--perm 5000]
For each sampled match and each winner market (match winner, or Map N winner for the map in play), signed move:
  s*(P(t+H) - P(t))  and  s*(P(t) - P(t-H)),  H=15 s, P=last public trade price before the time, outcome 0.
s=+1 if the event favours the outcome-0 team: kill = opponent alive count drops; round end = that team's score rises.
Events within 15 s of the previous kept event of the same kind are dropped (clustering). Bomb events are reported unsigned only.
Statistic: mean post move (lead) and mean pre move (anticipation). Sign test: flip s at random 5000x, p = share of |mean| >= observed.
Placebo: same count of random event-free times per match, random sign. Pooled over matches (match = unit, also reported)."""
import sys, os, json, gzip, glob, bisect, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ps_chart_samples as C
H = 15; random.seed(7)
def team_events(msgs):
    out = []; prev = None
    for d in msgs:
        p = d["payload"]; t = d["recv_ns"] / 1e9; cr = p.get("current_round") or {}
        al = {}
        for tm in ("home_team", "away_team"):
            pl = (cr.get(tm) or {}).get("players") or []
            al[tm] = sum(bool(x.get("alive")) for x in pl) if pl else None
        cur = dict(sc=((p.get("home_team") or {}).get("score"), (p.get("away_team") or {}).get("score")), al=al, rnd=cr.get("round_number"), mp=p.get("map_id"))
        if prev and cur["mp"] == prev["mp"]:
            if cur["rnd"] == prev["rnd"]:
                for tm in ("home_team", "away_team"):
                    if cur["al"][tm] is not None and prev["al"][tm] is not None and cur["al"][tm] < prev["al"][tm]: out.append((t, "K", "away_team" if tm == "home_team" else "home_team", cur["mp"]))
            for i, tm in enumerate(("home_team", "away_team")):
                if None not in cur["sc"] + prev["sc"] and cur["sc"][i] > prev["sc"][i]: out.append((t, "T", tm, cur["mp"]))
        prev = cur
    ded = []; last = {}
    for e in out:
        if e[0] - last.get(e[1], -1e9) >= H: ded.append(e); last[e[1]] = e[0]
    return ded
def main(sd, nperm=5000, plant=0.0):
    rows = {"K": [], "T": []}; per = []
    for f in sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz"))):
        msgs = [json.loads(l) for l in gzip.open(f, "rt")]
        p0 = next((m["payload"] for m in reversed(msgs) if m["payload"].get("home_team")), None)
        if not p0: continue
        hn, an = p0["home_team"].get("team_name"), p0["away_team"].get("team_name"); t0, t1 = msgs[0]["recv_ns"] / 1e9, msgs[-1]["recv_ns"] / 1e9
        ev = team_events(msgs)
        for q, cid, outs in C.find_markets(hn, an, t0):
            ql = (q or "").lower()
            if any(w in ql for w in ("total", "handicap", "o/u")) or not outs: continue
            mapno = None
            if "map" in ql:
                import re; m = re.search(r"map (\d+)", ql); mapno = int(m.group(1)) if m else None
                if mapno is None: continue
            o0 = C.norm(outs[0]); tm0 = "home_team" if C.norm(hn) in o0 or o0 in C.norm(hn) else ("away_team" if C.norm(an) in o0 or o0 in C.norm(an) else None)
            if tm0 is None: continue
            tr = [x for x in C.trades(cid) if t0 - 60 <= x["timestamp"] <= t1 + 60 and x.get("outcome_index") == 0]
            if len(tr) < 30: continue
            tr.sort(key=lambda x: x["timestamp"]); ts = [x["timestamp"] for x in tr]; pr = [x["price"] for x in tr]
            if plant:  # PLANTED CHECK: inject a synthetic move of `plant` in the event direction 5 s after each event, undone at +H+1 s
                p_ = lambda t: pr[bisect.bisect_right(ts, t) - 1] if bisect.bisect_right(ts, t) else None
                add = []
                for t, k, fav, mp in ev:
                    if mapno is not None and mp != mapno: continue
                    b0 = p_(t)
                    if b0 is None: continue
                    s_ = 1 if fav == tm0 else -1
                    add += [(t + 5, min(.99, max(.01, b0 + s_ * plant))), (t + H + 1, b0)]
                z = sorted(list(zip(ts, pr)) + add, key=lambda x: x[0]); ts = [a for a, _ in z]; pr = [b for _, b in z]
            px = lambda t: pr[bisect.bisect_right(ts, t) - 1] if bisect.bisect_right(ts, t) else None
            for t, k, fav, mp in ev:
                if mapno is not None and mp != mapno: continue
                a, b, c = px(t - H), px(t), px(t + H)
                if None in (a, b, c): continue
                s = 1 if fav == tm0 else -1
                rows[k].append((f, q, s, s * (b - a), s * (c - b)))
            per.append((os.path.basename(f), q, len(tr)))
    for k, name in (("K", "kill"), ("T", "round end")):
        R = rows[k]
        if len(R) < 10: print(name, "n", len(R), "too few"); continue
        post = [r[4] for r in R]; pre = [r[3] for r in R]; obs = st.mean(post)
        base = []; 
        for _ in range(nperm):
            base.append(st.mean(p * random.choice((-1, 1)) for p in post))
        p = sum(abs(x) >= abs(obs) for x in base) / nperm
        pobs = st.mean(pre); bp = [st.mean(q * random.choice((-1, 1)) for q in pre) for _ in range(nperm)]
        pp = sum(abs(x) >= abs(pobs) for x in bp) / nperm
        bym = {}
        for r in R: bym.setdefault(r[0], []).append(r[4])
        print(f"{name}: n={len(R)} mean signed move after (lead) {obs*100:+.2f}c sign-permutation p={p:.4f} | before (anticipation) {pobs*100:+.2f}c p={pp:.4f} | per-match mean after (c): " + ", ".join(f"{os.path.basename(m)[10:17]}:{st.mean(v)*100:+.2f}(n={len(v)})" for m, v in bym.items()))
    print("markets used:", per)
if __name__ == "__main__": main(sys.argv[1], plant=float(sys.argv[2]) if len(sys.argv) > 2 else 0.0)
