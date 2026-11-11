#!/usr/bin/env python3
"""Chess capture (task agent/tasks/TASK-chess-wcc-capture-2026-11-08.md). One process, stdlib + websockets.
  python3 chess-wcc-capture.py --check                 # listing check: open per-game chess markets + Lichess broadcast
  python3 chess-wcc-capture.py --run --hours 6 [--round ROUNDID]
Outputs (JSONL, append) under ROOT/chess/<UTC date>_*.jsonl: clob, trades, lichess_pgn, lichess_round, log, markets.
Copy to /mnt/project-files/chess/live-2026-11/ every 10 min (cron/loop in task). Honest UA pkarbs-research/1.0.
Question: after a move/eval swing, how many s later does the PM price move? Lag = real vs random-time placebo, n events."""
import asyncio, json, os, sys, time, shutil, urllib.request, urllib.parse
from datetime import datetime, timezone
UA = {"User-Agent": "pkarbs-research/1.0"}
ROOT = os.environ.get("CHESS_ROOT", "/root/pkarbs/chess"); LIVE = "/mnt/project-files/chess/live-2026-11"
GAMMA = "https://gamma-api.polymarket.com/events?series_id=11480&closed=false&limit=100"
TRADES = "https://data-api.polymarket.com/v2/trades"; CLOB_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
LI = "https://lichess.org"
def get(url, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return r.read()
def jget(url):
    try: return json.loads(get(url))
    except Exception as e: return {"error": str(e)}
def now(): return int(time.time() * 1000)
def listed():
    ev = jget(GAMMA)
    if isinstance(ev, dict): return []
    return [e for e in ev if "Titled Tuesday" not in e["title"] and " vs" in e["title"].lower()]
def find_round():
    d = jget(f"{LI}/api/broadcast/search?q=" + urllib.parse.quote("FIDE World Championship"))
    out = []
    for it in (d.get("currentPageResults") or []) if isinstance(d, dict) else []:
        out.append({"tour": it["tour"]["name"], "tour_id": it["tour"]["id"], "rounds": [(r["id"], r["name"], r.get("startsAt"), r.get("ongoing")) for r in it.get("rounds", [])]})
    return out
def check():
    L = listed()
    print("per-game chess markets open:", len(L))
    for e in L[:20]: print(" ", e["title"], e.get("startTime"), round(e.get("volume") or 0))
    for t in find_round()[:5]: print("lichess:", t["tour"], t["tour_id"], t["rounds"][:3])
def rec(path, o):
    with open(path, "a") as f: f.write(json.dumps(o, default=str) + "\n")
async def clob(path, log, tokens, end):
    import websockets
    tries = 0
    while time.time() < end and tries < 4:
        try:
            async with websockets.connect(CLOB_WS, ping_interval=None) as ws:
                await ws.send(json.dumps({"assets_ids": tokens, "type": "market"})); log("clob connected")
                last = time.time()
                while time.time() < end:
                    try: s = await asyncio.wait_for(ws.recv(), 10)
                    except asyncio.TimeoutError:
                        if time.time() - last > 8: await ws.send("PING"); last = time.time()
                        continue
                    if s == "PONG": continue
                    try: m = json.loads(s)
                    except Exception: rec(path, {"recv_ms": now(), "raw": s[:200]}); continue
                    for it in (m if isinstance(m, list) else [m]): rec(path, {"recv_ms": now(), **it})
        except Exception as e: log(f"clob err {e}"); tries += 1; await asyncio.sleep(3)
async def trades(path, log, conds, end):
    seen = set()
    while time.time() < end:
        for c in conds:
            d = await asyncio.to_thread(jget, f"{TRADES}?condition={c}&limit=100")
            for z in d.get("data", []) if isinstance(d, dict) else []:
                k = (z.get("transaction_hash"), z["timestamp"], z.get("asset"), z["size"], z["price"])
                if k not in seen: seen.add(k); rec(path, {"recv_ms": now(), "condition": c, **z})
        await asyncio.sleep(10)
async def lichess_pgn(path, log, rid, end):
    # live PGN stream: full game PGNs re-sent on every move; stamp receipt time
    import urllib.request as u
    def run():
        req = u.Request(f"{LI}/api/stream/broadcast/round/{rid}.pgn", headers=UA)
        with u.urlopen(req, timeout=60) as r:
            buf = []
            for line in r:
                if time.time() > end: break
                s = line.decode("utf8", "replace").rstrip("\n"); buf.append(s)
                if s == "" and len(buf) > 1 and buf[-2] != "" and any(b.startswith("1.") or b.endswith(("1-0", "0-1", "1/2-1/2", "*")) for b in buf[-2:]):
                    rec(path, {"recv_ms": now(), "pgn": "\n".join(buf)}); buf = []
    while time.time() < end:
        try: await asyncio.to_thread(run)
        except Exception as e: log(f"lichess stream err {e}"); await asyncio.sleep(5)
async def lichess_round(path, log, rid, end):
    while time.time() < end:
        d = await asyncio.to_thread(jget, f"{LI}/api/broadcast/-/-/{rid}")
        rec(path, {"recv_ms": now(), "round": d}); await asyncio.sleep(10)
async def main(a):
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d"); os.makedirs(ROOT, exist_ok=True)
    P = lambda n: f"{ROOT}/{day}_{n}.jsonl"
    def log(m): rec(P("log"), {"t": datetime.now(timezone.utc).isoformat(), "m": m})
    L = listed(); rec(P("markets"), {"recv_ms": now(), "events": L})
    toks = [t for e in L for m in e["markets"] for t in json.loads(m["clobTokenIds"])] if L else []
    conds = [m["conditionId"] for e in L for m in e["markets"]]
    end = time.time() + a["hours"] * 3600; rid = a.get("round")
    if not rid:
        for t in find_round():
            for r in t["rounds"]:
                if r[3]: rid = r[0]
    log(f"markets={len(L)} tokens={len(toks)} round={rid}")
    tasks = []
    if toks: tasks += [clob(P("clob"), log, toks, end), trades(P("trades"), log, conds, end)]
    if rid: tasks += [lichess_pgn(P("lichess_pgn"), log, rid, end), lichess_round(P("lichess_round"), log, rid, end)]
    async def sync():
        while time.time() < end:
            await asyncio.sleep(600); os.makedirs(LIVE, exist_ok=True)
            for n in ("clob", "trades", "lichess_pgn", "lichess_round", "markets", "log"):
                if os.path.exists(P(n)): shutil.copy(P(n), f"{LIVE}/{day}_{n}.jsonl")
    await asyncio.gather(*tasks, sync())
if __name__ == "__main__":
    if "--check" in sys.argv: check()
    else:
        a = {"hours": float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 6}
        if "--round" in sys.argv: a["round"] = sys.argv[sys.argv.index("--round") + 1]
        asyncio.run(main(a))
