"""Daily P&L report for the metric pickoff paper node. Reads Nautilus's OWN fills report (CSV from trader.generate_order_fills_report()) and settles each held token
at resolution (payout 1 if the token's outcome won else 0, from Gamma outcomePrices of the market). No fill, queue or fee logic here: price, quantity and commission are Nautilus's.
Label on every $: SIM (paper fills on live books; fee = Nautilus PolymarketFeeModel/adapter; one day is not a verdict).
Usage: python3 daily_report.py fills.csv [--day YYYY-MM-DD]   (resolution read live from gamma-api.polymarket.com by condition id)"""
import csv, json, sys, collections, re


def split_id(instrument_id):
    """Nautilus Polymarket instrument id '<condition_id>-<token_id>.POLYMARKET' -> (condition_id, token_id)."""
    s = str(instrument_id).split(".")[0]
    c, _, t = s.partition("-")
    return c, t


def settle(fills, winners):
    """fills: dicts with instrument_id, side, filled_qty, avg_px, commissions, ts. winners: {condition_id: winning token_id or None (unresolved)}.
    Returns rows + totals by side (YES/NO decided from the side column the strategy logged in the client order tag when present, else by token)."""
    rows, tot = [], collections.defaultdict(float)
    for f in fills:
        if str(f["side"]).upper() != "BUY":
            continue
        cond, tok = split_id(f["instrument_id"])
        qty, px = float(f["filled_qty"]), float(f["avg_px"])
        m = re.findall(r"[-+]?\d*\.\d+|\d+", str(f.get("commissions", "0")))
        fee = float(m[0]) if m else 0.0
        w = winners.get(cond)
        if w is None:
            rows.append(dict(f, status="UNRESOLVED", pnl=None)); continue
        payout = 1.0 if tok == w else 0.0
        pnl = qty * (payout - px) - fee
        rows.append(dict(f, status="WON" if payout else "LOST", stake=round(qty * px, 2), fee=fee, pnl=round(pnl, 4)))
        tot["stake"] += qty * px; tot["fee"] += fee; tot["pnl"] += pnl; tot["n"] += 1; tot["won"] += payout
    return rows, dict(tot)


def gamma_winners(conds):
    import requests
    out = {}
    for c in conds:
        r = requests.get("https://gamma-api.polymarket.com/markets", params={"condition_ids": c}, timeout=30).json()
        if not r:
            out[c] = None; continue
        m = r[0]; op = [float(x) for x in json.loads(m["outcomePrices"])]; tk = json.loads(m["clobTokenIds"])
        out[c] = tk[op.index(1.0)] if 1.0 in op and m.get("closed") else None
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    fills = list(csv.DictReader(open(a[0])))
    winners = gamma_winners({split_id(f["instrument_id"])[0] for f in fills})
    rows, tot = settle(fills, winners)
    print(json.dumps(dict(label="SIM", fills=len(fills), totals=tot, unresolved=sum(1 for r in rows if r["status"] == "UNRESOLVED")), indent=1))
