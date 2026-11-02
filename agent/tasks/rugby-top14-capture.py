#!/usr/bin/env python3
"""Top 14 rugby capture (task agent/tasks/TASK-rugby-top14-capture-2026-11-07.md).

One bounded process per window A/B/C. Three concurrent async tasks:
  (a) sports WS reader        wss://sports-api.polymarket.com/ws          (filter rutopft)
  (b) CLOB market WS reader   wss://ws-subscriptions-clob.polymarket.com/ws/market (reconnect max 3)
  (c) poll loop: ESPN scoreboard every 30 s + Polymarket trades every 10 s

Outputs (append JSONL), under <root>/rugby/<window>_*.jsonl (+ _log.txt):
  sports, clob, espn, trades. Copy every 10 min to /mnt/project-files/rugby/live-2026-11/.
Stop at the window end time. Honest UA pkarbs-research/1.0 (contact nm@delphic.co).
Memory cap 600M, swap 0, timeout 10500 via the systemd-run wrapper in the task.

Serves the one question: after a score change, how many seconds later does the
Polymarket moneyline price move (measured on the streamed CLOB market channel).
Lag = distribution with n events, threshold 2c move vs last trade before score change.
No P&L. Fallback: if CLOB WS refused (403), REST book poll every 5 s, labelled
"5 s poll resolution", not a task failure.
"""
import asyncio, json, os, sys, time, urllib.request, urllib.error, websockets

UA = {"User-Agent": "pkarbs-research/1.0 (contact nm@delphic.co)"}
CONFIG_PATH = "/root/pkarbs/agent/tasks/rugby-top14-config-2026-11-07.json"
ROOT = "/root/pkarbs/rugby"            # scratch outputs
LIVE = "/mnt/project-files/rugby/live-2026-11"

SPORTS_WS = "wss://sports-api.polymarket.com/ws"
CLOB_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
ESPN = "https://site.api.espn.com/apis/site/v2/sports/rugby/270559/scoreboard"
TRADES = "https://data-api.polymarket.com/trades"
BOOK = "https://clob.polymarket.com/book"

def _w(h, *lines, append=True):
    mode = "a" if append else "w"
    with open(h, mode) as f:
        f.write("\n".join(lines) + "\n")

def _record(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj, default=str) + "\n")

def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

async def read_sports(sports_f, log):
    # primary score source; keep every rutopft message with a local receive ts
    n = 0
    try:
        async with websockets.connect(SPORTS_WS, user_agent_header=UA["User-Agent"], max_size=4*1024*1024) as ws:
            _w(log, f"{time.time():.3f} SPORTS open")
            async for raw in ws:
                s = raw.decode() if isinstance(raw, bytes) else raw
                if s == "ping":
                    await ws.send("pong"); continue
                try:
                    g = json.loads(s)
                except Exception:
                    continue
                if g.get("leagueAbbreviation") == "rutopft":
                    _record(sports_f, {"recv_ms": int(time.time()*1000), "recv_iso": datetime.utcnow().isoformat()+"Z", **g})
                    n += 1
    except Exception as e:
        _w(log, f"{time.time():.3f} SPORTS close {e!r}")
    return n

async def read_clob(clob_f, log, markets, use_rest):
    # prices primary: CLOB market WS; fallback REST book 5 s
    if use_rest:
        _w(log, f"{time.time():.3f} CLOB REST fallback (5 s poll)")
        while True:
            for m in markets:
                for tok in m.get("clobTokenIds", []):
                    try:
                        st, body = http_get(f"{BOOK}?token_id={tok}", timeout=10)
                        _record(clob_f, {"recv_ms": int(time.time()*1000), "token_id": tok, "status": st, "book": json.loads(body)})
                    except Exception as e:
                        _record(clob_f, {"recv_ms": int(time.time()*1000), "token_id": tok, "error": str(e)})
            await asyncio.sleep(5)
        return
    tokens = [t for m in markets for t in m.get("clobTokenIds", [])]
    attempts = 0
    while True:
        try:
            async with websockets.connect(CLOB_WS, user_agent_header=UA["User-Agent"], max_size=8*1024*1024) as ws:
                _w(log, f"{time.time():.3f} CLOB open")
                await ws.send(json.dumps({"assets_ids": tokens, "type": "market"}))
                async for raw in ws:
                    obj = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
                    _record(clob_f, {"recv_ms": int(time.time()*1000), "recv_iso": datetime.utcnow().isoformat()+"Z", **obj})
        except Exception as e:
            attempts += 1
            _w(log, f"{time.time():.3f} CLOB close {e!r} (attempt {attempts})")
            if attempts >= 3:
                return "REFUSED-3x"
            await asyncio.sleep(5)

async def poll_espn(espn_f, log):
    while True:
        try:
            st, body = http_get(ESPN, timeout=15)
            _record(espn_f, {"recv_ms": int(time.time()*1000), "status": st, "data": json.loads(body)})
        except Exception as e:
            _record(espn_f, {"recv_ms": int(time.time()*1000), "error": str(e)})
        await asyncio.sleep(30)

async def poll_trades(trades_f, log, markets):
    seen = set()
    while True:
        for m in markets:
            cond = m.get("conditionId")
            if not cond: continue
            try:
                st, body = http_get(f"{TRADES}?market={cond}&limit=100", timeout=12)
                rows = json.loads(body)
                for r in rows:
                    key = (r.get("transactionHash"), r.get("timestamp"), r.get("asset"))
                    if key not in seen:
                        seen.add(key)
                        _record(trades_f, {"recv_ms": int(time.time()*1000), "conditionId": cond, **r})
            except Exception as e:
                _w(log, f"{time.time():.3f} trades {cond[:12]} {e!r}")
        await asyncio.sleep(10)

async def main():
    win = sys.argv[1] if len(sys.argv) > 1 else "A"
    cfg = json.load(open(CONFIG_PATH))
    markets = cfg.get(win, [])
    kick0 = min(m.get("kickoffUTC", "2026-11-07T00:00:00Z") for m in markets)
    os.makedirs(ROOT, exist_ok=True); os.makedirs(LIVE, exist_ok=True)
    st = time.time()
    # window run length: kickoff -15min .. fulltime+10min = ~3h10; cap at window spec (~2h45) or 10500s
    run_for = 10500  # bounded
    log = f"{ROOT}/{win}_log.txt"
    _w(log, f"{time.time():.3f} WIN={win} start markets={len(markets)}", append=False)
    tasks = [
        asyncio.create_task(read_sports(f"{ROOT}/{win}_sports.jsonl", log)),
        asyncio.create_task(read_clob(f"{ROOT}/{win}_clob.jsonl", log, markets, use_rest=False)),
        asyncio.create_task(poll_espn(f"{ROOT}/{win}_espn.jsonl", log)),
        asyncio.create_task(poll_trades(f"{ROOT}/{win}_trades.jsonl", log, markets)),
    ]
    try:
        await asyncio.sleep(run_for)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    for t in tasks: t.cancel()
    _w(log, f"{time.time():.3f} END run_for={run_for}s")
    print(json.dumps({"window": win, "ran_for_s": round(time.time()-st,1)}))

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
