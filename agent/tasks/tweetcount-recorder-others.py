#!/usr/bin/env python3
"""Recorder for the NON-Elon xtracker count markets (Trump Truth Social, White House, Ted Cruz, Zelenskyy, NYC Mayor, CZ, Khamenei). stdlib only, no orders.
Why: the xtracker /posts list under-counts Trump (about 60% of the tracker's own total), so past windows cannot be rebuilt; the tracker's hourly stats are the resolution truth and exist only while a window is active.
Every 5 min, for every active tracking (from GET /api/trackings) that is not Elon and whose window has not ended + 1h:
  - tracking stats: total and the FULL hourly array (daily[])
  - Polymarket book (top 5 levels) for every bracket of the event named in marketLink
Writes one JSONL per slug into OUT. Exits after 2 h with nothing active, or --max-hours.
Usage: python3 tweetcount-recorder-others.py --out /vol2/pkarbs/tweetcount-others [--probe] [--max-hours 200]
"""
import argparse, json, os, time, urllib.request, calendar
UA = {"User-Agent": "Mozilla/5.0 (compatible; research-recorder)"}
XT = "https://xtracker.polymarket.com/api"

def j(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def active():
    out = []
    for t in j(XT + "/trackings")["data"]:
        if t["title"].startswith("Elon") or not t.get("isActive") or not t.get("marketLink"): continue
        end = calendar.timegm(time.strptime(t["endDate"][:19], "%Y-%m-%dT%H:%M:%S"))
        if end > time.time() - 3600: out.append(t)
    return out

def book(tok):
    b = j("https://clob.polymarket.com/book?token_id=" + tok)
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)[:5]
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))[:5]
    return bids, asks

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--probe", action="store_true"); ap.add_argument("--max-hours", type=float, default=200)
    a = ap.parse_args()
    if a.probe:
        ts = active(); print("active non-Elon trackings", len(ts))
        for t in ts[:3]:
            s = j("%s/trackings/%s?includeStats=true" % (XT, t["id"]))["data"]["stats"]
            slug = t["marketLink"].rstrip("/").split("/")[-1]
            ev = j("https://gamma-api.polymarket.com/events?slug=" + slug)[0]
            print(t["title"], "total", s["total"], "hours", len(s.get("daily", [])), "markets", len(ev["markets"]))
        return
    os.makedirs(a.out, exist_ok=True); start = time.time(); idle = None
    while time.time() - start < a.max_hours * 3600:
        t0 = time.time()
        try: ts = active()
        except Exception as ex:
            print("discover error", ex, flush=True); time.sleep(60); continue
        for t in ts:
            slug = t["marketLink"].rstrip("/").split("/")[-1]
            row = {"ts": t0, "slug": slug, "title": t["title"], "end": t["endDate"]}
            try:
                s = j("%s/trackings/%s?includeStats=true" % (XT, t["id"]))["data"]["stats"]
                row["xt_total"] = s["total"]; row["xt_hours"] = s.get("daily", [])
            except Exception as ex: row["xt_error"] = str(ex)
            br = []
            try:
                ev = j("https://gamma-api.polymarket.com/events?slug=" + slug)[0]
                for m in ev["markets"]:
                    try:
                        tok = json.loads(m["clobTokenIds"])[0]; bids, asks = book(tok)
                        br.append({"title": m.get("groupItemTitle"), "token": tok, "bids": bids, "asks": asks})
                    except Exception: pass
            except Exception as ex: row["ev_error"] = str(ex)
            row["brackets"] = br
            with open(os.path.join(a.out, "tw_%s.jsonl" % slug), "a") as f: f.write(json.dumps(row) + "\n")
        if not ts:
            idle = idle or t0
            if t0 - idle > 7200: print("nothing active for 2 h, exiting", flush=True); return
        else: idle = None
        time.sleep(max(1, 300 - (time.time() - t0)))

if __name__ == "__main__": main()
