import json, sys, datetime as dt, statistics as st, collections
def P(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def events(frames):
    prev=None; rows=[]
    pairs=[('bk','blue kills'),('rk','red kills'),('bt','blue towers'),('rt','red towers'),('bd','blue dragons'),('rd','red dragons'),('bb','blue barons'),('rb','red barons'),('bi','blue inhibitors'),('ri','red inhibitors')]
    for f in frames:
        b,r=f['blueTeam'],f['redTeam']
        cur={'bk':b['totalKills'],'rk':r['totalKills'],'bt':b['towers'],'rt':r['towers'],'bd':len(b['dragons']),'rd':len(r['dragons']),'bb':b['barons'],'rb':r['barons'],'bi':b['inhibitors'],'ri':r['inhibitors']}
        if prev:
            for k,lab in pairs:
                if cur[k]!=prev[k]: rows.append((P(f['rfc460Timestamp']), lab))
        prev=cur
    return rows
def run(name, frames, trades, outcome0):
    fin=[f for f in frames if f['gameState']=='finished']
    end = P(fin[0]['rfc460Timestamp']) if fin else P(frames[-1]['rfc460Timestamp'])
    evs=[(t,l) for t,l in events(frames) if t < end-60]
    tr=[]
    for t in trades:
        ph = t['price'] if t['outcome']==outcome0 else 1-t['price']
        tr.append((t['timestamp'], ph, t['side'], t['proxyWallet']))
    tr.sort()
    lags=[]; wallets=collections.Counter(); n=0
    for E,lab in evs:
        if E < P(frames[0]['rfc460Timestamp'])+60: continue
        pre=[x for x in tr if x[0] < E]
        if not pre: continue
        base=pre[-1][1]
        hit=None
        for x in tr:
            if x[0] >= E and abs(x[1]-base)>=0.02: hit=x; break
            if x[0] > E+300: break
        n+=1
        if hit:
            lags.append(hit[0]-E); wallets[hit[3]]+=1
    if not lags: print(name,'no lags'); return None
    lags.sort(); k=len(lags)
    res=dict(game=name,events=n,with_lag=k,median=round(st.median(lags),2),p25=round(lags[k//4],2),p75=round(lags[3*k//4],2),p90=round(lags[int(.9*k)],2),share_le2=round(sum(l<=2 for l in lags)/k,2),top_wallets=wallets.most_common(3))
    print(res); return res
if __name__=='__main__':
    import glob
    for d in sorted(glob.glob('out/*')):
        mid=d.split('/')[-1]
        m=[x for x in json.load(open('matched.json')) if x['match_id']==mid][0]
        frames=json.load(open(d+'/frames.json')); trades=json.load(open(d+'/trades.json'))
        run(mid+' '+'-'.join(m['teams']), frames, trades, m['outcomes'][0])
