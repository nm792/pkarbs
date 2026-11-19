import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_store as P, families as F
slugs = sorted({(r.get("series") or [{}])[0].get("slug") for r in P.load_events("/home/user/pk_cache/events.jsonl")
                if not F.excluded_reason(r) and (r.get("series") or [{}])[0].get("recurrence") in ("daily", "hourly", "4h", "15m")} - {None})
print(len(slugs), "series", flush=True)
for s in slugs:
    print(s, P.pull_series(s, "/home/user/pk_cache/events_deep.jsonl"), flush=True)
