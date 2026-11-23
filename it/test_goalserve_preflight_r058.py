import os, sys, json, time, gzip, tempfile, subprocess
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, "goalserve_preflight_r058.py"); F = []
def chk(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: F.append(n)
def run(d, *x):
    r = subprocess.run([sys.executable, "-I", P, d, "/nonexistent/x.py", "--skip-second", "--freegb", "0", "--pids", "123"] + list(x), capture_output=True, text=True); return r.returncode, r.stdout
def mk(rows=40, err=False, stale=False):
    d = tempfile.mkdtemp(); now = time.time()
    with open(os.path.join(d, "goalserve_20261117.jsonl"), "w") as f:
        for i in range(rows):
            t = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now - i)) + ".000+00:00"
            f.write(json.dumps({"t": t, "esports": {"err": "x"} if (err and i == 3) else {"recv_ns": 1}}) + "\n")
    for s in ("esports", "tennis", "hockey_nhl"):
        os.makedirs(os.path.join(d, s + "_payloads")); p = os.path.join(d, s + "_payloads", s + "_2026112303.jsonl.gz"); gzip.open(p, "wt").write("{}\n")
        if stale: os.utime(p, (now - 900, now - 900))
    return d
rc, out = run(mk()); chk("healthy dir PASSES", rc == 0 and "VERDICT: PASS" in out)
rc, out = run(mk(rows=5)); chk("too few polls FAILS", rc == 1 and "FAIL poll log" in out)
rc, out = run(mk(err=True)); chk("err row FAILS", rc == 1 and "err entries" in out)
rc, out = run(mk(stale=True)); chk("stale payload files FAIL", rc == 1 and "newest file" in out)
r = subprocess.run([sys.executable, "-I", P, mk(), "/x.py", "--skip-second", "--freegb", "0", "--pids", "1,2"], capture_output=True, text=True); chk("two writers FAIL", r.returncode == 1 and "single writer" in r.stdout)
r = subprocess.run([sys.executable, "-I", P, mk(), "/x.py", "--skip-second", "--freegb", "99999", "--pids", "1"], capture_output=True, text=True); chk("low disk FAILS", r.returncode == 1)
# lock-holder fail-fast (R-067): planted cases that can fail
import fcntl
stub = os.path.join(tempfile.mkdtemp(), "stub.py"); open(stub, "w").write("import sys; sys.exit(3)\n")
def run2(d, st):
    t0 = time.time(); r = subprocess.run([sys.executable, "-I", P, d, st, "--freegb", "0", "--pids", "123"], capture_output=True, text=True); return r.returncode, r.stdout, time.time() - t0
d = mk(); rc, out, dt = run2(d, stub)
chk("no live lock holder FAILS fast (<5 s, message)", rc == 1 and "no live lock holder" in out and dt < 5)
d = mk(); fd = open(os.path.join(d, ".capture.lock"), "a"); fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
rc, out, dt = run2(d, stub); chk("held lock + second copy exit 3 PASSES", rc == 0 and "second copy refused" in out and "PASS second copy" in out)
slow = os.path.join(tempfile.mkdtemp(), "slow.py"); open(slow, "w").write("import time; time.sleep(60)\n")
rc, out, dt = run2(d, slow); chk("second copy that does not refuse FAILS (<15 s)", rc == 1 and "FAIL second copy" in out and dt < 15)
print("ALL PASS" if not F else "FAILED: " + "; ".join(F)); sys.exit(1 if F else 0)
