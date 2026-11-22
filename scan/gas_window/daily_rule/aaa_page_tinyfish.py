#!/usr/bin/env python3
"""AAA page log fed by TinyFish Fetch (owner-approved 22 Nov 02:26Z; replaces direct fetch that returns Cloudflare 403). Same row schema as aaa_page_log.py:
recv_ns, status (200 only when a price AND date were parsed from a live read, else the HTTP/parse failure code), price_as_of ('m/d/yy'), regular_current (float), plus src='tinyfish'.
Every attempt is logged, failures included; a failed row never carries a price. Key from env TINYFISH_API_KEY (never logged). One read per --interval s (default 60)."""
import argparse, json, os, re, sys, time, urllib.request
URL = "https://gasprices.aaa.com/"; API = "https://api.fetch.tinyfish.ai"
def parse(text):
    """Returns (price_as_of, regular_current) from the fetched markdown, or (None, None). Reads the 'Current Avg.' Regular cell and the 'Price as of' date."""
    d = re.search(r"Price as of\s*(\d{1,2}/\d{1,2}/\d{2})", text or "")
    p = re.search(r"\|\s*Current Avg\.\s*\|\s*\$(\d\.\d{3,4})\s*\|", text or "")
    return (d.group(1), float(p.group(1))) if d and p else (None, None)
def fetch(key, timeout=150):
    req = urllib.request.Request(API, data=json.dumps({"urls": [URL], "format": "markdown", "ttl": 0}).encode(), headers={"X-API-Key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, json.loads(r.read())
def read_once(key, fetcher=fetch):
    req_ns = time.time_ns()   # R-020: recv_ns is stamped AFTER the response (decision time), request start kept separately
    try:
        st, body = fetcher(key); ns = time.time_ns(); res = (body.get("results") or [{}])[0]; asof, price = parse(res.get("text"))
        ok = st == 200 and asof is not None
        return dict(request_ns=req_ns, recv_ns=ns, status=200 if ok else (st if st != 200 else 599), price_as_of=asof if ok else None, regular_current=price if ok else None, src="tinyfish", latency_ms=res.get("latency_ms"))
    except Exception as e:
        return dict(request_ns=req_ns, recv_ns=time.time_ns(), status=getattr(e, "code", 599), price_as_of=None, regular_current=None, src="tinyfish", error=type(e).__name__)
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--start-epoch", type=float, default=0); ap.add_argument("--until-epoch", type=float, required=True); ap.add_argument("--interval", type=float, default=60)
    a = ap.parse_args(argv); key = os.environ.get("TINYFISH_API_KEY")
    if not key: print("TINYFISH_API_KEY not set", file=sys.stderr); return 2
    while time.time() < a.start_epoch: time.sleep(2)
    while time.time() < a.until_epoch:
        t0 = time.time(); row = read_once(key)
        with open(a.out, "a") as f: f.write(json.dumps(row) + "\n")
        time.sleep(max(0.0, a.interval - (time.time() - t0)))
if __name__ == "__main__": sys.exit(main())
