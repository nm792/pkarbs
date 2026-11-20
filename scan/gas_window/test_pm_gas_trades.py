#!/usr/bin/env python3
"""Can-fail tests for pm_gas_trades: dedupe across polls, keep new rows, survive a failing poll, write recv_ns."""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pm_gas_trades as t
def row(h, p, s, ts=1): return {"transaction_hash": h, "token_id": "T", "price": p, "size": s, "timestamp": ts, "outcome": "Yes", "side": "BUY", "proxy_wallet": "w"}
def t1_dedupe_and_new_rows():
    seen = set(); a = t.new_rows([row("h1", .7, 20), row("h2", .85, 80)], seen); assert len(a) == 2
    b = t.new_rows([row("h1", .7, 20), row("h3", .85, 5)], seen); assert [r["transaction_hash"] for r in b] == ["h3"]
    assert len(t.new_rows([row("h1", .7, 20, ts=2)], seen)) == 1          # same tx, other timestamp is a different row
def t2_survives_failed_poll_and_writes_file():
    calls = {"n": 0}
    def fake(c):
        calls["n"] += 1
        if calls["n"] == 1: raise OSError("reset")
        return [row("h1", .7, 20), row("h2", .85, 80)]
    d = tempfile.mkdtemp(); clock = [0.0]
    def now(): clock[0] += 0.4; return clock[0]
    n, err = t.run("s", d, 1e9, interval=1.0, max_seconds=3, fetch_fn=fake, cids=["c1"], sleep=lambda s: None, now=now)
    lines = [json.loads(l) for l in open(os.path.join(d, "s.trades.jsonl"))]
    assert err == 1 and n == 2 and len(lines) == 2 and all("recv_ns" in l for l in lines), (n, err, lines)
TESTS = [t1_dedupe_and_new_rows, t2_survives_failed_poll_and_writes_file]
if __name__ == "__main__":
    ok = 0
    for x in TESTS:
        try: x(); ok += 1; print("PASS", x.__name__)
        except AssertionError as e: print("FAIL", x.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
