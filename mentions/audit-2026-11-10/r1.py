from audit import *
for thr in (.03,):
  for causal in (False,True):
    allU=[];allLS=[]
    for s in SER:
        U,LS=run(s,thr,causal=causal);allU+=U;allLS+=LS
        if not causal or True: report(U,f'{s} thr={thr} causal={causal}',nsim=500)
    report(allU,f'POOLED thr={thr} causal={causal}',LS=allLS)
