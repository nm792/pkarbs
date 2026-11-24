#!/usr/bin/env python3
"""Smoke test for ll_capture_v4.py (no network, no token, writes only to a temp dir). Usage: python3 -I test_ll_capture_v4_smoke.py ll_capture_v4.py"""
import sys, types, os, asyncio, time, gzip, json, importlib.util, tempfile
import builtins, io
_open = builtins.open
def fake_open(p, *a, **k):   # never touches the real token files: the env paths are served from memory during import only
    if str(p) in ("/etc/pkarbs/pandascore.env", "/root/API_KEYS/pandascore/.env"):
        return io.StringIO("PANDASCORE_TOKEN=dummy\n")
    return _open(p, *a, **k)
builtins.open = fake_open
_mk = os.makedirs
os.makedirs = lambda p, exist_ok=False: None if str(p).startswith("/mnt/HC_Volume") else _mk(p, exist_ok=exist_ok)
sys.modules["websockets"] = types.ModuleType("websockets")
spec = importlib.util.spec_from_file_location("cap", sys.argv[1]); cap = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap)
builtins.open = _open; os.makedirs = _mk
td = tempfile.mkdtemp(); cap.OUT = td; cap.EV = os.path.join(td, "events.jsonl.gz"); cap.free_ok = lambda: True
cap.HEARTBEAT_S, cap.IDLE_CLOSE_S = 1, 1
calls = {"n": 0}
def fake_http(url, bearer=True, timeout=20):
    calls["n"] += 1
    if calls["n"] == 2: time.sleep(3)            # a slow discovery call
    return [{"match": {"id": 7, "videogame": {"slug": "cs-go"}, "opponents": []}, "endpoint": {"url": "wss://x", "opens_at": "2099-01-01T00:00:00Z"}}]
cap.http_get = fake_http
cap.DISCOVERY_TIMEOUT_S = 2
async def fake_sleep_main():
    orig = real_sleep
    t = asyncio.create_task(cap.main())
    cap.HW.write({"x": 1}); assert cap.HW.h is not None
    await orig(5); hb = cap.state.get("hb_task"); print("hb", hb, hb.done() and hb.exception()); print("main", t.done() and t.exception()); t.cancel()
real_sleep = asyncio.sleep
async def short_sleep(s, *a): await real_sleep(min(s, 0.5))
cap.asyncio.sleep = short_sleep
asyncio.run(fake_sleep_main())
ev = [json.loads(l) for l in gzip.open(cap.EV, "rt")]
kinds = [e["kind"] for e in ev]; print(kinds)
assert "heartbeat" in kinds and "discovery_summary" in kinds and "hour_file_closed_idle" in kinds and "discovery_timeout" in kinds, kinds
raw = [f for f in os.listdir(td) if f.startswith("pandascore_")]; assert raw
for f in raw:
    list(gzip.open(os.path.join(td, f), "rt"))     # must read to the end without EOFError (file was closed)
print("SMOKE PASS")
