import aaa_page_tinyfish as T, paper_post as P, datetime as dt
SAMPLE = "Today's AAA National Average $3.6594\n\nPrice as of 11/21/26\n\n| Current Avg. | $3.6594 | $4.1987 | $4.5875 |\n| Yesterday Avg. | $3.6898 | $4.2238 |"
bad = 0
def chk(n, c):
    global bad
    print(("ok  " if c else "FAIL"), n); bad += 0 if c else 1
chk("parse sample", T.parse(SAMPLE) == ("11/21/26", 3.6594))
chk("parse junk -> None", T.parse("Access denied") == (None, None))
chk("parse date only -> None (no price)", T.parse("Price as of 11/21/26") == (None, None))
r = T.read_once("k", lambda k: (200, {"results": [{"text": SAMPLE, "latency_ms": 5}]}))
chk("good row", r["status"] == 200 and r["regular_current"] == 3.6594 and r["price_as_of"] == "11/21/26")
r = T.read_once("k", lambda k: (200, {"results": [{"text": "Just a moment..."}]}))
chk("challenge page -> not 200, no price", r["status"] != 200 and r["regular_current"] is None)
def boom(k): raise OSError("x")
r = T.read_once("k", boom); chk("exception -> 599 no price", r["status"] == 599 and r["regular_current"] is None)
D = dt.date(2026, 11, 21)
good = T.read_once("k", lambda k: (200, {"results": [{"text": SAMPLE}]})); good["recv_ns"] = 5
chk("row works with paper_post.page_change", P.page_change([good], D) == (5, 3.6594))
print("ALL PASS" if not bad else "FAILED", bad); raise SystemExit(bad)
