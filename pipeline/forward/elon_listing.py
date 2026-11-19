"""Elon 48h tweet-count bracket listing: capture to the second, pre-registered resting-bid paper test, plausibility check.
Subcommands: record --out DIR --hourly FILE [--max-hours H]; evaluate --out DIR --hourly FILE; check --out DIR [--hourly FILE].
Rule: RULE-elon-listing.md. Never places orders."""
import argparse, bisect, collections, datetime as dt, gzip, json, math, os, re, sys, time, urllib.request
SERIES = "elon-tweets-48h"; GAMMA = "https://gamma-api.polymarket.com"; CLOB = "https://clob.polymarket.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip", "Content-Type": "application/json"}
K, BIAS = 0.3428, -0.0342
BANKROLL, STAKE_CAP, KELLY, PMIN, MARGIN = 1000.0, 100.0, 0.25, 0.10, 0.05


def jget(url, body=None, timeout=15):
    req = urllib.request.Request(url, data=(json.dumps(body).encode() if body is not None else None), headers=UA)
    r = urllib.request.urlopen(req, timeout=timeout); b = r.read()
    if r.headers.get("Content-Encoding") == "gzip": b = gzip.decompress(b)
    return json.loads(b)


def parse_bracket(q):
    m = re.search(r"post (<?\d+\+?|\d+-\d+) tweets", q or "")
    if not m: return None
    s = m.group(1)
    if s.startswith("<"): return (0, int(s[1:]) - 1)
    if s.endswith("+"): return (int(s[:-1]), 10 ** 9)
    a, b = s.split("-"); return (int(a), int(b))


def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def load_hourly(path):
    h = json.load(open(path)); ks = sorted(h)
    return (dict((dt.datetime.fromisoformat(k.replace("Z", "+00:00")).timestamp(), float(h[k])) for k in ks))


def model(hourly, t0, end):
    """p_i inputs: mu, sd from the 21 days before t0 (hours strictly before t0)."""
    prof = collections.defaultdict(list)
    for ts, v in hourly.items():
        if t0 - 21 * 86400 <= ts < t0: prof[int((ts % 86400) // 3600)].append(v)
    p = [sum(prof[h]) / len(prof[h]) if prof[h] else 0.0 for h in range(24)]
    start = end - 172800; mu = 0.0; x = start
    while x < end:
        nx = min(end, (x // 3600 + 1) * 3600); mu += p[int((x % 86400) // 3600)] * (nx - x) / 3600; x = nx
    mu0 = mu; mu = mu0 * (1 + BIAS); sd = max(K * mu0, math.sqrt(max(mu0, 1)))
    latest = max([t for t in hourly if t < t0], default=0)
    return mu, sd, (t0 - latest) / 86400


def bprob(lo, hi, mu, sd): return Phi((hi + 0.5 - mu) / sd) - Phi((lo - 0.5 - mu) / sd)


def event_brackets(ev):
    out = []
    for m in ev["markets"]:
        br = parse_bracket(m.get("question")); toks = json.loads(m["clobTokenIds"]) if isinstance(m["clobTokenIds"], str) else m["clobTokenIds"]
        outs = json.loads(m["outcomes"]) if isinstance(m["outcomes"], str) else m["outcomes"]
        if not br or len(toks) != 2: continue
        iy = [o.lower() for o in outs].index("yes"); out.append(dict(lo=br[0], hi=br[1], yes=toks[iy], no=toks[1 - iy], cond=m["conditionId"]))
    return out


def orders_for(ev, hourly, t0):
    end = dt.datetime.fromisoformat(ev["endDate"].replace("Z", "+00:00")).timestamp()
    mu, sd, age_days = model(hourly, t0, end); res = []
    for b in event_brackets(ev):
        p = bprob(b["lo"], b["hi"], mu, sd); bid = math.floor(round((p - MARGIN) / 0.01, 9)) * 0.01
        o = dict(yes=b["yes"], lo=b["lo"], hi=b["hi"], p=p, bid=round(bid, 2), shares=0.0)
        if p >= PMIN and o["bid"] >= 0.02:
            f = (p - o["bid"]) / (1 - o["bid"]); o["shares"] = min(STAKE_CAP, KELLY * f * BANKROLL) / o["bid"]
        res.append(o)
    return dict(mu=mu, sd=sd, hourly_age_days=age_days, stale=age_days > 3.0, orders=res)


def slim_book(b):
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))[:20]
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)[:5]
    return dict(asks=asks, bids=bids, ts=b.get("timestamp"))


def snapshot(tokens):
    t0 = time.time(); d = jget(CLOB + "/books", [{"token_id": t} for t in tokens]); t1 = time.time()
    return dict(t_local=t0, t_resp=t1, books={x["asset_id"]: slim_book(x) for x in d})


def cadence_ok(t0, now, end):
    a = now - t0
    if a <= 1800: return 1.0
    if a <= 7200: return 5.0
    if a <= 21600: return 30.0
    return 300.0


def in_poll_window(now):
    h = now.hour + now.minute / 60
    return 15 + 55 / 60 <= h <= 17 + 40 / 60


def record(out, hourly_path, max_hours, poll=None):
    os.makedirs(out, exist_ok=True); seen = set(json.load(open(f"{out}/seen.json"))) if os.path.exists(f"{out}/seen.json") else set()
    active = {}; t_end = time.time() + max_hours * 3600
    # on start, existing open events are marked seen (not captured as listings)
    if not seen:
        for e in jget(f"{GAMMA}/events/keyset?closed=false&limit=20&series_slug={SERIES}").get("events", []): seen.add(e["id"])
        json.dump(sorted(seen), open(f"{out}/seen.json", "w"))
    last_poll = 0.0
    while time.time() < t_end:
        now = time.time(); nd = dt.datetime.fromtimestamp(now, dt.timezone.utc)
        if now - last_poll >= (2.0 if in_poll_window(nd) else 30.0):
            last_poll = now
            try:
                for e in jget(f"{GAMMA}/events/keyset?closed=false&limit=20&series_slug={SERIES}").get("events", []):
                    if e["id"] in seen: continue
                    seen.add(e["id"]); json.dump(sorted(seen), open(f"{out}/seen.json", "w"))
                    t0 = time.time(); hourly = load_hourly(hourly_path); od = orders_for(e, hourly, t0)
                    d = f"{out}/{e['id']}"; os.makedirs(d, exist_ok=True)
                    toks = [x for b in event_brackets(e) for x in (b["yes"], b["no"])]
                    meta = dict(event_id=e["id"], slug=e.get("slug"), title=e["title"], t0=t0, createdAt=e.get("createdAt"), startDate=e.get("startDate"), endDate=e["endDate"],
                                tokens=toks, orders=od, brackets=event_brackets(e)); json.dump(meta, open(f"{d}/meta.json", "w"))
                    active[e["id"]] = dict(meta=meta, dir=d, next=0.0)
                    print("NEW EVENT", e["title"], "T0", t0, "stale" if od["stale"] else "", flush=True)
            except Exception as ex:
                print("poll error", ex, flush=True)
        for eid, a in list(active.items()):
            end = dt.datetime.fromisoformat(a["meta"]["endDate"].replace("Z", "+00:00")).timestamp()
            if now >= end - 172800 + 60: del active[eid]; continue
            if now >= a["next"]:
                try:
                    s = snapshot(a["meta"]["tokens"]); open(f"{a['dir']}/books.jsonl", "a").write(json.dumps(s) + "\n")
                except Exception as ex:
                    print("snap error", ex, flush=True)
                a["next"] = now + cadence_ok(a["meta"]["t0"], now, end)
        time.sleep(0.2)


def load_capture(d):
    meta = json.load(open(f"{d}/meta.json")); snaps = [json.loads(l) for l in open(f"{d}/books.jsonl")]
    return meta, snaps


def simulate(meta, snaps):
    """paper fills for every order from recorded asks only. returns list of fills dicts."""
    fills = []
    for o in meta["orders"]["orders"]:
        if o["shares"] <= 0: continue
        left = o["shares"]; cap = {}; seen_max = {}; got = []
        for s in snaps:
            bk = s["books"].get(o["yes"])
            if not bk or left <= 1e-9: continue
            for px, sz in bk["asks"]:
                seen_max[px] = max(seen_max.get(px, 0.0), sz)
            for px, sz in bk["asks"]:
                if px > o["bid"] + 1e-9: break
                room = seen_max[px] - cap.get(px, 0.0); take = min(left, sz, room)
                if take > 1e-9:
                    cap[px] = cap.get(px, 0.0) + take; left -= take; got.append(dict(t=s["t_local"], px=px, shares=take, depth_at_px=sz))
                if left <= 1e-9: break
        fills.append(dict(yes=o["yes"], lo=o["lo"], hi=o["hi"], p=o["p"], bid=o["bid"], ordered=o["shares"], fills=got))
    return fills


def settle(fills, winner_yes):
    pnl = stake = 0.0
    for f in fills:
        for g in f["fills"]:
            stake += g["px"] * g["shares"]; pnl += g["shares"] * ((1 - g["px"]) if f["yes"] == winner_yes else -g["px"])
    return pnl, stake


def winner_of(event_id):
    e = jget(f"{GAMMA}/events?id={event_id}")[0]
    for m in e["markets"]:
        pr = json.loads(m["outcomePrices"]) if isinstance(m["outcomePrices"], str) else m["outcomePrices"]
        toks = json.loads(m["clobTokenIds"]) if isinstance(m["clobTokenIds"], str) else m["clobTokenIds"]
        outs = json.loads(m["outcomes"]) if isinstance(m["outcomes"], str) else m["outcomes"]
        if float(pr[[o.lower() for o in outs].index("yes")]) == 1.0: return toks[[o.lower() for o in outs].index("yes")]
    return None


def evaluate(out):
    rows = []
    for eid in sorted(os.listdir(out)):
        d = f"{out}/{eid}"
        if not os.path.exists(f"{d}/books.jsonl"): continue
        meta, snaps = load_capture(d); w = winner_of(eid)
        if w is None: print(eid, "unresolved"); continue
        fl = simulate(meta, snaps); pnl, stake = settle(fl, w)
        rows.append(dict(event=eid, stale=meta["orders"]["stale"], pnl=pnl, stake=stake, n_fills=sum(len(f["fills"]) for f in fl)))
    return rows


def check(out, hourly_path=None):
    """Plausibility check of the latest capture. Returns list of (name, ok, detail)."""
    evs = sorted([e for e in os.listdir(out) if os.path.exists(f"{out}/{e}/books.jsonl")], key=lambda e: os.path.getmtime(f"{out}/{e}/meta.json"))
    if not evs: return [("capture exists", False, "no event with books.jsonl")]
    meta, snaps = load_capture(f"{out}/{evs[-1]}"); res = []
    nb = len(meta["brackets"]); res.append(("brackets", nb == 10, f"{nb} brackets, {len(meta['tokens'])} tokens"))
    first = snaps[0]["books"]; miss = [t for t in meta["tokens"] if t not in first]; res.append(("all tokens in first snapshot", not miss, f"missing {len(miss)}"))
    bad = []
    for s in snaps[:300]:
        for t, b in s["books"].items():
            if b["asks"] and b["bids"] and not (b["bids"][0][0] < b["asks"][0][0]): bad.append(t)
            for px, _ in b["asks"] + b["bids"]:
                if not 0 < px < 1: bad.append(t)
    res.append(("bid < ask and prices in (0,1)", not bad, f"{len(bad)} violations"))
    gaps = [snaps[i + 1]["t_local"] - snaps[i]["t_local"] for i in range(len(snaps) - 1) if snaps[i]["t_local"] - meta["t0"] <= 300]
    res.append(("snapshot gaps first 5 min", bool(gaps) and sorted(gaps)[len(gaps) // 2] <= 1.5 and max(gaps) <= 10, f"n {len(gaps)} median {sorted(gaps)[len(gaps)//2]:.2f}s max {max(gaps):.2f}s" if gaps else "no gaps"))
    ca = meta.get("createdAt"); lat = (meta["t0"] - dt.datetime.fromisoformat(ca.replace("Z", "+00:00")).timestamp()) if ca else None
    res.append(("detection latency vs createdAt (s)", lat is not None and 0 <= lat <= 120, f"{lat}"))
    ya = sum(first[b["yes"]]["asks"][0][0] for b in meta["brackets"] if b["yes"] in first and first[b["yes"]]["asks"])
    res.append(("sum of YES best asks >= 0.98", ya >= 0.98, f"{ya:.3f}"))
    ps = sum(o["p"] for o in meta["orders"]["orders"]); res.append(("model p sums to 1 +- 0.02", abs(ps - 1) <= 0.02, f"{ps:.3f}"))
    res.append(("hourly file fresh (age days <= 3)", not meta["orders"]["stale"], f"{meta['orders']['hourly_age_days']:.2f}"))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["record", "evaluate", "check"]); ap.add_argument("--out", required=True); ap.add_argument("--hourly"); ap.add_argument("--max-hours", type=float, default=30.0)
    a = ap.parse_args()
    if a.cmd == "record": record(a.out, a.hourly, a.max_hours)
    elif a.cmd == "evaluate": print(json.dumps(evaluate(a.out), indent=1))
    else:
        for n, ok, d in check(a.out, a.hourly): print("PASS" if ok else "FAIL", n, d)
