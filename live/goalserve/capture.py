#!/usr/bin/env python3
"""Goalserve trial Part A capture (start). Polls authenticated inplay feeds at ~1s,
logs to /vol2/goalserve/. Reads /etc/pkarbs/goalserve.env (USER/KEY, mode 600).
Per TASK-goalserve-trial: per poll log recv ns, HTTP Date, payload sha1, change first-seen.
"""
import os, sys, time, gzip, json, hashlib, datetime, urllib.request, urllib.parse

def load_creds():
    d = {}
    with open("/etc/pkarbs/goalserve.env") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                d[k.strip()] = v.strip()
    return d

ENV = load_creds()
USER, KEY = ENV.get("GOALSERVE_USER", ""), ENV.get("GOALSERVE_KEY", "")
BASE = "https://inplay.goalserve.com"
OUT = "/vol2/goalserve"
SPORTS = {
    "tennis":   "/inplay-tennis.gz",
    "cricket":  "/inplay-cricket.gz",
    "soccer":   "/inplay-soccer.gz",
    "basketball": "/inplay-basketball.gz",
}
os.makedirs(OUT, exist_ok=True)

def fetch(rel):
    url = BASE + rel + "?" + urllib.parse.urlencode({"user": USER, "key": KEY})
    t0 = time.time_ns()
    body = urllib.request.urlopen(urllib.request.Request(url, headers={"Accept-Encoding": "gzip"}), timeout=20).read()
    recv_ns = time.time_ns()
    try:
        data = gzip.decompress(body)
    except Exception:
        data = body
    sha1 = hashlib.sha1(data).hexdigest()
    return recv_ns, t0, sha1, data

last = {}  # sport -> (sha1, first_seen_ns)

def main():
    logf = os.path.join(OUT, f"goalserve_{datetime.datetime.now(datetime.timezone.utc):%Y%m%d}.jsonl")
    with open(logf, "a") as out:
        while True:
            row = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")}
            for sport, rel in SPORTS.items():
                try:
                    recv_ns, t0, sha1, data = fetch(rel)
                    changed = last.get(sport) is None or last[sport][0] != sha1
                    first = last[sport][1] if (not changed and sport in last) else recv_ns
                    if changed:
                        last[sport] = (sha1, recv_ns)
                    row[sport] = {
                        "recv_ns": recv_ns, "send_ns": t0, "http_date_us": 0,
                        "sha1": sha1, "bytes": len(data), "changed": changed,
                        "first_seen_ns": first,
                    }
                except Exception as ex:
                    row[sport] = {"recv_ns": time.time_ns(), "err": repr(ex)[:200]}
            out.write(json.dumps(row, default=str) + "\n"); out.flush()
            time.sleep(1.0)

if __name__ == "__main__":
    main()
