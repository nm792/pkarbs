#!/usr/bin/env python3
"""EXPLORATORY: one chart per match. Goalserve winner-market implied probability (step, from the raw sample) vs Polymarket TRADE prices of each
token's OWN trades (never 1 - other token). Eyeball tool, not a test: no verdict. Trades come from the public data-api /v2/trades?condition=...
Usage: python3 -I chart_match.py --slug nhl-lak-tor-2026-11-19 --out out.png [--sample sample.jsonl.gz --eid EID] [--trades-json t.json] [--pad-min 20]
Prints a table of Goalserve >=2c moves with the median own-token trade price in the 60 s before and after (only when trades exist in both windows)."""
import argparse, gzip, json, re, statistics, subprocess, sys, datetime
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

UA = "curl/8"


def get(url):
    return json.loads(subprocess.run(["curl", "-s", "--compressed", "-H", "User-Agent: " + UA, url], capture_output=True, text=True).stdout)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def market_for(slug):
    ev = get("https://gamma-api.polymarket.com/events?slug=" + slug)[0]
    for m in ev["markets"]:
        if m.get("sportsMarketType") in ("moneyline", None) and len(json.loads(m["outcomes"])) == 2:
            return ev, m
    raise SystemExit("no two-outcome market in " + slug)


def trades_for(cond):
    out, cur = [], None
    while True:
        d = get("https://data-api.polymarket.com/v2/trades?condition=%s&limit=1000%s" % (cond, "&cursor=" + cur if cur else ""))
        if "data" not in d:
            raise SystemExit("data-api error: " + json.dumps(d)[:300])
        out += d["data"]
        cur = (d.get("pagination") or {}).get("next_cursor")
        if not cur or not (d.get("pagination") or {}).get("has_more"):
            return out


def feed_series(sample, eid):
    """-> [(t_s, p_home, p_away, home, away)] from the normalised winner odds (1/odds / sum), only rows with two open participants."""
    rows = []
    for l in gzip.open(sample, "rt"):
        r = json.loads(l)
        if eid and r["eid"] != eid:
            continue
        e = r["event"]
        ti = e.get("team_info") or {}
        h, a = (ti.get("home") or {}).get("name"), (ti.get("away") or {}).get("name")
        for m in (e.get("odds") or {}).values():
            ps = [x for x in (m.get("participants") or {}).values() if isinstance(x, dict)]
            if len(ps) != 2:
                continue
            try:
                o = [float(x["value_eu"]) for x in ps]
            except Exception:
                continue
            if min(o) <= 1.0 or m.get("suspend") not in (0, "0", False, None) or any(x.get("suspend") not in (0, "0", False, None) for x in ps):
                continue
            inv = [1 / x for x in o]
            ph = {norm(x.get("name")): inv[i] / sum(inv) for i, x in enumerate(ps)}
            rows.append((r["recv_ns"] / 1e9, ph.get(norm(h)), ph.get(norm(a)), h, a))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sample"); ap.add_argument("--eid"); ap.add_argument("--trades-json"); ap.add_argument("--pad-min", type=float, default=20)
    ap.add_argument("--t-from", type=float); ap.add_argument("--t-to", type=float)
    a = ap.parse_args()
    ev, m = market_for(a.slug)
    outs = json.loads(m["outcomes"])
    tr = json.load(open(a.trades_json)) if a.trades_json else trades_for(m["conditionId"])
    fs = feed_series(a.sample, a.eid) if a.sample else []
    lo = a.t_from or (min(x[0] for x in fs) - a.pad_min * 60 if fs else min(t["timestamp"] for t in tr))
    hi = a.t_to or (max(x[0] for x in fs) + a.pad_min * 60 if fs else max(t["timestamp"] for t in tr))
    tr = [t for t in tr if lo <= t["timestamp"] <= hi]
    ts = lambda x: datetime.datetime.fromtimestamp(x, datetime.timezone.utc)
    fig, ax = plt.subplots(figsize=(13, 5.5))
    cols = {outs[0]: "tab:blue", outs[1]: "tab:orange"}
    for o in outs:
        pts = [t for t in tr if t["outcome"] == o]
        ax.scatter([ts(t["timestamp"]) for t in pts], [t["price"] for t in pts], s=[max(6, min(120, t["size"] / 4)) for t in pts], alpha=.5, c=cols[o], label="PM trades of %s token (own price)" % o)
    if fs:
        h = fs[0][3]
        ax.step([ts(x[0]) for x in fs], [x[1] for x in fs], where="post", c="k", lw=1.6, label="Goalserve implied win prob, %s (normalised 1/odds)" % h)
        ax.step([ts(x[0]) for x in fs], [x[2] for x in fs], where="post", c="gray", lw=1.0, ls="--", label="Goalserve implied win prob, %s" % fs[0][4])
        for i in range(1, len(fs)):
            if fs[i][1] is not None and fs[i - 1][1] is not None and abs(fs[i][1] - fs[i - 1][1]) >= 0.02:
                ax.axvline(ts(fs[i][0]), c="red", alpha=.25, lw=1)
    ax.set_ylim(0, 1); ax.set_ylabel("probability / price"); ax.set_title("%s  (EXPLORATORY; red lines = Goalserve moves of 2c or more)" % ev["title"]); ax.legend(loc="best", fontsize=8); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(a.out, dpi=110)
    n = 0
    print("trades in window", len(tr), "goalserve rows", len(fs))
    for i in range(1, len(fs)):
        if fs[i][1] is None or fs[i - 1][1] is None or abs(fs[i][1] - fs[i - 1][1]) < 0.02:
            continue
        t = fs[i][0]; h = fs[i][3]
        pre = [x["price"] for x in tr if norm(x["outcome"]) == norm(h) and t - 60 <= x["timestamp"] < t]
        post = [x["price"] for x in tr if norm(x["outcome"]) == norm(h) and t <= x["timestamp"] < t + 60]
        n += 1
        print("%s Goalserve %s %.3f -> %.3f | PM %s trades 60s before median %s (n=%d), 60s after median %s (n=%d)" % (ts(t).strftime("%H:%M:%S"), h, fs[i - 1][1], fs[i][1], h, statistics.median(pre) if pre else None, len(pre), statistics.median(post) if post else None, len(post)))
    print("moves>=2c", n)


if __name__ == "__main__":
    main()
