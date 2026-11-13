"""Standard stats for every locked test (after the 10 Nov box-office audit).
units: list of dict(id, bet=dict(oi,p,sz,w)|None, fills=[(oi,p,sz,w,...)], cluster=hashable)
Reports: real P&L; same-event random-print placebo (expected value, bet-sized); paired t of real minus same-event placebo on bet events;
all-events random-print baseline; top-3 concentration; cluster t; Bonferroni over n variants; optional log-score vs market."""
import math,statistics as S
from math import erf,sqrt
def pnl(b): return ((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
def t_p(vals):
    n=len(vals)
    if n<3: return 0.0,1.0
    sd=S.stdev(vals)
    if sd==0: return 0.0,1.0
    t=S.mean(vals)/sd*sqrt(n)
    p=2*(1-.5*(1+erf(abs(t)/sqrt(2))))   # normal approx, conservative enough for n>=20; flag small n
    return t,p
def placebo_same_event(u):
    b=u['bet']; f=[x for x in u['fills'] if x[0]==b['oi']]
    if not f: return None
    return S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*min(x[2],b['sz']) for x in f)
def lockstat(units,label='',nvar=1,logscore=None):
    bets=[u for u in units if u['bet']]
    real=[pnl(u['bet']) for u in bets]; tot=sum(real); cost=sum(u['bet']['p']*u['bet']['sz'] for u in bets)
    pl=[placebo_same_event(u) for u in bets]; ok=[(r,p) for r,p in zip(real,pl) if p is not None]
    d=[r-p for r,p in ok]
    t_all,p_all=t_p([pnl(u['bet']) if u['bet'] else 0.0 for u in units])
    t_d,p_d=t_p(d)
    srt=sorted(real,reverse=True); top3=sum(srt[:3]); rest=tot-top3
    # cluster t on per-cluster summed real P&L
    cl={}
    for u in units: cl[u.get('cluster',u['id'])]=cl.get(u.get('cluster',u['id']),0)+(pnl(u['bet']) if u['bet'] else 0)
    t_c,p_c=t_p(list(cl.values()))
    # all-events random-print baseline (size 10 shares-equivalent per event, expected)
    base=[]
    for u in units:
        if u['fills']: base.append(S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*min(x[2],10) for x in u['fills']))
    print(f"{label} bets {len(bets)}/{len(units)} pnl ${tot:.0f} on ${cost:.0f}; same-event placebo ${sum(p for r,p in ok):.0f}; "
          f"paired t(real-placebo)={t_d:.2f} p={p_d:.2f} (Bonf x{nvar}: {min(1,p_d*nvar):.2f}); real-vs-0 t={t_all:.2f}; cluster t={t_c:.2f} p={p_c:.2f} n_cl={len(cl)}; "
          f"top3 ${top3:.0f} of ${tot:.0f} (rest ${rest:.0f}); wins {sum(1 for r in real if r>0)}/{len(real)}")
    if logscore: print('   log-score model minus market (nats/event, t):',logscore)
    return dict(tot=tot,t_paired=t_d,p_paired=p_d,t_cluster=t_c,top3=top3,rest=rest)
