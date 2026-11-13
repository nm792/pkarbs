#!/usr/bin/env python3
import sys, os, json, gzip, base64, tempfile, subprocess
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import record_charts as R
n = 0
def check(c, m):
    global n
    print(("ok   " if c else "FAIL ") + m); n += bool(c)
check(len(R.PAGES) == 5, "five pages")
check(all(u.startswith("https://") for _, u in R.PAGES), "https only")
check(len({nm for nm, _ in R.PAGES}) == 5, "unique names")
orig = R.fetch
R.fetch = lambda u: (200, b"<table>" + b"<tr><td>1</td></tr>" * 60 + b"</table>")
R.time.sleep = lambda s: None
d = tempfile.mkdtemp(); R.main(d)
f = [x for x in os.listdir(d) if x.startswith("charts_")][0]
rows = [json.loads(l) for l in gzip.open(os.path.join(d, f), "rt")]
check(len(rows) == 5 and all(r["n_rows"] == 60 for r in rows), "five rows written, 60 table rows each")
check(b"<table>" in gzip.decompress(base64.b64decode(rows[0]["html_gz_b64"])), "html round-trips")
print("%d of 5 checks pass" % n); sys.exit(0 if n == 5 else 1)
