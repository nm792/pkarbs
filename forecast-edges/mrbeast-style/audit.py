import sys; sys.argv=['x']; sys.path.insert(0,'/tmp/w')
import nf_full as N, math, collections, statistics as st
for o in ('o','a'):
    N.ORACLE=o; print('ORACLE' if o=='o' else 'ANTI-ORACLE (should lose)'); N.run(.05,7200,'start',label='  ')
N.ORACLE=None
cutm=sorted(r['start'] for r in N.EV if r['k'][0]=='global'); cut=cutm[len(cutm)//2]
par,nr=N.fit_decay(cut)
agree=collections.Counter(); br=[];bm=[]
for r in N.EV:
    if r['k'][0]!='global': continue
    r['T']=r['start']+3600
    pq=N.predict(r,cut,par,nr)
    if not pq: continue
    rows,P=pq
    win=[n for n,c,w in r['mk'] if w][0]
    mt=N.match(win,rows)
    agree[(r['k'][1],r['k'][2],mt is not None)]+=1
    for name,c,won in r['mk']:
        m=N.match(name,rows)
        if not m: continue
        pr=[(t,p) for t,s,p,sz,oi in N.TR.get(c,[]) if s=='BUY' and oi==0 and r['T']<=t<=r['T']+21600]
        if not pr: continue
        pm=min(max(sorted(pr)[0][1],.02),.98); pq_=min(max(P[m['title']],.02),.98); y=1.0 if won else 0.0
        br.append((pq_-y)**2); bm.append((pm-y)**2)
print('winner was in last-published top10 list: (type,rank,in_list)->events'); 
for k,v in sorted(agree.items(),key=str): print(' ',k,v)
print('candidate-level Brier: model %.4f vs market first print %.4f over %d candidate-events'%(st.mean(br),st.mean(bm),len(br)))
