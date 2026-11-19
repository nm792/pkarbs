#!/usr/bin/env python3
"""LIVE PROBE (exploratory, UNCHECKED; one process, one clock; preflight checks must pass or no number is printed): PandaScore CS2 low-latency round-score events vs each Polymarket
token's OWN book on today's live CS2 matches. Run on the server (token read from the same files as ll_capture.py;
never printed). One command:
  python3 -I it/REPLY-2026-11-19-live_probe_cs2.py --minutes 60 --out agent/status/pandascore-live-probe-2026-11-19.json
Prints a summary every 5 min and at the end; writes the full event table to --out. Needs `websockets` (already installed).
"""
import os, sys, re, json, time, asyncio, argparse, statistics, urllib.request, datetime, random, subprocess, collections
import websockets
TOKEN = ""
for p in ("/etc/pkarbs/pandascore.env", "/root/API_KEYS/pandascore/.env"):
    try:
        for l in open(p):
            l = l.strip()
            if l.startswith(("PANDASCORE_TOKEN=", "PANDASCORE_ACCESS_TOKEN=")):
                TOKEN = l.partition("=")[2].strip().strip('"').strip("'")
    except Exception:
        pass
    if TOKEN: break
if not TOKEN: sys.exit("FATAL no PandaScore token file readable")
def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
def get(url, bearer=False):
    h = {"Accept": "application/json", "User-Agent": "probe"}
    if bearer: h["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=25) as r: return json.load(r)
def jl(x):
    return json.loads(x) if isinstance(x, str) else (x or [])
T0 = time.time()
mids = {}    # token -> [(t, mid)]
last = {}
events = []  # dicts
matches = {}  # mid -> meta
pm_by_match = {}  # mid -> list of market dicts
pm_lag = []; ps_lag = []; pm_n = collections.Counter(); ps_n = collections.Counter(); pm_first = {}
def setmid(tok, bid, ask):
    try: bid, ask = float(bid), float(ask)
    except Exception: return
    if bid <= 0 or ask <= 0 or ask < bid: return
    m = (bid + ask) / 2
    if last.get(tok) != m:
        last[tok] = m; mids.setdefault(tok, []).append((time.time(), m))
async def pm_ws(tokens):
    while True:
        try:
            async with websockets.connect("wss://ws-subscriptions-clob.polymarket.com/ws/market", max_size=None) as ws:
                await ws.send(json.dumps({"assets_ids": tokens, "type": "market"}))
                async for raw in ws:
                    try: d = json.loads(raw)
                    except Exception: continue
                    rt = time.time()
                    for e in (d if isinstance(d, list) else [d]):
                        et = e.get("event_type")
                        try: pm_lag.append(rt - int(e.get("timestamp")) / 1000.0)
                        except Exception: pass
                        for tk in ([e.get("asset_id")] if e.get("asset_id") else [c.get("asset_id") for c in e.get("price_changes", [])]):
                            if tk: pm_n[tk] += 1; pm_first.setdefault(tk, rt)
                        if et == "book":
                            b = [float(x["price"]) for x in e.get("bids", [])]; a = [float(x["price"]) for x in e.get("asks", [])]
                            if b and a: setmid(e["asset_id"], max(b), min(a))
                        elif et == "price_change":
                            for c in e.get("price_changes", []):
                                if c.get("best_bid") and c.get("best_ask"): setmid(c["asset_id"], c["best_bid"], c["best_ask"])
                        elif et == "best_bid_ask":
                            setmid(e["asset_id"], e.get("best_bid"), e.get("best_ask"))
        except Exception as ex:
            print("pm ws error", repr(ex)[:100], flush=True); await asyncio.sleep(3)
async def ps_ws(mid, url):
    prev = {}; maps = []
    while True:
        try:
            async with websockets.connect(url + ("&" if "?" in url else "?") + "token=" + TOKEN, max_size=None) as ws:
                async for raw in ws:
                    t = time.time()
                    try: m = json.loads(raw)
                    except Exception: continue
                    ps_n[mid] += 1
                    try: ps_lag.append(t - datetime.datetime.fromisoformat(m["updated_at"].replace("Z", "+00:00")).timestamp())
                    except Exception: pass
                    if "round_score" not in (m.get("available_fields") or []): continue
                    gid = m.get("map_id") or m.get("game_id") or "?"
                    if gid not in maps: maps.append(gid)
                    lat = {x.get("field"): x.get("delay") for x in (m.get("latency") or []) if isinstance(x, dict)}
                    for k in ("home_team", "away_team"):
                        tm = m.get(k) or {}
                        sc = tm.get("score")
                        if not isinstance(sc, int): continue
                        key = (gid, tm.get("team_name"))
                        if key in prev and sc > prev[key]:
                            events.append(dict(match=mid, label=matches[mid]["label"], map_no=maps.index(gid) + 1, team=tm.get("team_name"),
                                               t=t, updated_at=m.get("updated_at"), round_score_delay=lat.get("round_score")))
                        prev[key] = sc
        except Exception as ex:
            print("ps ws error", mid, repr(ex)[:100], flush=True); await asyncio.sleep(3)
def onset(tok, t0, sign):
    base = None
    for (t, m) in mids.get(tok, []):
        if t < t0 - 60: base = m; continue
        if t > t0 + 60: break
        if base is None: base = m; continue
        if sign * (m - base) >= 0.02: return t - t0
    return None
def summarize():
    rows = []
    for e in events:
        if time.time() < e["t"] + 65: continue
        for mk in pm_by_match.get(e["match"], []):
            kind = "map" if mk["map_no"] == e["map_no"] else ("match" if mk["map_no"] is None else None)
            if kind is None: continue
            for tok, name in zip(mk["tokens"], mk["outcomes"]):
                own_up = norm(name) == norm(e["team"]) or norm(name) in norm(e["team"]) or norm(e["team"]) in norm(name)
                s = 1 if own_up else -1
                rows.append(dict(e, series=kind, token=tok[:10], outcome=name, direction=s, lead=onset(tok, e["t"], s), q=mk["q"][:60]))
    # placebo (STANDARD v1): 10 random event-free times per match, same onset rule, both signs
    rnd = random.Random(20261119); plc = []
    for mid, mks in pm_by_match.items():
        ev_t = [e["t"] for e in events if e["match"] == mid]
        lo, hi = T0 + 90, time.time() - 65
        tries = 0; got = 0
        while got < 10 and hi > lo and tries < 500:
            tries += 1; pt = rnd.uniform(lo, hi)
            if any(abs(pt - x) < 90 for x in ev_t): continue
            got += 1
            for mk in mks:
                for tok in mk["tokens"]:
                    for sg in (1, -1):
                        plc.append(dict(series="map" if mk["map_no"] else "match", direction=sg, lead=onset(tok, pt, sg)))
    out = {}
    for ser in ("map", "match"):
        for d in (1, -1):
            r = [x for x in rows if x["series"] == ser and x["direction"] == d]
            l = [x["lead"] for x in r if x["lead"] is not None]
            pl = [x["lead"] for x in plc if x["series"] == ser and x["direction"] == d and x["lead"] is not None]
            out["%s_%s" % (ser, "rising_team_token" if d == 1 else "other_token")] = dict(
                n_events=len(r), n_with_onset=len(l), median_onset_s=(round(statistics.median(l), 2) if l else None),
                share_onset_after_feed=(round(sum(1 for v in l if v > 0) / len(l), 3) if l else None),
                n_placebo_with_onset=len(pl), placebo_median_s=(round(statistics.median(pl), 2) if pl else None),
                real_minus_placebo_s=(round(statistics.median(l) - statistics.median(pl), 2) if l and pl else None))
    return rows, out
def clock_check():
    for cmd in (["chronyc", "tracking"], ["timedatectl", "show", "-p", "NTPSynchronized"], ["ntpq", "-pn"]):
        try: o = subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
        except Exception: continue
        if cmd[0] == "chronyc":
            mm = re.search(r"System time\s*:\s*([0-9.]+) seconds (fast|slow)", o)
            if mm: return dict(tool="chronyc", offset_s=float(mm.group(1)), ok=float(mm.group(1)) < 0.05 and "Not synchronised" not in o)
        elif cmd[0] == "timedatectl" and "NTPSynchronized=yes" in o: return dict(tool="timedatectl", synced=True, ok=True)
        elif cmd[0] == "ntpq":
            mm = re.search(r"^\*\S+.*?\s(-?[0-9.]+)\s+[0-9.]+\s*$", o, re.M)
            if mm: return dict(tool="ntpq", offset_ms=float(mm.group(1)), ok=abs(float(mm.group(1))) < 50)
    return dict(tool=None, ok=False)
def q(x, p):
    x = sorted(x); return round(x[int(p * (len(x) - 1))], 3) if x else None
def preflight(toks, live):
    ck = clock_check()
    c = dict(clock_synchronised_under_50ms=ck["ok"],
             every_pm_token_has_a_book_message=all(pm_n[t] > 0 for t in toks),
             pandascore_messages_on_every_open_match=all(ps_n[m] > 0 for m in live),
             pm_server_timestamp_lag_plausible=bool(pm_lag) and -0.25 < statistics.median(pm_lag) < 2.0,
             pandascore_updated_at_lag_plausible=bool(ps_lag) and -0.25 < statistics.median(ps_lag) < 5.0)
    return dict(all_ok=all(c.values()), checks=c, clock=ck, pm_lag_s_p10_p50_p90=[q(pm_lag, .1), q(pm_lag, .5), q(pm_lag, .9)],
                ps_updated_at_lag_s_p10_p50_p90=[q(ps_lag, .1), q(ps_lag, .5), q(ps_lag, .9)], n_pm_msgs=sum(pm_n.values()),
                tokens_without_book=[t[:10] for t in toks if pm_n[t] == 0], matches_without_ps_msgs=[live[m]["label"] for m in live if ps_n[m] == 0])
async def main():
    a = argparse.ArgumentParser(); a.add_argument("--minutes", type=float, default=60); a.add_argument("--out", required=True); a = a.parse_args()
    feeds = get("https://api.pandascore.co/low_latency_feeds", True)
    feeds = feeds if isinstance(feeds, list) else feeds.get("data", [])
    now = time.time(); live = {}
    for it in feeds:
        m = it.get("match") or {}; ep = it.get("endpoint") or {}
        if ((m.get("videogame") or {}).get("slug")) != "cs-go" or not ep.get("url"): continue
        try: op = datetime.datetime.fromisoformat((ep.get("opens_at") or "").replace("Z", "+00:00")).timestamp()
        except Exception: op = 0
        if op > now + 600: continue
        names = [((o or {}).get("opponent") or {}).get("name") for o in (m.get("opponents") or [])]
        live[str(m["id"])] = dict(url=ep["url"], label=" vs ".join(n for n in names if n), names=[n for n in names if n])
    matches.update(live); print("CS2 feeds open now:", {k: v["label"] for k, v in live.items()}, flush=True)
    toks = []; scanned = 0
    for off in range(0, 5000, 500):
        try: ms = get("https://gamma-api.polymarket.com/markets?closed=false&active=true&limit=500&offset=%d" % off)
        except Exception as ex: print("gamma error", repr(ex)[:100]); break
        scanned += len(ms)
        for mk in ms:
            qn = norm(mk.get("question"))
            for mid, meta in live.items():
                if len(meta["names"]) == 2 and all(norm(n) in qn for n in meta["names"]):
                    tk, oc = jl(mk.get("clobTokenIds")), jl(mk.get("outcomes"))
                    if len(tk) != 2 or len(oc) != 2: continue
                    hit = [any(norm(n) in norm(o) or norm(o) in norm(n) for o in oc) for n in meta["names"]]
                    if not all(hit): print("MAPPING SKIP (outcomes do not name both teams):", mk.get("question", "")[:70], oc, flush=True); continue
                    mm = re.search(r"(?:map|game)\s*(\d+)", qn)
                    pm_by_match.setdefault(mid, []).append(dict(q=mk.get("question", ""), map_no=int(mm.group(1)) if mm else None, tokens=tk, outcomes=oc))
                    toks += tk
        if len(ms) < 500: break
    print("gamma markets scanned:", scanned, "| matched PM markets:", {live[k]["label"]: [(x["q"][:50], x["map_no"]) for x in v] for k, v in pm_by_match.items()}, flush=True)
    if not toks: sys.exit("NO live CS2 match with a matching Polymarket market; nothing to measure (write this as the reason)")
    tasks = [asyncio.create_task(pm_ws(toks))] + [asyncio.create_task(ps_ws(mid, v["url"])) for mid, v in live.items()]
    await asyncio.sleep(45); pre = preflight(toks, live)
    print("PREFLIGHT", json.dumps(pre, default=str), flush=True)
    if not pre["all_ok"]:
        sys.exit("PREFLIGHT FAILED (%s): no number is reported; fix the failed check and rerun" % ",".join(k for k, v in pre["checks"].items() if not v))
    end = time.time() + a.minutes * 60; nxt = time.time() + 300
    while time.time() < end:
        await asyncio.sleep(10)
        if time.time() > nxt:
            nxt += 300; _, s = summarize(); print(time.strftime("%H:%M:%SZ", time.gmtime()), "events:", len(events), json.dumps(s), flush=True)
    await asyncio.sleep(65); rows, s = summarize()
    json.dump(dict(status="EXPLORATORY LIVE PROBE, UNCHECKED, placebo per STANDARD v1 (no bootstrap CI), onset=first mid move >=2c within +-60s", preflight=pre, summary=s, n_events=len(events), rows=rows,
                   pm_markets=pm_by_match, events=events), open(a.out, "w"), indent=1, default=str)
    print("FINAL", json.dumps(s), flush=True)
asyncio.run(main())
