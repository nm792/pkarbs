#!/usr/bin/env python3
"""List CS2 match-winner windows for the next H hours from Gamma (tag_slug=counter-strike-2). Read-only.
usage: cs2_schedule.py [hours=48]   Prints markdown table; UTC. Match time = gameStartTime else startTime (Gamma)."""
import sys, json, urllib.request, gzip, datetime as dt
H = float(sys.argv[1]) if len(sys.argv) > 1 else 48
now = dt.datetime.now(dt.timezone.utc); end = now + dt.timedelta(hours=H)
def get(url):
    r = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "pk-sched"})
    b = urllib.request.urlopen(r, timeout=30).read()
    try: b = gzip.decompress(b)
    except Exception: pass
    return json.loads(b)
rows = {}
for off in range(0, 1000, 50):
    u = ("https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2&closed=false&limit=50&offset=%d&order=startDate&ascending=false" % off)
    try: evs = get(u)
    except Exception as e: print("fetch error", off, repr(e)[:100], file=sys.stderr); break
    if not evs: break
    for e in evs:
        for m in e.get("markets", []):
            q = m.get("question", ""); t = m.get("gameStartTime") or m.get("startTime") or e.get("startTime")
            if not t or " - " in q and "Game" in q: pass
            try: ts = dt.datetime.fromisoformat(t.replace("Z", "+00:00").replace(" ", "T"))
            except Exception: continue
            if ts.tzinfo is None: ts = ts.replace(tzinfo=dt.timezone.utc)
            if now <= ts <= end:
                if m.get("sportsMarketType") != "moneyline": continue
                rows[m.get("conditionId")] = (ts, q, m.get("sportsMarketType"), e.get("slug"))
out = sorted(rows.values())
print("generated %s, window next %gh, %d markets" % (now.strftime("%Y-%m-%d %H:%MZ"), H, len(out)))
print("| UTC start | PS socket opens (-15 min) | sportsMarketType | market |\n|---|---|---|---|")
for ts, q, k, s in out:
    print("| %s | %s | %s | %s |" % (ts.strftime("%d %b %H:%MZ"), (ts - dt.timedelta(minutes=15)).strftime("%H:%MZ"), k, q[:70]))
