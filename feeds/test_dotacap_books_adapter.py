import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from dotacap_books_adapter import convert
r = convert({"recv_ms": 1, "token": "T", "bid": 0.61, "ask": 0.62})
assert r == {"asset": "T", "recv_ms": 1, "bids": [{"price": 0.61}], "asks": [{"price": 0.62}]}
assert convert({"recv_ms": 1, "token": "T", "bid": None, "ask": 0.62}) is None   # empty side dropped, nothing inferred
assert convert({"recv_ms": 1, "bid": 0.5, "ask": 0.6}) is None                    # no token -> dropped
# mid equals what ps_lead_test computes
b = [float(x["price"]) for x in r["bids"]]; s = [float(x["price"]) for x in r["asks"]]
assert abs((max(b) + min(s)) / 2 - 0.615) < 1e-9
print("ALL PASS")
# multi-file and damaged-gz input
import tempfile, gzip, json, subprocess
d = tempfile.mkdtemp()
rows = [{"recv_ms": i, "token": "T", "bid": 0.5, "ask": 0.52} for i in range(300)]
open(d + "/a.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows[:100]))
open(d + "/b.jsonl.gz", "wb").write(gzip.compress("".join(json.dumps(r) + "\n" for r in rows[100:200]).encode()))
bad = gzip.compress("".join(json.dumps(r) + "\n" for r in rows[200:]).encode()); open(d + "/c.jsonl.gz", "wb").write(bad[: len(bad) // 2] + b"\xffXX" * 40)
out = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotacap_books_adapter.py"), d + "/a.jsonl", d + "/*.gz", d + "/o"], capture_output=True, text=True)
c = json.loads(out.stdout.strip().splitlines()[-1])
assert c["files"] == 3 and c["rows_out"] >= 200 and c["partial_files"] == 1, (c, out.stderr)
assert "PARTIAL FILE" in out.stderr
print("ALL PASS multi/gz", c)
