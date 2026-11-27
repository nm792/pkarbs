"""Weekend fade of Friday after-hours gaps on the NVDA stock perp (Hyperliquid xyz).
Implements reviewer/pkarbs/specs/SPEC-weekend-ah-gap-fade-NVDA-2026-11-25.md exactly (rule locked 25 Nov 07:50Z).
Inputs (all files, no network):
  --candles  JSON list of 1h candles {t(ms open), o, h, l, c} for xyz:NVDA (HL info candleSnapshot)
  --funding  JSON list {time(ms), fundingRate} hourly (HL info fundingHistory); a long pays rate x notional each hour
  --daily    CSV date,open,close for NVDA regular session (ET dates)
  --half-spread-bp  half spread used where no logged book exists (stated assumption; run 2/5/10)
Output: JSON with per-weekend rows, primary verdict, secondary cells, MC type 1 placebo and MC type 2 planted checks.
"""
import argparse, csv, json, math, random, datetime as dt
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York"); UTC = dt.timezone.utc
FEE_BP = 0.9  # HL xyz taker fee, measured (SETTLED B.2)

def et(d, hh, mm):  # ET wall time -> UTC epoch seconds
    return dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=ET).timestamp()

def price_at(candles, t):
    """mid proxy at time t: close of the last 1h candle that ended at or before t (candle t is its open)."""
    best = None
    for c in candles:
        end = c["t"] / 1000 + 3600
        if end <= t + 1e-6: best = float(c["c"])
        else: break
    return best

def funding_bp(funding, t0, t1, side):
    s = sum(float(f["fundingRate"]) for f in funding if t0 < f["time"] / 1000 <= t1)
    return -side * s * 1e4  # long (side=+1) pays positive funding

def weekends(daily):
    """pairs (friday_row, monday_row) where Friday is the last session of its week and the next session is the next Monday."""
    rows = sorted(daily, key=lambda r: r["date"])
    out = []
    for a, b in zip(rows, rows[1:]):
        da, db = a["date"], b["date"]
        if da.weekday() == 4 and db.weekday() == 0 and (db - da).days == 3: out.append((a, b))
    return out

def trade(fri, mon, candles, funding, thr, exit_hhmm, half_bp, plant_bp=None):
    R = fri["close"]
    t_in = et(fri["date"], 20, 0)
    t_out = et(mon["date"], *exit_hhmm)
    m_in, m_out = price_at(candles, t_in), price_at(candles, t_out)
    if m_in is None or m_out is None: return None
    G = m_in / R - 1
    row = dict(friday=str(fri["date"]), R=R, mid_in=m_in, G_pct=round(G * 100, 3))
    if abs(G) < thr: row["trade"] = False; return row
    side = -1 if G > 0 else 1  # fade
    if plant_bp is not None:  # MC type 2: planted reversion toward R, in bp of price
        m_out = m_in * (1 + side * plant_bp / 1e4)  # exit = entry moved plant_bp toward R; real move removed
    p_in = m_in * (1 + side * half_bp / 1e4)      # buy at ask / sell at bid
    p_out = m_out * (1 - side * half_bp / 1e4)    # exit at opposite touch
    gross_bp = side * (p_out / p_in - 1) * 1e4
    net = gross_bp - 2 * FEE_BP + funding_bp(funding, t_in, t_out, side)
    row.update(trade=True, side=side, mid_out=m_out, gross_bp=round(gross_bp, 2), net_bp=round(net, 2))
    return row

def run(candles, funding, daily, thr=0.01, exit_hhmm=(9, 35), half_bp=5.0, plant_bp=None):
    rows = [trade(f, m, candles, funding, thr, exit_hhmm, half_bp, plant_bp) for f, m in weekends(daily)]
    rows = [r for r in rows if r]
    key = "net_bp" if plant_bp is None else "plant_gross_ex_spread_bp"
    for r in rows:
        if r.get("trade") and plant_bp is not None: r["plant_gross_ex_spread_bp"] = round(r["gross_bp"] + 2 * half_bp, 2)
    return rows, [r[key] for r in rows if r.get("trade")]

def boot(v, B=5000, seed=7):
    rnd = random.Random(seed)
    if not v: return None
    bs = sorted(sum(rnd.choice(v) for _ in v) / len(v) for _ in range(B))
    return dict(mean=sum(v) / len(v), lo=bs[int(.025 * B)], hi=bs[int(.975 * B)])

def placebo(candles, funding, daily, half_bp, n=10000, seed=11):
    """MC type 1: random sign, same entry/exit, every weekend regardless of G."""
    rnd = random.Random(seed); base = []
    for f, m in weekends(daily):
        r = trade(f, m, candles, funding, 0.0, (9, 35), half_bp)
        if r and r.get("trade"):
            base.append((r["mid_in"], r["mid_out"], et(f["date"], 20, 0), et(m["date"], 9, 35)))
    if not base: return None
    means = []
    for _ in range(n):
        tot = 0
        for mi, mo, t0, t1 in base:
            s = rnd.choice((-1, 1)); pi = mi * (1 + s * half_bp / 1e4); po = mo * (1 - s * half_bp / 1e4)
            tot += s * (po / pi - 1) * 1e4 - 2 * FEE_BP + funding_bp(funding, t0, t1, s)
        means.append(tot / len(base))
    means.sort(); return dict(n_weekends=len(base), p95=means[int(.95 * n)])

def verdict(v, plc):
    b = boot(v)
    if b is None or len(v) < 13: return "UNDERPOWERED" if v is not None else "NO DATA", b
    if b["mean"] > 0 and b["lo"] > 0 and plc and b["mean"] > plc["p95"]: return "PASS", b
    if b["mean"] <= 0 and b["hi"] < 10: return "FAIL", b
    return "INCONCLUSIVE", b

def load(a):
    candles = sorted(json.load(open(a.candles)), key=lambda c: c["t"])
    funding = json.load(open(a.funding))
    daily = [dict(date=dt.date.fromisoformat(r["date"]), open=float(r["open"]), close=float(r["close"])) for r in csv.DictReader(open(a.daily))]
    return candles, funding, daily

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--candles"); ap.add_argument("--funding"); ap.add_argument("--daily")
    ap.add_argument("--half-spread-bp", type=float, default=5.0); a = ap.parse_args()
    candles, funding, daily = load(a); h = a.half_spread_bp
    rows, v = run(candles, funding, daily, 0.01, (9, 35), h)
    plc = placebo(candles, funding, daily, h)
    vd, b = verdict(v, plc)
    _, v30 = run(candles, funding, daily, 0.01, (9, 35), h, plant_bp=30)
    _, v0 = run(candles, funding, daily, 0.01, (9, 35), h, plant_bp=0)
    sec = {f"thr{t}_exit{e[0]}{e[1]:02d}": boot(run(candles, funding, daily, t, e, h)[1]) for t, e in [(0.005, (9, 35)), (0.02, (9, 35)), (0.01, (16, 0))]}
    print(json.dumps(dict(half_spread_bp_assumed=h, weekends=len(rows), qualifying=len(v), verdict=vd, primary=b, placebo_mc_type1=plc,
                          planted_30bp_mc_type2=boot(v30), planted_0bp=boot(v0), secondary=sec, rows=rows), indent=1, default=str))

if __name__ == "__main__": main()
