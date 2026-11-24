#!/usr/bin/env python3
"""7-day traded $ per event from data-api /v2/trades?event_id= (price*size summed; Gamma 'volume' is SHARES, not $, so it is not used).
Usage: python3 volumes.py RUNDIR [days=7]   (reads RUNDIR/universe.json, writes RUNDIR/volumes.json). Read-only, public API."""
import json, sys, time, urllib.request, urllib.parse
from pscanlib import notional
from pmtrades import check_rows   # R-080: v2 ignores unknown params, so verify every page against the event's markets

D = "https://data-api.polymarket.com"


def get(u):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "data-scan"}), timeout=60))
        except Exception as e:
            time.sleep(1 + 2 * i)
    return None


def event_conds(slug):
    ev = get("https://gamma-api.polymarket.com/events?slug=" + slug)
    return {m["conditionId"] for m in (ev[0].get("markets") or []) if m.get("conditionId")} if isinstance(ev, list) and ev else set()


def pull(event_id, t_from, conds, max_pages=400):
    rows, cur, pages, complete = [], None, 0, False
    while pages < max_pages:
        q = "event_id=%s&limit=500" % event_id + ("&cursor=" + urllib.parse.quote(cur) if cur else "")
        r = get(D + "/v2/trades?" + q)
        pages += 1
        if r is None:
            return rows, pages, False
        data = r.get("data") or []
        check_rows(data, conds, "event %s page %d" % (event_id, pages))
        rows += [dict(price=x["price"], size=x["size"], timestamp=x["timestamp"], token_id=x.get("token_id"), side=x.get("side")) for x in data]
        pg = r.get("pagination") or {}
        if not data or (data and min(x["timestamp"] for x in data) < t_from):
            complete = True
            break
        cur = pg.get("next_cursor")
        if not pg.get("has_more") or not cur:
            complete = True
            break
    return rows, pages, complete


def main(run, days=7):
    uni = json.load(open(run + "/universe.json"))["events"]
    now = time.time(); t_from = now - days * 86400
    out = []
    for e in uni:
        rows, pages, complete = pull(e["id"], t_from, event_conds(e["slug"]))
        rows = [r for r in rows if r["timestamp"] >= t_from]
        v7 = notional(rows)
        v24 = notional(rows, now - 86400)
        days_active = len({int(r["timestamp"] // 86400) for r in rows})
        out.append(dict(slug=e["slug"], family=e["family"], under=e["under"], n_trades=len(rows), usd_7d=v7, usd_per_day_7d=v7 / days, usd_24h=v24,
                        days_with_trades=days_active, pages=pages, complete=complete))
        print("%-58s %-14s trades %5d  $7d %9.0f  $/day %8.0f  24h %8.0f  complete=%s" % (e["slug"][:58], e["family"], len(rows), v7, v7 / days, v24, complete), flush=True)
    json.dump(dict(pulled=now, days=days, rows=out), open(run + "/volumes.json", "w"))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 7)
