#!/usr/bin/env python3
"""Volume-first opportunity scanner (Polymarket + Kalshi). ONE script, public data only.

STEP 1  VOLUME GATE. Daily volume per market category/series (live, public). Only units with
        >= GATE_USD/day (conservative notional) go on. Everything else is printed and dropped.
STEP 2  Only for units that pass: random sample of resolved markets over the last WINDOW_DAYS
        (min market size MIN_MKT_USD, so no tiny markets), hourly price paths, then SIX fixed
        candidate rules (calibration/favourite-longshot + drift after big moves), each with
        held-out half, Bernoulli-null placebo, cluster bootstrap CI, top-3 concentration,
        Bonferroni over (rules x units), after fees and slippage.
OUTPUT  one table ranked by capturable $/day (lower-95%-CI edge, test half only, >=0).
        No dollar figure is quoted unless the unit passed the gate; the capturable column is 0
        unless the rule PASSES. Run:  python3 scan/volume_first_scan.py [--quick]

Conventions (blunt and conservative):
 * Polymarket gamma volume counts ~2x trade notional (project memory) -> multiplied by 0.5.
 * Kalshi volume is contracts; notional = contracts * min(p,1-p) (understates, never overstates).
 * Weather and Polymarket up/down 5-minute markets are excluded (other projects own them).
 * Entry costs: Kalshi buy at ask (YES) / 1-bid (NO). Polymarket: mid +/- SLIP (PM history has
   no book). Fee: PM feeSchedule.rate*p*(1-p) per share if feesEnabled; Kalshi 0.07*p*(1-p).
 * Capturable $/day = min(CAP_USD, PARTICIPATION * unit adjusted daily volume * share of that
   volume the rule's state covers) * max(0, lower-95% net edge per $ on the TEST half) -- only
   when the rule passes; the 'if-edge-were-real' column is shown separately and labelled so.
"""
import argparse, json, math, os, random, re, sys, time, hashlib
from collections import defaultdict
import numpy as np
import requests

GATE_USD = 1_000_000          # adjusted $/day floor
CAP_USD = 10_000              # target $/day of trades
PARTICIPATION = 0.02          # max share of the volume we assume we can take
WINDOW_DAYS = 60              # resolved-market window (Kalshi live API only goes back to the cutoff)
MIN_MKT_USD = 25_000          # min market size entering the test
SAMPLE_MKTS = 150             # markets per unit
SLIP_PM = float(os.environ.get("SCAN_SLIP", 0.015))               # assumed adverse entry slippage on Polymarket
PM_FACTOR = 0.5               # gamma volume -> trade notional
MOVE_C, MOVE_H = 0.10, 3      # "big move": >=10c within 3 hours
RULES = ["LS_fade", "LS_buy", "FAV_buy", "FAV_fade", "MOVE_follow", "MOVE_fade"]
N_SIM = 2000
SEED = int(os.environ.get("SCAN_SEED", 7))

# Nick 11 Nov 03:09Z: never re-check markets already scanned in this project. Matched on lower-case unit name.
ALREADY_SCANNED = {
    # tested by this script on 11 Nov (scan/OUT-volume-first-scan-2026-11-11.md)
    "nba", "elections", "politics", "fed", "league:nba", "league:ncaaf", "league:nfl", "league:ncaamb", "league:nhl",
    # earlier project work
    "nhl", "nfl", "cfb", "tennis", "atp", "wta", "league:atp", "league:wta", "cs2", "counter-strike", "league-of-legends",
    "lol", "dota-2", "esports", "league:cs2", "league:lol", "league:dota", "rugby", "chess", "cricket", "mentions",
    "elon-musk", "tweet-markets", "box-office", "movies", "netflix", "bitcoin", "ethereum", "crypto", "league:valorant",
    "inflation", "economy", "gas", "weather",
}
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
KAL = "https://api.elections.kalshi.com/trade-api/v2"
CACHE = os.environ.get("SCAN_CACHE", "/tmp/claude-0/scan_cache")
os.makedirs(CACHE, exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "volume-first-scan/1.0"
_last = [0.0]


def get(url, params=None, sleep=0.25, tries=8):
    key = hashlib.md5((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    fp = f"{CACHE}/{key}.json"
    if os.path.exists(fp) and "events?" not in url and time.time() - os.path.getmtime(fp) < 6 * 3600:
        return json.load(open(fp))
    for i in range(tries):
        w = _last[0] + sleep - time.time()
        if w > 0:
            time.sleep(w)
        _last[0] = time.time()
        try:
            r = S.get(url, params=params, timeout=40)
        except requests.RequestException:
            time.sleep(2 ** i); continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(30, 2 ** i)); continue
        if r.status_code != 200:
            return None
        d = r.json()
        if d != {"history": []}:
            json.dump(d, open(fp, "w"))
        return d
    return None


def fl(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


# ------------------------------------------------------------------ STEP 1: volume gate
PM_PRIORITY = ["nba", "nfl", "nhl", "mlb", "cfb", "college-football", "ncaab", "college-basketball", "wnba",
               "epl", "premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "champions-league", "ucl", "mls",
               "soccer", "tennis", "atp", "wta", "cs2", "counter-strike", "league-of-legends", "lol", "dota-2",
               "valorant", "esports", "ufc", "mma", "boxing", "golf", "cricket", "rugby", "f1", "formula-1",
               "mentions", "elon-musk", "tweet-markets", "box-office", "movies", "netflix", "music", "spotify",
               "bitcoin", "ethereum", "solana", "crypto", "fed", "fed-rates", "economy", "inflation", "stocks", "finance",
               "elections", "politics", "trump", "geopolitics", "world", "tech", "ai", "culture", "pop-culture"]


def pm_cat(ev):
    tags = [t.get("slug", "") for t in ev.get("tags") or []]
    ts = " ".join(tags)
    title = (ev.get("title") or "").lower()
    if "weather" in ts or "temperature" in ts or "highest-temperature" in (ev.get("slug") or ""):
        return "EXCL weather", None
    if "up or down" in title or "up-or-down" in ts or "5m" in tags or "15m" in tags:
        return "EXCL crypto up/down", None
    for p in PM_PRIORITY:
        if p in tags:
            return p, p
    generic = {"sports", "hide-from-new", "recurring", "all", "featured", "parent-for-derivative"}
    for t in tags:
        if t not in generic:
            return t, t
    return "untagged", None


def pm_volumes():
    out = defaultdict(lambda: {"d1": 0.0, "d7": 0.0, "n": 0, "slug": None})
    off = 0
    while off < 6000:
        d = get(f"{GAMMA}/events", {"closed": "false", "order": "volume24hr", "ascending": "false",
                                    "limit": 100, "offset": off})
        if not d:
            break
        for ev in d:
            c, slug = pm_cat(ev)
            o = out[c]
            o["d1"] += fl(ev.get("volume24hr")) * PM_FACTOR
            o["d7"] += fl(ev.get("volume1wk")) / 7 * PM_FACTOR
            o["n"] += 1
            o["slug"] = o["slug"] or slug
        if fl(d[-1].get("volume24hr")) < 500:
            break
        off += 100
    return out


KAL_LEAGUE = re.compile(r"^KX(NBA|NFL|NHL|MLB|NCAAF|NCAAMB|NCAAWB|WNBA|MLS|EPL|UCL|LALIGA|BUNDESLIGA|SERIEA|LIGUE1|ATP|WTA|UFC|PGA|CS2|LOL|DOTA|VALORANT|F1|NASCAR)")


def kal_family(series, cat):
    m = KAL_LEAGUE.match(series)
    return ("league:" + m.group(1)) if m else series


def kal_volumes(max_pages=500):
    out = defaultdict(lambda: {"d1": 0.0, "n": 0, "series": defaultdict(float), "cat": ""})
    cur = None
    for _ in range(max_pages):
        p = {"status": "open", "with_nested_markets": "true", "limit": 200}
        if cur:
            p["cursor"] = cur
        d = get(f"{KAL}/events", p, sleep=0.35)
        if not d:
            break
        for ev in d.get("events", []):
            cat = ev.get("category") or ""
            if "Weather" in cat:
                continue
            fam = kal_family(ev.get("series_ticker", ""), cat)
            for m in ev.get("markets", []):
                v = fl(m.get("volume_24h_fp"))
                if v <= 0:
                    continue
                p_ = fl(m.get("last_price_dollars"), 0.5)
                if p_ <= 0 or p_ >= 1:
                    p_ = (fl(m.get("yes_bid_dollars")) + fl(m.get("yes_ask_dollars"))) / 2 or 0.5
                o = out[fam]
                o["d1"] += v * min(p_, 1 - p_)
                o["n"] += 1
                o["series"][ev.get("series_ticker", "")] += v * min(p_, 1 - p_)
                o["cat"] = cat
        cur = d.get("cursor")
        if not cur:
            break
    return out


# ------------------------------------------------------------------ STEP 2: market samples
def jl(x):
    return json.loads(x) if isinstance(x, str) else (x or [])


def pm_markets(slug, since):
    """Resolved Polymarket markets of tag `slug`, closed since `since` (epoch)."""
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
    res, off = [], 0
    while off < 900:
        d = get(f"{GAMMA}/events", {"closed": "true", "tag_slug": slug, "end_date_min": iso,
                                    "limit": 100, "offset": off, "order": "endDate", "ascending": "false"})
        if not d:
            break
        for ev in d:
            if "up or down" in (ev.get("title") or "").lower():
                continue
            for m in ev.get("markets", []):
                try:
                    pr = [float(x) for x in jl(m.get("outcomePrices"))]
                    tok = jl(m.get("clobTokenIds"))[0]
                except Exception:
                    continue
                if len(pr) != 2 or max(pr) < 0.99:
                    continue                                   # unresolved/voided
                vol = fl(m.get("volumeNum")) * PM_FACTOR
                if vol < MIN_MKT_USD:
                    continue
                fs = m.get("feeSchedule") or {}
                rate = fl(fs.get("rate")) if m.get("feesEnabled") else 0.0
                ct = m.get("closedTime") or ev.get("closedTime") or ""
                try:
                    cts = time.mktime(time.strptime(ct[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S"))
                except Exception:
                    continue
                if cts < since:
                    continue
                st = m.get("startDate") or ev.get("startDate") or ""
                res.append({"id": m["conditionId"], "ev": ev["id"], "tok": tok, "y": 1 if pr[0] > 0.5 else 0,
                            "close": cts, "vol": vol, "rate": rate, "start": st})
        if len(d) < 100:
            break
        off += 100
    return res


def pm_path(m):
    d = get(f"{CLOB}/prices-history", {"market": m["tok"], "interval": "max", "fidelity": 60}, sleep=0.2)
    h = (d or {}).get("history") or []
    if len(h) < 8:
        return None
    t = np.array([x["t"] for x in h], float)
    p = np.array([x["p"] for x in h], float)
    k = t <= m["close"]
    t, p = t[k], p[k]
    if len(t) < 8:
        return None
    # hourly grid, forward-filled
    g = np.arange(t[0], t[-1] + 1, 3600.0)
    idx = np.searchsorted(t, g, side="right") - 1
    mid = p[np.clip(idx, 0, len(p) - 1)]
    return {"mid": mid, "ask": np.minimum(mid + SLIP_PM, 0.995), "bid": np.maximum(mid - SLIP_PM, 0.005)}


def kal_markets(series_list, since, per_series=400):
    res = []
    for s in series_list:
        cur, got = None, 0
        while got < per_series:
            p = {"series_ticker": s, "status": "settled", "min_close_ts": int(since), "limit": 1000}
            if cur:
                p["cursor"] = cur
            d = get(f"{KAL}/markets", p, sleep=0.35)
            if not d:
                break
            for m in d.get("markets", []):
                if m.get("result") not in ("yes", "no"):
                    continue
                vol = fl(m.get("volume_fp")) * 0.5
                if vol < MIN_MKT_USD:
                    continue
                try:
                    ct = time.mktime(time.strptime(m["close_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
                    ot = time.mktime(time.strptime(m["open_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
                except Exception:
                    continue
                res.append({"id": m["ticker"], "ev": m.get("event_ticker"), "series": s, "y": int(m["result"] == "yes"),
                            "close": ct, "open": ot, "vol": vol, "rate": 0.07})
            got += len(d.get("markets", []))
            cur = d.get("cursor")
            if not cur:
                break
    return res


def kal_path(m):
    start = max(m["open"], m["close"] - 21 * 86400)
    d = get(f"{KAL}/series/{m['series']}/markets/{m['id']}/candlesticks",
            {"start_ts": int(start), "end_ts": int(m["close"]), "period_interval": 60}, sleep=0.3)
    c = (d or {}).get("candlesticks") or []
    if len(c) < 8:
        return None
    ask, bid = [], []
    la, lb = None, None
    for x in c:
        a = fl((x.get("yes_ask") or {}).get("close_dollars"), -1)
        b = fl((x.get("yes_bid") or {}).get("close_dollars"), -1)
        if a >= 0:
            la = a
        if b >= 0:
            lb = b
        ask.append(la)
        bid.append(lb)
    ask = np.array([np.nan if v is None else v for v in ask])
    bid = np.array([np.nan if v is None else v for v in bid])
    ok = ~np.isnan(ask) & ~np.isnan(bid) & (ask > bid)
    if ok.sum() < 8:
        return None
    ask, bid = ask[ok], bid[ok]
    return {"mid": (ask + bid) / 2, "ask": ask, "bid": bid}


# ------------------------------------------------------------------ rules & stats
def fee(p, rate):
    return rate * p * (1 - p)


def observations(m, path):
    """Return {rule: (side, entry_price, net_return_per_$)} - first qualifying hour per market per rule."""
    mid, ask, bid, y, rate = path["mid"], path["ask"], path["bid"], m["y"], m["rate"]
    n = len(mid)
    out = {}
    life = [int(n * f) for f in (0.25, 0.5, 0.75)]

    def ret(side, i):
        cost = ask[i] if side == "Y" else 1 - bid[i]
        if not (0.01 <= cost <= 0.99):
            return None
        win = (y == 1) if side == "Y" else (y == 0)
        return (float(win) - cost - fee(cost, rate)) / cost, cost

    def add(rule, side, idxs):
        for i in idxs:
            if i < n - 2:
                r = ret(side, i)
                if r:
                    out.setdefault(rule, []).append((side, r[1], r[0]))

    ls = [i for i in life if 0.02 < mid[i] <= 0.10]
    fav = [i for i in life if 0.85 <= mid[i] < 0.98]
    cheap = [i for i in life if 0.03 < mid[i] <= 0.30]
    add("CHEAP_BUY", "Y", cheap); add("CHEAP_FADE", "N", cheap)
    add("LS_fade", "N", ls); add("LS_buy", "Y", ls)
    add("FAV_buy", "Y", fav); add("FAV_fade", "N", fav)
    # drift after big move: first hour (with 1h delay) where |mid[i]-mid[i-H]| >= MOVE_C
    for i in range(MOVE_H, n - 3):
        dlt = mid[i] - mid[i - MOVE_H]
        if abs(dlt) >= MOVE_C and 0.05 < mid[i] < 0.95:
            j = i + 1                                   # act one hour later
            up = dlt > 0
            add("MOVE_follow", "Y" if up else "N", [j])
            add("MOVE_fade", "N" if up else "Y", [j])
            break
    return out


def boot_ci(vals, groups, rng, B=1000):
    g = defaultdict(list)
    for v, k in zip(vals, groups):
        g[k].append(v)
    keys = list(g)
    sums = np.array([sum(g[k]) for k in keys]); cnt = np.array([len(g[k]) for k in keys])
    if len(keys) < 5:
        return (float("nan"),) * 3
    idx = rng.integers(0, len(keys), (B, len(keys)))
    means = sums[idx].sum(1) / cnt[idx].sum(1)
    return float(sums.sum() / cnt.sum()), float(np.percentile(means, 2.5)), float(np.std(means))


def evaluate(unit_obs, rule, rng, ntests):
    rows = unit_obs  # list of dict(close, ev, mid_id, side, cost, ret)
    rows = sorted(rows, key=lambda r: r["close"])
    if len(rows) < 30:
        return None
    half = len(rows) // 2
    tr, te = rows[:half], rows[half:]
    def mean(x): return float(np.mean([r["ret"] for r in x])) if x else float("nan")
    res = {"n": len(rows), "markets": len({r["mid_id"] for r in rows}), "train": mean(tr), "test": mean(te)}
    m, lo, sd = boot_ci([r["ret"] for r in te], [r["ev"] for r in te], rng)
    res.update(test_lo=lo, test_sd=sd)
    # placebo: outcomes ~ Bernoulli(entry price) with the same fees (efficient-market null), test half
    sims = np.zeros(N_SIM)
    cost = np.array([r["cost"] for r in te]); side_n = np.array([r["side"] == "N" for r in te])
    fe = np.array([r["fee"] for r in te])
    win = rng.random((N_SIM, len(te))) < cost            # side wins w.p. its cost (fair price)
    simret = (win.astype(float) - cost - fe) / cost
    sims = simret.mean(1)
    res["placebo_mean"], res["placebo_sd"] = float(sims.mean()), float(sims.std())
    res["z"] = (res["test"] - res["placebo_mean"]) / res["placebo_sd"] if res["placebo_sd"] > 0 else float("nan")
    # top-3 concentration of test-half profit (by market)
    pm_ = defaultdict(float)
    for r in te:
        pm_[r["mid_id"]] += r["ret"]
    tot = sum(pm_.values())
    top = sum(sorted(pm_.values(), reverse=True)[:3])
    res["top3"] = top / tot if tot > 0 else float("nan")
    zthr = abs(np.sqrt(2) * math.erf(0) + 0) or 0
    from statistics import NormalDist
    zthr = NormalDist().inv_cdf(1 - 0.05 / ntests)
    res["zthr"] = zthr
    res["pass"] = bool(res["train"] > 0 and res["test"] > 0 and res["test_lo"] > 0 and res["z"] >= zthr
                       and (res["top3"] != res["top3"] or res["top3"] <= 0.5))
    return res


# ------------------------------------------------------------------ main
def usd(x): return f"${x:,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="40 markets per unit")
    ap.add_argument("--max-units", type=int, default=12)
    ap.add_argument("--only", default="", help="comma list of unit names to test (replication runs)")
    ap.add_argument("--out", default="scan/OUT-volume-first-scan.md")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED); random.seed(SEED)
    n_samp = 40 if a.quick else SAMPLE_MKTS
    now = time.time(); since = now - WINDOW_DAYS * 86400
    lines = []
    def P(s=""): print(s, flush=True); lines.append(s)

    P(f"# Volume-first scan {time.strftime('%Y-%m-%d %H:%MZ', time.gmtime(now))}")
    P(f"Gate = {usd(GATE_USD)}/day conservative notional. PM gamma volume x{PM_FACTOR}; Kalshi contracts x min(p,1-p). "
      f"Weather + PM up/down excluded.\n")
    # STEP 1
    pm = pm_volumes(); kl = kal_volumes()
    units = []
    P("## STEP 1 - volume gate")
    P("| venue | unit | 24h $ (adj) | 7d avg $/day (adj) | gate value | pass |")
    P("|---|---|---:|---:|---:|---|")
    for c, o in sorted(pm.items(), key=lambda kv: -kv[1]["d1"]):
        if c.startswith("EXCL"):
            P(f"| PM | {c} | {usd(o['d1'])} | {usd(o['d7'])} | - | excluded |"); continue
        gv = min(o["d1"], o["d7"]) if o["d7"] else o["d1"]
        if c.lower() in ALREADY_SCANNED:
            P(f"| PM | {c} | {usd(o['d1'])} | {usd(o['d7'])} | - | already scanned, skipped |"); continue
        ok = gv >= GATE_USD and o["slug"]
        if o["d1"] >= 0.3 * GATE_USD or ok:
            P(f"| PM | {c} ({o['n']} events) | {usd(o['d1'])} | {usd(o['d7'])} | {usd(gv)} | {'PASS' if ok else 'no'} |")
        if ok:
            units.append({"venue": "PM", "name": c, "slug": o["slug"], "daily": gv})
    for c, o in sorted(kl.items(), key=lambda kv: -kv[1]["d1"]):
        if c.lower() in ALREADY_SCANNED or any(x.lower() in ALREADY_SCANNED for x in ("league:" + c,)):
            continue
        ok = o["d1"] >= GATE_USD
        if o["d1"] >= 0.3 * GATE_USD:
            P(f"| Kalshi | {c} [{o['cat']}] ({o['n']} mkts) | {usd(o['d1'])} | n/a | {usd(o['d1'])} | {'PASS' if ok else 'no'} |")
        if ok:
            units.append({"venue": "K", "name": c, "series": [k for k, _ in sorted(o["series"].items(), key=lambda kv: -kv[1])], "daily": o["d1"]})
    # gap table: top 15 unscanned units by volume, always printed
    gap = [("PM", c, min(o["d1"], o["d7"]) if o["d7"] else o["d1"], o["d1"]) for c, o in pm.items()
           if not c.startswith("EXCL") and c.lower() not in ALREADY_SCANNED]
    gap += [("Kalshi", c, o["d1"], o["d1"]) for c, o in kl.items() if c.lower() not in ALREADY_SCANNED]
    gap.sort(key=lambda g: -g[2])
    P("\n### Top 15 unscanned units by volume (gate value, 24h)")
    P("| # | venue | unit | gate $/day | 24h $ |\n|---|---|---|---:|---:|")
    for i, g in enumerate(gap[:15], 1):
        P(f"| {i} | {g[0]} | {g[1]} | {usd(g[2])} | {usd(g[3])} |")
    P(f"\nPassed gate: {len(units)} units. Categories under the floor are dropped, no estimates for them.\n")
    units = sorted(units, key=lambda u: -u["daily"])[:a.max_units]
    if a.only:
        units = [u for u in units if u["name"] in a.only.split(",")]
    if not units:
        P("Nothing passes the volume gate. Stop."); open(a.out, "w").write("\n".join(lines)); return

    # STEP 2
    ntests = len(units) * len(RULES)
    P(f"## STEP 2 - candidate rules on gated units only ({len(units)} units x {len(RULES)} rules = {ntests} tests; "
      f"Bonferroni alpha 0.05/{ntests})")
    table = []
    for u in units:
        if u["venue"] == "PM":
            mk = pm_markets(u["slug"], since)
        else:
            mk = kal_markets(u["series"][:25], since)
        random.shuffle(mk)
        mk = mk[:n_samp]
        obs = defaultdict(list); used = 0
        for m in mk:
            path = pm_path(m) if u["venue"] == "PM" else kal_path(m)
            if not path:
                continue
            used += 1
            for rule, lst in observations(m, path).items():
                for side, cost, r in lst:
                    obs[rule].append({"close": m["close"], "ev": m["ev"], "mid_id": m["id"], "side": side,
                                      "cost": cost, "ret": r, "fee": fee(cost, m["rate"])})
        P(f"- {u['venue']} {u['name']}: {len(mk)} resolved markets sampled (>= {usd(MIN_MKT_USD)} each), {used} with usable price paths")
        tot_obs = sum(len(v) for v in obs.values()) or 1
        for rule in RULES:
            r = evaluate(obs.get(rule, []), rule, rng, ntests)
            if not r:
                table.append({"unit": f"{u['venue']} {u['name']}", "rule": rule, "daily": u["daily"], "res": None}); continue
            share = min(1.0, len(obs[rule]) / max(1, used * 3))     # share of sampled market-checkpoints in the rule's state
            deploy = min(CAP_USD, PARTICIPATION * u["daily"] * share)
            lb = max(0.0, r["test_lo"]) if r["pass"] else 0.0
            table.append({"unit": f"{u['venue']} {u['name']}", "rule": rule, "daily": u["daily"], "res": r,
                          "deploy": deploy, "cap": deploy * lb, "ifreal": deploy * max(0.0, r["test"])})
    table.sort(key=lambda t: (-(t.get("cap") or 0), -(t["res"]["z"] if t["res"] and t["res"]["z"] == t["res"]["z"] else -9)))
    P("\n## RESULT - ranked by capturable $/day (PASS only; otherwise $0)")
    P("| # | unit | rule | unit $/day | n obs | markets | train net/$ | TEST net/$ | TEST lo95 | placebo z (need) | top3 | verdict | capturable $/day |")
    P("|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|")
    for i, t in enumerate(table, 1):
        r = t["res"]
        if not r:
            P(f"| {i} | {t['unit']} | {t['rule']} | {usd(t['daily'])} | <30 | - | - | - | - | - | - | too few | $0 |"); continue
        P(f"| {i} | {t['unit']} | {t['rule']} | {usd(t['daily'])} | {r['n']} | {r['markets']} | {r['train']*100:+.1f}% | "
          f"{r['test']*100:+.1f}% | {r['test_lo']*100:+.1f}% | {r['z']:+.1f} ({r['zthr']:.1f}) | "
          f"{'n/a' if r['top3']!=r['top3'] else f'{r['top3']*100:.0f}%'} | {'PASS' if r['pass'] else 'FAIL'} | {usd(t['cap'])} |")
    npass = sum(1 for t in table if t["res"] and t["res"]["pass"])
    P(f"\n{npass} of {len(table)} tests pass. Net returns are per $ staked after fees and slippage, hold to settlement.")
    P("Not a claim of edge: the sample is the last 60 days of resolved markets only (venue API limit), a PASS still needs a forward test.")
    open(a.out, "w").write("\n".join(lines) + "\n")


# ====================================================================== LATE-WINNER MODE (default)
# Nick 11 Nov 03:28Z: target PROFIT POTENTIAL. Tell = good-size markets whose winning bucket only emerges late.
WIN_PM_DAYS, WIN_K_DAYS = 60, 21
LOW_PX = 0.30
ALREADY_RE = re.compile(r"^KX(BTC|ETH|SOL|XRP|DOGE|CPI|GAS|FED|HIGH|LOW|RAIN|SNOW|TEMP|WIND|HURR|ELON|TRUMPTWEET|TWEET|MENTION|"
                        r"BOXOFFICE|NETFLIX|CHESS|CRICKET|RUGBY|TENNIS|ITF|WTA|ATP|CHALL|NBA|NFL|NHL|NCAA|WNBA|CFB|CBB)")


def pm_trades(cond, tok, maxpages=20):
    """BUY trades of token `tok` (newest first). Returns (list[(price,size)], truncated)."""
    out, cur, trunc = [], None, False
    for pg in range(maxpages):
        d = get("https://data-api.polymarket.com/v2/trades", {"condition": cond, "limit": 500, **({"cursor": cur} if cur else {})}, sleep=0.2)
        if not d:
            break
        for t in d.get("data", []):
            if t.get("token_id") == tok and t.get("side") == "BUY":
                out.append((fl(t["price"]), fl(t["size"])))
        pg_ = d.get("pagination") or {}
        cur = pg_.get("next_cursor")
        if not (pg_.get("has_more") and cur):
            return out, False
    return out, True


def emergence(pw):
    """fraction of life at which winner-side price first STAYS above 0.5 (0 = always above)."""
    n = len(pw)
    below = np.where(pw <= 0.5)[0]
    if len(below) == 0:
        return 0.0
    if below[-1] >= n - 1:
        return None
    return float((below[-1] + 1) / n)


def title_key(t):
    t = re.sub(r"\d+(\.\d+)?", "#", (t or "").lower())
    t = re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", "M", t)
    return " ".join(t.split()[:6])


def pm_universe(since, max_events=1500):
    evs, off = [], 0
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
    while off < max_events:
        d = get(f"{GAMMA}/events", {"closed": "true", "end_date_min": iso, "order": "volume", "ascending": "false",
                                    "limit": 100, "offset": off})
        if not d:
            break
        evs += d
        if len(d) < 100:
            break
        off += 100
    out = []
    for ev in evs:
        cat, _ = pm_cat(ev)
        if cat.startswith("EXCL") or cat.lower() in ALREADY_SCANNED or "up or down" in (ev.get("title") or "").lower():
            continue
        evvol = fl(ev.get("volume")) * PM_FACTOR
        if evvol < 50_000:
            continue
        ms = []
        for m in ev.get("markets", []):
            try:
                pr = [float(x) for x in jl(m.get("outcomePrices"))]; toks = jl(m.get("clobTokenIds"))
            except Exception:
                continue
            if len(pr) != 2 or max(pr) < 0.99 or len(toks) != 2:
                continue
            fs = m.get("feeSchedule") or {}
            ct = (m.get("closedTime") or ev.get("closedTime") or "")[:19].replace("T", " ")
            try:
                cts = time.mktime(time.strptime(ct, "%Y-%m-%d %H:%M:%S"))
            except Exception:
                continue
            if cts < since:
                continue
            ms.append({"id": m["conditionId"], "ev": ev["id"], "toks": toks, "y": 1 if pr[0] > 0.5 else 0, "close": cts,
                       "vol": fl(m.get("volumeNum")) * PM_FACTOR, "rate": fl(fs.get("rate")) if m.get("feesEnabled") else 0.0})
        if ms:
            out.append({"ev": ev["id"], "cat": cat, "title": ev.get("title"), "vol": evvol, "markets": ms,
                        "multi": len(ms) >= 3, "tkey": title_key(ev.get("title"))})
    cnt = defaultdict(int)
    for e in out:
        cnt[e["tkey"]] += 1
    for e in out:
        e["series"] = ("PM " + e["tkey"]) if cnt[e["tkey"]] >= 3 else ("PM cat:" + e["cat"])
    return out


def kal_universe(since, max_pages=70):
    ms, cur = [], None
    for _ in range(max_pages):
        p = {"status": "settled", "min_close_ts": int(since), "limit": 1000, "mve_filter": "exclude"}
        if cur:
            p["cursor"] = cur
        d = get(f"{KAL}/markets", p, sleep=0.4)
        if not d:
            break
        ms += d.get("markets", [])
        cur = d.get("cursor")
        if not cur:
            break
    evs = defaultdict(list)
    for m in ms:
        if m.get("result") in ("yes", "no") and m.get("event_ticker"):
            evs[m["event_ticker"]].append(m)
    out = []
    for et, lst in evs.items():
        series = et.split("-")[0]
        if ALREADY_RE.match(series):
            continue
        vol = sum(fl(m.get("volume_fp")) for m in lst) * 0.5
        if vol < 50_000:
            continue
        mk = []
        for m in lst:
            try:
                ct = time.mktime(time.strptime(m["close_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
                ot = time.mktime(time.strptime(m["open_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            except Exception:
                continue
            mk.append({"id": m["ticker"], "ev": et, "series": series, "y": int(m["result"] == "yes"), "close": ct,
                       "open": ot, "vol": fl(m.get("volume_fp")) * 0.5, "rate": 0.07})
        if mk:
            out.append({"ev": et, "series": "K " + series, "vol": vol, "markets": mk, "multi": len(mk) >= 3})
    return out


def kal_winner_stats(m):
    """returns (emergence f, ceiling $ on cheap winner, cheap $ traded) from hourly candles; contracts*0.5 = taker-buy share."""
    start = max(m["open"], m["close"] - 21 * 86400)
    d = get(f"{KAL}/series/{m['series']}/markets/{m['id']}/candlesticks",
            {"start_ts": int(start), "end_ts": int(m["close"]), "period_interval": 60}, sleep=0.3)
    c = (d or {}).get("candlesticks") or []
    if len(c) < 8:
        return None
    mid, vol, la, lb = [], [], None, None
    for x in c:
        a = fl((x.get("yes_ask") or {}).get("close_dollars"), -1); b = fl((x.get("yes_bid") or {}).get("close_dollars"), -1)
        la = a if a >= 0 else la; lb = b if b >= 0 else lb
        mid.append(np.nan if la is None or lb is None else (la + lb) / 2)
        vol.append(fl(x.get("volume_fp")))
    mid, vol = np.array(mid), np.array(vol)
    ok = ~np.isnan(mid)
    if ok.sum() < 8:
        return None
    mid, vol = mid[ok], vol[ok]
    pw = mid if m["y"] == 1 else 1 - mid
    f = emergence(pw)
    if f is None:
        return None
    cheap = pw <= LOW_PX
    ceil = float((vol[cheap] * 0.5 * (1 - pw[cheap])).sum())
    cheap_usd = float((vol[cheap] * 0.5 * pw[cheap]).sum())
    return f, ceil, cheap_usd


def pm_winner_stats(m, side):
    tok = m["toks"][0 if side == "Y" else 1]
    d = get(f"{CLOB}/prices-history", {"market": tok, "interval": "max", "fidelity": 60}, sleep=0.2)
    h = (d or {}).get("history") or []
    pw = np.array([x["p"] for x in h if x["t"] <= m["close"]], float)
    if len(pw) < 8:
        return None
    f = emergence(pw)
    if f is None:
        return None
    tr, trunc = pm_trades(m["id"], tok)
    lo = [(p, s) for p, s in tr if p <= LOW_PX]
    return f, float(sum(s * (1 - p) for p, s in lo)), float(sum(s * p for p, s in lo)), trunc


def winners(ev):
    """list of (market, side) whose winning-side path is the object of study."""
    if ev["multi"]:
        return [(m, "Y") for m in ev["markets"] if m["y"] == 1]
    return [(m, "Y" if m["y"] == 1 else "N") for m in ev["markets"]]


def main_late(a):
    rng = np.random.default_rng(SEED); random.seed(SEED)
    now = time.time()
    lines = []
    def P(s=""): print(s, flush=True); lines.append(s)
    P(f"# Late-winner scan {time.strftime('%Y-%m-%d %H:%MZ', time.gmtime(now))}")
    P("Universe: resolved events, event size >= $50k adj, NOT already scanned in this project, weather/5-min excluded. "
      f"PM window {WIN_PM_DAYS}d (top by volume), Kalshi window {WIN_K_DAYS}d.\n")
    pu = pm_universe(now - WIN_PM_DAYS * 86400)
    ku = kal_universe(now - WIN_K_DAYS * 86400)
    P(f"Universe: PM {len(pu)} events, Kalshi {len(ku)} events.")
    series = defaultdict(lambda: {"evs": [], "days": 0})
    for e in pu:
        series[e["series"]]["evs"].append(e); series[e["series"]]["days"] = WIN_PM_DAYS
    for e in ku:
        series[e["series"]]["evs"].append(e); series[e["series"]]["days"] = WIN_K_DAYS
    # ---- screen: emergence + cheap-winner ceiling per series (sampled winners, extrapolated)
    rows = []
    nsamp = a.screen_per_series
    for name, sr in sorted(series.items(), key=lambda kv: -sum(e["vol"] for e in kv[1]["evs"]))[:a.max_series]:
        evs = sr["evs"]
        pool = [(e, m, side) for e in evs for (m, side) in winners(e)]
        if len(pool) < 3:
            continue
        random.shuffle(pool)
        stats = []
        for e, m, side in pool[:nsamp]:
            r = kal_winner_stats(m) if name.startswith("K ") else pm_winner_stats(m, side)
            if r:
                stats.append((e, r))
        if len(stats) < 3:
            continue
        f = np.array([r[0] for _, r in stats]); ceil = np.array([r[1] for _, r in stats]); cu = np.array([r[2] for _, r in stats])
        trunc = sum(1 for _, r in stats if len(r) > 3 and r[3])
        n_w = len(pool)
        days = sr["days"]
        vol_day = sum(e["vol"] for e in evs) / days
        rows.append({"series": name, "events": len(evs), "winners": n_w, "n": len(stats), "vol_day": vol_day,
                     "f_mean": float(f.mean()), "late_share": float((f >= 0.7).mean()),
                     "ceil_day": float(ceil.mean() * n_w / days), "cheap_usd_day": float(cu.mean() * n_w / days),
                     "trunc": trunc, "evs": evs})
        P(f"- screened {name}: {len(stats)}/{n_w} winners, f_mean {f.mean():.2f}, ceiling ${rows[-1]['ceil_day']:,.0f}/day")
    rows.sort(key=lambda r: -r["ceil_day"])
    P("\n## SCREEN - ranked by hindsight ceiling (cheap-winner profit potential, NOT P&L)")
    P("Ceiling = sum over winner shares bought at <=30c of (1 - price), per day; assumes we knew the winner. Extrapolated from sampled winners.")
    P("| # | series | events | volume $/day | winners sampled/total | winner emerges at (mean life) | share emerging after 70% | ceiling $/day | tier | trunc |")
    P("|---|---|---:|---:|---|---:|---:|---:|---|---:|")
    for i, r in enumerate(rows, 1):
        tier = ">=10k" if r["ceil_day"] >= 10_000 else ("1-10k" if r["ceil_day"] >= 1_000 else "<1k")
        P(f"| {i} | {r['series']} | {r['events']} | {usd(r['vol_day'])} | {r['n']}/{r['winners']} | {r['f_mean']:.2f} | "
          f"{r['late_share']*100:.0f}% | {usd(r['ceil_day'])} | {tier} | {r['trunc']} |")
    top = [r for r in rows if r["ceil_day"] >= 1_000 and r["late_share"] >= 0.3][:a.top_n]
    P(f"\nSeries carried to the stat check: {len(top)} (ceiling >= $1k/day and >= 30% of winners emerging after 70% of life).")
    # ---- stat check
    rules = ["CHEAP_BUY", "CHEAP_FADE"]
    ntests = max(1, len(top) * len(rules))
    table = []
    for r in top:
        isk = r["series"].startswith("K ")
        mk = [(m, e) for e in r["evs"] for m in e["markets"]]
        random.shuffle(mk)
        obs = defaultdict(list); used = 0
        for m, e in mk[:a.stat_markets]:
            if isk:
                path = kal_path(m)
            else:
                m = dict(m, tok=m["toks"][0]); path = pm_path(m)
            if not path:
                continue
            used += 1
            for rule, lst in observations(m, path).items():
                for side, cost, ret in lst:
                    obs[rule].append({"close": m["close"], "ev": m["ev"], "mid_id": m["id"], "side": side, "cost": cost,
                                      "ret": ret, "fee": fee(cost, m["rate"])})
        P(f"- stat check {r['series']}: {used} markets with paths (winners AND losers, so no hindsight)")
        for rule in rules:
            res = evaluate(obs.get(rule, []), rule, rng, ntests)
            if not res:
                table.append({"series": r["series"], "rule": rule, "res": None, "cap": 0.0, "ceil": r["ceil_day"]}); continue
            share = min(1.0, len(obs[rule]) / max(1, used * 3))
            deploy = min(CAP_USD, PARTICIPATION * r["vol_day"] * share)
            lb = max(0.0, res["test_lo"]) if res["pass"] else 0.0
            table.append({"series": r["series"], "rule": rule, "res": res, "cap": deploy * lb, "ceil": r["ceil_day"], "deploy": deploy})
    table.sort(key=lambda t: (-t["cap"], -(t["res"]["z"] if t["res"] and t["res"]["z"] == t["res"]["z"] else -9)))
    P("\n## RESULT - ranked by capturable $/day (PASS only, else $0)")
    P("Rules: at 25/50/75% of a market's life, buy every bucket priced 3-30c (CHEAP_BUY) or fade it (CHEAP_FADE), fills at ask/bid + fees, held to settlement. "
      "If late emergence were an inefficiency, CHEAP_BUY would earn more than the fair-price placebo.")
    P("| # | series | rule | hindsight ceiling $/day | n | markets | train net/$ | TEST net/$ | TEST lo95 | placebo z (need) | top3 | verdict | capturable $/day |")
    P("|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|")
    for i, t in enumerate(table, 1):
        x = t["res"]
        if not x:
            P(f"| {i} | {t['series']} | {t['rule']} | {usd(t['ceil'])} | <30 | - | - | - | - | - | - | too few | $0 |"); continue
        P(f"| {i} | {t['series']} | {t['rule']} | {usd(t['ceil'])} | {x['n']} | {x['markets']} | {x['train']*100:+.1f}% | {x['test']*100:+.1f}% | "
          f"{x['test_lo']*100:+.1f}% | {x['z']:+.1f} ({x['zthr']:.1f}) | {'n/a' if x['top3']!=x['top3'] else str(round(x['top3']*100))+'%'} | "
          f"{'PASS' if x['pass'] else 'FAIL'} | {usd(t['cap'])} |")
    P(f"\n{sum(1 for t in table if t['res'] and t['res']['pass'])} of {len(table)} tests pass.")
    open(a.out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    import sys
    if "--mode" in sys.argv and sys.argv[sys.argv.index("--mode") + 1] == "gate":
        sys.argv = [x for i, x in enumerate(sys.argv) if x != "--mode" and (i == 0 or sys.argv[i - 1] != "--mode")]
        main()
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("--mode", default="late")
        ap.add_argument("--max-series", type=int, default=60)
        ap.add_argument("--screen-per-series", type=int, default=12)
        ap.add_argument("--top-n", type=int, default=8)
        ap.add_argument("--stat-markets", type=int, default=120)
        ap.add_argument("--out", default="scan/OUT-late-winner-scan.md")
        main_late(ap.parse_args())
