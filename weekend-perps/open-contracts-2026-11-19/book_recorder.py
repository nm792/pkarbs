#!/usr/bin/env python3
"""Read-only recorder of OWN-TOKEN order books for the Polymarket 'Opens Up or Down' events (SPX, SPY). No keys, no orders.
usage: book_recorder.py --out DIR [--interval 10]
One JSON line per token per poll in DIR/ocbooks_YYYYMMDD.jsonl.gz: {"t":unix,"slug":..,"side":"Up"|"Down","token":..,"bids":[[px,sz]..],"asks":[[px,sz]..]} or {"err":..}.
NOTE the book order: bids ascend and asks DESCEND, so the best bid is the LAST bid and the best ask is the LAST ask (min price). Never take [0].
Records every event whose open is still ahead or was within the last 5 minutes (market opens ~13:01Z the day before)."""
import argparse, gzip, json, time, datetime, calendar, urllib.request, urllib.parse
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York"); G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"
def slugs_for(date):
    return [f"{p}-opens-up-or-down-on-{calendar.month_name[date.month].lower()}-{date.day}-{date.year}" for p in ("spx", "spy")]
def open_ts(date):
    return datetime.datetime(date.year, date.month, date.day, 9, 30, tzinfo=NY).timestamp()
def active_dates(now, days_ahead=4):
    """dates (weekdays) whose open is not more than 300 s in the past and at most days_ahead calendar days ahead"""
    d0 = datetime.datetime.fromtimestamp(now, NY).date(); out = []
    for i in range(-1, days_ahead + 1):
        d = d0 + datetime.timedelta(i)
        if d.weekday() < 5 and now <= open_ts(d) + 300: out.append(d)
    return out
def getj(u, t=10):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "data-logger"}), timeout=t))
def book_lines(now, slug, side, token, fetch=getj):
    try:
        b = fetch(C + "/book?token_id=" + token); b = b.get("data", b)
        return dict(t=now, slug=slug, side=side, token=token, bids=[[x["price"], x["size"]] for x in b.get("bids", [])], asks=[[x["price"], x["size"]] for x in b.get("asks", [])])
    except Exception as e: return dict(t=now, slug=slug, side=side, token=token, err=str(e)[:80])
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--interval", type=float, default=10); a = ap.parse_args(); toks = {}
    while True:
        t0 = time.time(); lines = []
        for d in active_dates(t0):
            for slug in slugs_for(d):
                if slug not in toks:
                    try:
                        e = getj(G + "/events?slug=" + slug)
                        if e: m = e[0]["markets"][0]; ts = json.loads(m["clobTokenIds"]); os_ = json.loads(m["outcomes"]); toks[slug] = {os_[i]: ts[i] for i in range(len(ts))}
                        else: continue
                    except Exception as ex: lines.append(dict(t=t0, slug=slug, err="gamma " + str(ex)[:60])); continue
                for side, tok in toks[slug].items(): lines.append(book_lines(t0, slug, side, tok))
        if lines:
            fn = "%s/ocbooks_%s.jsonl.gz" % (a.out, datetime.datetime.fromtimestamp(t0, datetime.timezone.utc).strftime("%Y%m%d"))
            with gzip.open(fn, "at") as f:
                for l in lines: f.write(json.dumps(l) + "\n")
        time.sleep(max(0, a.interval - (time.time() - t0)))
if __name__ == "__main__": main()
