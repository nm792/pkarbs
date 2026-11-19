"""SPY daily Up/Down: Yahoo 5m underlying vs Polymarket taker prints. Rule: RULE.md (locked before scoring)."""
import bisect, gzip, json, math, os, random, sys, datetime as dt
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
D = sys.argv[1] if len(sys.argv) > 1 else "/home/user/spy"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/home/user/pkarbs/pipeline/spy_lag/out"
os.makedirs(OUT, exist_ok=True)
TRAIN_END = "2026-10-07"; FIRST = "2026-08-27"
def Phi(z): return 0.5 * math.erfc(-z / math.sqrt(2))
y = json.load(open(f"{D}/spy5m.json"))["chart"]["result"][0]
ts = y["timestamp"]; cl = y["indicators"]["quote"][0]["close"]
bars = [(t, c) for t, c in zip(ts, cl) if c is not None]; bts = [b[0] for b in bars]
def reg(t):
    l = dt.datetime.fromtimestamp(t, NY); return (l.hour, l.minute) >= (9, 30) and l.hour < 16
def close_of(date):  # last regular-session bar close on `date` (NY date)
    best = None
    for t, c in bars:
        l = dt.datetime.fromtimestamp(t, NY)
        if l.date().isoformat() == date and reg(t): best = (t, c)
    return best
days = sorted({dt.datetime.fromtimestamp(t, NY).date().isoformat() for t, _ in bars if reg(t)})
close = {d: close_of(d) for d in days}
def prior(d):
    i = days.index(d); return days[i - 1] if i > 0 else None
def bar_price(s):  # last bar that ended at or before s
    i = bisect.bisect_right(bts, s - 300) - 1
    return bars[i][1] if i >= 0 else None
ev = {e["date"]: e for e in json.load(open(f"{D}/events.json"))}
BUCK = [0.5, 1, 2, 3, 6, 12, 24, 48]
def bucket(tau):
    for b in BUCK:
        if tau <= b: return b
    return None
def K_of(d): return close[d][0] + 300  # bar start + 5 min = 16:00 NY
# ---- load events in range with trades
rows = []  # (date, token_is_up, q, size, s, tau, x, final_win)
used = []
for d, e in sorted(ev.items()):
    if d < FIRST or d not in close: continue
    p0 = prior(d)
    if not p0: continue
    f = f"{D}/trades_{d}.json.gz"
    if not os.path.exists(f): continue
    used.append(d)
    c0 = close[p0][1]; K = K_of(d)
    fin = [float(v) for v in e["final"]]
    if sorted(fin) != [0.0, 1.0]: continue
    up_idx = e["outcomes"].index("Up"); up_tok = e["tokens"][up_idx]; up_won = fin[up_idx] == 1.0
    for t in json.load(gzip.open(f, "rt")):
        if t["side"] != "BUY": continue
        s = t["timestamp"]
        if s >= K or s < K - 48 * 3600: continue
        P = bar_price(s)
        if P is None: continue
        isup = t["token_id"] == up_tok
        rows.append(dict(d=d, isup=isup, q=t["price"], usd=t["price"] * t["size"], sh=t["size"], s=s, tau=(K - s) / 3600,
                         x=math.log(P / c0), res=math.log(close[d][1] / P), win=(up_won if isup else not up_won)))
train = [r for r in rows if r["d"] <= TRAIN_END]; test = [r for r in rows if r["d"] > TRAIN_END]
sig = {}
for b in BUCK:
    v = [r["res"] for r in train if bucket(r["tau"]) == b]
    sig[b] = math.sqrt(sum(a * a for a in v) / len(v)) if len(v) > 30 else None
print("events used", len(used), "prints", len(rows), "train", len(train), "test", len(test), {b: (round(s_ * 1e4) if s_ else None) for b, s_ in sig.items()})
def prob(r, flip=False):
    sg = sig.get(bucket(r["tau"]))
    if not sg: return None
    pu = Phi(r["x"] / sg)
    p = pu if r["isup"] else 1 - pu
    return 1 - p if flip else p
def fee(q): return 0.04 * q * (1 - q)
def run(rs, mode="real", thr=0.03):
    out = []
    for r in rs:
        p = prob(r, flip=(mode == "placebo"))
        if p is None: continue
        q = r["q"]
        if mode == "plant": q = max(0.01, p - 0.05 - 0.0)  # price set so edge = 0.05 before fee
        if mode == "null": q = p
        if not (0.02 < q < 0.98): continue
        edge = p - q - fee(q)
        if edge < thr and mode != "plant": continue
        if mode == "plant": 
            if p - q - fee(q) < 0.0: continue
        out.append(dict(r, q=q, edge=edge, pay=(1.0 if r["win"] else 0.0) - q - fee(q)))
    return out
def summarize(tr, ndays, label):
    if not tr: return dict(label=label, n=0)
    usd = sum(t["usd"] for t in tr); sh = sum(t["sh"] for t in tr)
    pay_sh = sum(t["pay"] * t["sh"] for t in tr)
    byday = {}
    for t in tr: byday.setdefault(t["d"], [0.0, 0.0]); byday[t["d"]][0] += t["pay"] * t["sh"]; byday[t["d"]][1] += t["sh"]
    ds = list(byday); rnd = random.Random(1); ps, dd = [], []
    for _ in range(10000):
        pick = [byday[rnd.choice(ds)] for _ in ds]
        ssh = sum(p[1] for p in pick); ps.append(sum(p[0] for p in pick) / ssh if ssh else 0)
        dd.append(0.1 * sum(p[0] for p in pick) / ndays)
    ps.sort(); dd.sort()
    top5 = sorted(((v[0]) for v in byday.values()), reverse=True)[:5]
    return dict(label=label, n=len(tr), usd=round(usd), mean_q=round(sum(t["q"] * t["sh"] for t in tr) / sh, 3),
                exante=round(sum(t["edge"] * t["sh"] for t in tr) / sh, 4), real_per_share=round(pay_sh / sh, 4),
                real_ci=[round(ps[250], 4), round(ps[9750], 4)], per_day_10pct=round(0.1 * pay_sh / ndays, 2),
                per_day_ci=[round(dd[250], 2), round(dd[9750], 2)], flow_usd_per_day=round(0.1 * usd / ndays, 1),
                days_with_trades=len(byday), top5_share_of_pnl=round(sum(top5) / pay_sh, 2) if pay_sh else None)
tdays = len({r["d"] for r in test}); res = {}
for part, rs, nd in (("TEST", test, tdays), ("TRAIN", train, len({r["d"] for r in train}))):
    for mode in ("real", "placebo", "plant", "null"):
        res[f"{part}-{mode}"] = summarize(run(rs, mode), nd, f"{part} {mode}")
    for lab, f_ in (("tau<=3h", lambda r: r["tau"] <= 3), ("tau>3h", lambda r: r["tau"] > 3)):
        res[f"{part}-real-{lab}"] = summarize(run([r for r in rs if f_(r)], "real"), nd, f"{part} real {lab}")
res["meta"] = dict(events_used=len(used), test_days=tdays, sigma_bp={str(b): (round(s_ * 1e4) if s_ else None) for b, s_ in sig.items()})
json.dump(res, open(f"{OUT}/result.json", "w"), indent=1)
for k, v in res.items(): print(k, json.dumps(v))
