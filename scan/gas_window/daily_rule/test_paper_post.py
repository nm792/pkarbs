"""Can-fail tests for paper_post.py. Synthetic books/page rows in the exact recorder format (labels as in fixtures/gas20_books_two_snapshots.json)."""
import datetime as dt, json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paper_post as P, rule as R
D = dt.date(2026, 11, 21)
ET = P.ET
def ns(h, m, s=0, day=D): return int(dt.datetime(day.year, day.month, day.day, h, m, s, tzinfo=ET).timestamp() * 1e9)
LAB = {0: "Will the US national average gas price be less than $3.7000 on November 21?",
       1: "Will the US national average gas price be between $3.7000 and $3.7099 on November 21?",
       2: "Will the US national average gas price be between $3.7100 and $3.7199 on November 21?",
       3: "Will the US national average gas price be $3.7200+ on November 21?"}
def snap(t, asks):
    """asks: {(bucket, 'Yes'/'No'): [[p, size], ...]} ; unspecified tokens have no asks."""
    tok = {}
    for b, lab in LAB.items():
        for out in ("Yes", "No"):
            tok[f"t{b}{out}"] = dict(label=f"{lab}|{out}", best_ask=None, asks=asks.get((b, out), []), bids=[], ltp=None, book_ts=None)
    return dict(recv_ns=t, tok=tok)
def page(t, status=200, asof="11/21/26", val=3.705): return dict(recv_ns=t, status=status, price_as_of=asof, regular_current=val)
PRM = R.Params(fee_rate=0.05, bank=10000, rule_caps=(("yes_fav", .10), ("no_out", .05), ("post", .10)))
fails = 0
def check(name, cond):
    global fails
    print(("ok   " if cond else "FAIL ") + name); fails += 0 if cond else 1

# 1. no decision before the logged page change, even at 03:30 ET with cheap asks
cheap = {(1, "Yes"): [[0.90, 50]], (0, "No"): [[0.90, 50]]}
books = [snap(ns(3, 30), cheap), snap(ns(3, 31), cheap)]
check("no decision when no page row shows D", P.run(books, [page(ns(3, 0), asof="11/20/26")], D, PRM) == [])
# 2. 403 rows never count as a page change
check("403 rows do not trigger", P.run(books, [page(ns(3, 15, 1), status=403, val=None)], D, PRM) == [])
check("page_change ignores a 200 row with the OLD date", P.page_change([page(ns(3, 0), asof="11/20/26")], D) is None)
# 3. decision only from the snapshot at/after the change, own-token asks, correct side
books = [snap(ns(3, 10), cheap), snap(ns(3, 15, 1), cheap)]
dec = P.run(books, [page(ns(3, 15))], D, PRM)
check("only snapshots at/after the page change are used", dec and all(d["recv_ns"] >= ns(3, 15) for d in dec))
toks = {d["token"] for d in dec}
check("YES of page bucket (3.7000-3.7099 -> bucket 1) and NO of others only", toks == {"t1Yes", "t0No"})
check("price comes from the displayed ask, not a print", all(d["price"] == 0.90 for d in dec))
check("fee uses the passed rate 0.05", abs(dec[0]["fee"] - 0.05 * 0.9 * 0.1 * dec[0]["shares"]) < 1e-9)
check("all counted decisions are non-shadow post", all(d["kind"] == "post" and d["shadow"] is False for d in dec))
# 4. wrong-side token with a cheap ask is never taken
wrong = {(2, "Yes"): [[0.10, 99]], (1, "No"): [[0.10, 99]]}
check("YES of a non-page bucket / NO of the page bucket never taken", P.run([snap(ns(3, 15, 1), wrong)], [page(ns(3, 15))], D, PRM) == [])
# 5. price above the edge threshold not taken (0.995-p-fee<0.003 at p=0.993)
check("ask 0.993 is not taken (edge 0.0016 < 0.003)", P.run([snap(ns(3, 15, 1), {(1, "Yes"): [[0.993, 50]]})], [page(ns(3, 15))], D, PRM) == [])
# 6. one decision, one snapshot: 5 identical snapshots in the window give at most the displayed 5 shares
many = [snap(ns(3, 15, s), {(1, "Yes"): [[0.90, 5]]}) for s in range(5)]
dec = P.run(many, [page(ns(3, 15))], D, PRM)
check("same displayed 5 shares seen 5 times -> at most 5 shares", sum(d["shares"] for d in dec) <= 5 + 1e-9 and sum(d["shares"] for d in dec) > 0)
# 7. the latest book at decision time decides the size
grow = [snap(ns(3, 15, 0), {(1, "Yes"): [[0.90, 5]]}), snap(ns(3, 15, 1), {(1, "Yes"): [[0.90, 8]]})]
check("size 5 then 8: only the latest book counts, total 8 not 13", abs(sum(d["shares"] for d in P.run(grow, [page(ns(3, 15))], D, PRM)) - 8) < 1e-9)
# 8. page value outside every bucket (cannot happen live) -> no decision, no crash
check("value outside buckets -> no decision", P.run(books, [page(ns(3, 15), val=9.99)], D, PRM) != None)
# 9. clock_end cuts off
check("no snapshot after clock_end used", P.run(books, [page(ns(3, 15))], D, PRM, clock_end=ns(3, 12)) == [])
# 10. shadow rules before 03:00 ET are logged but never counted as post
pre = [snap(ns(1, 0), {(1, "Yes"): [[0.40, 30]], (3, "No"): [[0.90, 30]]})]
sh = P.run(pre, [], D, PRM, nowcast=(3.705, 0.004))
check("pre-page shadow decisions exist and are all shadow", sh and all(d["shadow"] for d in sh))
check("no shadow decision without --nowcast", P.run(pre, [], D, PRM) == [])
# 11. settle from gamma outcomePrices
dec = P.run([snap(ns(3, 15, 1), cheap)], [page(ns(3, 15))], D, PRM)
gm = [dict(clobTokenIds=json.dumps(["t1Yes", "t1No"]), outcomes='["Yes","No"]', outcomePrices='["1","0"]'),
      dict(clobTokenIds=json.dumps(["t0Yes", "t0No"]), outcomes='["Yes","No"]', outcomePrices='["0","1"]')]
rows, un = P.settle(dec, gm)
check("both fills win and pnl = shares*(1-p)-fee", un == 0 and all(r["won"] for r in rows) and all(abs(r["pnl"] - (r["shares"] * 0.1 - r["fee"])) < 1e-9 for r in rows))
gm_lose = [dict(clobTokenIds=json.dumps(["t1Yes", "t1No"]), outcomes='["Yes","No"]', outcomePrices='["0","1"]'),
           dict(clobTokenIds=json.dumps(["t0Yes", "t0No"]), outcomes='["Yes","No"]', outcomePrices='["1","0"]')]
rows, un = P.settle(dec, gm_lose)
check("losing fills lose cost+fee", all(abs(r["pnl"] + r["cost"] + r["fee"]) < 1e-9 for r in rows))
rows, un = P.settle(dec, [dict(clobTokenIds=json.dumps(["t1Yes", "t1No"]), outcomes='["Yes","No"]', outcomePrices='["0.62","0.38"]')])
check("unresolved/unknown tokens give pnl None and are counted", un == len(dec) and all(r["pnl"] is None for r in rows))
check("day_pnl ignores unresolved", P.day_pnl(rows) == 0)
# 12. report: planted constant +300/day clears 200, planted +100/day does not
r = P.report([300.0] * 20); check("CI: constant 300 clears $200", r["clears_target"] and r["mean"] == 300)
r = P.report([100.0] * 20); check("CI: constant 100 does NOT clear $200", not r["clears_target"])
r = P.report([2.63, -5, 40, 0, 1, 3, 2, 12, -3, 4] * 3); check("CI: gas-like $/day does NOT clear $200", not r["clears_target"])
# 13. sanity flags
with tempfile.TemporaryDirectory() as td:
    pg, bk, dc = (os.path.join(td, n) for n in ("page.jsonl", "books.jsonl", "dec.jsonl"))
    now = ns(2, 50)
    open(pg, "w").write(json.dumps(page(now - 10 * 10**9, status=403, val=None)) + "\n")
    open(bk, "w").write(json.dumps(snap(now - 5 * 10**9, {})) + "\n" + '{"recv_ns": 1, "tok"')   # half-written last line
    open(dc, "w").write("")
    s = P.sanity(pg, bk, dc, now)
    check("sanity: 403-only page log is NOT ok (fresh but no good fetch)", s["page_fresh"] and s["page_good_fetches"] == 0 and not s["ok"])
    open(pg, "a").write(json.dumps(page(now - 3 * 10**9)) + "\n")
    s = P.sanity(pg, bk, dc, now); check("sanity: good page+fresh books+decisions file -> ok", s["ok"])
    s = P.sanity(pg, bk, dc, now + 600 * 10**9); check("sanity: stale logs -> not ok", not s["ok"])
    s = P.sanity(pg, bk, os.path.join(td, "none"), now); check("sanity: missing decisions file -> not ok", not s["ok"])
    # main end to end
    out = os.path.join(td, "o.jsonl"); open(bk, "w").write("\n".join(json.dumps(x) for x in [snap(ns(3, 15, 1), cheap)]) + "\n")
    open(pg, "w").write(json.dumps(page(ns(3, 15))) + "\n")
    P.main(["--books", bk, "--page", pg, "--date", "2026-11-21", "--out", out]); o = [json.loads(l) for l in open(out)]
    check("main writes decisions at fee 0.05 default", o and abs(o[0]["fee"] - 0.05 * 0.9 * 0.1 * o[0]["shares"]) < 1e-9)
# 14. R-003/R-006: the fill uses ONLY the latest own-token book at or before decision time + 2 s latency
late = [snap(ns(3, 15, 1), {(1, "Yes"): [[0.995, 50]]}), snap(ns(3, 16, 30), {(1, "Yes"): [[0.90, 50]]})]
check("cheap ask first shown 90 s after the page change is rejected", P.run(late, [page(ns(3, 15))], D, PRM) == [])
soon = [snap(ns(3, 15, 1), {(1, "Yes"): [[0.995, 50]]}), snap(ns(3, 15, 4), {(1, "Yes"): [[0.90, 50]]})]
check("cheap ask shown 4 s after the change is outside the 2 s latency: rejected", P.run(soon, [page(ns(3, 15))], D, PRM) == [])
check("same 4 s book is used if the assumed latency is 5 s (parameter is live)", len(P.run(soon, [page(ns(3, 15))], D, PRM, latency_s=5)) == 1)
sup = [snap(ns(3, 15, 0), {(1, "Yes"): [[0.90, 50]]}), snap(ns(3, 15, 1), {(1, "Yes"): [[0.995, 50]]})]
check("a cheap ask in an earlier book superseded by a newer one at decision time is rejected", P.run(sup, [page(ns(3, 15))], D, PRM) == [])
okb = [snap(ns(3, 15, 1), {(1, "Yes"): [[0.90, 50]]})]
check("cheap ask in the latest book at decision time + 1 s is filled", len(P.run(okb, [page(ns(3, 15))], D, PRM)) == 1)
pre = [snap(ns(3, 14, 59), {(1, "Yes"): [[0.90, 50]]}), snap(ns(3, 15, 9), {(1, "Yes"): [[0.99, 50]]})]
check("latest book at or before the decision (taken 1 s before the page read) is the fill book", len(P.run(pre, [page(ns(3, 15))], D, PRM)) == 1)
stale = [snap(ns(3, 10), {(1, "Yes"): [[0.90, 50]]})]
check("a book 5 minutes older than the decision is not a decision-time book", P.run(stale, [page(ns(3, 15))], D, PRM) == [])
print("FAILED" if fails else "ALL PASS", fails); sys.exit(1 if fails else 0)
