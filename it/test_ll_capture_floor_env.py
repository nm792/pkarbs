#!/usr/bin/env python3
# Each check can fail. Run: python3 test_ll_capture_floor_env.py <orig_ll_capture.py> <ll_capture_floor_env.py>
import sys, os, difflib, py_compile, re
a, b = sys.argv[1:3]
A, B = open(a).read().splitlines(), open(b).read().splitlines()
d = [l for l in difflib.unified_diff(A, B, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
assert len(d) == 2 and d[0].startswith("-FLOOR = 15e9") and d[1].startswith("+FLOOR = float(os.environ"), f"diff is not exactly the FLOOR line: {d}"
py_compile.compile(b, doraise=True)
line = [l for l in B if l.startswith("FLOOR = ")][0]
def floor(env):
    os.environ.pop("PS_FLOOR_GB", None)
    if env is not None: os.environ["PS_FLOOR_GB"] = env
    g = {"os": os}; exec(line, g); return g["FLOOR"]
assert floor(None) == 15e9, "default must stay 15 GB"
assert floor("10") == 10e9, "env 10 must give 10 GB"
assert floor("10") != floor(None), "override must change the floor"
print("PASS (4 checks, each able to fail)")
