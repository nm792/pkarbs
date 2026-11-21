#!/usr/bin/env python3
"""AAA national-average PAGE LOG for the paper run (Reviewer condition 1: value + fetch time every minute 02:45-04:00 ET).
Difference from aaa_watch.py: EVERY poll writes a row, including HTTP errors (403 Cloudflare, timeouts), with status, cf-ray and body hash, so a blocked page is visible in the log, not silent. paper_post.page_change() only trusts rows with status 200.
Read-only GET of the public page; no evasion of blocks (if the page returns 403 the log says so and the owner is told).
Usage: aaa_page_log.py --out FILE --until 2026-11-21T09:00:00Z [--interval 30] [--start 2026-11-21T07:45:00Z]"""
import json, re, sys, time, argparse, hashlib, calendar, urllib.request, urllib.error
URL = "https://gasprices.aaa.com/"
def parse(html):
    txt = re.sub(r"<[^>]+>", " ", html); txt = re.sub(r"\s+", " ", txt)
    m = re.search(r"Price as of\s*([0-9/]+)", txt, re.I); asof = m.group(1) if m else None
    row = {}
    for lab, key in (("Current Avg\\.", "current"), ("Yesterday Avg\\.", "yesterday"), ("Week Ago Avg\\.", "week_ago")):
        r = re.search(lab + r"\s*\$?\s*([0-9]\.[0-9]{2,3})", txt, re.I); row[key] = float(r.group(1)) if r else None
    i = txt.find("Current Avg"); snip = txt[max(0, i - 100): i + 100] if i >= 0 else None
    return {"price_as_of": asof, "regular_current": row["current"], "regular_yesterday": row["yesterday"], "regular_week_ago": row["week_ago"], "snippet": snip}
def fetch(url, timeout=15):
    """Returns (status, headers dict, body bytes). HTTP errors are returned, not raised."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: st, h, body = r.status, r.headers, r.read()
    except urllib.error.HTTPError as e: st, h, body = e.code, e.headers, e.read()
    return st, {k: h.get(k) for k in ("Date", "Last-Modified", "ETag", "Age", "Cache-Control", "cf-ray", "Server")}, body
def poll_once(url, fetch_fn=fetch, now_ns=time.time_ns):
    """One log row for one poll; never raises."""
    t = now_ns()
    try: st, hd, body = fetch_fn(url)
    except Exception as ex: return {"recv_ns": t, "url": url, "status": None, "error": repr(ex)[:160], "regular_current": None, "price_as_of": None}
    rec = {"recv_ns": t, "url": url, "status": st, "headers": hd, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
    try: rec.update(parse(body.decode("utf-8", "replace")))
    except Exception as ex: rec.update({"price_as_of": None, "regular_current": None, "error": "parse " + repr(ex)[:100]})
    if st != 200: rec["regular_current"] = None; rec["price_as_of"] = None      # a block page must never look like a price
    return rec
def run(out, until_ts, interval=30.0, start_ts=0.0, fetch_fn=fetch, sleep=time.sleep, now=time.time, max_polls=None):
    n = 0
    with open(out, "a") as f:
        while now() < until_ts and (max_polls is None or n < max_polls):
            if now() < start_ts: sleep(min(30.0, start_ts - now())); continue
            t0 = now(); f.write(json.dumps(poll_once(URL, fetch_fn)) + "\n"); f.flush(); n += 1
            sleep(max(0.0, interval - (now() - t0)))
    return n
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--until", required=True); ap.add_argument("--start", default="1970-01-01T00:00:00Z"); ap.add_argument("--interval", type=float, default=30.0)
    a = ap.parse_args(); fmt = "%Y-%m-%dT%H:%M:%SZ"
    print("polls", run(a.out, calendar.timegm(time.strptime(a.until, fmt)), a.interval, calendar.timegm(time.strptime(a.start, fmt))))
