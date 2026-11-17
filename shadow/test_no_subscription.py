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
    ok("T2 NO update re-checks the event, but opens no run without an edge", lg.asset_event.get("N1") == "1" and not lg.runs)

    lg.apply(3.0, book("Y2", 10, [0.40], [0.45]))
    lg.apply(3.0, book("N2", 10, [0.55], [0.60]))
    lg.log_no_compare(4.0)
    rows = [json.loads(x) for x in open(os.path.join(out, "nocompare.jsonl"))]
    r1 = next(r for r in rows if r["yes"] == "Y1")
    r2 = next(r for r in rows if r["yes"] == "Y2")
    ok("T3 planted NO 2c below mirror: mirror=False, stored NO ask kept",
       r1["mirror"] is False and r1["n_ask"] == 0.58 and abs((1 - r1["y_bid"]) - r1["n_ask"]) > 0.01)
    ok("T3 NO equal to mirror: mirror=True", r2["mirror"] is True)
    # T4 planted edge on the NO tokens' own asks: n = 2 legs, NO set pays 1, own asks 0.40 + 0.40 -> edge 0.20
    lg2 = sl.Logger(tempfile.mkdtemp(), ["sports"], 0.0, 4, 0)
    lg2.stream = fake_stream
    await lg2.refresh()
    for tok, bid, ask in (("Y1", 0.40, 0.45), ("Y2", 0.40, 0.45)):
        lg2.apply(1.0, book(tok, 10, [bid], [ask]))
    lg2.apply(1.0, book("N1", 10, [0.55], [0.40]))
    lg2.apply(1.0, book("N2", 10, [0.55], [0.40]))
    lg2.check(1.0, "1")
    run = lg2.runs.get(("1", "no"))
    ok("T4 planted NO own-ask edge opens a NO run priced at the NO asks",
       run is not None and run["assets"] == ["N1", "N2"] and run["quotes0"] == [[0.40, 100.0], [0.40, 100.0]]
       and run.get("own_book") is True and abs(run["px0"] - 0.80) < 1e-9)
    # T5 mirror-only edge: YES bids 0.60 + 0.60 would make a mirrored NO set cost 0.80, but the NO tokens'
    # own asks are 0.55 + 0.55 = 1.10 -> NO run must NOT open (a derived price would have opened one)
    lg3 = sl.Logger(tempfile.mkdtemp(), ["sports"], 0.0, 4, 0)
    lg3.stream = fake_stream
    await lg3.refresh()
    for tok in ("Y1", "Y2"):
        lg3.apply(1.0, book(tok, 10, [0.60], [0.65]))
    lg3.apply(1.0, book("N1", 10, [0.30], [0.55]))
    lg3.apply(1.0, book("N2", 10, [0.30], [0.55]))
    lg3.check(1.0, "1")
    ok("T5 YES-mirror edge with no NO-ask edge opens no NO run", ("1", "no") not in lg3.runs)
    # T6 sim: an own_book NO run is filled from the NO tokens' own asks (hand value 100 x (1 - 0.80) = 20);
    # a legacy NO run (no own_book flag) is skipped and counted, never priced from the YES mirror
    import gzip, subprocess
    d = tempfile.mkdtemp()
    legs = [dict(mkleg(1), fee_rate=0.0), dict(mkleg(2), fee_rate=0.0)]
    json.dump({"t": 0, "id": "1", "title": "t", "complete": True, "n_markets": 2, "legs": legs}, open(os.path.join(d, "events.jsonl"), "w"))
    T0 = 1792800000.0
    with gzip.open(os.path.join(d, "raw-2026102500.jsonl.gz"), "wt") as f:
        f.write(json.dumps({"r": T0 - 1, "m": [book("Y1", 1, [0.30], [0.70]), book("Y2", 1, [0.30], [0.70]),
                                                book("N1", 1, [0.30], [0.40]), book("N2", 1, [0.30], [0.40])]}) + "\n")
        f.write(json.dumps({"r": T0 + 5, "m": book("N1", 2, [0.30], [0.40])}) + "\n")
    base = {"event": "1", "side": "no", "title": "t", "t0": T0, "t1": T0 + 1, "dur": 1, "cost0": 0.80, "px0": 0.80,
            "fee0": 0.0, "edge_full_fee": 1, "payout": 1, "size0": 100.0, "quotes0": [[0.40, 100.0], [0.40, 100.0]]}
    with open(os.path.join(d, "runs.jsonl"), "w") as f:
        f.write(json.dumps(dict(base, assets=["N1", "N2"], own_book=True)) + "\n")
        f.write(json.dumps(dict(base, assets=["Y1", "Y2"], t0=T0 + 50)) + "\n")
    out = subprocess.run([sys.executable, os.path.join(HERE, "shadow_sim.py"), "--data", d, "--delays", "0"],
                         capture_output=True, text=True).stdout
    ok("T6 own_book NO run filled from NO asks: pnl 20.00", "side=no delay=     0" in out and "sim=$    20.00" in out)
    ok("T6 legacy NO run skipped and counted", "skipped 1 legacy NO runs" in out)
    print(out[-600:] if fails else "")
    print("FAILED" if fails else "ALL PASS")
    return 1 if fails else 0

sys.exit(asyncio.run(main()))
