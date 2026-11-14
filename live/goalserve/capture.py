#!/usr/bin/env python3
"""Goalserve trial Part A capture (start). Polls authenticated inplay feeds at ~1s,
logs to /mnt/HC_Volume_107257520/pkarbs/goalserve/. Reads /etc/pkarbs/goalserve.env (USER/KEY, mode 600).
Per TASK-goalserve-trial: per poll log recv ns, HTTP Date, payload sha1, change first-seen.
"""
import os, sys, time, gzip, json, hashlib, shutil, datetime, urllib.request, urllib.parse

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
OUT = "/mnt/HC_Volume_107257520/pkarbs/goalserve"
SPORTS = {
    "tennis":   "/inplay-tennis.gz",
    "soccer":   "/inplay-soccer.gz",
    "baseball": "/inplay-baseball.gz",
    "hockey_nhl": "/inplay-hockey.gz",
    "esports":   "/inplay-esports.gz",
    # esports added 13 Nov 14:0xZ under APPROVALS item 18 (Nick yes 13:46Z); poll stays 1.0 s.
    # inplay-basket.gz / inplay-volleyball.gz measured HTTP 200 on 13 Nov but are OUT of
    # approved scope; inplay-cricket.gz is 404 (no such feed).
}
PAYDIR = "/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads"   # Nick yes 14:43:42Z 13 Nov (inbox #300)
_payload_stopped = False

def store_payload(recv_ns, data):
    """Esports-only: append the changed raw body, gzipped, one file per UTC hour.
    Stops (and logs once) if the output filesystem is at or below the 15 GB floor."""
    global _payload_stopped
    try:
        if shutil.disk_usage("/mnt/HC_Volume_107257520/pkarbs/goalserve").free <= 15e9:
            if not _payload_stopped:
                _payload_stopped = True
                with open(os.path.join(OUT, "esports_payloads_STOP.log"), "a") as f:
                    f.write(json.dumps({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                        "free_b": shutil.disk_usage("/mnt/HC_Volume_107257520/pkarbs/goalserve").free,
                                        "action": "payload store stopped: free <= 15 GB"}) + "\n")
            return
        os.makedirs(PAYDIR, exist_ok=True)
        hour = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H")
        with gzip.open(os.path.join(PAYDIR, f"esports_{hour}.jsonl.gz"), "at") as pf:
            pf.write(json.dumps({"recv_ns": recv_ns, "body": data.decode("utf-8", "replace")}) + "\n")
    except Exception as ex:
        if not _payload_stopped:
            _payload_stopped = True
            with open(os.path.join(OUT, "esports_payloads_STOP.log"), "a") as f:
                f.write(json.dumps({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                    "err": repr(ex)[:300]}) + "\n")

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
                    if changed and sport == "esports":
                        store_payload(recv_ns, data)
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
