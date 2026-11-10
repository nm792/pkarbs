from pmaudit import *
for causal in (False,True):
    for thr in (.03,.05,.10):
        U,LS=run(thr,causal=causal);report(U,f'ALL909 thr={thr} causal={causal}',LS=LS)
