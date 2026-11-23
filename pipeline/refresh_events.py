"""Append the newest closed events of each series to events_refresh.jsonl (newest first, stops at the first already-known event). R-036 final refresh; run on Prime.
Usage: python3 refresh_events.py SERIES_FILE [CACHE_DIR]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_store as P


def new_events(fetch, known, max_pages=30, page=100):
    """fetch(cursor) -> dict(events=[...], next_cursor=...). Newest first. Stops at a page whose events are all known. Returns list of slim events not in known."""
    out, cur = [], None
    for _ in range(max_pages):
        d = fetch(cur); evs = d.get("events", [])
        fresh = [e for e in evs if e["id"] not in known]
        for e in fresh: known.add(e["id"]); out.append(e)
        cur = d.get("next_cursor")
        if not cur or not evs or not fresh: break
    return out


def main(series_file, cache="/home/user/pk_cache"):
    slugs = [l.strip() for l in open(series_file) if l.strip() and not l.startswith("#")]
    known = set()
    for fn in ("events.jsonl", "events_deep.jsonl", "events_refresh.jsonl"):
        p = os.path.join(cache, fn)
        if os.path.exists(p): known |= {json.loads(l)["id"] for l in open(p)}
    n = 0
    with open(os.path.join(cache, "events_refresh.jsonl"), "a") as f:
        for s in slugs:
            def fetch(cur, s=s):
                u = f"{P.GAMMA}/events/keyset?closed=true&limit=100&series_slug={s}&order=endDate&ascending=false" + (f"&after_cursor={cur}" if cur else "")
                return P.http_json(u)
            for e in new_events(fetch, known):
                e = P.slim_event(e); e["_fetched_at"] = int(time.time()); f.write(json.dumps(e) + "\n"); n += 1
    print("new events", n)


if __name__ == "__main__": main(*sys.argv[1:])
