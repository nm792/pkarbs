from pmaudit import *
import json
D=data()
SAMP=set(json.load(open('pm_mm_sample.json')).keys())
U3,_=run(.03);med=sorted(u['t0'] for u in U3)[len(U3)//2]
print('== 300-event sample (seed 7), causal')
for thr in (.03,.05,.10):
    U,LS=run(thr,subset=SAMP);report(U,f'sample300 thr {thr}',LS=LS,nsim=1500)
    report([u for u in U if u['t0']>=med],f'sample300 thr {thr} later half',nsim=1500)
print('== delay sensitivity (all 909, causal)')
for thr in (.03,.10):
  for d in (0,5,30,60,300,900):
    U,_=run(thr,delay=d);report(U,f'thr {thr} delay {d}s',nsim=1000)
print('== size cap')
for thr in (.03,.10):
  for c in (10,25,100):
    U,_=run(thr,cap=c);report(U,f'thr {thr} cap {c} shares',nsim=1000)
print('== anchor on first trade of event instead of market startDate')
for thr in (.03,.10):
    U,LS=run(thr,anchor='firsttrade');report(U,f'thr {thr} anchor=first trade',LS=LS,nsim=1000)
print('== window length')
for thr in (.03,.10):
  for w in (900,21600,86400):
    U,_=run(thr,win=w);report(U,f'thr {thr} window {w}s',nsim=1000)
print('== lag stats')
U,_=run(.10);lags=sorted(u['bet']['lag'] for u in U if u['bet']);n=len(lags);print('bet lag pctiles 10/25/50/75/90',[round(lags[int(n*q)]) for q in (.1,.25,.5,.75,.9)])
fl=[]
for f,evs in D.items():
    for e in evs:
        if e['burn']:continue
        ft=[m['first']-e['t0'] for m in e['mk'] if m['first']];
        if ft:fl.append(min(ft))
fl.sort();n=len(fl);print('first-trade lag after startDate pctiles',[round(fl[int(n*q)]) for q in (.1,.25,.5,.75,.9)],'events with trades',n)
