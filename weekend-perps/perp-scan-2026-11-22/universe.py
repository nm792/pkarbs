#!/usr/bin/env python3
"""Build the contract universe for the perp-related arbs scan. Usage: python3 universe.py OUTDIR
Reads public Polymarket gamma (public-search, per-underlying queries), keeps events on underlyings that have a Hyperliquid xyz perp
(or a Polymarket perp), and tags each with a family. Universe comes from SEARCH, so low-volume events can be missed: stated in the result.
No orders, no keys."""
import json, re, sys, time, urllib.parse, urllib.request

G = "https://gamma-api.polymarket.com"
# underlying keyword (as in the slug) -> (HL xyz symbol, yahoo symbol, kind, gap margin)
UNDER = {
    "xauusd": ("GOLD", "GC=F", "METALS", 0.005), "xagusd": ("SILVER", "SI=F", "METALS", 0.005),
    "wti": ("CL", "CL=F", "OIL", 0.005), "ng": ("NATGAS", "NG=F", "OIL", 0.005),
    "nvda": ("NVDA", "NVDA", "STOCK", 0.002), "aapl": ("AAPL", "AAPL", "STOCK", 0.002), "msft": ("MSFT", "MSFT", "STOCK", 0.002),
    "meta": ("META", "META", "STOCK", 0.002), "googl": ("GOOGL", "GOOGL", "STOCK", 0.002), "tsla": ("TSLA", "TSLA", "STOCK", 0.002),
    "coin": ("COIN", "COIN", "STOCK", 0.002), "hood": ("HOOD", "HOOD", "STOCK", 0.002), "pltr": ("PLTR", "PLTR", "STOCK", 0.002),
    "mu": ("MU", "MU", "STOCK", 0.002), "amzn": ("AMZN", "AMZN", "STOCK", 0.002), "mstr": ("MSTR", "MSTR", "STOCK", 0.002),
    "nflx": ("NFLX", "NFLX", "STOCK", 0.002), "spx": ("SP500", "^GSPC", "INDEX", 0.002),
}


def family_of(slug):
    """-> (family, underlying key or None). Families: OPEN, TOUCH-<kind>, CLOSE-<kind>, HL-BINANCE-FUT, HIP3-OI. None if out of scope."""
    s = slug
    if re.match(r"^(spx|spy)-opens-up-or-down-on-", s):
        return ("OPEN", "spx" if s.startswith("spx") else "spy")
    if s.startswith("what-price-will-hyperliquid-hit"):
        return ("HL-BINANCE-FUT", "hype")
    if s.startswith("what-will-hyperliquid-hip-3-open-interest"):
        return ("HIP3-OI", None)
    m = re.match(r"^what-price-will-([a-z]+)-hit-in-november-2026$", s) or re.match(r"^will-([a-z]+)-hit-week-of-", s)
    if m and m.group(1) in UNDER:
        return ("TOUCH-" + UNDER[m.group(1)][2], m.group(1))
    m = re.match(r"^spx-hit-dec-2026$", s)
    if m:
        return ("TOUCH-INDEX", "spx")
    m = re.match(r"^([a-z]+)-(?:close-above-on|above-in)-", s) or re.match(r"^(spy)-(?:closes-above|up-or-down)-on-", s)
    if m and (m.group(1) in UNDER or m.group(1) == "spy"):
        return ("CLOSE-" + (UNDER[m.group(1)][2] if m.group(1) in UNDER else "INDEX"), m.group(1))
    return None


def j(u):
    for _ in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "data-scan"}), timeout=40))
        except Exception:
            time.sleep(1.5)
    return {}


def main(out):
    qs = set()
    for k in list(UNDER) + ["spy", "qqq", "hyperliquid"]:
        qs |= {k + " hit", "what price will " + k + " hit", "will " + k + " hit week of", k + " up or down", k + " close above", k + " above in november"}
    qs |= {"spx opens up or down", "spy opens up or down", "hyperliquid hip-3 open interest", "what price will hyperliquid hit", "spx hit", "spy up or down"}
    ev = {}
    for q in sorted(qs):
        for pg in (1, 2):
            d = j(G + "/public-search?q=" + urllib.parse.quote(q) + "&limit_per_type=25&events_status=active&page=%d" % pg)
            for e in (d.get("events") or []):
                ev[e["slug"]] = e
    rows = []
    for s, e in ev.items():
        f = family_of(s)
        if not f:
            continue
        rows.append(dict(slug=s, family=f[0], under=f[1], id=e.get("id"), title=e.get("title"), end=e.get("endDate"), nm=len(e.get("markets") or []),
                         gamma_v24=float(e.get("volume24hr") or 0), gamma_liq=float(e.get("liquidity") or 0)))
    rows.sort(key=lambda r: (r["family"], -r["gamma_v24"]))
    json.dump(dict(built=time.time(), n_queries=len(qs), n_search_events=len(ev), events=rows), open(out + "/universe.json", "w"))
    from collections import Counter
    print("queries", len(qs), "search events", len(ev), "in-scope events", len(rows))
    for fam, n in sorted(Counter(r["family"] for r in rows).items()):
        print(" ", fam, n)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
