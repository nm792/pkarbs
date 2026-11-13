#!/usr/bin/env python3
"""PandaScore low-latency feed capture - TASK-pandascore-trial-2026-11-12.md Part A (v2).
Discovery every 60 s (Bearer), one socket per Dota 2 / CS2 match at or after endpoint.opens_at,
raw payload logged with recv_ns + sha1 + updated_at, gzip per UTC hour under /vol2/pandascore/.
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

OUT = "/vol2/pandascore/raw"
EV = "/vol2/pandascore/events.jsonl.gz"
GAME_SLUGS = {"cs-go", "dota-2"}          # cs-go = CS2; LoL excluded per task
FLOOR = 15e9
os.makedirs(OUT, exist_ok=True)

state = {"socks": {}, "last_msg_ns": {}, "opened": set(), "silence_warned": set()}

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")

def free_ok():
    import shutil
    return shutil.disk_usage("/vol2").free > FLOOR

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
        ev(kind="discovery_error", err=redact(repr(ex))[:300])
        return out
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
            ev(kind="stopped", reason="free space <= 15 GB on /vol2", free_b=__import__("shutil").disk_usage("/vol2").free)
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
            ev(match_id=mid, kind="stopped", reason="free space <= 15 GB on /vol2")
            return
        if datetime.datetime.now(datetime.timezone.utc).timestamp() < open_ts(meta["opens_at"]) - 5:
            await asyncio.sleep(5); continue
        try:
            async with websockets.connect(url, open_timeout=20, max_size=None) as ws:
                ev(match_id=mid, kind="connected", label=meta["label"], slug=meta["slug"])
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
            ev(match_id=mid, kind="close_error", code=code, err=txt[:300])
            if code == 4004:
                ev(match_id=mid, kind="recheck_discovery", note="match unavailable - discovery will retry")
                await asyncio.sleep(10); continue
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

async def main():
    ev(kind="start", pid=os.getpid(), out=OUT, token_src=SRC)
    seen = set()
    while True:
        if not free_ok():
            ev(kind="stopped", reason="free space <= 15 GB on /vol2")
            return
        feeds = discovery()
        now = time.time()
        for mid, meta in feeds.items():
            if mid in seen:
                continue
            if open_ts(meta["opens_at"]) > now + 900:
                continue                       # not connectable yet (opens_at 15 min before start)
            seen.add(mid)
            asyncio.create_task(socket_for(mid, meta))
            ev(match_id=mid, kind="task_started", label=meta["label"], slug=meta["slug"],
               opens_at=meta["opens_at"])
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        HW.close()
