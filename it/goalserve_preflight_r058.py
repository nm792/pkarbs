#!/usr/bin/env python3
"""R-058 PRE-FLIGHT for the Goalserve capture, run by IT on Prime ~60 s AFTER starting capture_store_all.py. Any FAIL = exit 1 = IT kills the new copy and restarts the old one; nothing counts as started.
Checks: (1) exactly ONE writer process matching the script; (2) a SECOND copy is refused (exit 3, before any poll, so it cannot trigger a 429); (3) poll log grew >= MINROWS rows in the last 60 s with no `err` rows;
(4) newest payload file in each of the three payload folders touched within 120 s (store is change-driven; 120 s is an operational bound, stated); (5) disk free >= 10.5 GB (the gate).
Usage: python3 -I goalserve_preflight_r058.py GOALSERVE_DIR SCRIPT --pids NEWPID [--minrows 25] [--freegb 10.5]  (ALWAYS pass --pids NEWPID: pgrep also counts the systemd fallback copy) [--second-cmd 'python3 SCRIPT']"""
import argparse, fcntl, glob, json, os, shutil, subprocess, sys, time

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("script")
    ap.add_argument("--minrows", type=int, default=25); ap.add_argument("--freegb", type=float, default=10.5)
    ap.add_argument("--pids", default=""); ap.add_argument("--now", type=float); ap.add_argument("--skip-second", action="store_true")
    a = ap.parse_args(); now = a.now or time.time(); fails = []
    def chk(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else "")); 
        if not ok: fails.append(name)
    pids = [p for p in a.pids.split(",") if p] or subprocess.run(["pgrep", "-f", os.path.basename(a.script)], capture_output=True, text=True).stdout.split()
    pids = [p for p in pids if p != str(os.getpid())]
    chk("single writer: exactly 1 process", len(pids) == 1, "pids=" + ",".join(pids))
    if not a.skip_second:
        held = False
        try:
            fd = open(os.path.join(a.dir, ".capture.lock"), "a")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                held = True
            fd.close()
        except OSError:
            pass
        chk("live lock holder exists (.capture.lock is held)", held, "no live lock holder: the new copy is not running or not holding the lock" if not held else "")
        if held:
            try:
                r = subprocess.run([sys.executable, a.script], capture_output=True, text=True, timeout=10); rc = r.returncode
            except subprocess.TimeoutExpired:
                rc = "timeout"
            chk("second copy refused (exit 3)", rc == 3, "rc=%s" % rc)
    logs = sorted(glob.glob(os.path.join(a.dir, "goalserve_*.jsonl")))
    n = errs = 0
    if logs:
        for l in open(logs[-1], errors="replace").readlines()[-400:]:
            try: row = json.loads(l)
            except Exception: continue
            t = row.get("t", "")
            try: ts = time.mktime(time.strptime(t[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            except Exception: continue
            if now - ts <= 60:
                n += 1; errs += sum(1 for v in row.values() if isinstance(v, dict) and "err" in v)
    chk("poll log: >= %d rows in last 60 s" % a.minrows, n >= a.minrows, "rows=%d" % n)
    chk("poll log: 0 err entries in last 60 s", errs == 0, "errs=%d" % errs)
    for d in ("esports_payloads", "tennis_payloads", "hockey_nhl_payloads"):
        fs = glob.glob(os.path.join(a.dir, d, "*.jsonl.gz"))
        age = min((now - os.path.getmtime(f) for f in fs), default=None)
        chk("%s newest file < 120 s old" % d, age is not None and age < 120, "age=%s" % (None if age is None else int(age)))
    free = shutil.disk_usage(a.dir).free / 1e9
    chk("disk free >= %.1f GB" % a.freegb, free >= a.freegb, "free=%.1f" % free)
    print("PREFLIGHT VERDICT: %s" % ("FAIL: " + "; ".join(fails) if fails else "PASS"))
    sys.exit(1 if fails else 0)
main()
