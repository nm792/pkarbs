"""Pull trades for ALL other eligible families (non-excluded, not already in the deep series set): <=40 events/family, top-2 markets."""
import sys, os, json, collections, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, families as F, pit_store as P
deep = {F.family_key(e) for e in P.load_events("/home/user/pk_cache/events_deep.jsonl")}
by = collections.defaultdict(list)
for e in P.load_events("/home/user/pk_cache/events.jsonl"):
    if F.excluded_reason(e): continue
    k = F.family_key(e)
    if k in deep: continue
    by[k].append(e)
jobs = []; out = []
for fam, es in by.items():
    if len(es) < 3: continue
    for e in screen.sample_events(es, 40, 2026):
        ms = sorted([m for m in (screen.binary_resolved(m) for m in e["markets"]) if m], key=lambda m: -m["vol"])[:2]
        for m in ms: jobs.append(m["cond"]); out.append(dict(fam=fam, event=e["id"], cond=m["cond"]))
print(len(by), "families", len(jobs), "markets", flush=True)
json.dump([e for fam in by for e in screen.sample_events(by[fam], 40, 2026) if len(by[fam]) >= 3], open("/home/user/pk_cache/events_extra.json", "w"))
done = 0
with cf.ThreadPoolExecutor(16) as ex:
    for _ in ex.map(screen.get_trades, jobs):
        done += 1
        if done % 500 == 0: print(done, flush=True)
print("done", flush=True)
