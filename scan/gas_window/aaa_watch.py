#!/usr/bin/env python3
"""Timestamped watcher of the AAA national average page, to find WHEN the daily value changes (UTC and ET) and what the page shows.
Read-only HTTPS GET of public pages. Usage: aaa_watch.py --out DIR --until 2026-11-20T09:00:00Z [--interval 10] [--max-seconds 540]
One JSON line per poll in DIR/aaa_watch.jsonl: recv_ns, http status, Date / Last-Modified / ETag headers, body sha256, parsed price_as_of,
regular current / yesterday / week-ago averages, and a 200 char snippet around the first 'Current Avg.' for audit. Parser is tolerant: if it
cannot parse, fields are null and the hash still shows a change."""
import json, os, re, sys, time, argparse, hashlib, calendar, urllib.request
URLS = ["https://gasprices.aaa.com/"]
def parse(html):
    txt = re.sub(r"<[^>]+>", " ", html); txt = re.sub(r"\s+", " ", txt)
    m = re.search(r"Price as of\s*([0-9/]+)", txt, re.I); asof = m.group(1) if m else None
    row = {}
    for lab, key in (("Current Avg\\.", "current"), ("Yesterday Avg\\.", "yesterday"), ("Week Ago Avg\\.", "week_ago")):
        r = re.search(lab + r"\s*\$?\s*([0-9]\.[0-9]{2,3})", txt, re.I); row[key] = float(r.group(1)) if r else None
    i = txt.find("Current Avg"); snip = txt[max(0, i - 100): i + 100] if i >= 0 else None
    return {"price_as_of": asof, "regular_current": row["current"], "regular_yesterday": row["yesterday"], "regular_week_ago": row["week_ago"], "snippet": snip}
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read(); h = r.headers
        return r.status, {k: h.get(k) for k in ("Date", "Last-Modified", "ETag", "Age", "Cache-Control")}, body
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--until", required=True)
    ap.add_argument("--interval", type=float, default=10.0); ap.add_argument("--max-seconds", type=float, default=540)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    until = calendar.timegm(time.strptime(a.until, "%Y-%m-%dT%H:%M:%SZ")); t_start = time.time(); n = err = 0
    with open(os.path.join(a.out, "aaa_watch.jsonl"), "a") as f:
        while time.time() < until and time.time() - t_start < a.max_seconds:
            t0 = time.time()
            for u in URLS:
                try:
                    st, hd, body = fetch(u); rec = {"recv_ns": time.time_ns(), "url": u, "status": st, "headers": hd, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
                    rec.update(parse(body.decode("utf-8", "replace"))); f.write(json.dumps(rec) + "\n"); f.flush(); n += 1
                except Exception as ex: err += 1; print("ERR", repr(ex)[:120], flush=True)
            time.sleep(max(0.0, a.interval - (time.time() - t0)))
    print(f"polls {n} errors {err}")
