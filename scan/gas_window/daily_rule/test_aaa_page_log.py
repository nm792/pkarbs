import json, os, sys, tempfile, urllib.error, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aaa_page_log as A
fails = 0
def check(n, c):
    global fails; print(("ok   " if c else "FAIL ") + n); fails += 0 if c else 1
HTML = "<html>Price as of 11/21/26 <b>Regular</b> Current Avg. $3.705 Yesterday Avg. $3.711 Week Ago Avg. $3.720</html>"
r = A.poll_once(A.URL, lambda u: (200, {"Date": "x"}, HTML.encode()), lambda: 5)
check("parses a good page", r["status"] == 200 and r["price_as_of"] == "11/21/26" and r["regular_current"] == 3.705 and r["recv_ns"] == 5)
r = A.poll_once(A.URL, lambda u: (403, {"cf-ray": "abc-IAD"}, b"<html>Attention Required! Cloudflare Current Avg. $9.999 Price as of 11/21/26</html>"), lambda: 6)
check("403 row is logged with status+cf-ray and NEVER carries a price", r["status"] == 403 and r["headers"]["cf-ray"] == "abc-IAD" and r["regular_current"] is None and r["price_as_of"] is None)
def boom(u): raise TimeoutError("t")
r = A.poll_once(A.URL, boom, lambda: 7)
check("exception becomes a row with status None", r["status"] is None and "error" in r)
def httperr(u):
    raise urllib.error.HTTPError(u, 403, "Forbidden", {"cf-ray": "z"}, io.BytesIO(b"blocked"))
orig = A.urllib.request.urlopen
A.urllib.request.urlopen = lambda *a, **k: httperr("u")
st, hd, body = A.fetch("http://x"); A.urllib.request.urlopen = orig
check("fetch() returns HTTPError status instead of raising", st == 403 and body == b"blocked")
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "page.jsonl"); clock = [100.0]
    n = A.run(p, 1e12, interval=1, fetch_fn=lambda u: (403, {}, b"x"), sleep=lambda s: clock.__setitem__(0, clock[0] + s), now=lambda: clock[0], max_polls=4)
    rows = [json.loads(l) for l in open(p)]
    check("run writes one row per poll even when every poll is 403", n == 4 and len(rows) == 4 and all(x["status"] == 403 for x in rows))
    import paper_post as P, datetime as dt
    check("paper_post.page_change ignores them", P.page_change(rows, dt.date(2026, 11, 21)) is None)
print("FAILED" if fails else "ALL PASS", fails); sys.exit(1 if fails else 0)
