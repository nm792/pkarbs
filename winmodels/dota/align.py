"""Fit, per game, the offset o such that wall time = start_time + game_time + o best lines up OpenDota events with
Polymarket game-winner price moves. Events: kills +-1, towers +-2, roshan +-3, barracks +-4 (sign: radiant=+).
Score: correlation of 10 s binned event impulse with the price change over the same bin + next 10 s."""
import sys, json, gzip, os, collections
import numpy as np
sys.path.insert(0, '..'); import common as C
def evlist(d):
    ev = [(t, 1 if r else -1) for r, t in d['kills']]
    for o in d.get('objectives') or []:
        ty = o.get('type', ''); t = o['time']
        if ty == 'building_kill':
            k = o.get('key', ''); w = 4 if 'rax' in k else 2 if 'tower' in k else 0
            if not w: continue
            s = -1 if 'goodguys' in k else 1   # radiant building lost -> bad for radiant
            ev.append((t, s * w))
        elif ty == 'CHAT_MESSAGE_ROSHAN_KILL':
            ev.append((t, 3 if o.get('team') == 2 else -3))
    return sorted(ev)
def load(r):
    fo = f'{C.RAW}/dota/od/{r["match_id"]}.json.gz'; ft = f'{C.RAW}/dota/trades/{r["cond"]}.json.gz'
    if not (os.path.exists(fo) and os.path.exists(ft)): return None
    d = json.load(gzip.open(fo)); tr = json.load(gzip.open(ft))
    if len(tr) < 50: return None
    pr = C.prints(tr); return d, pr, C.Mid(pr)
def fit(r, offs=range(-120, 721, 5), B=10):
    x = load(r)
    if not x: return None
    d, pr, M = x; ev = evlist(d); sgn = 1 if r['o0_rad'] else -1
    t0 = d['start_time']; T = d['duration']
    grid = np.arange(0, T + 60, B)
    best = []
    for o in offs:
        imp = np.zeros(len(grid))
        for t, s in ev:
            i = int(t // B)
            if 0 <= i < len(grid): imp[i] += s * sgn
        dp = []
        for g in grid:
            a = M.at(t0 + g + o); b = M.at(t0 + g + o + 2 * B)
            dp.append(np.nan if a is None or b is None else b - a)
        dp = np.array(dp); ok = ~np.isnan(dp)
        if ok.sum() < 20 or imp[ok].std() == 0: best.append(np.nan); continue
        best.append(np.corrcoef(imp[ok], dp[ok])[0, 1])
    best = np.array(best); i = int(np.nanargmax(best)) if np.isfinite(best).any() else None
    if i is None: return None
    srt = np.sort(best[np.isfinite(best)])[::-1]
    return dict(match_id=r['match_id'], cond=r['cond'], off=list(offs)[i], corr=float(best[i]), second=float(srt[min(5, len(srt) - 1)]), pre=d.get('pre_game_duration'))
if __name__ == '__main__':
    R = sorted(json.load(open('matched.json')), key=lambda r: -r['vol'])[:int(sys.argv[1]) if len(sys.argv) > 1 else 150]
    out = [f for f in map(fit, R) if f]
    offs = np.array([f['off'] for f in out]); cs = np.array([f['corr'] for f in out])
    print('games', len(out), 'offset median', np.median(offs), 'p10/p25/p75/p90', np.percentile(offs, [10, 25, 75, 90]), 'corr median', round(float(np.median(cs)), 2))
    print('offset hist', sorted(collections.Counter(int(o // 30 * 30) for o in offs).items()))
    json.dump(out, open('align.json', 'w'), indent=0)
