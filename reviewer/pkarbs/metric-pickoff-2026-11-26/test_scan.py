# planted checks: each must be able to fail. run: python3 test_scan.py
import scan
R=1_800_000_000; W="WIN"; LOSE="LOSE"
def row(dt_,tok,side,p,sz=100): return dict(ts=R+dt_,tok=tok,side=side,p=p,sz=sz)
rows=[row(-1,W,"BUY",0.80),      # pre-release stale-looking print: MUST be rejected
      row(5,W,"BUY",0.80,50),     # planted stale ask: MUST be found
      row(6,W,"BUY",0.96),        # >=0.95: reject
      row(7,W,"SELL",0.70),       # seller side: reject
      row(8,LOSE,"BUY",0.60),     # loser token: reject
      row(61,W,"BUY",0.80)]       # outside window: reject
f=scan.scan_market(rows,W,R)
assert f[0]==[(R+5,0.80,50)], f[0]
assert f[5]==[(R+5,0.80,50)] and f[15]==[], (f[5],f[15])     # latency L=15 misses the R+5 print
# mutation proof: if the window started before R the pre-release print would leak in (check can fail)
leak=[r for r in rows if r["tok"]==W and r["side"]=="BUY" and r["p"]<0.95 and R-10<=r["ts"]<=R+60]
assert len(leak)==2
# jump detection: planted jump and planted no-jump
series=[(R-3600,0.30),(R-60,0.35),(R-1,0.36),(R+4,0.50),(R+5,0.80),(R+40,0.97),(R+90,0.99)]
assert scan.jump_time(series)==R+5
assert scan.jump_time([(R-100,0.9),(R,0.95),(R+9,0.99)]) is None
# snap: R_cal 13:30Z (EST Nov 2026) must be picked for jump at 13:30:20Z, rejected at 13:36Z
import datetime as dt
t=int(dt.datetime(2026,11,6,13,30,tzinfo=dt.timezone.utc).timestamp())
assert scan.snap("jobs_unemp",t+20)==t
assert scan.snap("jobs_unemp",t+700) is None
assert scan.snap("elon_tweets",t+20) is None
# caps
paid,edge=scan.day_cap([(R+1,0.5,10000)]); assert abs(paid-200)<1e-9 and abs(edge-200)<1e-9
paid,edge=scan.day_cap([(R+i,0.5,1000) for i in range(30)]); assert abs(paid-2000)<1e-9
print("ALL PLANTED CHECKS PASS")
