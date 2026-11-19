"""Test 1 of LOCKED-RULE-divergence-followups-2026-11-17.md. usage: eval1.py [LOGDIR] [--funding funding.json]
net = gross - 2 x 4 bp - funding paid when a top-of-hour settlement falls between entry and exit fills (PM funding: positive rate = long pays)."""
import gzip, json, glob, sys, collections, datetime, urllib.request, numpy as np, random
LOG = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "out"
FJ = sys.argv[sys.argv.index("--funding") + 1] if "--funding" in sys.argv else None
AFTER = float(sys.argv[sys.argv.index("--after") + 1]) if "--after" in sys.argv else 1794881580.0   # only sessions recorded after the rule merge (#374 merge)
MAXGAP = 7.5   # a 5 s sample series: any step wider than this breaks the 5 s latency assumption
rnd = random.Random(1); NOT = 1000.0; FEE = 4.0; NBOOT = 10000  # FEE: Polymarket equity/index perp taker 4 bp at $0 volume, source https://api.perpetuals.polymarket.com/v1/info/fees (taker_fee_rate 0.0004)
recs = []
for f in sorted(glob.glob(LOG + "/*.jsonl.gz")):
    try:
        for l in gzip.open(f, "rt"):
            try: recs.append(json.loads(l))
            except Exception: break
    except Exception: pass
recs = [r for r in recs if "pm" in r and "hl" in r and r.get("books") is not None]; recs = [r for r in recs if r["t"] >= AFTER]; recs.sort(key=lambda r: r["t"])
T = [r["t"] for r in recs]; print("polls", len(recs), "span min", round((T[-1] - T[0]) / 60, 1) if T else 0)
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "data-eval"}), timeout=20))
def load_funding(symbols):
    """Polymarket /funding returns only the LAST 24 hourly rows, so every run merges what it fetches into LOG/funding_cache.json
    (accumulates across runs). Any settlement without a rate makes the verdict PRELIMINARY."""
    if FJ: return json.load(open(FJ))
    cache_f = LOG + "/funding_cache.json"
    try: out = {s: [tuple(x) for x in v] for s, v in json.load(open(cache_f)).items()}
    except Exception: out = {}
    try:
        ins = get("https://api.perpetuals.polymarket.com/v1/info/instruments"); ins = ins["data"] if isinstance(ins, dict) else ins
        ids = {i["symbol"]: i["instrument_id"] for i in ins}
        for s in symbols:
            r = get("https://api.perpetuals.polymarket.com/v1/info/funding?instrument_id=%s" % ids[s])
            have = {round(ts) for ts, _ in out.get(s, [])}
            out.setdefault(s, []).extend((x["timestamp"] / 1000, float(x["funding_rate"])) for x in r["data"] if round(x["timestamp"] / 1000) not in have)
        json.dump(out, open(cache_f, "w"))
    except Exception as ex: print("FUNDING FETCH FAILED", ex)
    return out
def session(t):
    d = datetime.datetime.fromtimestamp(t, datetime.timezone.utc); wd, hr = d.weekday(), d.hour
    if (wd == 4 and hr >= 22) or wd == 5 or (wd == 6 and hr < 22): c = "weekend"
    elif wd < 5 and 13 <= hr < 21: c = "US"
    else: c = "other"
    return (d.date().isoformat(), c)
sym = collections.defaultdict(list)
for r in recs:
    bk = r["books"]
    for x in r["pm"]:
        s, idx, mk, mid, last = x
        try: idx = float(idx); mid = float(mid)
        except Exception: continue
        sym[s].append((r["t"], (mid / idx - 1) * 1e4, bk.get(s)))
def vwap(levels, usd):
    need = usd; cost = 0.0; qty = 0.0
    for px, sz in levels:
        px = float(px); sz = float(sz); take = min(sz * px, need); cost += take; qty += take / px; need -= take
        if need <= 1e-9: break
    return cost / qty if need <= 1e-9 and qty > 0 else None
def fill(book, side):
    if not book or "asks" not in book: return None
    return vwap(book["asks"] if side > 0 else book["bids"], NOT)
FUND = {}; funding_missing = [0]; GAPS = [0]
def funding_paid(s, pos, t_in, t_out):
    """bp paid by the position for settlements with t_in < boundary <= t_out; boundaries are top-of-hour"""
    tot = 0.0; b = (int(t_in // 3600) + 1) * 3600
    while b <= t_out:
        rate = None
        for ts, r in FUND.get(s, []):
            if abs(ts - b) <= 120: rate = r; break
        if rate is None: funding_missing[0] += 1
        else: tot += pos * rate * 1e4
        b += 3600
    return tot
def trade(ser, i, pos):
    """entry at sample i+1 (book), exit trigger first sample j>=i+1 with |g|<5 or 300 s since entry, fill at sample j+1"""
    t1, g1, b1 = ser[i + 1]; ep = fill(b1, pos)
    if ser[i + 1][0] - ser[i][0] > MAXGAP: GAPS[0] += 1; return None
    if ep is None: return None
    j = i + 1
    while j < len(ser) - 1:
        if ser[j + 1][0] - ser[j][0] > MAXGAP: GAPS[0] += 1; return None
        if abs(ser[j][1]) < 5 or ser[j][0] - t1 >= 300:
            ex = fill(ser[j + 1][2], -pos)
            if ex is None: return None
            return j, ep, ex, t1, ser[j + 1][0]
        j += 1
    return None
FUND = load_funding(list(sym)) if sym else {}
events = []; missed = 0; nobook = 0
for s, ser in sym.items():
    i = 0
    while i < len(ser) - 3:
        t, g, b = ser[i]
        if abs(g) >= 25:
            pos = -1 if g > 0 else 1
            if abs(ser[i + 1][1]) < 15: missed += 1; i += 1; continue
            res = trade(ser, i, pos)
            if res is None: nobook += 1; i += 1; continue
            j, ep, ex, t1, tx = res; gross = pos * (ex / ep - 1) * 1e4; fp = funding_paid(s, pos, t1, tx)
            events.append(dict(sym=s, t=t, day=int(t // 86400), sess=session(t), g=g, gross=gross, fund=fp, net=gross - 2 * FEE - fp, hold=tx - t1)); i = j + 2
        else: i += 1
print("signals dropped because sample spacing > 7.5 s:", GAPS[0]); print("events", len(events), "missed (gap gone at entry)", missed, "no usable book", nobook, "funding settlements without a rate:", funding_missing[0])
placebo_mean = None
if events:
    ne = np.array([e["net"] for e in events]); gr = np.array([e["gross"] for e in events])
    cl = collections.defaultdict(list)
    for e in events: cl[(e["sym"], e["sess"])].append(e["net"])     # event cluster = symbol x session
    k = list(cl); sums = np.array([sum(cl[x]) for x in k]); cnt = np.array([len(cl[x]) for x in k], float)
    idx = np.random.default_rng(1).integers(0, len(k), size=(NBOOT, len(k))); bs = sums[idx].sum(1) / cnt[idx].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5]); days = len(set(e["day"] for e in events))
    # placebo: per event, one random entry sample in the SAME symbol and SAME session with |g| < 10, random direction, same exit rule and costs
    pl = []
    for e in events:
        ser = sym[e["sym"]]; cand = [i for i in range(len(ser) - 3) if abs(ser[i][1]) < 10 and ser[i + 1][2] is not None and session(ser[i][0]) == e["sess"]]
        if not cand: continue
        i = rnd.choice(cand); pos = rnd.choice((-1, 1)); res = trade(ser, i, pos)
        if res is None: continue
        j, ep, ex, t1, tx = res; pl.append(pos * (ex / ep - 1) * 1e4 - 2 * FEE - funding_paid(e["sym"], pos, t1, tx))
    placebo_mean = float(np.mean(pl)) if pl else None
    print("gross mean", gr.mean().round(1), "median", np.median(gr).round(1), "net mean", ne.mean().round(1), "median", np.median(ne).round(1), "CI95", lo.round(1), hi.round(1), "pos", (ne > 0).mean().round(2), "median hold s", np.median([e["hold"] for e in events]), "days", days, "mean funding paid bp", np.mean([e["fund"] for e in events]).round(2))
    print("placebo n", len(pl), "mean net", None if placebo_mean is None else round(placebo_mean, 1))
    bysym = collections.defaultdict(list)
    for e in events: bysym[e["sym"]].append(e["net"])
    for s, v in sorted(bysym.items(), key=lambda kv: -len(kv[1])): print(" ", s, len(v), "net", round(float(np.mean(v)), 1))
    verdict = "PASS" if (len(events) >= 30 and days >= 2 and ne.mean() > 0 and lo > 0 and placebo_mean is not None and ne.mean() > placebo_mean and funding_missing[0] == 0) else "PRELIMINARY / NOT PASS"
    print("VERDICT:", verdict, "(funding settlements without a rate force PRELIMINARY)" if funding_missing[0] else "", "| need >=30 events over >=2 days; have", len(events), "events over", days, "day(s)")
else: print("VERDICT: PRELIMINARY (no events)")
