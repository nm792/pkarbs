#!/usr/bin/env python3
"""Polymarket tradfi (index/stock up-or-down, open/close, daily) - direct search by tag + title (Nick 11 Nov 05:18Z).
Step 1 columns (volume/day, resolved markets, late share, early-leader share) then early-leader price vs win rate."""
import sys, os, re, time, random, json
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v

random.seed(5); rng = np.random.default_rng(5)
DAYS = 60
since = time.time() - DAYS * 86400
iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
TAGS = ["spx", "equities", "stocks", "up-or-down", "daily-close", "nvda", "tsla", "finance", "indices", "stock-market", "nasdaq", "dow-jones", "daily-open", "opening"]
CRYPTO = re.compile(r"bitcoin|ethereum|solana|xrp|dogecoin|crypto|\bbtc\b|\beth\b|\bsol\b", re.I)
EXCL5 = re.compile(r"\d{1,2}:\d{2}\s?(AM|PM)", re.I)       # 5/15-minute windows
evs = {}
for tg in TAGS:
    off = 0
    while off < 1000:
        d = v.get(v.GAMMA + "/events", {"tag_slug": tg, "closed": "true", "end_date_min": iso, "limit": 100, "offset": off,
                                        "order": "volume", "ascending": "false"})
        if not d: break
        for e in d: evs[e["id"]] = e
        if len(d) < 100: break
        off += 100
sel = []
for e in evs.values():
    t = e.get("title") or ""
    if CRYPTO.search(t) or EXCL5.search(t): continue
    if not re.search(r"up or down|open|close|hit|above|below|range|finish", t, re.I): continue
    sel.append(e)
def series_key(t):
    k = v.title_key(re.sub(r"\(([A-Z.]{1,6})\)", r"(\1)", t))
    t2 = re.sub(r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d*,?\s*\d*", "M", t)
    t2 = re.sub(r"\d+", "#", t2)
    return " ".join(t2.split()[:9])
groups = defaultdict(list)
for e in sel: groups[series_key(e.get("title") or "")].append(e)
print(f"{len(evs)} events from tags, {len(sel)} tradfi-looking after filters, {len(groups)} title patterns")
L = []
def P(s=""): print(s, flush=True); L.append(s)
P(f"# Polymarket tradfi: direct search (last {DAYS} days, crypto and 5/15-minute windows excluded)")
rows = []
for k, es in sorted(groups.items(), key=lambda kv: -sum(float(e.get("volume") or 0) for e in kv[1])):
    vol = sum(float(e.get("volume") or 0) for e in es) * v.PM_FACTOR
    if vol / DAYS < 5_000 or len(es) < 3: continue
    mk = []
    for e in es:
        for m in e.get("markets", []):
            try:
                pr = [float(x) for x in v.jl(m.get("outcomePrices"))]; toks = v.jl(m.get("clobTokenIds"))
            except Exception: continue
            if len(pr) != 2 or max(pr) < 0.99 or len(toks) != 2: continue
            fs = m.get("feeSchedule") or {}
            ct = (m.get("closedTime") or e.get("closedTime") or "")[:19].replace("T", " ")
            try: cts = time.mktime(time.strptime(ct, "%Y-%m-%d %H:%M:%S"))
            except Exception: continue
            mk.append({"id": m["conditionId"], "ev": e["id"], "toks": toks, "y": 1 if pr[0] > .5 else 0, "close": cts,
                       "rate": v.fl(fs.get("rate")) if m.get("feesEnabled") else 0.0, "vol": v.fl(m.get("volumeNum")) * v.PM_FACTOR})
    if len(mk) < 5: continue
    multi = len(mk) / len(es) >= 3
    random.shuffle(mk)
    fl_, obs = [], []
    ladder = bool(re.search(r"closes above|above ___", k))
    for m in (mk[:60] if not ladder else mk[:200]):
        if multi and m["y"] == 0 and not ladder: continue
        side = "Y" if m["y"] == 1 else "N"
        tok = m["toks"][0 if side == "Y" else 1]
        d = v.get(v.CLOB + "/prices-history", {"market": tok, "interval": "max", "fidelity": 60}, sleep=0.2)
        h = (d or {}).get("history") or []
        pw = np.array([x["p"] for x in h if x["t"] <= m["close"]], float)
        if len(pw) < 8: continue
        f = v.emergence(pw)
        if f is not None and (not ladder or True): fl_.append(f)
        if multi and not ladder: continue
        n = len(pw)
        # favourite at checkpoints from YES-token path (same as winner path when side=Y; invert when N)
        ypath = pw if side == "Y" else 1 - pw
        for name, fr in (("first hour", None), ("10% of life", .10), ("25% of life", .25)):
            i = 1 if fr is None else max(1, int(n * fr))
            if i >= n - 1: continue
            p = float(ypath[i]); fav = "Y" if p >= .5 else "N"
            cost = min((p if fav == "Y" else 1 - p) + v.SLIP_PM, .995)
            win = (m["y"] == 1) == (fav == "Y")
            fee = m["rate"] * cost * (1 - cost)
            obs.append({"cp": name, "cost": cost, "win": float(win), "ret": (win - cost - fee) / cost, "gap": win - cost - fee,
                        "ev": m["ev"], "close": m["close"]})
    if len(fl_) < 5: continue
    fl_ = np.array(fl_)
    rows.append({"k": k, "vol_day": vol / DAYS, "n_res": len(mk), "n_ev": len(es), "n": len(fl_), "late": float((fl_ > .7).mean()),
                 "early": float((fl_ <= .10).mean()), "mean": float(fl_.mean()), "obs": obs, "avg_mkt": float(np.mean([m['vol'] for m in mk]))})
    print(rows[-1]["k"], round(rows[-1]["vol_day"]), rows[-1]["late"], rows[-1]["early"], flush=True)
rows.sort(key=lambda r: -r["vol_day"])
P("\n| series (title pattern) | volume $/day | resolved markets (events) | winners measured | late share (>70% of life) | early-leader share (<=10%) | mean emergence |\n|---|---:|---|---:|---:|---:|---:|")
for r in rows:
    P(f"| {r['k']} | ${r['vol_day']:,.0f} | {r['n_res']} ({r['n_ev']}) | {r['n']} | {r['late']*100:.0f}% | {r['early']*100:.0f}% | {r['mean']:.2f} |")
P("\n## Early leader: price vs win rate (favourite side at ask = mid + 1.5c slippage, + fee, hold to settlement; binary up/down series)")
P("| series | checkpoint | half | markets | fav ask | win rate | gap net of fee (95% CI) | net/$ |\n|---|---|---|---:|---:|---:|---|---:|")
for r in rows:
    o = r["obs"]
    if len(o) < 30: continue
    mid_t = np.median([x["close"] for x in o])
    for cp in ("first hour", "10% of life", "25% of life"):
        for half, sel_ in (("train", lambda x: x["close"] <= mid_t), ("TEST", lambda x: x["close"] > mid_t)):
            s = [x for x in o if x["cp"] == cp and sel_(x)]
            if len(s) < 10: continue
            g = np.array([x["gap"] for x in s]); bs = rng.integers(0, len(g), (1000, len(g))); gm = g[bs].mean(1)
            P(f"| {r['k']} | {cp} | {half} | {len(s)} | {np.mean([x['cost'] for x in s])*100:.1f}c | {np.mean([x['win'] for x in s])*100:.1f}% | "
              f"{g.mean()*100:+.2f}c ({np.percentile(gm,2.5)*100:+.2f}, {np.percentile(gm,97.5)*100:+.2f}) | {np.mean([x['ret'] for x in s])*100:+.2f}% |")
open("scan/OUT-pm-tradfi-2026-11-11.md", "w").write("\n".join(L) + "\n")
