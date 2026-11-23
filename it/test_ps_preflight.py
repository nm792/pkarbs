#!/usr/bin/env python3
"""Tests for ps_preflight.py (python3 -I it/test_ps_preflight.py). Offline: fake discovery json, fake events gz, a real flock and a dummy process named llfake_capture."""
import os, sys, json, gzip, time, subprocess, tempfile
here = os.path.dirname(os.path.abspath(__file__)); fails = []
def chk(n, ok, x=""):
    print(("PASS " if ok else "FAIL ") + n, x)
    if not ok: fails.append(n)
d = tempfile.mkdtemp(); os.makedirs(d + "/raw"); lock = d + "/lock"; open(lock, "w").close()
now = time.time(); iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
def feeds(ids): return [dict(match=dict(id=i, videogame=dict(slug="cs-go")), endpoint=dict(url="wss://x", opens_at=iso(now - 600))) for i in ids]
def events(lines):
    with gzip.open(d + "/events.jsonl.gz", "wt") as f:
        for l in lines: f.write(json.dumps(l) + "\n")
def run(fd, wait=2):
    json.dump(fd, open(d + "/fd.json", "w"))
    r = subprocess.run([sys.executable, "-I", here + "/ps_preflight.py", "--root", d, "--lock", lock, "--pidpat", "llfake_capture", "--wait", str(wait), "--discovery-json", d + "/fd.json"], capture_output=True, text=True)
    return r.stdout
# dummy capture process holding the lock
dummy = d + "/llfake_capture.py"; open(dummy, "w").write("import time\nwhile True: time.sleep(1)\n")
p = subprocess.Popen(["flock", "-n", lock, sys.executable, dummy], start_new_session=True)
time.sleep(1)
# writer that grows the raw file
raw = d + "/raw/pandascore_2026112303.jsonl.gz"
w = subprocess.Popen([sys.executable, "-c", "import gzip,time,sys\nwhile True:\n    f=gzip.open(sys.argv[1],'at'); f.write('{}\\n'); f.close(); time.sleep(0.3)", raw])
events([dict(kind="start"), dict(kind="connected", match_id="1"), dict(kind="connected", match_id="2")]); time.sleep(1)
out = run(feeds([1, 2])); chk("E==S, lock held, one pid, data growing -> PASS", "PREFLIGHT VERDICT: PASS" in out, out.splitlines()[-1])
out = run(feeds([1, 2, 3])); chk("expected 3 but 2 subscribed -> FAIL", "VERDICT: FAIL" in out and "subscriptions!=expected" in out)
out = run([]); chk("no live match -> WAIT, never PASS", "VERDICT: WAIT" in out)
events([dict(kind="start"), dict(kind="connected", match_id="1"), dict(kind="closed", match_id="1")]); out = run(feeds([1])); chk("closed socket not counted as subscribed -> FAIL", "VERDICT: FAIL" in out)
w.kill(); time.sleep(0.5); events([dict(kind="start"), dict(kind="connected", match_id="1")]); out = run(feeds([1])); chk("raw file not growing -> FAIL", "no-growth" in out and "VERDICT: FAIL" in out)
p2 = subprocess.run(["flock", "-n", lock, "true"]).returncode; chk("second copy refused by the lock while the first runs", p2 != 0)
os.killpg(p.pid, 9); time.sleep(0.5); out = run(feeds([1])); chk("capture not running -> single-instance FAIL", "single-instance" in out and "VERDICT: FAIL" in out)
try: os.killpg(p.pid, 9)
except Exception: pass
w.kill()
print("ALL PASS" if not fails else "FAILED %s" % fails); sys.exit(1 if fails else 0)
