"""Fit the in-play goal model on 13.8k ESPN matches (15 Jul - 20 Oct 2026), all before the backtest window.
Outputs params.json: goal-rate profile over effective minutes (incl. stoppage), red-card multipliers."""
import sys, os, json, gzip, re, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import RAW
H = json.load(gzip.open(f'{RAW}/soccer/espn_hist_2026-07-15_10-20.json.gz'))
S1, S2 = 3, 6           # assumed average stoppage minutes (1st, 2nd half) -> effective clock 0..48 | 48..99
END = 90 + S1 + S2
def eff(disp):
    """ESPN minute string -> effective minute on a 0..END clock (1st-half stoppage 45..48, 2nd half 48..93, stoppage 93..99)."""
    m = re.match(r"(\d+)'(?:\+(\d+)')?", disp or '')
    if not m: return None
    a, b = int(m.group(1)), int(m.group(2) or 0)
    if a < 45: return a - 0.5
    if a == 45: return 45 + min(b, S1) - 0.5 if b else 44.5
    if a < 90: return a + S1 - 0.5
    return 90 + S1 + min(b, S2) - 0.5 if b else 90 + S1 - 0.5
ok = bad = 0; goals = []; reds = []; nm = 0
for e in H:
    if any(d[6] for d in e['det']): pass
    side = {tid: ha for ha, tid, _ in e['comp']}; sc = {ha: int(s) for ha, _, s in e['comp'] if s not in (None, '')}
    if len(sc) < 2: continue
    gs = [(eff(d[1]), side.get(d[2]), d[5]) for d in e['det'] if d[3] and not d[6]]
    cnt = collections.Counter(g[1] for g in gs)
    if cnt.get('home', 0) != sc['home'] or cnt.get('away', 0) != sc['away'] or any(g[0] is None for g in gs): bad += 1; continue
    ok += 1; nm += 1
    goals += [(g[0], g[1], e['id']) for g in gs]
    rs = [(eff(d[1]), side.get(d[2])) for d in e['det'] if d[4]]
    reds.append((e['id'], rs, gs))
print('matches with consistent goal list', ok, 'inconsistent', bad)
# goal-rate profile (goals per match per effective minute), 3-minute bins
edges = np.arange(0, END + 3, 3); edges[-1] = END
gm = np.array([g[0] for g in goals])
cnt, _ = np.histogram(gm, edges)
rate = cnt / ok / np.diff(edges)
tot = rate @ np.diff(edges)
# remaining-goal fraction R(t) at each edge
R = np.array([(rate[k:] @ np.diff(edges)[k:]) for k in range(len(rate))] + [0.0]) / tot
print('goals/match', round(tot, 3), 'R at 0,24,45(48),60,75,90(93),95:', [round(float(np.interp(x, edges, R)), 3) for x in (0, 24, 48, 63, 78, 93, 97)])
# red cards: goals after the first red, carded vs opponent, vs expected (avg team rate x R)
obs_c = obs_o = exp_ = 0.0; nred = 0
for mid, rs, gs in reds:
    rs = [r for r in rs if r[0] is not None and r[1]]
    if not rs: continue
    t, sd = min(rs); nred += 1
    e_ = tot / 2 * np.interp(t, edges, R)
    exp_ += e_
    obs_c += sum(1 for g in gs if g[0] > t and g[1] == sd); obs_o += sum(1 for g in gs if g[0] > t and g[1] != sd)
mc, mo = obs_c / exp_, obs_o / exp_
print('matches with a red card', nred, 'goal-rate multiplier after red: carded', round(mc, 3), 'opponent', round(mo, 3))
# home share
hs = sum(1 for g in goals if g[1] == 'home') / len(goals)
json.dump(dict(n_matches=ok, S1=S1, S2=S2, END=END, edges=edges.tolist(), R=R.tolist(), goals_per_match=tot, red_carded=mc, red_opp=mo,
               n_red=nred, home_goal_share=hs), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json'), 'w'), indent=1)
