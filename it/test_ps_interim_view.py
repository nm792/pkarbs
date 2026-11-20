#!/usr/bin/env python3
"""Each check can fail. Run: python3 test_ps_interim_view.py <ps_interim_view.py>"""
import sys, json, subprocess, tempfile, os
S = sys.argv[1]; d = tempfile.mkdtemp(); T = 1_700_000_000
tok = "1234567890"; full = tok + "99999"
rows = [dict(match=7, series="map", t=T + i * 100, direction=1, token=tok, lead=l, team="A") for i, l in enumerate([3.0, 3.0, 5.0, -1.0])]
rows.append(dict(match=7, series="map", t=T, direction=-1, token="0000000000", lead=2.0, team="A"))
rows.append(dict(match=8, series="map", t=T + 500, direction=1, token="5555555555", lead=None, team="B"))
json.dump(dict(summary={"x": 1}, rows=rows), open(d + "/p.json", "w"))
with open(d + "/b.jsonl", "w") as f:
    for i in range(4):  # a stale snapshot, then the one that must be used (planted ask sizes 40, 30, 20)
        t = T + i * 100
        f.write(json.dumps(dict(recv_ms=(t - 5) * 1000 - 1, asset=full, asks=[{"price": 0.6, "size": 999}])) + "\n")
        f.write(json.dumps(dict(recv_ms=(t - 1) * 1000, asset=full, asks=[{"price": 0.62, "size": 30}, {"price": 0.61, "size": 40}, {"price": 0.63, "size": 20}, {"price": 0.9, "size": 1000}])) + "\n")
        f.write(json.dumps(dict(recv_ms=(t + 3) * 1000, asset=full, asks=[{"price": 0.7, "size": 5}])) + "\n")  # after the event: must be ignored
o = subprocess.run([sys.executable, "-I", S, d + "/b.jsonl", d + "/p.json"], capture_output=True, text=True).stdout
line7 = [l for l in o.splitlines() if l.startswith("7 | map")][0]
assert "| 4 | 4 | 3.0 | 0.75 |" in line7, "median/share wrong: " + line7           # leads 3,3,5,-1 -> median 3.0, share 3/4
assert "| 40.0 | 90.0" in line7, "depth must be 40 best and 90 top3 from the last snapshot before the event: " + line7  # 999 stale and 5 after-event rejected
line8 = [l for l in o.splitlines() if l.startswith("8 | map")][0]
assert "NO_BOOK_ROWS" in line8 and "| 1 | 0 | None | None |" in line8, "match with no onset/no books must say so: " + line8
assert "ALL: matches=2" in o and "median_lead_s=3.0" in o, o
print("PASS (4 checks, each able to fail)")
