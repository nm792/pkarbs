#!/usr/bin/env python3
"""Read-only snapshot of OWN-TOKEN books for the perp-related universe at a decision time. No keys, no orders.
Usage: python3 snapshot.py RUNDIR LABEL      (reads RUNDIR/universe.json; appends RUNDIR/snap_<LABEL>.jsonl)
Line 1 = meta (time, Hyperliquid xyz marks, last Yahoo closes). Then one row per token (YES and NO separately, each from its own book)."""
import gzip, json, sys, time, urllib.request
from universe import UNDER
from snaplib import market_tokens, token_row
from pscanlib import perp_depth_usd

G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"


def req(u, body=None, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(u, data=json.dumps(body).encode() if body is not None else None,
                                       headers={"user-agent": "data-scan", "content-type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=60))
        except Exception as e:
            err = repr(e)[:120]
            time.sleep(1 + 2 * i)
    return {"_error": err}


def hl_marks():
    m = req("https://api.hyperliquid.xyz/info", {"type": "metaAndAssetCtxs", "dex": "xyz"})
    if not isinstance(m, list):
        return {}
    px = {u["name"].split(":")[1]: float(c["markPx"]) for u, c in zip(m[0]["universe"], m[1]) if c.get("markPx")}
    return {k: px[v[0]] for k, v in UNDER.items() if v[0] in px}


def yahoo_close(sym):
    d = req("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=7d&interval=1d" % sym.replace("^", "%5E"))
    try:
        r = d["chart"]["result"][0]
        cl = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
        return cl[-1]
    except Exception:
        return None


def main(run, label):
    uni = json.load(open(run + "/universe.json"))["events"]
    t0 = time.time()
    marks = hl_marks()
    closes = {k: yahoo_close(v[1]) for k, v in UNDER.items()}
    hl_depth = {}
    for k, v in UNDER.items():
        b = req("https://api.hyperliquid.xyz/info", {"type": "l2Book", "coin": "xyz:" + v[0]})
        try:
            bids, asks = b["levels"]
            bb = [(float(x["px"]), float(x["sz"])) for x in bids]; aa = [(float(x["px"]), float(x["sz"])) for x in asks]
            mid = (max(p for p, _ in bb) + min(p for p, _ in aa)) / 2
            hl_depth[k] = dict(mid=mid, ask5bp=perp_depth_usd(aa, mid, 5, "ask"), bid5bp=perp_depth_usd(bb, mid, 5, "bid"))
        except Exception:
            hl_depth[k] = None
    out = open("%s/snap_%s.jsonl" % (run, label), "a")
    out.write(json.dumps(dict(kind="meta", t=t0, label=label, marks=marks, closes=closes, margins={k: v[3] for k, v in UNDER.items()}, hl_depth=hl_depth)) + "\n")
    toks = []   # (event slug, family, under, market dict, outcome, token)
    for e in uni:
        ev = req(G + "/events?slug=" + e["slug"])
        if not isinstance(ev, list) or not ev:
            out.write(json.dumps(dict(kind="err", slug=e["slug"], err="gamma event missing")) + "\n"); continue
        for m in ev[0].get("markets") or []:
            if m.get("closed") or not m.get("clobTokenIds"):
                continue
            for outc, tk in market_tokens(m):
                toks.append((e["slug"], e["family"], e["under"], m, outc, tk))
    books = {}
    for i in range(0, len(toks), 80):
        chunk = toks[i:i + 80]
        r = req(C + "/books", [{"token_id": x[5]} for x in chunk])
        if isinstance(r, list):
            for b in r:
                books[b.get("asset_id")] = b
    ts = time.time()
    n_ok = 0
    for slug, fam, under, m, outc, tk in toks:
        row = token_row(slug, fam, m, outc, tk, books.get(tk), ts)
        row["under"] = under; row["kind"] = "tok"
        n_ok += row["book_ok"]
        out.write(json.dumps(row) + "\n")
    out.close()
    print("snapshot %s: %d events, %d tokens, %d with a recorded book, %.0fs, marks %d, closes %d" % (label, len(uni), len(toks), n_ok, time.time() - t0, len(marks), sum(v is not None for v in closes.values())))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
