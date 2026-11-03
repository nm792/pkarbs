"""Two-step alignment: coarse offset from gold-advantage level fit (align3), then 1 s refinement within +-120 s using
signed price moves after events. Accuracy: refine separately on odd- and even-numbered events; report |diff|."""
import sys, json, numpy as np
sys.path.insert(0, '..'); import align as A, align2 as B
def score(M, t0, ev, sgn, o):
    v = []
    for t, s in ev:
        a = M.at(t0 + t + o - 5); b = M.at(t0 + t + o + 20)
        if a is not None and b is not None: v.append(s * sgn * (b - a))
    return np.mean(v) if len(v) >= 3 else -9
def refine(M, t0, ev, sgn, c):
    offs = range(c - 120, c + 121, 1); sc = [score(M, t0, ev, sgn, o) for o in offs]
    return list(offs)[int(np.argmax(sc))], max(sc)
coarse = {f['match_id']: f for f in json.load(open('align3.json'))}
if __name__ == '__main__':
    R = sorted(json.load(open('matched.json')), key=lambda r: -r['vol'])[:int(__import__('os').environ.get('N','150'))]
    out = []
    for r in R:
        c = coarse.get(r['match_id'])
        if not c or c['corr'] < 0.8: continue
        x = A.load(r); d, pr, M = x; sgn = 1 if r['o0_rad'] else -1; t0 = d['start_time']
        ev = sorted(B.big(d) + [(t, 1 if rr else -1) for rr, t in d['kills']])
        if len(ev) < 10: continue
        o, pk = refine(M, t0, ev, sgn, c['off'])
        o1, _ = refine(M, t0, ev[0::2], sgn, c['off']); o2, _ = refine(M, t0, ev[1::2], sgn, c['off'])
        out.append(dict(match_id=r['match_id'], cond=r['cond'], coarse=c['off'], off=o, peak=pk, split_diff=abs(o1 - o2)))
    sd = np.array([f['split_diff'] for f in out]); dc = np.array([f['off'] - f['coarse'] for f in out])
    print('games', len(out), 'split-half |diff| s pct 25/50/75/90', np.percentile(sd, [25, 50, 75, 90]), 'refine-coarse pct', np.percentile(dc, [10, 50, 90]))
    print('share split diff <=5 s', round(float((sd <= 5).mean()), 2), '<=10 s', round(float((sd <= 10).mean()), 2))
    json.dump(out, open('align4.json', 'w'))
