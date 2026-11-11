import sys;sys.argv=['x','pm_trades_full.json']
import exitaudit as X
from exitaudit import *
orig=X.exit_val
def ev2(v,t,oi,p,sz,resv,allt,close,pre=None):
    if v=='V4' or v=='V4s' or v=='V4q':
        pass
    return orig(v,t,oi,p,sz,resv,allt,close)
# monkeypatch generic: handle V4 variants and second-print variant by wrapping
def exit_val2(v,t,oi,p,sz,resv,allt,close,pre=None):
    if v.startswith('V4'):
        # tok passed through global TOK set by caller
        tok=X.CUR['tok']
        if tok<=p:return resv,None
        for x in allt:
            if x[0]<=t:continue
            if x[4]!=oi or x[1]!='BUY' or x[3]<=0:continue
            if v=='V4' and x[2]>=tok:return tok,None
            if v=='V4s' and x[2]>tok+1e-9:
                f=min(1.0,x[3]/sz);return f*tok+(1-f)*resv,None
            if v=='V4q' and x[2]>tok+1e-9 and x[0]>=t+60:
                f=min(1.0,x[3]/sz);return f*tok+(1-f)*resv,None
        return resv,None
    if v.endswith('n2'):
        te=t+H[v[:2]];k=0
        for x in allt:
            if x[0]<te:continue
            if x[4]==oi and x[1]=='SELL' and x[3]>0:
                k+=1
                if k==2:
                    f=min(1.0,x[3]/sz);return f*x[2]+(1-f)*resv,None
        return resv,None
    return orig(v,t,oi,p,sz,resv,allt,close)
X.exit_val=exit_val2
# need tok in CUR: patch run's inner loop by redefining run quickly
import types,inspect
src=inspect.getsource(X.run).replace("tok=q if oi==0 else 1-q;edge=tok-p;resv=w if oi==0 else 1-w","tok=q if oi==0 else 1-q;edge=tok-p;resv=w if oi==0 else 1-w;CUR['tok']=tok")
X.CUR={'tok':0}
exec(src,X.__dict__)
V=['V0','V1','V1n2','V2n2','V4','V4s','V4q']
out,info=X.run(variants=V)
for v in V:
    U=sorted(out[v],key=lambda u:u['t0']);h=len(U)//2
    X.stats(U,f'{v} all',nvar=5);X.stats(U[h:],f'{v} later-half',nvar=5)
