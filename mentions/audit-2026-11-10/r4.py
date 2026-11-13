import warnings;warnings.filterwarnings('ignore')
from audit import *
def pt(U,mode):
    d=[]
    for u in U:
        b=u['bet']
        if not b:continue
        f=u['fills'] if mode=='any' else [x for x in u['fills'] if x[0]==b['oi']]
        if not f:continue
        pe=S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*(b['sz'] if mode!='old' else min(x[2],b['sz'])) for x in f)
        d.append(pnl(b)-pe)
    return round(tstat(d),2),len(d)
for causal in (False,True):
    allU=[];perser={};H=[]
    for s in SER:
        U,_=run(s,.03,causal=causal);allU+=U;perser[s]=U
        us=sorted(U,key=lambda u:u['t0']);H+=us[len(us)//2:]
    med=sorted(u['t0'] for u in allU)[len(allU)//2]
    print('causal',causal)
    for mode in ('old','same','any'):
        print(' mode',mode,'pooled',pt(allU,mode),'NBA',pt(perser['KXNBAMENTION'],mode),'held-out per-series half',pt(H,mode),'calendar later half',pt([u for u in allU if u['t0']>=med],mode))
