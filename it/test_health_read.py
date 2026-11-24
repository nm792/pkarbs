"""Self test for health_read.py: a good ws folder PASSES; each of four planted faults must FAIL its own bar. Ends ALL PASS."""
import gzip, json, os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); F = []; NOW = 1795400000.0
def chk(n, c): print(("PASS " if c else "FAIL ") + n); (F.append(n) if not c else None)
def mk(d, minutes=15, gap_from=None, bad_asset=False, err=False, empty=False):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "markets.jsonl"), "w") as f:
        f.write(json.dumps({"cond": "c", "tokens": ["A", "B"], "outcomes": ["x", "y"]}) + "\n")
    with gzip.open(os.path.join(d, "books.jsonl.gz"), "wt") as f:
        for k in range(minutes * 4):
            t = NOW - minutes * 60 + 15 * k + 1
            if gap_from is not None and gap_from <= (t - (NOW - minutes * 60)) / 60 < gap_from + 3:
                continue
            f.write(json.dumps({"recv_ms": t * 1000, "asset": "Z" if (bad_asset and k == 5) else "A", "bids": [] if (empty and k == 6) else [{"price": .5, "size": 1}], "asks": [] if (empty and k == 6) else [{"price": .52, "size": 1}]}) + "\n")
    open(os.path.join(d, "recorder.log"), "w").write("start\n" + ("discover error HTTP 500\n" if err else "ws open, tokens 2\n"))
def run(d):
    p = subprocess.run([sys.executable, "-I", os.path.join(H, "health_read.py"), "ws", d, "--now", str(NOW)], capture_output=True, text=True)
    return p.returncode, p.stdout
with tempfile.TemporaryDirectory() as t:
    rc, o = run((mk(os.path.join(t, "good")), os.path.join(t, "good"))[1]); chk("good folder: HEALTH VERDICT PASS", rc == 0 and "HEALTH VERDICT PASS" in o)
    rc, o = run((mk(os.path.join(t, "gap"), gap_from=4), os.path.join(t, "gap"))[1]); chk("3-minute gap: snapshot bar FAILS", rc == 1 and "FAIL snapshots" in o)
    rc, o = run((mk(os.path.join(t, "ba"), bad_asset=True), os.path.join(t, "ba"))[1]); chk("row from an unlisted token: own-book bar FAILS", rc == 1 and "FAIL own-token" in o)
    rc, o = run((mk(os.path.join(t, "er"), err=True), os.path.join(t, "er"))[1]); chk("logged error: error bar FAILS", rc == 1 and "FAIL unhandled errors" in o)
    rc, o = run((mk(os.path.join(t, "em"), empty=True), os.path.join(t, "em"))[1]); chk("empty book: error bar FAILS", rc == 1 and "FAIL unhandled errors" in o)
with tempfile.TemporaryDirectory() as t:
    def poll(n_skip):
        with open(os.path.join(t, "goalserve_20261117.jsonl"), "w") as f:
            k = 0; x = NOW - 900
            while x < NOW:
                k += 1
                if not (n_skip and k % 4 == 0):
                    f.write(json.dumps({"esports": {"recv_ns": int(x * 1e9)}}) + "\n")
                x += 1.8
    poll(False)
    p = subprocess.run([sys.executable, "-I", os.path.join(H, "health_read.py"), "capture", t, "--now", str(NOW), "--sports", "esports"], capture_output=True, text=True)
    chk("capture: full 1.8 s cadence PASSES the poll bar", "PASS esports polls" in p.stdout)
    poll(True)
    p = subprocess.run([sys.executable, "-I", os.path.join(H, "health_read.py"), "capture", t, "--now", str(NOW), "--sports", "esports"], capture_output=True, text=True)
    chk("capture: 25% of polls missing FAILS the poll bar", "FAIL esports polls" in p.stdout and p.returncode == 1)
    def disk(*extra):
        return subprocess.run([sys.executable, "-I", os.path.join(H, "health_read.py"), "capture", t, "--now", str(NOW), "--sports", "esports", "--free-gb-test", "9.7"] + list(extra), capture_output=True, text=True).stdout
    poll(False)
    chk("floor: free 9.7 GB with --floor-gb 5 PASSES the disk bar", "PASS disk free 9.70 GB (floor 5 GB)" in disk("--floor-gb", "5"))
    chk("floor: free 9.7 GB with the default floor FAILS the disk bar", "FAIL disk free 9.70 GB (floor 10 GB)" in disk())
print("ALL PASS" if not F else "FAILED: " + ", ".join(F)); sys.exit(1 if F else 0)
