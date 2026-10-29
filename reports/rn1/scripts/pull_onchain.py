# OrderFilled logs with maker = rn1 on Polygon, 22-29 Oct 2026 (blocks found by timestamp bisection).
# Role: taker topic == emitting exchange contract -> rn1's own taker order; otherwise rn1 was the resting maker.
import json,urllib.request,time,os,sys
U=["https://polygon.gateway.tenderly.co"]
def rpc(m,p,k=0):
    for i in range(6):
        u=U[(k+i)%len(U)]
        try:
            r=urllib.request.Request(u,data=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),headers={"Content-Type":"application/json","User-Agent":"curl/8"})
            d=json.load(urllib.request.urlopen(r,timeout=60))
            if "result" in d: return d["result"],u
            err=d.get("error")
        except Exception as e: err=str(e)
        time.sleep(1+i)
    raise Exception(str(err))
S,E=1792634632,1793239431
b0,b1=95952843,96356034  # first block >= S, last block <= E
T0="0xd543adfd945773f1a62f74f0ee55a5e3b9b1a28262980ba90b1a89f2ea84d8ee"
W="0x0000000000000000000000002005d16a84ceefa912d4e380cd32e7ff827875ea"
OUT=sys.argv[1] if len(sys.argv)>1 else "onchain"; os.makedirs(OUT,exist_ok=True)
json.dump({"start_ts":S,"end_ts":E,"from_block":b0,"to_block":b1},open(f"{OUT}/bounds.json","w"))
step=10000
for a in range(b0,b1+1,step):
    b=min(b1,a+step-1); fn=f"{OUT}/maker_{a}_{b}.json"
    if os.path.exists(fn): continue
    logs,u=rpc("eth_getLogs",[{"fromBlock":hex(a),"toBlock":hex(b),"topics":[T0,None,W]}],a//step)
    json.dump({"fromBlock":a,"toBlock":b,"rpc":u,"filter":{"topics":[T0,None,W]},"pulled_at":int(time.time()),"logs":logs},open(fn,"w"))
    print(a,b,len(logs),u,flush=True)
