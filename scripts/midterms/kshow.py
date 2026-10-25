import json,sys; sys.path.insert(0,'.')
from tf import results
def f(x):
    try: return float(x)
    except: return None
def kev(F, store='k_events_store.json'):
    try: S=json.load(open(store))
    except: S={}
    for u,s in results(F):
        if isinstance(s,tuple): print(u[-60:],s[:2]); continue
        for e in s.get('events',[]):
            S[e['event_ticker']]=e
            ms=[m for m in e.get('markets',[]) if m.get('status') in ('active','open')]
            print(f"=== {e['event_ticker']} | {e['title'][:60]} | mutex {e.get('mutually_exclusive')} | n {len(ms)}")
            sa=0
            for m in ms:
                ya=f(m.get('yes_ask_dollars')) ; yb=f(m.get('yes_bid_dollars'))
                if ya is None: ya=(m.get('yes_ask') or 0)/100; yb=(m.get('yes_bid') or 0)/100
                sa+=ya
                print(f"   {m['ticker'][:34]:34} {(m.get('yes_sub_title') or m.get('subtitle') or '')[:40]:40} bid {yb} ask {ya} vol {m.get('volume')} oi {m.get('open_interest')} close {m.get('close_time','')[:10]} exp {m.get('expected_expiration_time','')[:10]}")
            print('   SUM ask',round(sa,3))
    json.dump(S,open(store,'w'))
if __name__=='__main__': kev(sys.argv[1])
