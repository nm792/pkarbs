#!/usr/bin/env python3
"""Can-fail test for wait_listing.main: it must keep polling through errors and empty lists, detect the listing, write the detect file, and start the trades poller. Network is replaced."""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wait_listing as w, pm_gas_books as b
def t1_survives_errors_then_detects():
    calls = {"n": 0}
    def fake_tokens(slug):
        calls["n"] += 1
        if calls["n"] == 1: raise IndexError()                      # empty list
        if calls["n"] == 2: raise OSError("connection reset")        # network error must not stop the loop
        return [("t", "x|Yes")]
    b.event_tokens = fake_tokens
    b._get = lambda u, data=None: [{"markets": [{"createdAt": "2026-11-19T15:00:11Z", "startDate": "2026-11-19T15:00:26Z"}]}]
    import subprocess; subprocess.call = lambda cmd: 0; launched = []; subprocess.Popen = lambda cmd: launched.append(cmd)
    d = tempfile.mkdtemp()
    rc = w.main(["--slug", "s", "--out", d, "--wait-until", "2099-01-01T00:00:00Z"], sleep=lambda s: None)
    assert rc == 0 and calls["n"] == 3, (rc, calls)
    assert len(launched) == 1 and "pm_gas_trades.py" in launched[0][1]      # trades poller must be started with the books
    j = json.load(open(os.path.join(d, "s.listing.json"))); assert j["polls"] == 3 and j["created"] == ["2026-11-19T15:00:11Z"]
def t2_gives_up_after_deadline():
    b.event_tokens = lambda s: (_ for _ in ()).throw(IndexError())
    d = tempfile.mkdtemp(); t = [0.0]
    def now(): t[0] += 1.0; return t[0]
    rc = w.main(["--slug", "s", "--out", d, "--wait-until", "1970-01-01T00:00:05Z"], sleep=lambda s: None, now=now)
    assert rc == 1 and not os.path.exists(os.path.join(d, "s.listing.json"))
TESTS = [t1_survives_errors_then_detects, t2_gives_up_after_deadline]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
