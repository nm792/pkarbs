import sys, os, gzip, io, json, tempfile, zlib
sys.path.insert(0, os.path.dirname(__file__))
import ps_lead_test as T, ps_lead_audit as A
d = tempfile.mkdtemp(); p = os.path.join(d, "x.jsonl.gz")
good = b"".join((json.dumps({"i": i}) + "\n").encode() for i in range(2000))
raw = gzip.compress(good)
open(p, "wb").write(raw[: len(raw) // 2] + b"\xff\xfe\x00garbage" * 50)   # damaged mid-stream
for mod in (T, A):
    rows = list(mod.lines(p))   # must not raise
    assert len(rows) < 2000
print("ALL PASS (rows kept before damage:", len(list(T.lines(p))), ")")
