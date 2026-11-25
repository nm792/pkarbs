#!/usr/bin/env python3
"""PandaScore low-latency feed capture - TASK-pandascore-trial-2026-11-12.md Part A (v2).
Discovery every 60 s (Bearer), one socket per Dota 2 / CS2 match at or after endpoint.opens_at,
raw payload logged with recv_ns + sha1 + updated_at, gzip per UTC hour under /mnt/HC_Volume_107257520/pkarbs/pandascore/.
Token: /etc/pkarbs/pandascore.env (mode 600) if present, else /root/API_KEYS/pandascore/.env.
Never prints or logs the token; the socket URL (which carries ?token=) is never logged.
"""
import os, sys, json, time, gzip, hashlib, asyncio, datetime, urllib.request, urllib.error
import websockets

TOKEN = ""
for path in ("/etc/pkarbs/pandascore.env", "/root/API_KEYS/pandascore/.env"):
    try:
        for line in open(path):
            line = line.strip()
            if line.startswith(("PANDASCORE_TOKEN=", "PANDASCORE_ACCESS_TOKEN=")) and "=" in line:
                TOKEN = line.partition("=")[2].strip().strip('"').strip("'")
                SRC = path
                break
    except Exception:
        pass
    if TOKEN:
        break
if not TOKEN:
    print("FATAL: no PANDASCORE token found", flush=True)
    sys.exit(1)

OUT = "/mnt/HC_Volume_107257520/pkarbs/pandascore/raw"
EV = "/mnt/HC_Volume_107257520/pkarbs/pandascore/events.jsonl.gz"
GAME_SLUGS = {"cs-go", "dota-2"}          # cs-go = CS2; LoL excluded per task
FLOOR = float(os.environ.get("PS_FLOOR_GB", "15")) * 1e9   # v3: floor from env (default 15 GB as before)
os.makedirs(OUT, exist_ok=True)

state = {"socks": {}, "last_msg_ns": {}, "opened": set(), "silence_warned": set(), "beat_ns": time.time_ns(), "disc_fail": 0, "disc_ok_ns": time.time_ns(), "live": set()}

# ---- v4 watchdog (R-094): a silent-but-alive process is the failure that cost 41 h. Exit NON-ZERO so a supervisor/IT sees it.
WD_LOOP_S = 120        # event loop did not run its 10 s heartbeat for this long -> frozen loop (blocking call / disk stall)
WD_DATA_S = 900        # a socket is connected for a live match and NO message arrived on ANY socket for this long
WD_DISC_FAILS = 15     # discovery failed this many 60 s rounds in a row (token / entitlement / network)

def wd_decide(now_ns, st_, wd_loop_s=WD_LOOP_S, wd_data_s=WD_DATA_S, wd_disc=WD_DISC_FAILS):
    """returns (exit_code, reason) or None. Pure function; tested."""
    if (now_ns - st_["beat_ns"]) / 1e9 > wd_loop_s:
        return 5, "event loop frozen: no heartbeat for >%d s" % wd_loop_s
    if st_["disc_fail"] >= wd_disc:
        return 4, "discovery failed %d rounds in a row (see discovery_error lines: token/entitlement/network)" % st_["disc_fail"]
    live = [m for m in st_["live"] if m in st_["last_msg_ns"]]
    if live and (now_ns - max(st_["last_msg_ns"][m] for m in live)) / 1e9 > wd_data_s:
        return 6, "no message on any live socket for >%d s with %d subscribed" % (wd_data_s, len(live))
    return None

def wd_thread(st_, interval=30, now_fn=time.time_ns, exit_fn=None):
    import threading
    def run():
        while True:
            time.sleep(interval)
            d = wd_decide(now_fn(), st_)
            if d:
                print(json.dumps({"kind": "watchdog_exit", "code": d[0], "reason": d[1]}), flush=True)
                (exit_fn or os._exit)(d[0])
    t = threading.Thread(target=run, daemon=True); t.start(); return t


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")

def free_ok():
    import shutil
    return shutil.disk_usage("/mnt/HC_Volume_107257520/pkarbs/pandascore").free > FLOOR

def ev(**kw):
    kw["t"] = now_iso()
    try:
        with gzip.open(EV, "at") as f:
            f.write(json.dumps(kw, default=str) + "\n")
    except Exception as ex:
        print("event-log error", repr(ex)[:200], flush=True)
    print(json.dumps(kw, default=str), flush=True)

def redact(msg):
    """Strip any token value from text destined for a log line."""
    return msg.replace(TOKEN, "<token>")

def http_get(url, bearer=True, timeout=20):
    hdr = {"Accept": "application/json"}
    if bearer:
        hdr["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def discovery():
    """Return {match_id: {"url":..., "opens_at":..., "slug":..., "label":...}} for Dota2/CS2 only."""
    out = {}
    try:
        feeds = http_get("https://api.pandascore.co/low_latency_feeds")
    except Exception as ex:
        state["disc_fail"] += 1
        ev(kind="discovery_error", err=redact(repr(ex))[:300], fails_in_a_row=state["disc_fail"])
        return out
    state["disc_fail"] = 0; state["disc_ok_ns"] = time.time_ns()
    items = feeds if isinstance(feeds, list) else feeds.get("data", [])
    for it in items:
        m = it.get("match") or {}
        ep = it.get("endpoint") or {}
        slug = ((m.get("videogame") or {}).get("slug")) or ""
        if slug not in GAME_SLUGS:
            continue
        url = ep.get("url") or ""
        if not url:
            continue
        mid = str(m.get("id"))
        opp = m.get("opponents") or []
        names = []
        for o in opp:
            team = (o or {}).get("opponent") or {}
            if team.get("name"):
                names.append(team["name"])
        out[mid] = {"url": url, "opens_at": ep.get("opens_at") or "",
                    "slug": slug, "label": " vs ".join(names) or mid}
    return out

def open_ts(iso):
    try:
        return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0

class Hourly:
    """gzip JSON-lines writer, one file per UTC hour, closed on rollover."""
    def __init__(self):
        self.h = None; self.hour = None
    def write(self, obj):
        if not free_ok():
            ev(kind="stopped", reason="free space <= 15 GB on /mnt/HC_Volume_107257520/pkarbs/pandascore", free_b=__import__("shutil").disk_usage("/mnt/HC_Volume_107257520/pkarbs/pandascore").free)
            sys.exit(0)
        hour = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H")
        if self.hour != hour:
            if self.h:
                self.h.close()
            self.h = gzip.open(os.path.join(OUT, f"pandascore_{hour}.jsonl.gz"), "at")
            self.hour = hour
        self.h.write(json.dumps(obj, default=str) + "\n")
        self.h.flush()
    def close(self):
        if self.h:
            self.h.close(); self.h = None

HW = Hourly()

async def socket_for(mid, meta):
    url = meta["url"] + ("&" if "?" in meta["url"] else "?") + "token=" + TOKEN
    backoff = 1
    while True:
        if not free_ok():
            ev(match_id=mid, kind="stopped", reason="free space <= 15 GB on /mnt/HC_Volume_107257520/pkarbs/pandascore")
            return
        if datetime.datetime.now(datetime.timezone.utc).timestamp() < open_ts(meta["opens_at"]):
            await asyncio.sleep(5); continue
        try:
            async with websockets.connect(url, open_timeout=20, max_size=None) as ws:
                ev(match_id=mid, kind="connected", label=meta["label"], slug=meta["slug"])
                state["live"].add(mid)
                backoff = 1
                state["last_msg_ns"][mid] = time.time_ns()
                state["silence_warned"].discard(mid)
                async for raw in ws:
                    recv_ns = time.time_ns()
                    state["last_msg_ns"][mid] = recv_ns
                    state["silence_warned"].discard(mid)
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        msg = {"_unparsed": True}
                    kind = msg.get("type") or ("status" if "match_status" in msg else "update")
                    HW.write({
                        "recv_ns": recv_ns, "host": "pandascore-ll", "match_id": mid,
                        "label": meta["label"], "slug": meta["slug"], "kind": kind,
                        "updated_at": msg.get("updated_at"),
                        "available_fields": msg.get("available_fields"),
                        "sha1": hashlib.sha1(raw if isinstance(raw, bytes) else raw.encode()).hexdigest(),
                        "bytes": len(raw) if isinstance(raw, (bytes, str)) else 0,
                        "payload": msg,
                    })
                state["live"].discard(mid)
                ev(match_id=mid, kind="closed", code=1000, note="server closed 1000 - match finished")
                return
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            code = None
            rc = getattr(ex, "rcvd", None)
            if rc is not None:
                code = getattr(rc, "code", None)
            txt = redact(repr(ex))
            state["live"].discard(mid)
            ev(match_id=mid, kind="close_error", code=code, err=txt[:300])
            if code == 4004:
                count = state.setdefault("4004_count", {}).get(mid, 0) + 1
                state["4004_count"][mid] = count
                ev(match_id=mid, kind="4004_count", count=count)
                ev(match_id=mid, kind="recheck_discovery", note="match unavailable - discovery retry eligible after 300 s")
                return
            if code in (4001, 4003, 4029):
                ev(match_id=mid, kind="stop_for_match", code=code, note="logged, never retried for this match")
                return
            # 1xxx / no close frame / network error: reconnect with backoff 1..30 s
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

async def silence_watcher():
    while True:
        await asyncio.sleep(30)
        now = time.time_ns()
        for mid, last in list(state["last_msg_ns"].items()):
            gap_s = (now - last) / 1e9
            if gap_s > 300 and mid not in state["silence_warned"]:
                state["silence_warned"].add(mid)
                ev(match_id=mid, kind="silent", gap_s=round(gap_s, 1),
                   note="no message for >300 s; silent socket is not an error, not killed")

async def heartbeat():
    n = 0
    while True:
        state["beat_ns"] = time.time_ns(); n += 1
        if n % 6 == 0:   # every 60 s: an idle night (no match) is now distinguishable from a dead process
            now = time.time_ns(); lm = [state["last_msg_ns"][m] for m in state["live"] if m in state["last_msg_ns"]]
            ev(kind="heartbeat", live=len(state["live"]), last_msg_age_s=round((now - max(lm)) / 1e9, 1) if lm else None, disc_ok_age_s=round((now - state["disc_ok_ns"]) / 1e9), disc_fail=state["disc_fail"])
        await asyncio.sleep(10)

async def discovery_nb():
    """discovery() in a thread with a hard 60 s cap: a hung DNS/TLS call can no longer freeze the event loop."""
    try:
        return await asyncio.wait_for(asyncio.get_running_loop().run_in_executor(None, discovery), 60)
    except Exception as ex:
        state["disc_fail"] += 1
        ev(kind="discovery_error", err=redact(repr(ex))[:300], fails_in_a_row=state["disc_fail"], note="discovery thread cap")
        return {}

async def main():
    ev(kind="start", pid=os.getpid(), out=OUT, token_src=SRC, version="v4-watchdog")
    asyncio.create_task(heartbeat()); wd_thread(state)
    # None means a task is active; a float is its last completion time.
    seen = {}
    while True:
        if not free_ok():
            ev(kind="stopped", reason="free space <= 15 GB on /mnt/HC_Volume_107257520/pkarbs/pandascore")
            return
        feeds = await discovery_nb()
        now = time.time()
        for mid, meta in feeds.items():
            last_end = seen.get(mid)
            if mid in seen and (last_end is None or now - last_end < 300):
                continue
            if open_ts(meta["opens_at"]) > now + 900:
                continue                       # not connectable yet (opens_at 15 min before start)
            seen[mid] = None
            task = asyncio.create_task(socket_for(mid, meta))
            task.add_done_callback(lambda _task, match_id=mid: seen.__setitem__(match_id, time.time()))
            ev(match_id=mid, kind="task_started", label=meta["label"], slug=meta["slug"],
               opens_at=meta["opens_at"])
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        HW.close()
