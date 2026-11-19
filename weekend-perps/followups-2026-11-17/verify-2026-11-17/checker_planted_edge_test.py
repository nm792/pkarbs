"""Planted-edge / no-edge check for the 17 Nov follow-up test code (analyze.py, follow23.py, eval1.py). usage: checker_planted_edge_test.py WORKDIR [SCRIPTDIR]  (independent of the author thread's planted_edge_check.py; written by the checker thread, 17 Nov 2026)
Synthetic data, SYNTHETIC numbers only. For each of the two worlds it writes hist.json, cand.json, growth.json (history tests) and a 5 s log (Test 1),
runs the real scripts unchanged and checks the verdicts:
  EDGE world:    price moves back toward the oracle/index by a planted amount right after a divergence -> scripts must report tradable / PASS / net ~ planted - costs.
  NO-EDGE world: divergences are closed by the ORACLE/INDEX moving to the perp (perp price does not move) -> scripts must NOT report tradable / PASS; net ~ -costs.
Exit status 1 if any expectation fails."""
import json, gzip, os, re, subprocess, sys, random, math
import numpy as np
W = sys.argv[1]; HERE = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = 3600000   # HERE = directory holding perplib.py, analyze.py, follow23.py, eval1.py
PLANT_BP = 60.0            # planted reversion in the hour after |premium| >= 50 bp
def hist_world(d, edge, seed):
    rng = np.random.default_rng(seed); os.makedirs(d, exist_ok=True)
    T0 = 1790000000000 // H * H; N = 24 * 7 * 24    # 24 weeks of hours
    syms = ["xyz:S%d" % i for i in range(12)] + ["flx:F%d" % i for i in range(3)]
    oi = {s: float(10 ** rng.uniform(5, 8)) for s in syms}; fund = {}; cand = {}; hs = {}; growth = {"xyz": {}, "flx": {}}
    for s in syms:
        # premium (bp): quiet AR(1) with sparse spikes; spikes of 3-8 h at +-150 bp are the 'frozen oracle' episodes
        p = np.zeros(N); k = 0
        while k < N:
            if rng.random() < 0.02:
                L = int(rng.integers(3, 9)); sg = rng.choice([-1, 1]); p[k:k + L] = sg * rng.uniform(120, 200, size=min(L, N - k)); k += L + 1
            else:
                p[k] = 0.6 * (p[k - 1] if k else 0) + rng.normal(0, 12) + (rng.choice([-1, 1]) * 60 if rng.random() < 0.01 else 0); k += 1
        ret = rng.normal(0, 25, size=N)                    # candle return in bp, independent noise
        for k in range(N - 1):
            if edge and abs(p[k]) >= 50: ret[k + 1] = -np.sign(p[k]) * PLANT_BP + rng.normal(0, 10)   # planted: next candle moves toward the oracle
        # Test 3 planted: in the reset hour (first |p|<25 hour after a >=3h run of >=100bp) the candle moves toward the oracle by 0.5 x last |p|
        if edge:
            for k in range(3, N - 1):
                if abs(p[k]) < 25 and all(abs(p[k - i]) >= 100 for i in (1, 2, 3)) and np.sign(p[k - 1]) == np.sign(p[k - 2]) == np.sign(p[k - 3]):
                    ret[k] = -np.sign(p[k - 1]) * 0.5 * abs(p[k - 1])
        px = 100 * np.cumprod(1 + ret / 1e4); opens = np.concatenate([[100.0], px[:-1]])
        fr = p / 1e4 / 400 + rng.normal(0, 1e-6, size=N)   # funding per hour: small, so funding carry is NOT itself a planted edge (a first draft with p/8 made the no-edge world profitable via funding, which the scripts correctly reported)
        fund[s] = [(int(T0 + (k + 1) * H + 20), float(p[k] / 1e4), float(fr[k])) for k in range(N)]   # record time t = end of hour k, +20 ms like the venue
        cand[s] = {str(T0 + k * H): [float(opens[k]), float(px[k])] for k in range(N)}                  # candle open time = start of hour k
        hs[s] = 1.0; growth[s.split(":")[0]][s] = "enabled"
    json.dump(dict(oi=oi, fund=fund), open(d + "/hist.json", "w")); json.dump(dict(candles=cand, halfspread=hs), open(d + "/cand.json", "w")); json.dump(growth, open(d + "/growth.json", "w"))
def log_world(d, edge, seed):
    rng = random.Random(seed); os.makedirs(d + "/logs", exist_ok=True); syms = ["NVDA-USD", "MU-USD", "AMD-USD"]; FUND = {s: [] for s in syms}
    for day in range(4):
        t0 = 1790000000 // 86400 * 86400 + day * 86400 + 14 * 3600; n = 4 * 720; recs = []
        mid = {s: 100.0 for s in syms}; idx = {s: 100.0 for s in syms}; gap = {s: 0.0 for s in syms}; hold = {s: 0 for s in syms}
        for i in range(n):
            t = t0 + 5 * i; pm = []; books = {}
            for s in syms:
                if hold[s] == 0 and rng.random() < 0.004: gap[s] = rng.choice([-1, 1]) * rng.uniform(35, 60); hold[s] = rng.randint(4, 9)   # spike lasts 20-45 s
                noise = rng.gauss(0, 2.5)
                if hold[s] > 0:
                    hold[s] -= 1
                    if hold[s] == 0:
                        gap[s] = 0.0
                        if not edge: idx[s] = mid[s] * (1 + rng.gauss(0, 1e-4))        # NO-EDGE: oracle moves to the perp, perp price stays
                if edge and hold[s] == 0 and abs(gap[s]) < 1e-9: pass
                # price paths: random walk common to both; in the EDGE world the perp mid itself carries the gap and reverts, in NO-EDGE the INDEX carries the offset
                step = rng.gauss(0, 2e-5)
                if edge:
                    idx[s] *= 1 + step; mid[s] = idx[s] * (1 + (gap[s] + noise) / 1e4)
                else:
                    mid[s] *= 1 + step
                    if hold[s] > 0 or abs(gap[s]) > 0: idx[s] = mid[s] / (1 + (gap[s] + noise) / 1e4)
                    else: idx[s] = mid[s] / (1 + noise / 1e4)
                m = mid[s]; half = m * 1e-4
                pm.append([s, "%.6f" % idx[s], "%.6f" % m, "%.6f" % m, "%.6f" % m])
                books[s] = dict(bids=[["%.6f" % (m - half - j * half), "50000"] for j in range(10)], asks=[["%.6f" % (m + half + j * half), "50000"] for j in range(10)])
            recs.append(dict(t=float(t), pm=pm, books=books, hl={}))
        with gzip.open("%s/logs/pmhl5s_%d.jsonl.gz" % (d, day), "wt") as f:
            for r in recs: f.write(json.dumps(r) + "\n")
    for s in syms: FUND[s] = [[1790000000 // 3600 * 3600 + k * 3600 + 0.02, 0.00001] for k in range(0, 24 * 5)]
    json.dump(FUND, open(d + "/funding.json", "w"))
def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800)
fails = []
def expect(name, ok, detail=""):
    print(("OK   " if ok else "FAIL ") + name + (" | " + detail if detail else "")); 
    if not ok: fails.append(name)
for world, edge in (("edge", True), ("noedge", False)):
    d = "%s/%s" % (W, world); hist_world(d, edge, 1); log_world(d, edge, 2)
    a = run([sys.executable, HERE + "/analyze.py", d], cwd=d); f = run([sys.executable, HERE + "/follow23.py", d], cwd=d)
    e0 = run([sys.executable, HERE + "/eval1.py", d + "/logs", "--funding", d + "/funding.json"], cwd=d)     # default --after (merge cut-off): synthetic Sept data must be EXCLUDED
    expect(world + ": eval1 default --after cut-off drops pre-merge sessions (M1)", re.search(r"polls 0 ", e0.stdout) is not None and "VERDICT: PRELIMINARY (no events)" in e0.stdout, e0.stdout.splitlines()[0] if e0.stdout else e0.stderr[-120:])
    e = run([sys.executable, HERE + "/eval1.py", d + "/logs", "--funding", d + "/funding.json", "--after", "0"], cwd=d)
    open(d + "/analyze.out", "w").write(a.stdout + a.stderr); open(d + "/follow23.out", "w").write(f.stdout + f.stderr); open(d + "/eval1.out", "w").write(e.stdout + e.stderr)
    expect(world + ": scripts ran", a.returncode == 0 and f.returncode == 0 and e.returncode == 0, "rc %d %d %d" % (a.returncode, f.returncode, e.returncode))
    tr = [l for l in a.stdout.splitlines() if "reversion trade" in l]
    nets = [float(re.search(r"net=(-?[\d.]+)", l).group(1)) for l in tr]; tradable = [("tradable=True" in l) for l in tr]
    expect(world + ": analyze metric 4 " + ("tradable" if edge else "NOT tradable"), (any(tradable) if edge else not any(tradable)), "nets %s" % nets[:6])
    if edge: expect("edge: analyze net near planted 60 - cost 7.8 (>=30)", any(n > 30 for n in nets))
    else: expect("noedge: analyze net negative (about -cost)", all(n < 0 for n in nets), "max %.1f" % max(nets) if nets else "none")
    carry = [l for l in f.stdout.splitlines() if "PASS=" in l]; k6 = f.stdout.split("Test 2 carry k=3")[0]
    p6 = [("PASS=True" in l) for l in k6.splitlines() if "PASS=" in l]
    expect(world + ": Test 2 primary k=6 " + ("PASS" if edge else "no PASS"), (any(p6) if edge else not any(p6)), "cells %d" % len(p6))
    m = re.search(r"slope (-?[\d.]+)", f.stdout); nb = re.search(r"ex-post bound .*? net (-?[\d.]+)", f.stdout)
    if edge: expect("edge: Test 3 slope near planted 0.5 and ex-post bound net > 0", m is not None and 0.3 < float(m.group(1)) < 0.7 and nb is not None and float(nb.group(1)) > 0, "slope %s net %s" % (m.group(1) if m else None, nb.group(1) if nb else None))
    else: expect("noedge: Test 3 slope ~0 and ex-post net <= 0", m is not None and abs(float(m.group(1))) < 0.15 and nb is not None and float(nb.group(1)) <= 0, "slope %s net %s" % (m.group(1) if m else None, nb.group(1) if nb else None))
    v = re.search(r"VERDICT: (\S+)", e.stdout); g = re.search(r"gross mean (-?[\d.]+).*?net mean (-?[\d.]+)", e.stdout); ev = re.search(r"events (\d+)", e.stdout)
    expect(world + ": Test 1 events found", ev is not None and int(ev.group(1)) >= 30, "events %s" % (ev.group(1) if ev else None))
    if edge: expect("edge: Test 1 VERDICT PASS and net > 0", v is not None and v.group(1) == "PASS" and g is not None and float(g.group(2)) > 0, "verdict %s gross/net %s" % (v.group(1) if v else None, g.groups() if g else None))
    else: expect("noedge: Test 1 not PASS and net < 0", v is not None and v.group(1) != "PASS" and g is not None and float(g.group(2)) < 0, "verdict %s gross/net %s" % (v.group(1) if v else None, g.groups() if g else None))
print("RESULT:", "ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
