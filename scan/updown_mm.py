#!/usr/bin/env python3
"""Up/down series as a market-making-for-rebates candidate (Nick 11 Nov 05:26Z, adaptation of the MFW 5-minute BTC approach).
Per up/down series on Polymarket (not 5-minute BTC) and Kalshi equivalents: volume/day, fee + maker rebate that applies,
typical spread and depth, and a rough ceiling of $/day = our share x volume x (rebate share of taker fee + half spread).
The spread term is GROSS (before adverse selection): Nick's premise is that direction cannot be won, so treat it as an upper limit."""
import sys, os, re, time, random
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v

SHARE = 0.05            # assumed share of taker volume we could rest against
now = time.time()
iso4 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 4 * 86400))
WIN = re.compile(r"(\d{1,2}):(\d{2})\s?(AM|PM)\s?-\s?(\d{1,2}):(\d{2})\s?(AM|PM)", re.I)
def minutes(t):
    m = WIN.search(t)
    if not m: return None
    def mm(h, mi, ap): return (int(h) % 12 + (12 if ap.upper() == "PM" else 0)) * 60 + int(mi)
    a, b = mm(*m.group(1, 2, 3)), mm(*m.group(4, 5, 6))
    return (b - a) % 1440
def asset(t):
    t = re.sub(r"\s*(Up or Down|Opens Up or Down).*", "", t).strip()
    return t[:40]
def tf(t):
    mn = minutes(t)
    if mn is not None: return "5-min" if mn <= 5 else ("15-min" if mn <= 15 else ("hourly" if mn <= 60 else f"{mn}-min"))
    if re.search(r"opens up or down", t, re.I): return "daily open"
    if re.search(r"\bon [A-Z][a-z]+ \d+\??$", t.strip()): return "daily"
    if re.search(r"[A-Z][a-z]+ \d+, \d+(AM|PM)", t): return "hourly"
    return "other"

# ---- Polymarket: closed events last 4 days (volume per day), open events (book)
ev, off = [], 0
while off < 4000:
    d = v.get(v.GAMMA + "/events", {"closed": "true", "end_date_min": iso4, "limit": 100, "offset": off, "order": "endDate", "ascending": "false",
                                   "tag_slug": "up-or-down"})
    if not d: break
    ev += d
    if len(d) < 100: break
    off += 100
# also stocks/indices up/down not tagged up-or-down
for tg in ["spx", "equities", "stocks", "daily-close"]:
    d = v.get(v.GAMMA + "/events", {"closed": "true", "end_date_min": iso4, "limit": 100, "tag_slug": tg, "order": "endDate", "ascending": "false"})
    ev += d or []
seen, ser = set(), defaultdict(lambda: {"vol": 0.0, "n": 0, "ev": []})
for e in ev:
    if e["id"] in seen: continue
    seen.add(e["id"])
    t = e.get("title") or ""
    if not re.search(r"up or down", t, re.I): continue
    k = (asset(t), tf(t))
    if k[1] == "5-min": continue
    ser[k]["vol"] += v.fl(e.get("volume")) * v.PM_FACTOR; ser[k]["n"] += 1; ser[k]["ev"].append(e)
# book sample from OPEN events
opn = {}
for tg in ["up-or-down", "spx", "equities", "stocks"]:
    d = v.get(v.GAMMA + "/events", {"closed": "false", "limit": 100, "tag_slug": tg, "order": "volume24hr", "ascending": "false"})
    for e in d or []:
        t = e.get("title") or ""
        if re.search(r"up or down", t, re.I) and tf(t) != "5-min": opn.setdefault((asset(t), tf(t)), []).append(e)
def book(tok):
    d = v.get(v.CLOB + "/book", {"token_id": tok}, sleep=0.15)
    if not d or not d.get("bids") or not d.get("asks"): return None
    bids = sorted([(float(x["price"]), float(x["size"])) for x in d["bids"]], reverse=True)
    asks = sorted([(float(x["price"]), float(x["size"])) for x in d["asks"]])
    bb, ba = bids[0][0], asks[0][0]
    dep = lambda lv, ref, sg: sum(p * s for p, s in lv if abs(p - ref) <= 0.02)
    return ba - bb, dep(bids, bb, 1) + dep(asks, ba, 1), (bb + ba) / 2
rows = []
for k, s in ser.items():
    days = 4.0
    vol_day = s["vol"] / days
    m0 = None
    for e in s["ev"]:
        for m in e.get("markets", []):
            m0 = m; break
        if m0: break
    fs = (m0 or {}).get("feeSchedule") or {}
    rate = v.fl(fs.get("rate")) if (m0 or {}).get("feesEnabled") else 0.0
    reb = v.fl(fs.get("rebateRate")) if rate else 0.0
    spr, dep_, pmid = [], [], []
    for e in (opn.get(k) or [])[:3]:
        for m in e.get("markets", [])[:1]:
            toks = v.jl(m.get("clobTokenIds"))
            b = book(toks[0]) if toks else None
            if b: spr.append(b[0]); dep_.append(b[1]); pmid.append(b[2])
    sp = float(np.mean(spr)) if spr else None
    rows.append({"venue": "PM", "name": f"{k[0]} {k[1]}", "vol_day": vol_day, "events": s["n"], "rate": rate, "reb": reb,
                 "spread": sp, "depth": float(np.mean(dep_)) if dep_ else None, "p": 0.5})
# ---- Kalshi equivalents
kl = v.kal_volumes()
ks = (v.get(v.KAL + "/series", {"limit": 5000}, sleep=0.4) or {}).get("series", [])
meta = {s["ticker"]: s for s in ks}
cand = [t for t, o in sorted(kl.items(), key=lambda kv: -kv[1]["d1"]) if t.startswith("league:") is False]
sel = []
for fam_, o in sorted(kl.items(), key=lambda kv: -kv[1]["d1"]):
    for t in o["series"]:
        mt = meta.get(t, {})
        title = (mt.get("title") or "") + " " + " ".join(mt.get("tags") or [])
        if mt.get("category") in ("Financials", "Crypto") and re.search(r"up|above|higher|hourly|15|min|close", title, re.I):
            sel.append((t, o["series"][t], mt))
sel = sorted({t: (t, vv, mt) for t, vv, mt in sel}.values(), key=lambda x: -x[1])[:10]
for t, d1, mt in sel:
    r = v.get(v.KAL + "/markets", {"series_ticker": t, "status": "open", "limit": 200}, sleep=0.35) or {}
    sp, dp = [], []
    for m in r.get("markets", []):
        if v.fl(m.get("volume_24h_fp")) <= 0: continue
        a, b = v.fl(m.get("yes_ask_dollars"), -1), v.fl(m.get("yes_bid_dollars"), -1)
        if 0 < a < 1 and 0 < b < 1:
            sp.append(a - b); dp.append(min(v.fl(m.get("yes_ask_size_fp")) * a, v.fl(m.get("yes_bid_size_fp")) * b))
    ft = mt.get("fee_type", "?")
    rows.append({"venue": "Kalshi", "name": f"{t} ({mt.get('title','')[:34]})", "vol_day": d1, "events": 0,
                 "rate": 0.07 * v.fl(mt.get("fee_multiplier"), 1), "reb": 0.0, "spread": float(np.mean(sp)) if sp else None,
                 "depth": float(np.mean(dp)) if dp else None, "p": 0.5, "ft": ft})
L = []
def P(s=""): print(s, flush=True); L.append(s)
P("# Up/down series as rebate market-making candidates (not 5-minute BTC)")
P(f"Volume = adjusted $/day (PM: events ended in last 4 days, gamma x0.5; Kalshi: 24h contracts x min(p,1-p) snapshot). Share assumed {SHARE*100:.0f}% of volume. "
  "Rebate/day = share x vol x taker fee per $ (rate x (1-p), p=0.5) x rebate share. Spread/day = share x vol x spread/2, GROSS before adverse selection.\n")
P("| # | series | volume $/day | taker fee | maker rebate | spread | book depth within 2c ($) | rebate ceiling $/day | gross spread ceiling $/day | total ceiling $/day | note |")
P("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for r in rows:
    r["rebate_d"] = SHARE * r["vol_day"] * r["rate"] * 0.5 * r["reb"]
    r["spread_d"] = SHARE * r["vol_day"] * (r["spread"] / 2) if r["spread"] else 0.0
    r["tot"] = r["rebate_d"] + r["spread_d"]
rows.sort(key=lambda r: -r["tot"])
for i, r in enumerate(rows, 1):
    note = ("NO REBATE: fee-free market" if r["venue"] == "PM" and not r["rate"] else "") if r["venue"] == "PM" else f"Kalshi: no maker rebate on this series (fee_type {r.get('ft')})"
    P(f"| {i} | {r['venue']} {r['name']} | ${r['vol_day']:,.0f} | {r['rate']*100:.1f}% | {r['reb']*100:.0f}% | "
      f"{'n/a' if r['spread'] is None else f'{r['spread']*100:.1f}c'} | {'n/a' if r['depth'] is None else f'${r['depth']:,.0f}'} | ${r['rebate_d']:,.0f} | ${r['spread_d']:,.0f} | ${r['tot']:,.0f} | {note} |")
open("scan/OUT-updown-mm-2026-11-11.md", "w").write("\n".join(L) + "\n")
