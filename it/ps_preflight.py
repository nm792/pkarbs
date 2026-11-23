#!/usr/bin/env python3
"""READ-ONLY PRE-FLIGHT / HEALTH for the PandaScore LL capture (R-058, 23 Nov 2026). Never prints the token. Changes nothing.
usage: python3 -I ps_preflight.py [--root /mnt/HC_Volume_107257520/pkarbs/pandascore] [--lock /run/pscap2.lock] [--pidpat ll_capture] [--wait 60] [--discovery-json FILE] [--now EPOCH]
Bars (each PASS/FAIL, any FAIL = nothing starts / health FAIL):
 1 single instance: exactly one process matching --pidpat AND the lock file is HELD (`flock -n LOCK true` must be refused) so a second copy is refused.
 2 expected sockets E = discovery (api.pandascore.co/low_latency_feeds, CS2 'cs-go' + dota-2) matches whose endpoint.opens_at <= now; subscriptions S = matches with a `connected` event since the last `start` event
   in events.jsonl.gz and no later `closed`. PASS iff E == S. E == 0 gives WAIT (no live match: real data cannot be proven; rerun at the next window), not PASS.
 3 real data: newest raw/pandascore_*.jsonl.gz line count grows over --wait seconds when S > 0 (decompresses what is readable; a growing gzip member may raise EOFError: counted as readable-so-far).
 4 disk free on the data volume and the pid.
Prints one line per bar and `PREFLIGHT VERDICT: PASS|FAIL|WAIT`."""
import argparse, glob, gzip, json, os, subprocess, sys, time, shutil, datetime, urllib.request

def token():
    for p in ("/etc/pkarbs/pandascore.env", "/root/API_KEYS/pandascore/.env"):
        try:
            for l in open(p):
                l = l.strip()
                if l.startswith(("PANDASCORE_TOKEN=", "PANDASCORE_ACCESS_TOKEN=")): return l.partition("=")[2].strip().strip('"').strip("'")
        except Exception: pass
    return ""

def discovery():
    req = urllib.request.Request("https://api.pandascore.co/low_latency_feeds", headers={"Accept": "application/json", "Authorization": "Bearer " + token()})
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)

def opens(iso):
    try: return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    except Exception: return 1e18

def expected(feeds, now):
    items = feeds if isinstance(feeds, list) else feeds.get("data", [])
    out = {}
    for it in items:
        m = it.get("match") or {}; ep = it.get("endpoint") or {}
        if ((m.get("videogame") or {}).get("slug")) in ("cs-go", "dota-2") and ep.get("url") and opens(ep.get("opens_at") or "") <= now: out[str(m.get("id"))] = 1
    return out

def subs(events_path):
    start = {}; 
    try:
        with gzip.open(events_path, "rt") as f:
            lines = []
            try:
                for l in f: lines.append(l)
            except EOFError: pass
    except OSError: return None
    last_start = max([i for i, l in enumerate(lines) if '"kind": "start"' in l] or [-1])
    live = set()
    for l in lines[last_start + 1:]:
        try: e = json.loads(l)
        except Exception: continue
        if e.get("kind") == "connected": live.add(str(e.get("match_id")))
        elif e.get("kind") in ("closed", "stop_for_match", "stopped") and e.get("match_id") is not None: live.discard(str(e.get("match_id")))
    return live

def nlines(p):
    n = 0
    try:
        with gzip.open(p, "rt") as f:
            try:
                for _ in f: n += 1
            except EOFError: pass
    except OSError: return None
    return n

def main():
    a = argparse.ArgumentParser(); a.add_argument("--root", default="/mnt/HC_Volume_107257520/pkarbs/pandascore"); a.add_argument("--lock", default="/run/pscap2.lock")
    a.add_argument("--pidpat", default="ll_capture"); a.add_argument("--wait", type=int, default=60); a.add_argument("--discovery-json"); a.add_argument("--now", type=float)
    o = a.parse_args(); now = o.now or time.time(); verdict = "PASS"; fails = []
    pids = []   # python processes whose command line holds the pattern (the flock/bash/tmux parents are not counted)
    for l in subprocess.run(["ps", "-eo", "pid=,comm=,args="], capture_output=True, text=True).stdout.splitlines():
        f = l.split(None, 2)
        if len(f) == 3 and f[1].startswith("python") and o.pidpat in f[2] and "ps_preflight" not in f[2] and int(f[0]) != os.getpid(): pids.append(f[0])
    held = subprocess.run(["flock", "-n", o.lock, "true"]).returncode != 0 if os.path.exists(o.lock) else False
    ok1 = len(pids) == 1 and held; print("1 single instance: pids=%s lock_held=%s -> %s" % (pids, held, "PASS" if ok1 else "FAIL")); 
    if not ok1: fails.append("single-instance")
    try: feeds = json.load(open(o.discovery_json)) if o.discovery_json else discovery()
    except Exception as e: feeds = None; print("2 discovery error:", type(e).__name__); fails.append("discovery")
    E = expected(feeds, now) if feeds is not None else {}; S = subs(os.path.join(o.root, "events.jsonl.gz"))
    if S is None: print("2 events log unreadable -> FAIL"); fails.append("events-log")
    elif feeds is not None:
        if not E: print("2 expected sockets E=0 (no live match now): cannot prove subscriptions -> WAIT"); verdict = "WAIT"
        else:
            ok2 = set(E) == S; print("2 expected E=%d subscribed S=%d missing=%s -> %s" % (len(E), len(S), sorted(set(E) - S), "PASS" if ok2 else "FAIL"))
            if not ok2: fails.append("subscriptions!=expected")
    raws = sorted(glob.glob(os.path.join(o.root, "raw", "pandascore_*.jsonl.gz")))
    if raws and E:
        n1 = nlines(raws[-1]); time.sleep(o.wait); n2 = nlines(raws[-1]); ok3 = n1 is not None and n2 is not None and n2 > n1
        print("3 real data: %s lines %s -> %s after %ds -> %s" % (os.path.basename(raws[-1]), n1, n2, o.wait, "PASS" if ok3 else "FAIL"))
        if not ok3: fails.append("no-growth")
    elif not E: print("3 real data: not measurable without a live match -> WAIT")
    else: print("3 real data: no raw file -> FAIL"); fails.append("no-raw")
    print("4 disk free GB %.1f pid %s" % (shutil.disk_usage(o.root).free / 1e9 if os.path.isdir(o.root) else -1, pids))
    if fails: verdict = "FAIL"
    print("PREFLIGHT VERDICT: %s %s" % (verdict, fails if fails else "")); return 0 if verdict == "PASS" else 1

if __name__ == "__main__": sys.exit(main())
