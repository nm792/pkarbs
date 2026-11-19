import sys, datetime as dt
sys.path.insert(0, __file__.rsplit("/",1)[0])
from pit_store import pull_events
end = dt.date(2026,11,19); start = end - dt.timedelta(days=int(sys.argv[1]))
# monthly-ish chunks so a failure only loses one chunk
d = start
while d < end:
    e = min(d + dt.timedelta(days=3), end)
    n = pull_events(d.isoformat(), e.isoformat(), "/home/user/pk_cache/events.jsonl")
    print(d, e, n, flush=True); d = e
