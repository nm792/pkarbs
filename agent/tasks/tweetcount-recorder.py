#!/usr/bin/env python3
"""Paper-test recorder for 'Elon Musk # tweets <window>' markets (stdlib only, one process, no orders).

Every 5 minutes, for every OPEN Polymarket event titled 'Elon Musk # tweets ...' whose window has not ended:
  - xtracker tracking stats (the market's own resolution source): total so far, last hourly buckets
  - Polymarket book for every bracket: top 5 bid and ask levels
Writes one JSONL file per event slug into OUT: {ts, slug, title, xt_total, xt_last_hours, brackets:[{title, token, bids, asks}]}
Exits when no open window is left for 2 hours (or after --max-hours).
Usage: python3 tweetcount-recorder.py --out /vol2/pkarbs/tweetcount [--probe] [--max-hours 200]
"""
import argparse, json, os, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; research-recorder)"}
XT = "https://xtracker.polymarket.com/api"

def get(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def j(url): return json.loads(get(url))

def open_events():
    out = {}
    for off in (0, 100):
        q = urllib.parse.urlencode({"tag_slug": "tweets-markets", "closed": "false", "limit": 100, "offset": off,
                                    "order": "endDate", "ascending": "true"})
        for e in j("https://gamma-api.polymarket.com/events?" + q):
            if e["title"].startswith("Elon Musk # tweets") and re.search(r"\d+ - ", e["title"]):
                out[e["id"]] = e
    return list(out.values())

def trackings(handle="elonmusk"):
    d = j("%s/users/%s" % (XT, handle))["data"]
    return {t["title"]: t["id"] for t in d["trackings"]}

def xt_stats(tid):
    d = j("%s/trackings/%s?includeStats=true" % (XT, tid))["data"]["stats"]
    return d["total"], d.get("daily", [])[-3:]

def book(tok):
    b = j("https://clob.polymarket.com/book?token_id=" + tok)
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)[:5]
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))[:5]
    return bids, asks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--max-hours", type=float, default=200)
    a = ap.parse_args()
    if a.probe:
        evs = open_events(); tr = trackings()
        print("open events", [e["title"] for e in evs])
        for e in evs[:2]:
            tid = tr.get(e["title"]); print(e["title"], "tracking", tid)
            if tid: print("  xt total", xt_stats(tid)[0])
            m = e["markets"][0]; print("  book", book(json.loads(m["clobTokenIds"])[0]))
        return
    os.makedirs(a.out, exist_ok=True)
    start = time.time(); idle_since = None
    while time.time() - start < a.max_hours * 3600:
        t = time.time(); live = 0
        try:
            evs = open_events(); tr = trackings()
        except Exception as ex:
            print("discover error", ex, flush=True); time.sleep(60); continue
        for e in evs:
            end = time.mktime(time.strptime(e["endDate"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            if end < t - 3600: continue
            live += 1
            row = {"ts": t, "slug": e["slug"], "title": e["title"], "end": e["endDate"]}
            try:
                tid = tr.get(e["title"])
                if tid: row["xt_total"], row["xt_last_hours"] = xt_stats(tid)
            except Exception as ex:
                row["xt_error"] = str(ex)
            br = []
            for m in e["markets"]:
                try:
                    tok = json.loads(m["clobTokenIds"])[0]; bids, asks = book(tok)
                    br.append({"title": m.get("groupItemTitle"), "token": tok, "bids": bids, "asks": asks})
                except Exception: pass
            row["brackets"] = br
            with open(os.path.join(a.out, "tw_%s.jsonl" % e["slug"]), "a") as f: f.write(json.dumps(row) + "\n")
        if live == 0:
            idle_since = idle_since or t
            if t - idle_since > 7200: print("no open windows for 2 h, exiting", flush=True); return
        else: idle_since = None
        time.sleep(max(1, 300 - (time.time() - t)))

if __name__ == "__main__":
    main()
