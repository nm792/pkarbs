from pmaudit import *
import random as R
D=data()
U3,_=run(.03);med=sorted(u['t0'] for u in U3)[len(U3)//2];print('median t0',dt.datetime.fromtimestamp(med),'events',len(U3))
for thr in (.03,.05,.10):
    U,LS=run(thr)
    report([u for u in U if u['t0']<med],f'thr {thr} EARLIER half (calendar)',nsim=1500)
    report([u for u in U if u['t0']>=med],f'thr {thr} LATER half (calendar)',nsim=1500)
    H=[]
    for f in D:
        us=sorted([u for u in U if u['series']==f],key=lambda u:u['t0']);H+=us[len(us)//2:]
    report(H,f'thr {thr} per-family later half (build style)',nsim=1500)
print('== by family (causal 3c / 5c / 10c)')
for thr in (.03,.05,.10):
    U,_=run(thr)
    for f in D:report([u for u in U if u['series']==f],f' {f} thr {thr}',nsim=800)
print('== by fee era: events started before/after 2026-03-01 (fees)')
cut=ts('2026-03-01T00:00:00Z')
for thr in (.03,.05,.10):
    U,_=run(thr);report([u for u in U if u['t0']<cut],f'thr {thr} pre-fee era',nsim=1000);report([u for u in U if u['t0']>=cut],f'thr {thr} fee era',nsim=1000)
