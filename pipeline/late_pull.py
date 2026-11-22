"""Pull trade tapes for every market of the last 40 events of each screened recurring family (R-036 item 1). Resumable (screen.get_trades caches)."""
import collections, concurrent.futures as cf, datetime as dt, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import families as F, pit_store as P, screen, pandas as pd
def targets(nmax=40):
    ev = [e for e in P.load_events("/home/user/pk_cache/events.jsonl") + P.load_events("/home/user/pk_cache/events_deep.jsonl") if not F.excluded_reason(e)]
    fams = set(pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out/listing1/listing_hours_series2.csv")).fam)
    now = max(screen.parse_ts(e["endDate"]) for e in ev if screen.parse_ts(e["endDate"]) < time.time())
    by = collections.defaultdict(dict)
    for e in ev:
        k = F.family_key(e)
        if (k in fams or k.replace("series:", "") in fams) and not k.startswith("tpl:") and screen.parse_ts(e["endDate"]) <= now: by[k][e["id"]] = e
    return {k: sorted(es.values(), key=lambda e: e["endDate"])[-nmax:] for k, es in by.items()}
if __name__ == "__main__":
    t = targets(); conds = [m["conditionId"] for es in t.values() for e in es for m in e["markets"]]
    have = set(x[:-8] for x in os.listdir(screen.CACHE)); todo = [c for c in dict.fromkeys(conds) if c not in have]
    print(len(conds), "markets", len(todo), "to pull", flush=True); n = 0
    def w(c):
        try: screen.get_trades(c); return 1
        except Exception as ex: return 0
    with cf.ThreadPoolExecutor(10) as ex:
        for r in ex.map(w, todo):
            n += 1
            if n % 200 == 0: print(n, time.strftime("%H:%M:%S"), flush=True)
    print("done", n, flush=True)
