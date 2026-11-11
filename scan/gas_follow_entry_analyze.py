#!/usr/bin/env python3
import pickle, glob
from collections import defaultdict
import numpy as np
rng = np.random.default_rng(21)
rows = sum((pickle.load(open(f, "rb")) for f in glob.glob("/tmp/fe_rows_*.pkl")), [])
L = []
def P(s=""): print(s, flush=True); L.append(s)
def stat(rs, g, a):
    gp = defaultdict(lambda: [0.0, 0.0, 0]);
    for r in rs: x = gp[r["ev"] + r["st"]]; x[0] += r[g]; x[1] += r[a]; x[2] += 1
    ks = list(gp); sm = np.array([gp[k][0] for k in ks]); sa = np.array([gp[k][1] for k in ks]); ct = np.array([gp[k][2] for k in ks])
    bs = rng.integers(0, len(ks), (2000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
    fl = rng.random((2000, len(ks))) < 0.5; sims = np.where(fl, sa, sm).sum(1) / ct.sum()
    real = sm.sum() / ct.sum(); z = (real - sims.mean()) / (sims.std() + 1e-9)
    pdy = sum(r["size"] * r[g] / r["cost"] for r in rs) / 30
    return real, float(np.percentile(gm, 0.415)), z, len(rs), len(ks), pdy
P("# Follow rule: later entry and early exit, locked grid (Bonferroni lower bound = 99.17% interval; windows A=latest 30 events, B=prior 30)")
P(f"Strikes loaded: {len(rows)}\n")
P("| entry (UTC ~) | window | strikes (events) | followed-side hit vs implied | mean spread | median $ traded next 2h per strike | hold gap (lo99) | exit-3h gap (lo99) | hold $/day | exit $/day | z hold / exit |\n|---|---|---|---|---:|---:|---|---|---:|---:|---|")
verd = {}
for k, lab in ((1, "14Z"), (6, "19Z"), (12, "01Z")):
    for w in ("A", "B", "A+B"):
        rs = [r for r in rows if r["k"] == k and (w == "A+B" or r["win"] == w)]
        if len(rs) < 20: P(f"| {lab} | {w} | {len(rs)} | too few | | | | | | | |"); continue
        h = stat(rs, "gh", "ah"); e = stat(rs, "ge", "ae")
        P(f"| {lab} | {w} | {h[3]} ({h[4]}) | {np.mean([r['hit'] for r in rs])*100:.1f}% vs {np.mean([r['imp'] for r in rs])*100:.1f}% | {np.mean([r['spread'] for r in rs])*100:.1f}c | ${np.median([r['dvol'] for r in rs]):,.0f} | {h[0]*100:+.1f}c ({h[1]*100:+.1f}) | {e[0]*100:+.1f}c ({e[1]*100:+.1f}) | ${h[5]:,.0f} | ${e[5]:,.0f} | {h[2]:+.1f} / {e[2]:+.1f} |")
        verd[(k, w)] = (h, e)
P("\nVerdict per combination (PASS needs both windows: gap>0, Bonferroni lower bound>0, >=100 strikes, >=40 events; pooled z>=2):")
for k, lab in ((1, "14Z"), (6, "19Z"), (12, "01Z")):
    for mode, i in (("hold", 0), ("exit-3h", 1)):
        try:
            ok = all(verd[(k, w)][i][0] > 0 and verd[(k, w)][i][1] > 0 and verd[(k, w)][i][3] >= 100 and verd[(k, w)][i][4] >= 40 for w in ("A", "B")) and verd[(k, "A+B")][i][2] >= 2
        except KeyError: ok = False
        P(f"- entry {lab}, {mode}: {'PASS' if ok else 'FAIL/UNPROVEN'}")
P("\nBy state (all windows pooled, followed side), entry 14Z / 19Z / 01Z: hit - implied, mean spread, hold gap")
P("| state | 14Z | 19Z | 01Z |\n|---|---|---|---|")
for st in sorted({r["st"] for r in rows}):
    cells = []
    for k in (1, 6, 12):
        rs = [r for r in rows if r["st"] == st and r["k"] == k]
        cells.append("n/a" if len(rs) < 8 else f"n={len(rs)}: {(np.mean([r['hit'] for r in rs])-np.mean([r['imp'] for r in rs]))*100:+.1f}c, sp {np.mean([r['spread'] for r in rs])*100:.0f}c, gap {np.mean([r['gh'] for r in rs])*100:+.1f}c")
    P(f"| {st} | " + " | ".join(cells) + " |")
open("scan/OUT-gas-follow-entry-test-2026-11-11.md", "w").write("\n".join(L) + "\n")
