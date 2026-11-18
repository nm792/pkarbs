# Usage: python3 -I feeds/null_sim_20k.py normal|t3 20000 feeds   (Reviewer condition 2, 18 Nov; pure stdlib, ~1 min)
import sys, os, re, math as _m, random, importlib.util
here = sys.argv[3]; dist = sys.argv[1]; RUNS = int(sys.argv[2])
src = open(os.path.join(here, "test_goalserve_odds_vs_pm_v2.py")).read()
a = src.index("def pois"); b = src.index("RUNS = 2000")
spec = importlib.util.spec_from_file_location("v2mod", os.path.join(here, "goalserve_odds_vs_pm_v2.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
g.MIN_EFFECT, g.MIN_SHARE = -1.0, -1.0
ns = dict(_m=_m, random=random, g=g); exec(src[a:b], ns)
rng = random.Random(777 if dist == "normal" else 778)
pos = {c: 0 for c in g.N_MAX}; neg = dict(pos); either = dict(pos)
for _ in range(RUNS):
    for cell, rate in (("cs2|Match Winner", 5.0), ("dota2|Match Winner", 2.5)):
        vals, hp, hn = [], False, False
        for day in range(20):
            vals += [ns["draw"](rng, dist, 0.0) for _ in range(ns["pois"](rng, rate))]
            used = vals[:g.N_MAX[cell]]
            v = g.decide(used, 30*len(used), 100.0, True, len(used) >= g.N_MAX[cell] or day == 19, cell)["verdict"]
            hp |= v.startswith("meets bar"); hn |= v.startswith("PM moved first")
        pos[cell] += hp; neg[cell] += hn; either[cell] += (hp or hn)
for nm, d in (("pass", pos), ("PM-first", neg), ("either", either)):
    print(dist, RUNS, nm, {c: (round(d[c]/RUNS, 4), round(d[c]/RUNS + 1.96*_m.sqrt(max(d[c]/RUNS,1e-9)*(1-d[c]/RUNS)/RUNS), 4)) for c in d})
