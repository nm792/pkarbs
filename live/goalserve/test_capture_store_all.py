#!/usr/bin/env python3
"""Offline test for capture_store_all.py (no network, no key, no real paths).
Rewrites the two hard-coded paths in a COPY of the source to a temp dir, then exercises store_payload.
Usage: python3 -I test_capture_store_all.py [path/to/capture_store_all.py]   -> prints PASS/FAIL lines, exit 0 only if all pass."""
import sys, os, gzip, json, tempfile, types, shutil, datetime

src_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "capture_store_all.py")
src = open(src_path).read()
tmp = tempfile.mkdtemp(prefix="gs_test_")
env = os.path.join(tmp, "goalserve.env")
open(env, "w").write("GOALSERVE_USER=u\nGOALSERVE_KEY=k\n")
real_root = "/mnt/HC_Volume_107257520/pkarbs/goalserve"
assert real_root in src and "/etc/pkarbs/goalserve.env" in src
out_dir = os.path.join(tmp, "out")
src = src.replace("/etc/pkarbs/goalserve.env", env).replace(real_root, out_dir)
mod = types.ModuleType("cap")
exec(compile(src, "cap", "exec"), mod.__dict__)

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)

check("SPORTS has NO basketball (dropped 20 Nov, NBA out)", "basketball" not in mod.SPORTS)
check("SPORTS has no volleyball (still out of scope)", "volleyball" not in mod.SPORTS)
check("STORE_SPORTS exact", tuple(mod.STORE_SPORTS) == ("esports", "tennis", "hockey_nhl"))
check("every stored sport is polled", all(s in mod.SPORTS for s in mod.STORE_SPORTS))
check("soccer and baseball are NOT stored", "soccer" not in mod.STORE_SPORTS and "baseball" not in mod.STORE_SPORTS)

hour = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H")
# The test must not depend on the free space of whatever disk the temp dir is on (the box root disk is under the 15 GB floor):
# fake 100 GB free for the normal-write checks, restore it before the floor section (which fakes 1 GB itself).
class BIG: free = 100e9; total = 1e12; used = 0
_real_du0 = shutil.disk_usage
shutil.disk_usage = lambda path: BIG
for i, s in enumerate(mod.STORE_SPORTS):
    body = json.dumps({"events": {"1": {"sport": s, "odds": [1.5 + i]}}}).encode()
    mod.store_payload(s, 1000 + i, body)
    p = os.path.join(mod.PAYDIR if s == "esports" else os.path.join(mod.OUT, s + "_payloads"), f"{s}_{hour}.jsonl.gz")
    ok = os.path.exists(p)
    if ok:
        rows = [json.loads(l) for l in gzip.open(p, "rt")]
        ok = len(rows) == 1 and rows[0]["recv_ns"] == 1000 + i and json.loads(rows[0]["body"])["events"]["1"]["sport"] == s
    check(f"{s}: one gzip row, recv_ns and body intact at {os.path.relpath(p, tmp)}", ok)
check("esports path unchanged (PAYDIR/esports_<hour>.jsonl.gz)", mod.PAYDIR.endswith("esports_payloads"))

# second write appends
mod.store_payload("tennis", 2000, b"{}")
shutil.disk_usage = _real_du0
p = os.path.join(mod.OUT, "tennis_payloads", f"tennis_{hour}.jsonl.gz")
check("tennis second write appends", len([l for l in gzip.open(p, "rt")]) == 2)

# 10 GB default floor: 12 GB free still writes (was blocked at 15 GB), 9 GB stops
class MID: free = 12e9; total = 1e12; used = 0
_d = shutil.disk_usage
shutil.disk_usage = lambda path: MID
mod.store_payload("esports", 2500, b"{}")
shutil.disk_usage = _d
pe = os.path.join(mod.PAYDIR, f"esports_{hour}.jsonl.gz")
check("floor 10 GB: write allowed at 12 GB free", len([l for l in gzip.open(pe, "rt")]) == 2)
check("floor value is 10 GB by default", mod.FLOOR_B == 10e9)
# 15 GB floor (old): stops, writes one STOP log line per sport, writes no body
class U: free = 1e9; total = 1e12; used = 0
real_du = shutil.disk_usage
shutil.disk_usage = lambda path: U
try:
    before = len([l for l in gzip.open(p, "rt")])
    mod.store_payload("tennis", 3000, b"{}")
    mod.store_payload("tennis", 3001, b"{}")
    mod.store_payload("hockey_nhl", 3002, b"{}")
finally:
    shutil.disk_usage = real_du
check("floor: no new tennis row", len([l for l in gzip.open(p, "rt")]) == before)
tl = os.path.join(mod.OUT, "tennis_payloads_STOP.log")
check("floor: tennis STOP log written once", os.path.exists(tl) and len(open(tl).read().splitlines()) == 1)
check("floor: hockey_nhl has its own STOP log", os.path.exists(os.path.join(mod.OUT, "hockey_nhl_payloads_STOP.log")))
check("floor: esports unaffected until it is called", not os.path.exists(os.path.join(mod.OUT, "esports_payloads_STOP.log")))
check("basketball store is a no-op (not in STORE_SPORTS)", not os.path.exists(os.path.join(mod.OUT, "basketball_payloads_STOP.log")))

os.makedirs(mod.OUT, exist_ok=True)
l1 = mod.acquire_lock()
check("first lock acquired", l1 is not None)
try:
    mod.acquire_lock(); refused = False
except SystemExit as e:
    refused = (e.code == 3)
check("second copy refused (exit 3) while first holds the lock", refused)
l1.close()
l3 = mod.acquire_lock()
check("lock re-acquirable after first copy exits", l3 is not None)

# trim option (GOALSERVE_STORE_SPORTS)
import subprocess
def _trim(val):
    env = dict(os.environ); env["GOALSERVE_STORE_SPORTS"] = val
    code = "import sys,types\nsrc=open(%r).read()\nsrc=src.replace('/etc/pkarbs/goalserve.env',%r).replace(%r,%r)\nm=types.ModuleType('c')\nexec(compile(src,'c','exec'),m.__dict__)\nprint(','.join(m.STORE_SPORTS))" % (src_path, env_path, real_root, out_dir)
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
env_path = env
r = _trim("esports,hockey_nhl"); check("GOALSERVE_STORE_SPORTS=esports,hockey_nhl stores only those (no tennis)", r.stdout.strip() == "esports,hockey_nhl")
r = _trim("esports,soccer"); check("unknown sport in GOALSERVE_STORE_SPORTS refuses to start", r.returncode != 0 and "subset" in (r.stderr + r.stdout))
r = _trim(""); check("unset/empty = all three stored (default unchanged)", r.stdout.strip() == "esports,tennis,hockey_nhl")

shutil.rmtree(tmp)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails))
sys.exit(1 if fails else 0)
