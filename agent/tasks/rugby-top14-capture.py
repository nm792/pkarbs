#!/usr/bin/env python3
"""Top 14 rugby capture (task agent/tasks/TASK-rugby-top14-capture-2026-11-07.md).

One bounded process per window A/B/C. Four concurrent async tasks:
  (a) sports WS reader        wss://sports-api.polymarket.com/ws          (filter rutopft)
  (b) CLOB market WS reader   wss://ws-subscriptions-clob.polymarket.com/ws/market (reconnect max 3)
  (c) poll loop: ESPN scoreboard every 30 s + Polymarket trades every 10 s
  (d) Rugbyrama match widget (extra score clock) every 15 s

Outputs (append JSONL), under <root>/rugby/<window>_*.jsonl (+ _log.txt):
  sports, clob, espn, trades, rugbyrama, rugbyrama_events. Copy every 10 min to /mnt/project-files/rugby/live-2026-11/.
Stop at the window end time. Honest UA pkarbs-research/1.0.
Memory cap 600M, swap 0, timeout 18000 (AB) via the systemd-run wrapper in the task.

Serves the one question: after a score change, how many seconds later does the
Polymarket moneyline price move (measured on the streamed CLOB market channel).
Lag = distribution with n events, threshold 2c move vs last trade before score change.
No P&L. Fallback: if CLOB WS refused (403), REST book poll every 5 s, labelled
"5 s poll resolution", not a task failure.
"""
import asyncio, json, os, re, sys, time, html, urllib.request, urllib.error, websockets
from datetime import datetime

UA = {"User-Agent": "pkarbs-research/1.0"}
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
            async with websockets.connect(CLOB_WS, user_agent_header=UA["User-Agent"], max_size=8*1024*1024, ping_interval=None) as ws:
                _w(log, f"{time.time():.3f} CLOB open")
                await ws.send(json.dumps({"assets_ids": tokens, "type": "market"}))

                async def keepalive():
                    # market channel drops idle clients: send the text PING every 10 s
                    while True:
                        await asyncio.sleep(10)
                        await ws.send("PING")
                ka = asyncio.create_task(keepalive())
                try:
                    async for raw in ws:
                        s_ = raw.decode() if isinstance(raw, bytes) else raw
                        if s_.strip().upper() == "PONG":
                            continue
                        try:
                            obj = json.loads(s_)
                        except Exception:
                            _record(clob_f, {"recv_ms": int(time.time()*1000), "unparsed": s_[:200]})
                            continue
                        # the initial snapshot arrives as a JSON LIST of books; later messages are dicts
                        for item in (obj if isinstance(obj, list) else [obj]):
                            if not isinstance(item, dict):
                                continue
                            _record(clob_f, {"recv_ms": int(time.time()*1000), "recv_iso": datetime.utcnow().isoformat()+"Z", **item})
                finally:
                    ka.cancel()
        except Exception as e:
            attempts += 1
            _w(log, f"{time.time():.3f} CLOB close {e!r} (attempt {attempts})")
            await asyncio.sleep(min(5 * attempts, 30))   # keep retrying; never give up silently

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

async def summarise(win, markets, log, every=300):
    """Every 5 min: one compact block per live match appended to <win>_summary.md, copied straight to LIVE.
    Reads the capture files incrementally (byte offsets), so it stays cheap. Counts only; no P&L."""
    names = {}   # token -> (title, outcome question)
    for ev in markets:
        for mk in ev.get("markets", []):
            for t in mk.get("clobTokenIds", []):
                names[t] = (ev.get("title", ev.get("ticker")), mk.get("question", "?"))
    kick = {ev.get("title", ev.get("ticker")): ev.get("kickoffUTC", "") for ev in markets}
    pos = {}; tot = {}; last = {}; recent = {}
    state = {"book": {}, "trades": {}, "espn": {}, "rr": {}, "sports": 0, "espn_err": 0, "espn_ok": 0}
    def new_lines(path):
        try:
            with open(path, "rb") as f:
                f.seek(pos.get(path, 0)); data = f.read(); pos[path] = pos.get(path, 0) + len(data)
        except FileNotFoundError:
            return []
        return [l for l in data.decode("utf-8", "ignore").split("\n") if l.strip()]
    while True:
        await asyncio.sleep(every)
        try:
            now = time.time(); nclob = 0; ntr = {}
            for l in new_lines(f"{ROOT}/{win}_clob.jsonl") + new_lines(f"{ROOT}/{win}_clob_rest.jsonl"):
                try: o = json.loads(l)
                except Exception: continue
                if isinstance(o, dict) and isinstance(o.get("book"), dict):   # REST poll row
                    bk_ = o["book"]; o = {"asset_id": o.get("token_id") or bk_.get("asset_id"), "bids": bk_.get("bids"), "asks": bk_.get("asks")}
                for item in (o if isinstance(o, list) else [o]):
                    nclob += 1
                    changes = item.get("price_changes") or [item]
                    for c in changes:
                        tok = c.get("asset_id") or item.get("asset_id")
                        if not tok: continue
                        bb, ba = c.get("best_bid"), c.get("best_ask")
                        if bb is None and item.get("bids"):
                            try: bb = max(float(x["price"]) for x in item["bids"]); ba = min(float(x["price"]) for x in item["asks"]) if item.get("asks") else None
                            except Exception: pass
                        if bb is not None or ba is not None:
                            state["book"][tok] = (bb, ba)
                        recent[tok] = recent.get(tok, 0) + 1
            for l in new_lines(f"{ROOT}/{win}_trades.jsonl"):
                try: o = json.loads(l)
                except Exception: continue
                cond = o.get("conditionId"); ntr[cond] = ntr.get(cond, 0) + 1
                state["trades"].setdefault(cond, [0, None])
                state["trades"][cond][0] += 1; state["trades"][cond][1] = o.get("price")
            for l in new_lines(f"{ROOT}/{win}_sports.jsonl"):
                state["sports"] += 1
            for l in new_lines(f"{ROOT}/{win}_espn.jsonl"):
                try: o = json.loads(l)
                except Exception: continue
                if o.get("status") == 200:
                    state["espn_ok"] += 1
                    for e in o.get("data", {}).get("events", []):
                        comp = (e.get("competitions") or [{}])[0]
                        sc = "-".join(str(c.get("score", "?")) for c in comp.get("competitors", []))
                        state["espn"][e.get("shortName")] = (e.get("status", {}).get("type", {}).get("name"), sc, e.get("status", {}).get("displayClock"))
                else:
                    state["espn_err"] += 1
            for l in new_lines(f"{ROOT}/{win}_rugbyrama_events.jsonl"):
                try: o = json.loads(l)
                except Exception: continue
                state["rr"][o.get("refMatch")] = (o.get("score"), o.get("minute"), o.get("text"))
            out = [f"## {datetime.utcnow().strftime('%H:%M:%SZ')} window {win} summary (last {every}s, counts only)",
                   f"- CLOB msgs {nclob}; sports WS rutopft msgs total {state['sports']}; ESPN polls ok {state['espn_ok']} err {state['espn_err']}"]
            for ev in markets:
                title = ev.get("title", ev.get("ticker"))
                try:
                    ko = datetime.strptime(ev.get("kickoffUTC", ""), "%Y-%m-%dT%H:%M:%SZ")
                    mins = (datetime.utcnow() - ko).total_seconds() / 60
                    if mins < -20 or mins > 135: continue   # only matches live or about to start
                except Exception:
                    pass
                bits = []
                for mk in ev.get("markets", []):
                    toks = mk.get("clobTokenIds", [])
                    b = state["book"].get(toks[0]) if toks else None
                    n = sum(recent.get(t, 0) for t in toks)
                    tr = state["trades"].get(mk.get("conditionId"), [0, None])
                    bits.append(f"{mk.get('question','?')[:28]}: bid/ask {b[0] if b else '-'}/{b[1] if b else '-'}, stream msgs {n}, trades {tr[0]} last {tr[1]}")
                out.append(f"- {title} (KO {kick.get(title,'?')[11:16]}Z): " + " | ".join(bits))
            if state["espn"]:
                out.append("- ESPN: " + "; ".join(f"{k} {v[0]} {v[1]} {v[2]}" for k, v in sorted(state["espn"].items())))
            if state["rr"]:
                out.append("- Rugbyrama latest event: " + "; ".join(f"{k} {v[0]} min {v[1]}" for k, v in state["rr"].items()))
            recent.clear()
            block = "\n".join(out) + "\n\n"
            for dst in (f"{ROOT}/{win}_summary.md", f"{LIVE}/{win}_summary.md"):
                try:
                    with open(dst, "a") as f: f.write(block)
                except Exception as e:
                    _w(log, f"{time.time():.3f} summary write {dst} {e!r}")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            _w(log, f"{time.time():.3f} summary error {e!r}")

async def main():
    win = sys.argv[1] if len(sys.argv) > 1 else "A"
    # single-instance guard (Nick approved 7 Nov 15:04Z): a second launch of the same window exits at once
    import fcntl
    os.makedirs(ROOT, exist_ok=True)
    global _LOCK
    _LOCK = open(f"{ROOT}/{win}.lock", "w")
    try:
        fcntl.flock(_LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(json.dumps({"window": win, "error": "already running (lock held), exiting"}))
        sys.exit(0)
    cfg = json.load(open(CONFIG_PATH))
    markets = cfg.get(win, [])
    kick0 = min(m.get("kickoffUTC", "2026-11-07T00:00:00Z") for m in markets)
    os.makedirs(ROOT, exist_ok=True); os.makedirs(LIVE, exist_ok=True)
    st = time.time()
    # window run length: per-window (AB merged to 5h / 18000s per Nick 15:50Z; D,C ~2h45 bounded)
    run_for = 18000 if win == "AB" else 10500
    log = f"{ROOT}/{win}_log.txt"
    _w(log, f"{time.time():.3f} WIN={win} start markets={len(markets)}")
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
    tasks.append(asyncio.create_task(summarise(win, markets, log)))
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
