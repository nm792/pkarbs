#!/usr/bin/env python3
"""Paper-test recorder for 'views of next <creator> video' markets (stdlib only, one process).

What it records (JSON lines in OUT):
  views_<videoid>.jsonl : {ts, video, age_s, source, views}  every 60 s for 26 h after upload, then every 15 min to +7 d
  books_<videoid>.jsonl : {ts, video, age_s, event, slug, brackets:[{title, token, bid, bid_sz, ask, ask_sz}]}  every 120 s for 26 h, then every 10 min
  uploads.jsonl         : every new upload seen on a watched channel
It places NO orders and needs no keys. It exits when no upload arrives within --max-wait-hours, or when all
tracked videos are finished.
Usage: python3 influencer-recorder.py --out /vol2/pkarbs/influencer [--max-wait-hours 72] [--probe]
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

CHANNELS = {  # name -> (channel id, polymarket title keyword)
    "mrbeast": ("UCX6OQ3DkcsbYNE6H8uQQuVA", "next MrBeast video"),
    "mrbeast-gaming": ("UCIPPMRA040LQr5QPyJEbmXA", "next MrBeast Gaming video"),
}
UA = {"User-Agent": "Mozilla/5.0 (compatible; research-recorder)"}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def parse_feed(xml_text):
    out = []
    root = ET.fromstring(xml_text)
    for e in root.findall("a:entry", NS):
        vid = e.find("yt:videoId", NS).text
        pub = e.find("a:published", NS).text
        title = e.find("a:title", NS).text
        st = e.find("m:group/m:community/m:statistics", NS)
        views = int(st.get("views")) if st is not None and st.get("views") else None
        out.append({"id": vid, "published": pub, "title": title, "rss_views": views})
    return out

def iso_to_ts(s):
    import datetime as dt
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def parse_watch_views(html):
    m = re.search(r'"viewCount":"(\d+)"', html)
    return int(m.group(1)) if m else None

def poly_events(keyword):
    q = urllib.parse.urlencode({"q": "views " + keyword, "events_status": "active", "limit_per_type": 30})
    d = json.loads(get("https://gamma-api.polymarket.com/public-search?" + q))
    return [e for e in d.get("events", []) if keyword.lower() in e["title"].lower()
            and e["title"].startswith("# of views")]

def books_for(event):
    rows = []
    for m in event.get("markets", []):
        try:
            tok = json.loads(m["clobTokenIds"])[0]
            b = json.loads(get("https://clob.polymarket.com/book?token_id=" + tok))
        except Exception:
            continue
        bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)
        asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))
        rows.append({"title": m.get("groupItemTitle"), "token": tok,
                     "bid": bids[0][0] if bids else None, "bid_sz": bids[0][1] if bids else None,
                     "ask": asks[0][0] if asks else None, "ask_sz": asks[0][1] if asks else None})
    return rows

def append(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-wait-hours", type=float, default=72)
    ap.add_argument("--probe", action="store_true", help="one-shot reachability check, then exit")
    a = ap.parse_args()
    if a.probe:
        for name, (cid, kw) in CHANNELS.items():
            feed = parse_feed(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid))
            v = feed[0]
            wv = parse_watch_views(get("https://www.youtube.com/watch?v=" + v["id"]))
            evs = poly_events(kw)
            print(name, "latest", v["id"], v["published"], "rss_views", v["rss_views"], "watch_views", wv,
                  "open_events", [e["title"] for e in evs])
            for e in evs[:1]:
                print("  book sample", books_for(e)[:3])
        return
    os.makedirs(a.out, exist_ok=True)
    start = time.time()
    seen, tracked = set(), {}   # tracked[vid] = dict(ch, kw, t0, nv, nb, title, ev, evts)
    for name, (cid, kw) in CHANNELS.items():   # existing uploads are ignored
        for v in parse_feed(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid)):
            seen.add(v["id"])
    print("watching", list(CHANNELS), "known videos", len(seen), flush=True)
    last_feed = 0
    while True:
        now = time.time()
        if now - last_feed >= 30:
            last_feed = now
            for name, (cid, kw) in CHANNELS.items():
                try:
                    feed = parse_feed(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid))
                except Exception as ex:
                    print("feed error", name, ex, flush=True); continue
                for v in feed:
                    if v["id"] in seen: continue
                    seen.add(v["id"])
                    t0 = iso_to_ts(v["published"])
                    append(os.path.join(a.out, "uploads.jsonl"),
                           {"seen_ts": now, "channel": name, **v})
                    if now - t0 < 6 * 3600:
                        tracked[v["id"]] = {"ch": name, "kw": kw, "t0": t0, "nv": now, "nb": now, "title": v["title"], "ev": None, "evts": 0}
                        print("tracking", v["id"], v["title"], flush=True)
        for vid, s in list(tracked.items()):
            age = now - s["t0"]
            if age > 7 * 86400 + 3600:
                del tracked[vid]; continue
            if now >= s["nv"]:
                s["nv"] = now + (60 if age < 26 * 3600 else 900)
                views, src = None, "watch"
                try: views = parse_watch_views(get("https://www.youtube.com/watch?v=" + vid))
                except Exception: pass
                if views is None:
                    src = "rss"
                    try:
                        for v in parse_feed(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNELS[s["ch"]][0])):
                            if v["id"] == vid: views = v["rss_views"]
                    except Exception: pass
                append(os.path.join(a.out, "views_%s.jsonl" % vid), {"ts": now, "video": vid, "age_s": age, "source": src, "views": views})
            if now >= s["nb"]:
                s["nb"] = now + (120 if age < 26 * 3600 else 600)
                try:
                    if now - s["evts"] > 300 or not s["ev"]:
                        s["ev"] = poly_events(s["kw"]); s["evts"] = now
                    for e in s["ev"]:
                        append(os.path.join(a.out, "books_%s.jsonl" % vid),
                               {"ts": now, "video": vid, "age_s": age, "event": e["title"], "slug": e.get("slug"), "brackets": books_for(e)})
                except Exception as ex:
                    print("book error", ex, flush=True)
        if not tracked and now - start > a.max_wait_hours * 3600:
            print("no upload within wait limit, exiting", flush=True); return
        time.sleep(5)

if __name__ == "__main__":
    main()
