"""Level-based offset: corr(price token0, sign x tanh(gold_adv/10000)) per minute, offsets -1800..+1800 s."""
import sys, json, numpy as np, collections
sys.path.insert(0, '..'); import align as A
def fit(r, offs=range(-1800, 1801, 15)):
    x = A.load(r)
    if not x: return None
    d, pr, M = x; g = np.array(d['radiant_gold_adv'] or []); sgn = 1 if r['o0_rad'] else -1
    if len(g) < 15: return None
    f = sgn * np.tanh(g / 10000.); t0 = d['start_time']; sc = []
    for o in offs:
        p = [M.at(t0 + 60 * i + o) for i in range(len(g))]
        ok = [i for i, v in enumerate(p) if v is not None]
        if len(ok) < 10: sc.append(np.nan); continue
        pp = np.array([p[i] for i in ok]); ff = f[ok]
        sc.append(np.corrcoef(pp, ff)[0, 1] if pp.std() > 0 and ff.std() > 0 else np.nan)
    sc = np.array(sc)
    if not np.isfinite(sc).any(): return None
    i = int(np.nanargmax(sc)); return dict(match_id=r['match_id'], off=list(offs)[i], corr=float(sc[i]), first=M.pr[0][0] - t0 if hasattr(M, 'pr') else None)
R = sorted(json.load(open('matched.json')), key=lambda r: -r['vol'])[:int(__import__('os').environ.get('N','150'))]
out = [f for f in map(fit, R) if f]
o = np.array([f['off'] for f in out]); c = np.array([f['corr'] for f in out])
print('games', len(out), 'corr median', round(float(np.median(c)), 2), 'offset pct', np.percentile(o, [10, 25, 50, 75, 90]))
s = o[c > 0.9]; print('corr>0.9', len(s), np.percentile(s, [10, 25, 50, 75, 90]) if len(s) else '')
print(sorted(collections.Counter(int(v // 60 * 60) for v in s).items()))
json.dump(out, open('align3.json', 'w'))
