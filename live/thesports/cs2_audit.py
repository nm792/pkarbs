import sys,os
os.environ['CS2']='zzz'
sys.argv=['x','rn1/scores/thesports/slim-1102-32295']
src=open('live/thesports/big_events.py').read()
i=src.index('# ================= big events')
exec(compile(src[:i],'head','exec'))
import statistics
print('CS2 paired maps:')
for key,(tk,sg) in sorted(tk_of.items(), key=lambda kv: kv[0][1]):
    if key[0]!='cs2': continue
    m=[m_ for m_ in mk.values() if tk in m_['tokens']][0]
    ts=T[tk]; n=len(ts)
    changes=sum(1 for a,b in zip(book[tk],book[tk][1:]) if (a[1],a[2])!=(b[1],b[2]))
    sp=[x[2]-x[1] for x in book[tk]]
    mids=[(x[1]+x[2])/2 for x in book[tk]]
    evs=ev[key]
    print(key[1][:8], 'box',box.get(key),'| q:',m['q'],'|',m['outcomes'],'smt',m['smt'],'| book rows',n,'changes',changes,'span %.0f min'%((ts[-1]-ts[0])/60) if n else '', '| median spread %.3f'%statistics.median(sp) if sp else '', '| mid range %.2f-%.2f'%(min(mids),max(mids)) if mids else '', '| rounds(events)',len(evs))
print()
# c_score vs round_num consistency
import json
rn={}
for r in msgs:
    if r['topic'].endswith('csgo/match/v1'):
        try:
            for p in json.loads(r['p']):
                rn.setdefault((p['match_id'],p.get('map_id')),[]).append((r['ms']/1000,p.get('round_num'),p['home']['c_score'],p['away']['c_score'],p['home'].get('score'),p['away'].get('score'),p.get('box_num'),p.get('status_id')))
        except Exception: pass
for (key,(tk,sg)) in list(tk_of.items()):
    if key[0]!='cs2': continue
    L=rn[(key[1],key[2])]
    last=L[-1]
    print(key[1][:8],'box',last[6],'last msg round_num',last[1],'c_score',last[2],last[3],'score',last[4],last[5],'status',last[7],'| max c_score sum',max(x[2]+x[3] for x in L))
    break
# detailed path on one map
key=[k for k in tk_of if k[0]=='cs2'][5]; tk,sg=tk_of[key]
print('MAP',key[1][:8],box.get(key),tk_sport[tk][1],'sign',sg)
for t0,sd in ev[key][:14]:
    f=tk if sd*sg>0 else partner[tk]
    print('round win side',sd,'t=%.0f'%t0,'fav mid path',' '.join('%+d:%s'%(d,('%.2f'%mid_at(f,t0+d)) if mid_at(f,t0+d) is not None else 'NA') for d in (-60,-30,-15,-5,0,5,15,30,60)))
print()
import random
random.seed(5)
def stats(lab,Lsh):
    out=[]
    for a,b in ((-90,-60),(-60,-30),(-30,-15),(-15,0),(0,15),(15,60),(-90,60)):
        v=[]
        for key,t0,sd in Lsh:
            tk,sg=tk_of[key]; f=tk if sd*sg>0 else partner[tk]
            for tt in ([t0] if lab=='real' else [t0+random.choice([-1,1])*random.uniform(60,600) for _ in range(3)]):
                x,y=mid_at(f,tt+a),mid_at(f,tt+b)
                if x is not None and y is not None and 0.1<=x<=0.9: v.append(y-x)
        out.append('[%+d,%+d] mean %+.2fc med %+.1fc p(|m|>=1c) %.0f%% n%d'%(a,b,100*sum(v)/len(v),100*statistics.median(v),100*sum(1 for z in v if abs(z)>=0.0099)/len(v),len(v)))
    print(lab,'\n  '+'\n  '.join(out))
Lsh=[(key,t0,sd) for key in tk_of if key[0]=='cs2' for t0,sd in ev[key][3:]]  # skip history-ish first events
print('CS2 all rounds (band 10-90%), signed move for the round winner:')
stats('real',Lsh); stats('placebo',Lsh)
