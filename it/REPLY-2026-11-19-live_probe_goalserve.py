#!/usr/bin/env python3
"""LIVE PROBE (exploratory, UNCHECKED; one process, one clock; preflight must pass per sport or that sport prints no number).
Goalserve in-play odds (polled over HTTP, as the capture does) vs each Polymarket token's OWN book (websocket), games live NOW.
Run on the server (creds read from /etc/pkarbs/goalserve.env, never printed). One command:
  python3 -I it/REPLY-2026-11-19-live_probe_goalserve.py --sports esports,tennis,hockey_nhl --minutes 90 --out agent/status/goalserve-live-probe-2026-11-19.json
Prints a summary every 5 min and at the end. Needs `websockets` (installed). Writes a small JSON only (disk gate: refuses under 15 GB free).
Event: vig-removed home probability moves >= 2c between consecutive polls (market open+valid in both; baseline cleared after a poll gap > 10 s).
Rising team's own token only (never 1 - other token). Placebo: 10 random event-free times per game, both signs. Bookmaker is not identified (bm empty; vendor docs say bet365).
Wording: 'odds moved before the price within the 60 s window' or 'did not'; never 'lead of N seconds'. Tennis: open-market moves only (tennis suspends after each point, reopen reprices excluded).
"""
import os, sys, re, json, time, gzip, zlib, asyncio, argparse, statistics, urllib.request, urllib.parse, shutil, random, bisect, subprocess, collections, hashlib
import websockets

CRED = {}
try:
    for l in open("/etc/pkarbs/goalserve.env"):
        l = l.strip()
        if "=" in l and not l.startswith("#"):
            k, _, v = l.partition("="); CRED[k.strip()] = v.strip()
except Exception:
    pass
ENDPOINT = {"esports": "/inplay-esports.gz", "tennis": "/inplay-tennis.gz", "hockey_nhl": "/inplay-hockey.gz",
            "basketball": "/inplay-basket.gz", "soccer": "/inplay-soccer.gz", "baseball": "/inplay-baseball.gz"}
GOOD = ("money line", "moneyline", "to win", "match winner", "home away", "winner")      # match-level winner market names
BAD = ("set", "period", "map", "game ", "handicap", "total", "margin", "race", "half", "quarter", "next", "odd", "draw", "first", "1st", "2nd", "3rd", "round", "break", "distance", "score")
STOP = {"team", "esports", "gaming", "fc", "club", "the", "of", "de", "vs"}
TAGS = {"esports": ["esports"], "tennis": ["tennis"], "hockey_nhl": ["nhl", "ahl", "hockey"], "basketball": ["basketball", "ncaab"], "soccer": [], "baseball": ["mlb"]}   # Polymarket gamma tag slugs per Goalserve sport
def kind_ok(name):
    n = norm(name)
    return any(g in n for g in GOOD) and not any(b in n for b in BAD)
THR, OUTAGE_S = 0.02, 10.0

def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
def key_of(name):
    t = [x for x in norm(name).split() if len(x) >= 2 and x not in STOP]
    return max(t, key=len) if t else norm(name)
def toks(name):
    t = [x for x in norm(name).split() if x not in STOP]
    return [x for x in t if len(x) >= 3] or [x for x in t if len(x) >= 2]     # 'G2 Esports' -> ['g2']
def tmatch(name, text):
    """Goalserve team name vs Polymarket text: any token of the name equals a text token or is a prefix of it ('uta' -> 'utah'), or the reverse for text tokens of 4+ letters."""
    qs = norm(text).split()
    return any(q == t or q.startswith(t) or (len(q) >= 4 and t.startswith(q)) for t in toks(name) for q in qs)
def jl(x): return json.loads(x) if isinstance(x, str) else (x or [])
def num(x):
    try:
        v = float(x); return v if v > 1.0 else None
    except Exception: return None
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "probe", "Accept-Encoding": "gzip"}), timeout=40) as r:
        b = r.read()
        if b[:2] == b"\x1f\x8b": b = gzip.decompress(b)
        return json.loads(b)

T0 = time.time(); SPORTS_RUN = []; SOURCE = {"mode": "capture", "root": "/mnt/HC_Volume_107257520/pkarbs/goalserve"}
mt = {}; mv = {}; last = {}          # token -> times list, mids list, last mid
games = {}                           # (sport, eid) -> dict(label, home, away, hk, ak)
pm_mk = {}                           # (sport, eid) -> list of dict(q, tokens, outcomes, tok_home, tok_away)
events = []; gs_poll_t = collections.defaultdict(list); gs_change_t = collections.defaultdict(list); gs_err = collections.Counter(); gs_err_kinds = collections.defaultdict(collections.Counter)
gs_seen_now = collections.defaultdict(dict)   # sport -> {eid: last time present}
mkt_names = collections.defaultdict(collections.Counter); mkt_ok = collections.defaultdict(collections.Counter); ambiguous = {}
pm_lag = []; pm_n = collections.Counter(); sub_tokens = []; ws_ref = {"ws": None}; odds_log = []

def setmid(tok, bid, ask):
    try: bid, ask = float(bid), float(ask)
    except Exception: return
    if bid <= 0 or ask <= 0 or ask < bid: return
    m = (bid + ask) / 2
    if last.get(tok) != m:
        last[tok] = m; mt.setdefault(tok, []).append(time.time()); mv.setdefault(tok, []).append(m)

async def pm_ws():
    while True:
        while not sub_tokens: await asyncio.sleep(2)
        try:
            async with websockets.connect("wss://ws-subscriptions-clob.polymarket.com/ws/market", max_size=None) as ws:
                ws_ref["ws"] = ws
                await ws.send(json.dumps({"assets_ids": list(sub_tokens), "type": "market"}))
                async for raw in ws:
                    try: d = json.loads(raw)
                    except Exception: continue
                    rt = time.time()
                    for e in (d if isinstance(d, list) else [d]):
                        if not isinstance(e, dict): continue
                        et = e.get("event_type")
                        try: pm_lag.append(rt - int(e.get("timestamp")) / 1000.0)
                        except Exception: pass
                        for tk in ([e.get("asset_id")] if e.get("asset_id") else [c.get("asset_id") for c in e.get("price_changes", [])]):
                            if tk: pm_n[tk] += 1
                        if et == "book":
                            b = [float(x["price"]) for x in e.get("bids", [])]; a = [float(x["price"]) for x in e.get("asks", [])]
                            if b and a: setmid(e["asset_id"], max(b), min(a))
                        elif et == "price_change":
                            for c in e.get("price_changes", []):
                                if c.get("best_bid") and c.get("best_ask"): setmid(c["asset_id"], c["best_bid"], c["best_ask"])
                        elif et == "best_bid_ask": setmid(e["asset_id"], e.get("best_bid"), e.get("best_ask"))
        except Exception as ex:
            ws_ref["ws"] = None; print("pm ws error", repr(ex)[:100], flush=True); await asyncio.sleep(3)

def fetch(sport):
    url = "https://inplay.goalserve.com" + ENDPOINT[sport] + "?" + urllib.parse.urlencode({"user": CRED["GOALSERVE_USER"], "key": CRED["GOALSERVE_KEY"]})
    body = urllib.request.urlopen(urllib.request.Request(url, headers={"Accept-Encoding": "gzip"}), timeout=20).read()
    rt = time.time()
    try: body = gzip.decompress(body)
    except Exception: pass
    return rt, body

def process_body(sport, rt, body, base):
    """One stored/polled Goalserve payload -> games, market names, 2c vig-removed events (market open+valid in both payloads)."""
    try: d = json.loads(body)
    except Exception: gs_err[sport] += 1; gs_err_kinds[sport]["bad json"] += 1; return
    valid = set()
    for eid, e in (d.get("events") or {}).items():
        if not isinstance(e, dict): continue
        ti = e.get("team_info") or {}
        h, a = (ti.get("home") or {}).get("name"), (ti.get("away") or {}).get("name")
        if not h or not a: continue
        g = (sport, eid)
        if g not in games:
            games[g] = dict(label="%s vs %s" % (h, a), home=h, away=a, hk=key_of(h), ak=key_of(a), league=str((e.get("info") or {}).get("league") or ""))
        gs_seen_now[sport][eid] = rt
        for mid, m in (e.get("odds") or {}).items():
            if not isinstance(m, dict): continue
            nm = m.get("name") or "?"; mkt_names[sport][nm] += 1
            if not kind_ok(nm): continue
            mkt_ok[sport][nm] += 1
            parts = [x for x in (m.get("participants") or {}).values() if isinstance(x, dict)]
            if len(parts) != 2: continue
            if m.get("suspend") not in (0, "0", False, None) or any(x.get("suspend") not in (0, "0", False, None) for x in parts): continue
            o = [num(x.get("value_eu")) for x in parts]
            if None in o: continue
            side = []
            for x in parts:
                n = norm(x.get("name"))
                side.append("h" if n == norm(h) else "a" if n == norm(a) else "h" if n in ("1", "home") else "a" if n in ("2", "away") else None)
            if sorted(side, key=str) != ["a", "h"]: continue
            ph = (1 / o[side.index("h")]) / (1 / o[0] + 1 / o[1])
            k = (eid, str(mid)); valid.add(k)
            if k in base and abs(ph - base[k]) >= THR:
                events.append(dict(sport=sport, eid=eid, label=games[g]["label"], t=rt, rising="home" if ph > base[k] else "away", ph_before=round(base[k], 4), ph_after=round(ph, 4)))
            base[k] = ph
    for k in [k for k in base if k not in valid]: del base[k]

async def gs_poll(sport):
    base = {}; prev_t = None; prev_sha = None
    while True:
        t_start = time.time()
        try:
            rt, body = await asyncio.to_thread(fetch, sport)
        except Exception as ex:
            gs_err[sport] += 1; gs_err_kinds[sport][repr(ex)[:80]] += 1; await asyncio.sleep(1.0); continue
        gs_poll_t[sport].append(rt)
        sha = hashlib.sha1(body).hexdigest()
        if sha != prev_sha: gs_change_t[sport].append(rt); prev_sha = sha
        else:
            await asyncio.sleep(max(0.0, 1.0 - (time.time() - t_start))); prev_t = rt; continue
        if prev_t is not None and rt - prev_t > OUTAGE_S: base.clear()
        prev_t = rt
        process_body(sport, rt, body, base)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t_start)))

def hour_file(root, sport, t):
    d = os.path.join(root, "esports_payloads" if sport == "esports" else sport + "_payloads")
    return os.path.join(d, "%s_%s.jsonl.gz" % (sport, time.strftime("%Y%m%d%H", time.gmtime(t))))

def read_new(path, off):
    """Rows appended to a capture hour file since compressed-byte offset `off`: the capture appends one complete gzip member per row, so decode whole members only and
    leave a partly written trailing member for the next call. -> (rows, new offset)."""
    try:
        with open(path, "rb") as f: f.seek(off); data = f.read()
    except FileNotFoundError: return [], off
    rows = []; pos = 0
    while pos < len(data):
        d = zlib.decompressobj(31)
        try: out = d.decompress(data[pos:])
        except zlib.error: break
        if not d.eof: break
        pos += len(data) - pos - len(d.unused_data)
        for l in out.decode("utf-8", "replace").splitlines():
            if l.strip():
                try: rows.append(json.loads(l))
                except Exception: gs_err["capture_bad_row"] += 1
    return rows, off + pos

async def gs_tail(sport):
    """Reads the capture's own stored payloads (same host and clock; recv_ns is the capture's receive time): no extra Goalserve requests, so no 429 for the key the capture uses."""
    base = {}; cur = None; off = 0
    while True:
        now = time.time(); path = hour_file(SOURCE["root"], sport, now)
        if cur is None:
            cur = path; off = os.path.getsize(path) if os.path.exists(path) else 0      # start at the end: only rows from now on
        rows = []
        if path != cur:                                                        # hour rollover: drain the old file, then start the new one at 0
            rows, off = await asyncio.to_thread(read_new, cur, off); cur, off = path, 0
        r2, off = await asyncio.to_thread(read_new, cur, off); rows += r2
        for r in rows:
            try: rt = int(r["recv_ns"]) / 1e9; body = r["body"]
            except Exception: gs_err["capture_bad_row"] += 1; continue
            gs_poll_t[sport].append(rt); gs_change_t[sport].append(rt)
            process_body(sport, rt, body, base)
        await asyncio.sleep(0.5)

def tok_match(meta, outcomes):
    """The two outcomes are exactly the two teams, each outcome matching one team only: -> (idx of home outcome, idx of away outcome) or None."""
    if len(outcomes) != 2: return None
    r = []
    for o in outcomes:
        h, a = tmatch(meta["home"], o), tmatch(meta["away"], o)
        r.append("h" if h and not a else "a" if a and not h else None)
    if sorted(r, key=str) != ["a", "h"]: return None
    return r.index("h"), r.index("a")

def discover(sports):
    """Polymarket gamma /events by tag slug (active, open); match each live Goalserve game to a 2-outcome moneyline (match winner) whose outcomes are exactly its two teams.
    A game that matches more than one Polymarket event is dropped as AMBIGUOUS (never guessed)."""
    cands = collections.defaultdict(dict); scanned = 0
    for sp in sports:
        for tag in TAGS.get(sp, []):
            for off in range(0, 2000, 100):
                try: evs = get("https://gamma-api.polymarket.com/events?tag_slug=%s&active=true&closed=false&limit=100&offset=%d" % (tag, off))
                except Exception as ex: print("gamma error", tag, repr(ex)[:100], flush=True); break
                if not isinstance(evs, list): break
                scanned += len(evs)
                for ev in evs:
                    for mk in ev.get("markets", []):
                        if mk.get("sportsMarketType") != "moneyline": continue
                        tk, oc = jl(mk.get("clobTokenIds")), jl(mk.get("outcomes"))
                        if len(tk) != 2 or len(oc) != 2: continue
                        txt = (ev.get("title") or "") + " " + (mk.get("question") or "")
                        for g, meta in games.items():
                            if g[0] != sp: continue
                            if not (tmatch(meta["home"], txt) and tmatch(meta["away"], txt)): continue
                            r = tok_match(meta, oc)
                            if r: cands[g][tuple(tk)] = dict(q=mk.get("question", ""), title=ev.get("title", ""), tokens=tk, outcomes=oc, tok_home=tk[r[0]], tok_away=tk[r[1]], start=mk.get("gameStartTime"))
                if len(evs) < 100: break
    new = []
    for g, d in cands.items():
        if len(d) > 1:
            if g not in ambiguous: print("AMBIGUOUS (dropped):", games[g]["label"], [x["title"][:60] for x in d.values()], flush=True)
            ambiguous[g] = [x["title"] for x in d.values()]; continue
        v = list(d.values())[0]; have = pm_mk.setdefault(g, [])
        if not any(x["tokens"] == v["tokens"] for x in have): have.append(v); new += v["tokens"]
    return new, scanned

async def discover_loop():
    while True:
        new, scanned = await asyncio.to_thread(discover, SPORTS_RUN)
        new = [t for t in new if t not in sub_tokens]
        if new:
            sub_tokens.extend(new)
            ws = ws_ref["ws"]
            if ws is not None:
                try: await ws.send(json.dumps({"assets_ids": new, "operation": "subscribe"}))
                except Exception as ex: print("subscribe error", repr(ex)[:100], flush=True)
            print(time.strftime("%H:%M:%SZ", time.gmtime()), "gamma scanned", scanned, "| new tokens", len(new), "| matched games", sorted(games[g]["label"] for g in pm_mk), flush=True)
        await asyncio.sleep(120)

def mid_at(tok, x):
    i = bisect.bisect_right(mt.get(tok, []), x) - 1
    return mv[tok][i] if i >= 0 else None
def onset(tok, t0, sign):
    ts, vs = mt.get(tok, []), mv.get(tok, [])
    i = bisect.bisect_right(ts, t0 - 60) - 1
    base = vs[i] if i >= 0 else None
    for j in range(max(i + 1, 0), len(ts)):
        if ts[j] > t0 + 60: break
        if base is None: base = vs[j]; continue
        if sign * (vs[j] - base) >= THR: return ts[j] - t0
    return None
def R(tok, t, sign):
    a, b, c, d = mid_at(tok, t + 60), mid_at(tok, t), mid_at(tok, t - 5), mid_at(tok, t - 60)
    if None in (a, b, c, d): return None
    return sign * ((a - b) - (c - d))

def summarize():
    rows = []
    for e in events:
        if time.time() < e["t"] + 65: continue
        g = (e["sport"], e["eid"])
        for mk in pm_mk.get(g, []):
            tok = mk["tok_home"] if e["rising"] == "home" else mk["tok_away"]
            rows.append(dict(e, token=tok[:10], q=mk["q"][:60], onset_s=onset(tok, e["t"], 1), R=R(tok, e["t"], 1)))
    rnd = random.Random(20261119); plc = collections.defaultdict(list)
    for g, mks in pm_mk.items():
        ev_t = [e["t"] for e in events if (e["sport"], e["eid"]) == g]
        lo, hi = T0 + 90, time.time() - 65; got = 0; tries = 0
        while got < 10 and hi > lo and tries < 500:
            tries += 1; pt = rnd.uniform(lo, hi)
            if any(abs(pt - x) < 90 for x in ev_t): continue
            got += 1
            for mk in mks:
                for tok in (mk["tok_home"], mk["tok_away"]):
                    for sg in (1, -1): plc[g[0]].append(dict(onset_s=onset(tok, pt, sg), R=R(tok, pt, sg)))
    out = {}
    for sp in sorted({r["sport"] for r in rows} | set(plc)):
        r = [x for x in rows if x["sport"] == sp]; p = plc[sp]
        l = [x["onset_s"] for x in r if x["onset_s"] is not None]; pl = [x["onset_s"] for x in p if x["onset_s"] is not None]
        rr = [x["R"] for x in r if x["R"] is not None]; pr = [x["R"] for x in p if x["R"] is not None]
        out[sp] = dict(n_events=len(r), n_games=len({x["eid"] for x in r}), n_with_onset=len(l),
                       median_onset_s=(round(statistics.median(l), 2) if l else None),
                       share_price_onset_after_odds_event=(round(sum(1 for v in l if v > 0) / len(l), 3) if l else None),
                       placebo_n=len(pl), placebo_median_onset_s=(round(statistics.median(pl), 2) if pl else None),
                       mean_R_real=(round(statistics.mean(rr), 4) if rr else None), mean_R_placebo=(round(statistics.mean(pr), 4) if pr else None),
                       mean_d=(round(statistics.mean(rr) - statistics.mean(pr), 4) if rr and pr else None))
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

def preflight(sports):
    ck = clock_check(); res = {}
    pml = bool(pm_lag) and -0.25 < statistics.median(pm_lag) < 2.0
    for sp in sports:
        now = time.time()
        live = {eid for eid, t in gs_seen_now[sp].items() if now - t < 20}
        matched = [g for g in pm_mk if g[0] == sp and g[1] in live]
        toks = [t for g in matched for mk in pm_mk[g] for t in mk["tokens"]]
        ts = gs_poll_t[sp]; gaps = [b - a for a, b in zip(ts, ts[1:])]
        c = dict(clock_synchronised_under_50ms=ck["ok"],
                 goalserve_polling_ok=(len(ts) >= 5 and bool(gaps) and now - ts[-1] < 120 and q(gaps, .9) < 30) if SOURCE["mode"] == "capture" else (len(ts) >= 30 and bool(gaps) and statistics.median(gaps) < 2.0 and q(gaps, .9) < 6.0 and gs_err[sp] <= 0.5 * (len(ts) + gs_err[sp])),
                 goalserve_has_live_games_now=bool(live),
                 goalserve_has_an_accepted_winner_market=bool(mkt_ok[sp]),
                 a_live_game_matched_to_a_polymarket_market_naming_both_teams=bool(matched),
                 every_matched_token_has_a_book_message=bool(toks) and all(pm_n[t] > 0 for t in toks),
                 pm_server_timestamp_lag_plausible=pml)
        res[sp] = dict(report=all(c.values()), checks=c, goalserve_poll_gap_s_p10_p50_p90=[q(gaps, .1), q(gaps, .5), q(gaps, .9)],
                       goalserve_payload_change_gap_s_p50=q([b - a for a, b in zip(gs_change_t[sp], gs_change_t[sp][1:])], .5),
                       n_polls=len(ts), n_poll_errors=gs_err[sp], poll_error_kinds=dict(gs_err_kinds[sp].most_common(4)), accepted_market_names=dict(mkt_ok[sp].most_common(6)), ambiguous=[games[g]["label"] for g in ambiguous if g[0] == sp],
                       n_live_games=len(live), n_matched_games=len(matched), matched=[games[g]["label"] for g in matched],
                       unmatched_live=[games[(sp, e)]["label"] for e in live if (sp, e) not in pm_mk][:15],
                       market_names_seen=dict(mkt_names[sp].most_common(40)))
    return dict(clock=ck, pm_lag_s_p10_p50_p90=[q(pm_lag, .1), q(pm_lag, .5), q(pm_lag, .9)], n_pm_msgs=sum(pm_n.values()), per_sport=res)

async def main():
    a = argparse.ArgumentParser(); a.add_argument("--sports", default="esports,tennis,hockey_nhl"); a.add_argument("--minutes", type=float, default=90); a.add_argument("--out", required=True); a.add_argument("--source", choices=["capture", "poll"], default="capture"); a.add_argument("--gs-root", default=SOURCE["root"]); a = a.parse_args()
    SOURCE["mode"] = a.source; SOURCE["root"] = a.gs_root
    if SOURCE["mode"] == "poll" and not (CRED.get("GOALSERVE_USER") and CRED.get("GOALSERVE_KEY")): sys.exit("FATAL no Goalserve credentials readable in /etc/pkarbs/goalserve.env")
    sports = [s for s in a.sports.split(",") if s in ENDPOINT]; SPORTS_RUN[:] = sports
    od = os.path.dirname(os.path.abspath(a.out)) or "."
    if shutil.disk_usage(od).free < 15e9: sys.exit("DISK GATE: under 15 GB free on the output volume; nothing started")
    tasks = [asyncio.create_task((gs_tail if SOURCE["mode"] == "capture" else gs_poll)(s)) for s in sports]
    await asyncio.sleep(20)                     # let live games appear before the first discovery
    tasks += [asyncio.create_task(discover_loop()), asyncio.create_task(pm_ws())]
    await asyncio.sleep(70)
    pre = preflight(sports)
    print("PREFLIGHT", json.dumps(pre, default=str), flush=True)
    ok = [s for s in sports if pre["per_sport"][s]["report"]]
    for s in sports:
        if s not in ok: print("NO NUMBER for %s: failed checks %s" % (s, [k for k, v in pre["per_sport"][s]["checks"].items() if not v]), flush=True)
    if not ok: print("No sport passed preflight now; probe keeps running and re-checks at the end.", flush=True)
    end = time.time() + a.minutes * 60; nxt = time.time() + 300
    while time.time() < end:
        await asyncio.sleep(10)
        if time.time() > nxt:
            nxt += 300; _, s = summarize(); pc = preflight(sports)
            print(time.strftime("%H:%M:%SZ", time.gmtime()), "events:", len(events), json.dumps(s), "| preflight", json.dumps({k: dict(report=v["report"], live=v["n_live_games"], matched=v["n_matched_games"], failed=[c for c, ok in v["checks"].items() if not ok], polls=v["n_polls"], errs=v["n_poll_errors"]) for k, v in pc["per_sport"].items()}), flush=True)
    await asyncio.sleep(65); pre2 = preflight(sports); rows, s = summarize()
    passed = {sp: v for sp, v in s.items() if pre2["per_sport"].get(sp, {}).get("report") or pre["per_sport"].get(sp, {}).get("report")}
    json.dump(dict(status="EXPLORATORY LIVE PROBE, UNCHECKED; bookmaker not identified (bm empty, vendor docs say bet365); tennis = open-market moves only",
                   preflight_start=pre, preflight_end=pre2, summary_passed_sports=passed, summary_all=s, n_events=len(events),
                   rows=rows, events=events, pm_markets={"%s|%s" % k: v for k, v in pm_mk.items()}), open(a.out, "w"), indent=1, default=str)
    print("FINAL", json.dumps(passed), flush=True)
if __name__ == "__main__":
    asyncio.run(main())
