import json,sys,datetime as dt,statistics as st
rows=[json.loads(l) for l in open(sys.argv[1])]
def iso(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
feed=sorted([r for r in rows if r['src']=='feed'],key=lambda r:r['ts'])
ws=sorted([r for r in rows if r['src']=='ws'],key=lambda r:r['recv'])
# first frame time & first recv for each total-kill count
ff={}
for r in feed:
    k=r['bk']+r['rk']
    for kk in range(1,k+1):
        if kk not in ff: ff[kk]=(iso(r['ts']),r['recv'])
fw={}
for r in ws:
    a,b=r['score'].split('|')[0].split('-'); k=int(a)+int(b)
    for kk in range(1,k+1):
        if kk not in fw: fw[kk]=r['recv']
ws_lag=[];feed_lag=[];adv=[]
print('kill  frame_ts  ws_lag  feed_lag  ws_ahead')
for k in sorted(ff):
    if k not in fw: continue
    t,fr=ff[k]; w=fw[k]
    ws_lag.append(w-t);feed_lag.append(fr-t);adv.append(fr-w)
    print(k,dt.datetime.utcfromtimestamp(t).strftime('%H:%M:%S'),round(w-t,1),round(fr-t,1),round(fr-w,1))
if ws_lag:
    q=lambda x,p: sorted(x)[min(len(x)-1,int(p*len(x)))]
    print('n',len(ws_lag),'ws lag median',round(st.median(ws_lag),1),'p90',round(q(ws_lag,.9),1),'| feed lag median',round(st.median(feed_lag),1),'| ws ahead median',round(st.median(adv),1))
print('ws msgs',len(ws),'gaps',[round(b['recv']-a['recv'],1) for a,b in zip(ws,ws[1:])][:40])
