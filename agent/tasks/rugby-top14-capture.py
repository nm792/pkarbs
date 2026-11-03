#!/usr/bin/env python3
"""Top 14 rugby capture (task agent/tasks/TASK-rugby-top14-capture-2026-11-07.md).

One bounded process per window A/B/C. Four concurrent async tasks:
  (a) sports WS reader        wss://sports-api.polymarket.com/ws          (filter rutopft)
  (b) CLOB market WS reader   wss://ws-subscriptions-clob.polymarket.com/ws/market (reconnect max 3)
  (c) poll loop: ESPN scoreboard every 30 s + Polymarket trades every 10 s
  (d) Rugbyrama match widget (extra score clock) every 15 s

Outputs (append JSONL), under <root>/rugby/<window>_*.jsonl (+ _log.txt):
  sports, clob, espn, trades, rugbyrama, rugbyrama_events. Copy every 10 min to /mnt/project-files/rugby/live-2026-11/.
Stop at the window end time. Honest UA pkarbs-research/1.0 (contact nm@delphic.co).
Memory cap 600M, swap 0, timeout 18000 (AB) via the systemd-run wrapper in the task.

Serves the one question: after a score change, how many seconds later does the
Polymarket moneyline price move (measured on the streamed CLOB market channel).
Lag = distribution with n events, threshold 2c move vs last trade before score change.
No P&L. Fallback: if CLOB WS refused (403), REST book poll every 5 s, labelled
"5 s poll resolution", not a task failure.
"""
import asyncio, json, os, re, sys, time, html, urllib.request, urllib.error, websockets
from datetime import datetime

UA = {"User-Agent": "pkarbs-research/1.0 (contact nm@delphic.co)"}
CONFIG_PATH = "/root/pkarbs/agent/tasks/rugby-top14-config-2026-11-07.json"
ROOT = "/root/pkarbs/rugby"            # scratch outputs
LIVE = "/mnt/project-files/rugby/live-2026-11"

SPORTS_WS = "wss://sports-api.polymarket.com/ws"
CLOB_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
ESPN = "https://site.api.espn.com/apis/site/v2/sports/rugby/270559/scoreboard"
TRADES = "https://data-api.polymarket.com/v2/trades"  # v1 /trades retired 3 Nov 2026
BOOK = "https://clob.polymarket.com/book"
RUGBYRAMA = "https://www.rugbyrama.fr/idalgo/cache/page/rugby_widget_match.php"
RR_MATCHES = {
    "AB": ["61243", "61242", "61237", "61239", "61240", "61241"],
    "D": ["61243"],
    "C": ["61238"],
    "A": ["61242"],
    "B": ["61242"],
}


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
                st, body = http_get(f"{TRADES}?condition={cond}&limit=100", timeout=12)
                rows = json.loads(body).get("data", [])  # v2: {data, pagination}, newest first
                for r in rows:
                    key = (r.get("transaction_hash"), r.get("timestamp"), r.get("token_id"), r.get("size"), r.get("price"))
                    if key not in seen:
                        seen.add(key)
                        _record(trades_f, {"recv_ms": int(time.time()*1000), "conditionId": cond, **r})
            except Exception as e:
                _w(log, f"{time.time():.3f} trades {cond[:12]} {e!r}")
        await asyncio.sleep(10)

def _parse_rugbyrama(body):
    """Return (score, events) from the Rugbyrama match widget HTML. events: list of (minute, text)."""
    s = body.decode("utf-8", errors="replace")
    score = ""
    sm = re.search(r">(\d+)\s*-\s*(\d+)<", s)
    if sm:
        score = f"{sm.group(1)} - {sm.group(2)}"
    events = []
    for li in re.finditer(r'<li class="li_idalgo_content_match_comment[^>]*>.*?</li>', s, re.S):
        lc = li.group(0)
        if "content_category" in lc:
            continue
        mm = re.search(r"span_idalgo_content_match_comment_info_minute[^>]*>([^<]*)<", lc)
        tx = re.sub(r"<[^>]+>", " ", lc)
        tx = re.sub(r"\s+", " ", html.unescape(tx)).strip()
        if not mm or not tx:
            continue
        events.append((mm.group(1).strip(), tx))
    return score, events

async def poll_rugbyrama(rr_f, ev_f, log, rr_ids):
    """Extra score clock: Rugbyrama match widget, 15 s poll, honest UA. First-seen, not broadcast."""
    seen = {}
    consec = {rid: 0 for rid in rr_ids}
    while True:
        for rid in rr_ids:
            now_ms = int(time.time() * 1000)
            try:
                st, body = http_get(f"{RUGBYRAMA}?refMatch={rid}", timeout=15)
                score, events = _parse_rugbyrama(body)
                _record(rr_f, {"recv_ms": now_ms, "recv_iso": datetime.utcnow().isoformat() + "Z",
                               "refMatch": rid, "status": st, "size": len(body), "score": score,
                               "events_n": len(events), "body": body.decode("utf-8", errors="replace")})
                consec[rid] = 0
                for minute, txt in events:
                    key = (rid, minute, txt)
                    if key not in seen:
                        seen[key] = now_ms
                        _record(ev_f, {"recv_ms": now_ms, "recv_iso": datetime.utcnow().isoformat() + "Z",
                                       "refMatch": rid, "minute": minute, "text": txt, "score": score})
            except Exception as e:
                consec[rid] = consec.get(rid, 0) + 1
                _record(rr_f, {"recv_ms": now_ms, "recv_iso": datetime.utcnow().isoformat() + "Z",
                               "refMatch": rid, "error": str(e), "consec_fail": consec[rid]})
                if consec[rid] >= 3:
                    _w(log, f"{time.time():.3f} RR {rid} FAILED (3 consecutive errors) -- report only")
        await asyncio.sleep(15)

async def main():
    win = sys.argv[1] if len(sys.argv) > 1 else "A"
    cfg = json.load(open(CONFIG_PATH))
    markets = cfg.get(win, [])
    kick0 = min(m.get("kickoffUTC", "2026-11-07T00:00:00Z") for m in markets)
    os.makedirs(ROOT, exist_ok=True); os.makedirs(LIVE, exist_ok=True)
    st = time.time()
    # window run length: per-window (AB merged to 5h / 18000s per Nick 15:50Z; D,C ~2h45 bounded)
    run_for = 18000 if win == "AB" else 10500
    log = f"{ROOT}/{win}_log.txt"
    _w(log, f"{time.time():.3f} WIN={win} start markets={len(markets)}", append=False)
    rr_ids = RR_MATCHES.get(win, [])
    tasks = [
        asyncio.create_task(read_sports(f"{ROOT}/{win}_sports.jsonl", log)),
        asyncio.create_task(read_clob(f"{ROOT}/{win}_clob.jsonl", log, markets, use_rest=False)),
        asyncio.create_task(poll_espn(f"{ROOT}/{win}_espn.jsonl", log)),
        asyncio.create_task(poll_trades(f"{ROOT}/{win}_trades.jsonl", log, markets)),
    ]
    if rr_ids:
        tasks.append(asyncio.create_task(poll_rugbyrama(f"{ROOT}/{win}_rugbyrama.jsonl",
                                                       f"{ROOT}/{win}_rugbyrama_events.jsonl", log, rr_ids)))
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
