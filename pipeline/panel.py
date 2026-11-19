"""Alpha158-style feature panel on Polymarket tokens, from each token's OWN prints strictly before the decision time.
Operators follow qlib's Alpha158 (ROC, MA, STD, BETA, RSQR, RESI, MAX, MIN, QTLU, QTLD, RANK, RSV, IMAX, IMIN, CNTP, CNTN, SUMP, VMA, KBAR) with
calendar windows instead of bar counts (Polymarket tokens have irregular prints, not daily OHLCV bars)."""
import bisect, gzip, json, math, os, sys, collections, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, families as F, pit_store as P
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
WINS = {"5m": 300, "15m": 900, "1h": 3600, "3h": 10800, "6h": 21600, "24h": 86400}
HORIZ = {"10m": 600, "1h": 3600, "6h": 21600, "24h": 86400}
NAN = float("nan")


class Tape:
    def __init__(self, rows):
        rows = sorted(rows)
        self.ts = np.array([r[0] for r in rows], float); self.side = np.array([1 if r[1] == "BUY" else -1 for r in rows])
        self.px = np.array([r[2] for r in rows], float); self.sz = np.array([r[3] for r in rows], float)

    def idx(self, t): return int(np.searchsorted(self.ts, t, "left"))

    def last_before(self, t):
        i = self.idx(t) - 1
        return self.px[i] if i >= 0 else NAN


def win_feats(tp, t, last, W, pre):
    f = {}
    i1 = tp.idx(t); i0 = tp.idx(t - W)
    pref = tp.last_before(t - W)
    f[f"ROC{pre}"] = pref / last if pref == pref else NAN
    n = i1 - i0
    f[f"CNT{pre}"] = float(n)
    keys = ["MA", "MAX", "MIN", "STD", "QTLU", "QTLD", "RANK", "RSV", "IMAX", "IMIN", "BETA", "RSQR", "RESI", "KMID", "KLEN", "KUP", "KLOW",
            "CNTP", "SUMP", "VOL", "IMB", "AVGSZ"]
    if n == 0:
        for k in keys: f[f"{k}{pre}"] = NAN
        f[f"VOL{pre}"] = 0.0
        return f
    p = tp.px[i0:i1]; s = tp.sz[i0:i1]; sd = tp.side[i0:i1]; tt = tp.ts[i0:i1]
    usd = float((p * s).sum())
    f[f"MA{pre}"] = (usd / s.sum()) / last; f[f"MAX{pre}"] = p.max() / last; f[f"MIN{pre}"] = p.min() / last
    f[f"STD{pre}"] = p.std() / last if n > 1 else 0.0
    f[f"QTLU{pre}"] = np.quantile(p, 0.8) / last; f[f"QTLD{pre}"] = np.quantile(p, 0.2) / last
    f[f"RANK{pre}"] = float((p <= last).mean()); f[f"RSV{pre}"] = (last - p.min()) / (p.max() - p.min() + 1e-9)
    f[f"IMAX{pre}"] = float(np.argmax(p)) / n; f[f"IMIN{pre}"] = float(np.argmin(p)) / n
    if n >= 3 and tt.std() > 0:
        x = (tt - tt.mean()) / W; b = np.polyfit(x, p, 1); fit = np.polyval(b, x); ssr = ((p - fit) ** 2).sum(); sst = ((p - p.mean()) ** 2).sum() + 1e-12
        f[f"BETA{pre}"] = b[0] / last; f[f"RSQR{pre}"] = 1 - ssr / sst; f[f"RESI{pre}"] = (last - fit[-1]) / last
    else:
        f[f"BETA{pre}"] = f[f"RSQR{pre}"] = f[f"RESI{pre}"] = NAN
    o = p[0]
    f[f"KMID{pre}"] = (p[-1] - o) / max(o, 1e-3); f[f"KLEN{pre}"] = (p.max() - p.min()) / max(o, 1e-3)
    f[f"KUP{pre}"] = (p.max() - max(o, p[-1])) / max(o, 1e-3); f[f"KLOW{pre}"] = (min(o, p[-1]) - p.min()) / max(o, 1e-3)
    d = np.diff(p) if n > 1 else np.array([0.0])
    f[f"CNTP{pre}"] = float((d > 0).mean()); f[f"SUMP{pre}"] = float(d[d > 0].sum() / (np.abs(d).sum() + 1e-9))
    f[f"VOL{pre}"] = math.log1p(usd); f[f"IMB{pre}"] = float((s * sd).sum() / s.sum()); f[f"AVGSZ{pre}"] = math.log1p(float(s.mean()))
    return f


def row_feats(tps, idx, t, H, meta):
    tp = tps[idx]; other = tps[1 - idx]
    last = tp.last_before(t)
    if not (last == last) or last <= 0: return None
    f = {"last": last, "logH": math.log(H)}
    for pre, W in WINS.items(): f.update(win_feats(tp, t, last, W, "_" + pre))
    # 24h-relative volume (qlib VMA analogue)
    f["VMA_1h_24h"] = f["VOL_1h"] - math.log1p(math.expm1(f["VOL_24h"]) / 24 + 0) if f["VOL_24h"] == f["VOL_24h"] else NAN
    ol = other.last_before(t); f["other_last"] = ol; f["sum_last"] = last + ol if ol == ol else NAN
    op = other.last_before(t - 3600); f["other_ROC_1h"] = op / ol if (op == op and ol == ol and ol > 0) else NAN
    i1 = tp.idx(t); f["n_before"] = math.log1p(i1); f["since_last"] = math.log1p(t - tp.ts[i1 - 1])
    f["age_h"] = (t - tp.ts[0]) / 3600 if i1 > 0 else NAN
    f["usd_total"] = math.log1p(float((tp.px[:i1] * tp.sz[:i1]).sum()))
    l = dt.datetime.fromtimestamp(t, NY); f["hour_ny"] = l.hour + l.minute / 60; f["dow"] = l.weekday()
    sellp = tp.px[max(0, i1 - 20):i1][tp.side[max(0, i1 - 20):i1] < 0]; buyp = tp.px[max(0, i1 - 20):i1][tp.side[max(0, i1 - 20):i1] > 0]
    f["bounce"] = (buyp[-1] - sellp[-1]) if len(buyp) and len(sellp) else NAN
    return f


def build(event_lists, out_path, workers=1):
    rows = []
    for fam_events in event_lists:
        for e in fam_events:
            fam = F.family_key(e); grp = screen.group_of(fam)
            for m in (screen.binary_resolved(x) for x in e["markets"]):
                if not m: continue
                path = f"{screen.CACHE}/{m['cond']}.json.gz"
                if not os.path.exists(path): continue
                d = json.load(gzip.open(path, "rt"))
                by = {t: [] for t in m["tokens"]}
                for ts, side, tok, px, sz, oi in d["rows"]:
                    if tok in by: by[tok].append((ts, side, px, sz))
                if not by[m["tokens"][0]] or not by[m["tokens"][1]]: continue
                tps = [Tape(by[t]) for t in m["tokens"]]
                end = m["end"] or screen.parse_ts(e["endDate"])
                for hn, H in HORIZ.items():
                    t = end - H
                    if m["closed"] and m["closed"] < t: continue
                    for idx in (0, 1):
                        tp = tps[idx]
                        # causal fill: first BUY print at/after t within window
                        i = tp.idx(t); w = max(H // 4, 60); fill = None
                        j = i
                        while j < len(tp.ts) and tp.ts[j] <= t + w:
                            if tp.side[j] > 0: fill = tp.px[j]; break
                            j += 1
                        if fill is None or fill <= 0.01 or fill >= 0.99: continue
                        f = row_feats(tps, idx, t, H, None)
                        if f is None: continue
                        cap = float(sum(tp.sz[k] for k in range(i, j + 1) if tp.side[k] > 0 and tp.ts[k] <= t + w))
                        win = 1.0 if idx == m["win"] else 0.0
                        f.update(outcome=m["labels"][idx], question=(m.get("question") or "")[:80], fam=fam, grp=grp, h=hn, H=H, cond=m["cond"], event=e["id"], token=idx, ts=t, end=end, day=int(t // 86400),
                                 fill=fill, win=win, edge=win - fill, cap_sh=cap)
                        rows.append(f)
    import pandas as pd
    df = pd.DataFrame(rows); df.to_pickle(out_path); return df


if __name__ == "__main__":
    deep = P.load_events("/home/user/pk_cache/events_deep.jsonl")
    # restrict to the 220-per-family sample used by run4 so cached trades exist
    by = collections.defaultdict(list)
    for e in deep:
        if not F.excluded_reason(e): by[F.family_key(e)].append(e)
    lists = [screen.sample_events(es, 220, 2026) for es in by.values()]
    lists.append(json.load(open("/home/user/pk_cache/events_extra.json")))
    df = build(lists, "/home/user/pk_cache/panel.pkl")
    print(df.shape, df["fam"].nunique(), df["event"].nunique(), df["cond"].nunique())
    print(df.groupby("grp").size().sort_values(ascending=False).head(8))
