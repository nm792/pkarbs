"""External drivers: Yahoo 5m underlying for finance Up/Down series -> features at decision time (bars ended at/before t only)."""
import json, math, os, re, sys, bisect
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_store as P
TICK = {"spx": "^GSPC", "spy": "SPY", "dow-jones": "^DJI", "russell-2000": "^RUT", "nya": "^NYA", "wti": "CL=F", "oil": "CL=F", "gold": "GC=F", "silver": "SI=F",
        "natural-gas": "NG=F", "dax": "^GDAXI", "hang-seng": "^HSI", "nik": "^N225", "ftse-100": "^FTSE", "dxy": "DX-Y.NYB", "ewy": "EWY", "spx-open": "^GSPC", "spy-open": "SPY"}
for t in "aapl msft nvda tsla googl amzn meta nflx pltr mu coin hood abnb rklb open".split(): TICK[t] = t.upper()


def ticker_of(fam):
    m = re.match(r"series:(.+?)-(daily-up-or-down|daily-up-down|daily-close-uo|up-or-down-daily|daily-close)$", fam)
    if not m: return None
    return TICK.get(m.group(1))


def fetch(tk, cache="/home/user/pk_cache/yahoo"):
    os.makedirs(cache, exist_ok=True); p = f"{cache}/{tk.replace('^','_').replace('=','_')}.json"
    if not os.path.exists(p):
        d = P.http_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?range=60d&interval=5m&includePrePost=true")
        json.dump(d, open(p, "w"))
    r = json.load(open(p))["chart"]["result"][0]
    ts = r["timestamp"]; cl = r["indicators"]["quote"][0]["close"]
    b = [(t, c) for t, c in zip(ts, cl) if c is not None]
    return np.array([x[0] for x in b], float), np.array([x[1] for x in b], float)


def add(df):
    df = df.copy()
    for c in ("ext_x", "ext_z", "ext_ret1h", "ext_ret5m", "ext_vol"): df[c] = np.nan
    # previous end of the same series (C0 anchor)
    import families as F, screen, collections
    ends = collections.defaultdict(set)
    for e in P.load_events("/home/user/pk_cache/events_deep.jsonl") + P.load_events("/home/user/pk_cache/events.jsonl"):
        t = screen.parse_ts(e.get("endDate"))
        if t: ends[F.family_key(e)].add(t)
    ends = {k: sorted(v) for k, v in ends.items()}
    cache = {}
    for fam, g in df.groupby("fam"):
        tk = ticker_of(fam)
        if not tk: continue
        try: bt, bc = cache.setdefault(tk, fetch(tk))
        except Exception as e: print("yahoo fail", tk, str(e)[:60]); continue
        es = ends[fam]
        sgn = g["outcome"].map(lambda o: 1.0 if str(o).lower() in ("up", "yes") else (-1.0 if str(o).lower() in ("down", "no") else np.nan))
        def px(t):
            i = bisect.bisect_right(bt, t - 300) - 1
            return bc[i] if i >= 0 and t - bt[i] < 6 * 3600 * 4 else np.nan
        # daily vol from bars: std of log changes between consecutive prev-end anchors
        anchors = [(e, px(e)) for e in es]; lr = [math.log(b[1] / a[1]) for a, b in zip(anchors, anchors[1:]) if a[1] == a[1] and b[1] == b[1]]
        vol = np.std(lr) if len(lr) >= 8 else np.nan
        for ix, r in g.iterrows():
            i = bisect.bisect_left(es, r["end"]); 
            if i == 0: continue
            c0 = px(es[i - 1]); pt = px(r["ts"])
            if not (c0 == c0 and pt == pt): continue
            x = math.log(pt / c0); s = sgn[ix]
            df.at[ix, "ext_x"] = x * s
            if vol == vol and vol > 0: df.at[ix, "ext_z"] = x * s / (vol * math.sqrt(min(1.0, r["H"] / 23400.0) + 0.05))
            p1 = px(r["ts"] - 3600); p5 = px(r["ts"] - 300)
            df.at[ix, "ext_ret1h"] = (math.log(pt / p1) * s) if p1 == p1 else np.nan
            df.at[ix, "ext_ret5m"] = (math.log(pt / p5) * s) if p5 == p5 else np.nan
            df.at[ix, "ext_vol"] = vol
    return df
