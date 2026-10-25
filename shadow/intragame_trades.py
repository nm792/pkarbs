"""Intra-game edge checks on public Polymarket trade prints (no raw books needed).

Pulls closed soccer negRisk 3-leg games from gamma, every taker trade per leg from
data-api /trades, and tests three things around goal-like shocks:
  1. drift on the jumping leg after a reachable entry (momentum or overshoot)
  2. stale quotes still being picked off on any leg 0..30 s after the shock
  3. maker markouts (what resting liquidity earned) in quiet vs near-shock periods

Prices are YES-equivalent (a NO trade at q counts as YES at 1-q). Trade timestamps are
whole seconds and already include the 1 s sports delay. No look-ahead in shock detection:
a shock needs 2 trades beyond the threshold within 15 s, and entry is 1 s after that.

    python3 intragame_trades.py --start 2026-10-18 --end 2026-10-25 --games 80
Needs network access to gamma-api and data-api (blocked from the project container;
ran in a remote sandbox on 25 Oct 2026).
"""
import argparse, json, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
import pandas as pd
import requests

H = {"User-Agent": "Mozilla/5.0"}
GAMMA = "https://gamma-api.polymarket.com"
TRADES = "https://data-api.polymarket.com/trades"
INPLAY_S = 8400  # kickoff to kickoff + 140 min
HORIZONS = [10, 30, 60, 300, 600]


def games_list(start, end, n):
    sel, cur = [], None
    for _ in range(40):
        p = {"tag_slug": "soccer", "limit": 50, "closed": "true",
             "end_date_min": start + "T00:00:00Z", "end_date_max": end + "T00:00:00Z"}
        if cur:
            p["after_cursor"] = cur
        r = requests.get(GAMMA + "/events/keyset", params=p, headers=H, timeout=30).json()
        for e in r.get("events", []):
            ms = e.get("markets", [])
            if e.get("negRisk") and not e.get("negRiskAugmented") and len(ms) == 3:
                sel.append({"title": e["title"], "vol": sum(float(m.get("volume") or 0) for m in ms),
                            "m": [{k: m.get(k) for k in ["conditionId", "gameStartTime", "secondsDelay",
                                                          "outcomePrices", "clobTokenIds", "groupItemTitle"]}
                                  for m in ms]})
        cur = r.get("next_cursor")
        if not cur:
            break
    sel.sort(key=lambda e: -e["vol"])
    return sel[:n]


def fetch(cid):
    rows, off = [], 0
    while off <= 10000:  # data-api caps offset at 10000
        for _ in range(3):
            r = requests.get(TRADES, params={"market": cid, "limit": 500, "offset": off}, headers=H, timeout=30)
            if r.status_code == 200:
                break
            time.sleep(1)
        j = r.json() if r.status_code == 200 else []
        rows += [(t["timestamp"], t["asset"], t["side"], float(t["price"]), float(t["size"])) for t in j]
        if len(j) < 500:
            break
        off += 500
    return cid, rows


def ts(s):
    return datetime.fromisoformat(s.replace(" ", "T").replace("+00", "+00:00").replace("Z", "+00:00")
                                  .replace("+00:00:00", "+00:00")).timestamp()


def build(sel, trades):
    games = []
    for e in sel:
        legs = []
        for m in e["m"]:
            tok = json.loads(m["clobTokenIds"])
            arr = []
            for t, a, side, p, sz in trades[m["conditionId"]]:
                yes = a == tok[0]
                arr.append((t, p if yes else 1 - p, (1 if side == "BUY" else -1) * (1 if yes else -1), sz))
            arr.sort()
            legs.append({"win": float(json.loads(m["outcomePrices"])[0]),
                         "tr": np.array(arr) if arr else np.zeros((0, 4))})
        games.append({"title": e["title"], "g0": ts(e["m"][0]["gameStartTime"]), "legs": legs})
    return games


def px_at(tr, t):
    i = np.searchsorted(tr[:, 0], t, side="right") - 1
    return tr[i, 1] if i >= 0 else np.nan


def med(tr, a, b):
    m = (tr[:, 0] >= a) & (tr[:, 0] <= b)
    return np.median(tr[m, 1]) if m.any() else np.nan


def clus(x, g):
    """Mean and game-clustered standard error."""
    df = pd.DataFrame({"x": x, "g": g}).dropna()
    m = df.x.mean()
    se = np.sqrt((df.groupby("g").x.apply(lambda v: (v - m).sum()) ** 2).sum()) / len(df)
    return round(m, 4), round(se, 4), len(df), df.g.nunique()


def detect(games, thr=0.10, n_conf=2, w_conf=15, refractory=600):
    out = []
    for gi, g in enumerate(games):
        cands = []
        for li, l in enumerate(g["legs"]):
            tr = l["tr"]
            if not len(tr):
                continue
            for i in np.where((tr[:, 0] >= g["g0"]) & (tr[:, 0] <= g["g0"] + INPLAY_S))[0]:
                t, p = tr[i, 0], tr[i, 1]
                pre = med(tr, t - 150, t - 20)
                if np.isnan(pre) or abs(p - pre) < thr:
                    continue
                d = np.sign(p - pre)
                w = (tr[:, 0] >= t) & (tr[:, 0] <= t + w_conf)
                hit = tr[w][d * (tr[w, 1] - pre) >= thr]
                if len(hit) >= n_conf:
                    cands.append((t, li, pre, d, hit[n_conf - 1, 0]))
        last = -1e18
        for t, li, pre, d, ct in sorted(cands):
            if t - last >= refractory:
                last = t
                out.append({"g": gi, "leg": li, "t": t, "pre": pre, "dir": d, "ct": ct})
    return out


def drift(games, shocks):
    res = []
    for s in shocks:
        g = games[s["g"]]
        tr, d = g["legs"][s["leg"]]["tr"], s["dir"]
        i = np.searchsorted(tr[:, 0], max(s["t"] + 2, s["ct"] + 1))
        if i >= len(tr):
            continue
        te, pe = tr[i, 0], tr[i, 1]
        r = {"g": s["g"], "jump": d * (pe - s["pre"])}
        for h in HORIZONS:
            r[h] = d * (px_at(tr, te + h) - pe) if te + h <= g["g0"] + INPLAY_S else np.nan
        r["res"] = d * (g["legs"][s["leg"]]["win"] - pe)
        res.append(r)
    return pd.DataFrame(res)


def stale(games, shocks, fee_rate=0.05):
    rows = []
    for k, s in enumerate(shocks):
        g, t = games[s["g"]], s["t"]
        for li, l in enumerate(g["legs"]):
            tr = l["tr"]
            if not len(tr):
                continue
            pre, post = med(tr, t - 150, t - 20), med(tr, t + 60, t + 180)
            if np.isnan(pre) or np.isnan(post) or abs(post - pre) < 0.05:
                continue
            dk, mv = np.sign(post - pre), abs(post - pre)
            for a, b in [(0, 0), (1, 1), (2, 2), (3, 5), (6, 10), (11, 30)]:
                pick = ((tr[:, 0] >= t + a) & (tr[:, 0] <= t + b) & (dk * (post - tr[:, 1]) >= 0.6 * mv)
                        & (tr[:, 2] == dk))
                p = tr[pick, 1]
                rows.append({"g": s["g"], "shock": k, "own": li == s["leg"], "b": f"{a}-{b}",
                             "n": int(pick.sum()), "usd": (tr[pick, 3] * (dk * (post - p) - fee_rate * p * (1 - p))).sum()})
    return pd.DataFrame(rows)


def markouts(games, shocks):
    rows = []
    for gi, g in enumerate(games):
        st = np.array([s["t"] for s in shocks if s["g"] == gi])
        for l in g["legs"]:
            tr = l["tr"]
            for i in np.where((tr[:, 0] >= g["g0"]) & (tr[:, 0] <= g["g0"] + INPLAY_S))[0]:
                t, p, d, sz = tr[i]
                r = {"g": gi, "near": bool(len(st) and np.any((t - st >= -5) & (t - st <= 60))), "sh": sz}
                for h in [60, 300]:
                    r[h] = -d * (px_at(tr, t + h) - p)  # maker side of the trade
                r["res"] = -d * (l["win"] - p)
                rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-10-18")
    ap.add_argument("--end", default="2026-10-25")
    ap.add_argument("--games", type=int, default=80)
    a = ap.parse_args()
    sel = games_list(a.start, a.end, a.games)
    with ThreadPoolExecutor(16) as ex:
        trades = dict(ex.map(fetch, [m["conditionId"] for e in sel for m in e["m"]]))
    games = build(sel, trades)
    shocks = detect(games)
    R = drift(games, shocks)
    print("shocks", len(shocks), "games", R.g.nunique())
    for h in HORIZONS + ["res"]:
        print("drift", h, clus(R[h], R.g))
    P = stale(games, shocks)
    print(P.groupby(["own", "b"]).agg(trades=("n", "sum"), usd=("usd", "sum"), shocks=("n", lambda x: (x > 0).sum())))
    M = markouts(games, shocks)
    for nr, X in M.groupby("near"):
        print("near" if nr else "quiet", len(X), [(h, round((X[h] * X.sh).sum() / X.sh.sum(), 4), clus(X[h], X.g)[:2])
                                                 for h in [60, 300, "res"]])
