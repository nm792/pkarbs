#!/usr/bin/env python3
"""Offline test: the shadow logger subscribes to and stores each leg's NO token as its own book.

  T1  refresh() subscribes to both the YES and the NO token of every leg;
  T2  a NO price_change updates only the NO book, never the YES book, and never opens a run;
  T3  nocompare.jsonl has the NO token's own prices: when the NO book is planted 2c cheaper than
      1 - YES bid, the row shows mirror=False and the NO ask as stored (not 1 - YES bid);
      when NO equals the mirror, mirror=True.
Run: python3 shadow/test_no_subscription.py   (needs: pip install websockets)
"""
import asyncio, json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shadow_logger as sl  # noqa: E402

fails = []


def ok(name, cond):
    print(("PASS " if cond else "FAIL ") + name, flush=True)
    if not cond:
        fails.append(name)


def mkleg(i):
    return {"cid": f"c{i}", "yes": f"Y{i}", "no": f"N{i}", "name": f"L{i}", "fee_rate": 0.0, "fee_exp": 1,
            "rebate_rate": 0.0, "seconds_delay": 1, "tick": 0.01, "min_size": 5}


EV = {"1": {"id": "1", "title": "t", "sport": "x", "start": 0, "n_markets": 2, "complete": True,
            "closed_legs": [], "legs": [mkleg(1), mkleg(2)]}}


def book(tok, ts, bids, asks):
    return {"event_type": "book", "asset_id": tok, "timestamp": str(ts),
            "bids": [{"price": str(p), "size": "100"} for p in bids],
            "asks": [{"price": str(p), "size": "100"} for p in asks]}


async def main():
    out = tempfile.mkdtemp()
    lg = sl.Logger(out, ["sports"], 0.0, 4, 0)
    subscribed = []

    async def fake_stream(assets):
        subscribed.append(list(assets))
    lg.stream = fake_stream
    sl.discover = lambda tags, w, l: EV
    await lg.refresh()
    await asyncio.sleep(0)
    flat = [a for c in subscribed for a in c]
    ok("T1 YES and NO tokens both subscribed", set(flat) == {"Y1", "Y2", "N1", "N2"})
    ok("T1 separate Book object per token", len({id(lg.books[a]) for a in flat}) == 4)

    lg.apply(1.0, book("Y1", 10, [0.40], [0.45]))
    lg.apply(1.0, book("N1", 10, [0.55], [0.60]))
    yb_before = dict(lg.books["Y1"].bids)
    touched = lg.apply(2.0, {"event_type": "price_change", "timestamp": "11", "price_changes": [
        {"asset_id": "N1", "side": "SELL", "price": "0.58", "size": "50"}]})
    ok("T2 NO update touches only the NO book", touched == ["N1"] and lg.books["Y1"].bids == yb_before
       and lg.books["N1"].best_ask() == 0.58)
    ok("T2 NO update triggers no detector run", lg.asset_event.get("N1") is None and not lg.runs)

    lg.apply(3.0, book("Y2", 10, [0.40], [0.45]))
    lg.apply(3.0, book("N2", 10, [0.55], [0.60]))
    lg.log_no_compare(4.0)
    rows = [json.loads(x) for x in open(os.path.join(out, "nocompare.jsonl"))]
    r1 = next(r for r in rows if r["yes"] == "Y1")
    r2 = next(r for r in rows if r["yes"] == "Y2")
    ok("T3 planted NO 2c below mirror: mirror=False, stored NO ask kept",
       r1["mirror"] is False and r1["n_ask"] == 0.58 and abs((1 - r1["y_bid"]) - r1["n_ask"]) > 0.01)
    ok("T3 NO equal to mirror: mirror=True", r2["mirror"] is True)
    print("FAILED" if fails else "ALL PASS")
    return 1 if fails else 0

sys.exit(asyncio.run(main()))
