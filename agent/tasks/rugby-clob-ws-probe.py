#!/usr/bin/env python3
"""Bounded CLOB market-WS probe (read-only, one process, ~150 s, stdlib + websockets).
Question: why did the capture's CLOB WS connect but deliver 0 messages (7 Nov)?
Runs 4 variants IN SEQUENCE (30 s each) against the same assets, logs every frame:
  A  default User-Agent  (what shadow_logger.py / chess capture use; they work)
  B  custom UA 'pkarbs-research/1.0' via user_agent_header (what rugby-top14-capture.py uses)
  C  default UA, subscribe with initial_dump true
  D  default UA, Yes tokens only
Assets: window C tokens (La Rochelle v Bayonne, books have 3-8 levels) so a snapshot MUST arrive.
Output: rugby/probe_clob_variants.jsonl (one line per frame) + summary line per variant on stdout.
Usage: python3 rugby-clob-ws-probe.py [config.json]   (default agent/tasks/rugby-top14-config-2026-11-07.json)
"""
import asyncio, json, sys, time
import websockets
WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
CFG = sys.argv[1] if len(sys.argv) > 1 else "/root/pkarbs/agent/tasks/rugby-top14-config-2026-11-07.json"
OUT = "/root/pkarbs/rugby/probe_clob_variants.jsonl"
SECS = 30

def tokens(yes_only=False):
    c = json.load(open(CFG))["C"]
    t = []
    for ev in c:
        for m in ev["markets"]:
            t += m["clobTokenIds"][:1] if yes_only else m["clobTokenIds"]
    return t

async def run(name, sub, **kw):
    n = 0; first = None; err = None
    try:
        async with websockets.connect(WS, ping_interval=None, open_timeout=15, **kw) as ws:
            await ws.send(json.dumps(sub))
            end = time.time() + SECS; last = 0
            while time.time() < end:
                if time.time() - last > 10:
                    await ws.send("PING"); last = time.time()
                try:
                    raw = await asyncio.wait_for(ws.recv(), 2)
                except asyncio.TimeoutError:
                    continue
                s = raw.decode() if isinstance(raw, bytes) else raw
                n += 1
                if first is None: first = s[:200]
                with open(OUT, "a") as f:
                    f.write(json.dumps({"variant": name, "t": time.time(), "len": len(s), "head": s[:300]}) + "\n")
    except Exception as e:
        err = repr(e)[:200]
    print(json.dumps({"variant": name, "frames": n, "first": first, "error": err}), flush=True)

async def main():
    t = tokens()
    await run("A_default_ua", {"assets_ids": t, "type": "market"})
    await run("B_custom_ua", {"assets_ids": t, "type": "market"}, user_agent_header="pkarbs-research/1.0")
    await run("C_initial_dump", {"assets_ids": t, "type": "market", "initial_dump": True})
    await run("D_yes_only", {"assets_ids": tokens(True), "type": "market"})
asyncio.run(main())
