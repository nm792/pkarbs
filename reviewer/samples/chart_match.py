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


def same(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a in b or b in a))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def market_for(slug):
    ev = get("https://gamma-api.polymarket.com/events?slug=" + slug)[0]
    for m in ev["markets"]:
        if m.get("sportsMarketType") in ("moneyline", None) and len(json.loads(m["outcomes"])) == 2:
            return ev, m
    raise SystemExit("no two-outcome market in " + slug)


def check_rows(rows, cond):
    """R-080a: v2 SILENTLY IGNORES unknown params and then returns OTHER markets' trades; every row must carry the requested condition id."""
    bad = [r for r in rows if (r.get("condition_id") or r.get("conditionId") or r.get("condition")) != cond]
    if bad:
        raise SystemExit("data-api returned %d of %d rows for another market (condition filter ignored?)" % (len(bad), len(rows)))
    return rows


def in_window(tr, lo, hi):
    """R-080 addendum: v2 /trades ignores start/end, so the window is applied here on each row's timestamp."""
    return [t for t in tr if lo <= t["timestamp"] <= hi]


def trades_for(cond, getter=None):
    getter = getter or get
    out, cur = [], None
    while True:
        d = getter("https://data-api.polymarket.com/v2/trades?condition=%s&limit=1000%s" % (cond, "&cursor=" + cur if cur else ""))
        if "data" not in d:
            raise SystemExit("data-api error: " + json.dumps(d)[:300])
        out += check_rows(d["data"], cond)
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
            side = {}
            for i, x in enumerate(ps):
                n = norm(x.get("name"))
                side["h" if n in ("home", "1", norm(h)) else "a" if n in ("away", "2", norm(a)) else "?%d" % i] = inv[i] / sum(inv)
            rows.append((r["recv_ns"] / 1e9, side.get("h"), side.get("a"), h, a, (e.get("info") or {}).get("score")))
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
    tr = in_window(tr, lo, hi)
    ts = lambda x: datetime.datetime.fromtimestamp(x, datetime.timezone.utc)
    fig, ax = plt.subplots(figsize=(13, 5.5))
    cols = {outs[0]: "tab:blue", outs[1]: "tab:orange"}
    for o in outs:
        pts = [t for t in tr if t["outcome"] == o]
        ax.scatter([ts(t["timestamp"]) for t in pts], [t["price"] for t in pts], s=[max(6, min(120, t["size"] / 4)) for t in pts], alpha=.5, c=cols[o], label="PM trades of %s token (own price)" % o)
    if fs:
        h = fs[-1][3]      # last row's names (hockey rows can list the teams swapped for the first pre-game rows)
        ax.step([ts(x[0]) for x in fs], [x[1] for x in fs], where="post", c="k", lw=1.6, label="Goalserve implied win prob, %s (normalised 1/odds)" % h)
        ax.step([ts(x[0]) for x in fs], [x[2] for x in fs], where="post", c="gray", lw=1.0, ls="--", label="Goalserve implied win prob, %s" % fs[-1][4])
        for i in range(1, len(fs)):
            if fs[i][1] is not None and fs[i - 1][1] is not None and abs(fs[i][1] - fs[i - 1][1]) >= 0.02:
                ax.axvline(ts(fs[i][0]), c="red", alpha=.25, lw=1)
            if fs[i][5] != fs[i - 1][5] and fs[i][5] not in (None, ""):
                ax.axvline(ts(fs[i][0]), c="green", alpha=.35, lw=1, ls=":")
    ax.set_ylim(0, 1); ax.set_ylabel("probability / price"); ax.set_title("%s  (EXPLORATORY; red = Goalserve odds move >=2c, green dotted = Goalserve score change)" % ev["title"]); ax.legend(loc="best", fontsize=8); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(a.out, dpi=110)
    n = 0
    both = []
    print("trades in window", len(tr), "goalserve rows", len(fs))
    for i in range(1, len(fs)):
        if fs[i][1] is None or fs[i - 1][1] is None or abs(fs[i][1] - fs[i - 1][1]) < 0.02:
            continue
        t = fs[i][0]; h = fs[-1][3]
        pre = [x["price"] for x in tr if same(x["outcome"], h) and t - 60 <= x["timestamp"] < t]
        post = [x["price"] for x in tr if same(x["outcome"], h) and t <= x["timestamp"] < t + 60]
        n += 1
        if pre and post:
            sg = 1 if fs[i][1] > fs[i - 1][1] else -1
            d = sg * (statistics.median(post) - statistics.median(pre))
            both.append(d)
        print("%s Goalserve %s %.3f -> %.3f | PM %s trades 60s before median %s (n=%d), 60s after median %s (n=%d)" % (ts(t).strftime("%H:%M:%S"), h, fs[i - 1][1], fs[i][1], h, statistics.median(pre) if pre else None, len(pre), statistics.median(post) if post else None, len(post)))
    print("moves>=2c", n)
    if both:
        print("SUMMARY moves with trades in both 60 s windows: %d; PM own-token median moved WITH the Goalserve move in %d (%.0f%%); mean signed change %.1f c; median %.1f c" % (len(both), sum(1 for x in both if x > 0), 100.0 * sum(1 for x in both if x > 0) / len(both), 100 * sum(both) / len(both), 100 * statistics.median(both)))
    else:
        print("SUMMARY no move had trades in both 60 s windows")


if __name__ == "__main__":
    main()
