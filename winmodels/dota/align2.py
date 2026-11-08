"""Offset fit using only big events (teamfights with >=3 deaths: signed by net deaths; roshan; barracks; tier-3/4 towers),
score = mean signed price move over [w+o, w+o+30 s] across events (sign: event good for token0). Peak sharpness reported."""
import sys, json, gzip, os, collections
import numpy as np
sys.path.insert(0, '..'); import common as C, align as A
def big(d):
    ev = []
    rad_slots = set(range(0, 5)) | set(range(0, 128))  # player_slot < 128 = radiant
    for tf in d.get('teamfights') or []:
        if tf['deaths'] < 3: continue
        # players list is ordered radiant 0-4 then dire 5-9
        dr = sum(p['deaths'] for p in tf['players'][:5]); dd = sum(p['deaths'] for p in tf['players'][5:])
        if dr == dd: continue
        ev.append((tf['last_death'], 1 if dd > dr else -1))
    for o in d.get('objectives') or []:
        ty = o.get('type', ''); t = o['time']
        if ty == 'building_kill' and ('rax' in o.get('key', '') or 'tower3' in o.get('key', '') or 'tower4' in o.get('key', '')):
            ev.append((t, -1 if 'goodguys' in o['key'] else 1))
        elif ty == 'CHAT_MESSAGE_ROSHAN_KILL':
            ev.append((t, 1 if o.get('team') == 2 else -1))
    return sorted(ev)
def fit(r, offs=range(-120, 721, 5)):
    x = A.load(r)
    if not x: return None
    d, pr, M = x; ev = big(d); sgn = 1 if r['o0_rad'] else -1; t0 = d['start_time']
    if len(ev) < 4: return None
    sc = []
    for o in offs:
        v = []
        for t, s in ev:
            a = M.at(t0 + t + o - 5); b = M.at(t0 + t + o + 30)
            if a is not None and b is not None: v.append(s * sgn * (b - a))
        sc.append(np.mean(v) if len(v) >= 3 else np.nan)
    sc = np.array(sc)
    if not np.isfinite(sc).any(): return None
    i = int(np.nanargmax(sc)); med = float(np.nanmedian(sc))
    return dict(match_id=r['match_id'], cond=r['cond'], off=list(offs)[i], peak=float(sc[i]), median=med, n=len(ev))
if __name__ == '__main__':
    R = sorted(json.load(open('matched.json')), key=lambda r: -r['vol'])[:150]
    out = [f for f in map(fit, R) if f]
    offs = np.array([f['off'] for f in out]); pk = np.array([f['peak'] for f in out])
    print('games', len(out), 'offset pct 10/25/50/75/90', np.percentile(offs, [10, 25, 50, 75, 90]), 'peak move median', round(float(np.median(pk)), 3))
    print(sorted(collections.Counter(int(o // 30 * 30) for o in offs).items()))
    s = [f for f in out if f['peak'] > 0.05]; print('peak>5c', len(s), np.percentile([f['off'] for f in s], [10, 25, 50, 75, 90]))
    json.dump(out, open('align2.json', 'w'), indent=0)
