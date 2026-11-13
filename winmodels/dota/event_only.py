"""Dota 2 event-only rule on replay events (OpenDota) aligned to wall clock (align4 offsets, which are fitted to the
price itself: results mean 'a feed as fast as the market' + lag). Game-winner markets. Train < 1 Oct 2026, holdout after.
Events: kill clusters (10 s, net kills), towers (+-2), barracks (+-4), roshan (+-3); jump j = beta_type x net, fitted on train.
Rule: within W s after event+lag, bid mkt x 0.975 on the side with j >= minj whose mid has not yet risen by j.
Corrected fills (print within 1% below bid), Q cap per print as common.py, rebate from feeSchedule."""
import sys, json, gzip, bisect
import numpy as np
sys.path.insert(0, '..'); import common as C, align as A
SPLIT = 1790812800  # 1 Oct 2026
AL = {f['match_id']: f for f in json.load(open('align4.json'))}
R = [r for r in json.load(open('matched.json')) if r['match_id'] in AL]
def evs(d):
    k = sorted((t, 1 if rr else -1) for rr, t in d['kills']); out = []; i = 0
    while i < len(k):
        j = i; net = 0
        while j < len(k) and k[j][0] - k[i][0] <= 10: net += k[j][1]; j += 1
        if net: out.append((k[j - 1][0], 'kill', net))
        i = j
    for o in d.get('objectives') or []:
        ty = o.get('type', ''); t = o['time']; key = o.get('key', '')
        if ty == 'building_kill' and ('tower' in key or 'rax' in key):
            out.append((t, 'rax' if 'rax' in key else 'tower', -1 if 'goodguys' in key else 1))
        elif ty == 'CHAT_MESSAGE_ROSHAN_KILL': out.append((t, 'rosh', 1 if o.get('team') == 2 else -1))
    return sorted(out)
CACHE = {}
def get(r):
    if r['match_id'] not in CACHE:
        d, pr, M = A.load(r); CACHE[r['match_id']] = (d, pr, M, evs(d))
    return CACHE[r['match_id']]
def fit_beta(rs):
    X = []; Y = []
    for r in rs:
        d, pr, M, ev = get(r); t0 = d['start_time'] + AL[r['match_id']]['off']; sgn = 1 if r['o0_rad'] else -1
        for t, ty, net in ev:
            a = M.at(t0 + t - 5); b = M.at(t0 + t + 30)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            x = {'kill': 0, 'tower': 1, 'rax': 2, 'rosh': 3}[ty]; row = [0, 0, 0, 0]; row[x] = net * sgn
            X.append(row); Y.append(b - a)
    X = np.array(X, float); Y = np.array(Y)
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    r2 = 1 - ((Y - X @ beta) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
    return beta, r2, len(Y)
def run(rs, beta, lag=0, W=30, minj=0.01, d_=0.025, max_gap=0.01, pre=5):
    per = []
    for r in rs:
        d, pr, M, ev = get(r); t0 = d['start_time'] + AL[r['match_id']]['off']; sgn = 1 if r['o0_rad'] else -1
        mk_ = C.Mid(pr); reb = C.reb_rate({'feeSchedule': r.get('fee')}) if r.get('fee') else 0.0
        E = []
        for t, ty, net in ev:
            j = beta[{'kill': 0, 'tower': 1, 'rax': 2, 'rosh': 3}[ty]] * net * sgn
            if abs(j) >= minj: E.append((t0 + t + lag, j, M.at(t0 + t - pre)))
        et = [e[0] for e in E]; tot = np.zeros(4)
        for (T, _, ph, sell0, sz) in pr:
            i = bisect.bisect_right(et, T) - 1
            if i < 0 or T > et[i] + W: continue
            _, j, base = E[i]; mk = M.at(T - 1)
            if base is None or mk is None or not (0.05 <= mk <= 0.95): continue
            if j > 0:
                if mk - base >= j: continue
                b = mk * (1 - d_); tok = 0
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                if base - mk >= -j: continue
                b = (1 - mk) * (1 - d_); tok = 1
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, C.Q); m60 = M.at(T + 60)
            if m60 is None: continue
            m60 = m60 if tok == 0 else 1 - m60; out = 1.0 if (r['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * reb * b * (1 - b)]
        per.append(tot)
    return C.summarize(per)
if __name__ == '__main__':
    tr = [r for r in R if r['start'] < SPLIT]; te = [r for r in R if r['start'] >= SPLIT]
    beta, r2, n = fit_beta(tr); print('train games', len(tr), 'holdout', len(te), 'beta kill/tower/rax/rosh', np.round(beta, 4), 'R2', round(r2, 3), 'n', n)
    res = []
    for name, rs in (('train', tr), ('holdout', te)):
        for lag in (0, 2, 5, 10):
            for W in (10, 30):
                s = run(rs, beta, lag, W); res.append(dict(set=name, lag=lag, W=W, **s))
                print(f"{name} lag{lag} W{W}: games {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} {s.get('ci_result_usd')} ex-top5 {s.get('ex_top5_result_pct')}%", flush=True)
    json.dump(dict(beta=list(beta), r2=r2, res=res), open('out_event_only.json', 'w'), indent=1, default=str)
