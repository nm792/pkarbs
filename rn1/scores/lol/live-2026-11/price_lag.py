import json,sys,datetime as dt,numpy as np,bisect
D=sys.argv[1]; MOVE=float(sys.argv[2]) if len(sys.argv)>2 else 0.015
iso=lambda s: dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
GAMES={'g1':'115660540726095116','g2':'115660540726095117','g3':'115660540726095118'}
frames={g:[] for g in GAMES.values()}
for l in open(f'{D}/GEN-LYON_frames.jsonl'):
    f=json.loads(l); frames[f['game_id']].append((iso(f['rfc460Timestamp']),f['blueTeam']['totalKills'],f['redTeam']['totalKills'],f['blueTeam']['totalGold']-f['redTeam']['totalGold'],f['recv_ms']/1000))
ws=[json.loads(l) for l in open(f'{D}/GEN-LYON_sportsws.jsonl')]
rows=[]
for gi,(g,gid) in enumerate(GAMES.items()):
    tr=json.load(open(f'{D}/trades_{g}.json'))
    P=sorted((t['timestamp'], t['price'] if t['outcome_index']==0 else 1-t['price']) for t in tr)
    pt=[p[0] for p in P]; pv=np.array([p[1] for p in P])
    F=sorted(frames[gid])
    # blue = Gen.G ? correlate gold diff with price at frame time (sampled each 30 s)
    xs=[];ys=[]
    for T,bk,rk,gd,_ in F[::300]:
        i=bisect.bisect_right(pt,T)-1
        if i>=0: xs.append(gd); ys.append(pv[i])
    blue_gen = np.corrcoef(xs,ys)[0,1]>0
    # WS first-seen per total kills
    wsf={}
    for w in ws:
        if w.get('period')==f'{gi+1}/5' and w.get('status')=='running':
            a,b=w['score'].split('|')[0].split('-'); k=int(a)+int(b)
            for kk in range(1,k+1): wsf.setdefault(kk,w['recv_ms']/1000)
    pb=pr=0; seen_tot=0
    for T,bk,rk,gd,rc in F:
        if bk+rk<=seen_tot: pb,pr=bk,rk; continue
        if F[0][1]+F[0][2]>0 and T<F[0][0]+5: pb,pr,seen_tot=bk,rk,bk+rk; continue  # capture start artefact
        side = 1 if bk>pb else -1          # +1 blue killed
        gen_up = (side==1)==blue_gen
        seen_tot=bk+rk; pb,pr=bk,rk
        i0=bisect.bisect_left(pt,T-30); i1=bisect.bisect_left(pt,T)
        if i1-i0<1: ref=pv[i1-1] if i1>0 else None
        else: ref=np.median(pv[i0:i1])
        if ref is None or not (0.05<ref<0.95): continue
        tp=None
        for j in range(bisect.bisect_left(pt,T-5), bisect.bisect_right(pt,T+120)):
            d=pv[j]-ref
            if (d>=MOVE if gen_up else d<=-MOVE): tp=pt[j]; break
        w=wsf.get(seen_tot)
        rows.append((g,seen_tot,T,tp,w,rc,blue_gen))
ok=[r for r in rows if r[3] is not None and r[4] is not None]
pl=np.array([r[3]-r[2] for r in ok]); wl=np.array([r[4]-r[3] for r in ok]); fl=np.array([r[5]-r[3] for r in ok])
print(f'MOVE {MOVE}: kills {len(rows)}, price moved within 120 s on {len(ok)}')
print('blue=Gen.G per game', {r[0]:r[6] for r in rows})
for n,a in [('price after kill',pl),('WS after price',wl),('Riot feed after price',fl)]:
    print(f'{n:22} median {np.median(a):6.1f}  p10 {np.percentile(a,10):6.1f}  p90 {np.percentile(a,90):6.1f}')
print('WS before price move:', int((wl<0).sum()), 'of', len(wl))
