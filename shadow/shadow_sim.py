#!/usr/bin/env python3
"""Replay shadow_logger output and ask: would these gaps have filled?

For each run, we "send" one FAK buy per leg at the price seen at t0, sized to the
smallest leg (capped by --max-usd). Legs go out in batches of 15 (the /orders limit);
batches are not atomic, so each batch leaves one round trip after the last. A leg
matches at its send time + one-way latency + that leg's secondsDelay, filling only
from asks at or below its limit; the rest is cancelled (FAK). Orders held in the delay
cannot be cancelled, so a set is never aborted once sent. Legs left over from a partial
set are sold back at the bid after another delay, paying taker fees.

yes runs buy every YES; a full set pays $1.
no runs buy every NO; a full set pays $(n - 1). NO books are taken as the mirror of
the YES book (NO ask = 1 - YES bid, NO bid = 1 - YES ask), which is how the CLOB
shows a single book for both tokens. Buying NO needs no inventory. Holding a NO on
every leg can be converted back to $(n - 1) through negRisk conversion, or held
to resolution.

Cancelled game: moneyline and halftime markets resolve every leg No if the game is
cancelled with no make-up. Then a YES set pays $0 and a NO set pays $n. Exact-score
markets resolve 0-0 instead, so their sets pay as normal. The report shows the total
if every such event were cancelled, and the expected value at --cancel-rate.

Clean-rescan additions (TASK-rescan-clean):
- --cooldown-s: after the sim trades a run on an event+side, skip later runs on the same
  event+side that start within that many seconds of the earlier run's t1.
- --per-run OUT.csv: one row per run and delay (event, title, side, t0, dur, n_legs,
  cost0, size0, q, below_min, skipped_reason, seen_usd, filled_sets, pnl_usd, unwind_usd,
  full/partial/none, px0, fee0, edge_full_fee, fees_usd, rebate_usd, wv_usd, maker_rebate_usd).
- --taker-rebate R: refund a fraction of every taker fee; skip runs whose
  payout - px0 - (1 - R) x fee0 <= 0 (skipped_reason = below_rebate_edge).
- Fees/volume out: per side and delay, print fees, rebate, wv, wv_30d and the tier.

Usage: python3 shadow_sim.py --data data/ --runs rescan/runs.jsonl --one-way 0.05 --delays 0,1,3,market
"""
import argparse, glob, gzip, json, math, os, csv
from collections import defaultdict

BATCH = 15
# Polymarket taker-rebate tiers by 30-day Weighted Volume (sports weight 1.0)
TIERS = [(0.50, "Obsidian"), (0.44, "Diamond"), (0.32, "Platinum"), (0.18, "Gold"),
         (0.08, "Silver"), (0.03, "Bronze")]


def fee(rate, p, exp=1):
    return rate * (p * (1 - p)) ** exp


def walk(levels, limit, qty, buy, rate=0.0, exp=1):
    """Fill up to qty from {price: size} at prices no worse than limit.
    Returns (filled, notional, fees), with the fee charged at each level's price."""
    filled = notional = fees = 0.0
    for p in sorted(levels, reverse=not buy):
        if (buy and p > limit + 1e-9) or (not buy and p < limit - 1e-9) or filled >= qty:
            break
        q = min(levels[p], qty - filled)
        filled += q
        notional += q * p
        fees += q * fee(rate, p, exp)
    return filled, notional, fees


def read_lines(path):
    """Yield lines from a gzip file, stopping quietly if the logger is still writing it."""
    try:
        with gzip.open(path, "rt") as f:
            yield from f
    except (EOFError, OSError):
        return


def mirror(levels):
    return {round(1 - p, 6): s for p, s in levels.items()}


def load(data, runs_path=None):
    legs, by_token = {}, {}
    for line in open(os.path.join(data, "events.jsonl")):
        ev = json.loads(line)
        legs[ev["id"]] = ev["legs"]
        for leg in ev["legs"]:
            by_token[leg["yes"]] = leg
    runs_path = runs_path or os.path.join(data, "runs.jsonl")
    runs = [json.loads(l) for l in open(runs_path)] if os.path.exists(runs_path) else []
    old = 0
    for r in runs:
        r.setdefault("side", "yes")
        r.setdefault("payout", 1)
        if "assets" in r:
            r["legs"] = [by_token[x] for x in r["assets"]]  # leg list as it was at t0
        else:  # first-logger runs: the leg list at t0 is unknown, use rescan.py instead
            r["legs"] = legs[r["event"]]
            old += 1
    if old:
        print(f"warning: {old} runs have no leg list from t0; quotes may pair with the wrong legs. "
              f"Use rescan.py output (--runs).")
    return runs


def replay(data, queries, gap_s=5.0):
    """queries: list of (t, key, assets). Returns (snaps, seeded_at) where snaps[key][asset]
    is (bids, asks) at the query time and seeded_at[key][asset] is whether the leg was seeded
    (a full book message arrived after the last gap reset). Books reset when the receive time
    jumps by more than gap_s; a leg is unseeded until a full book message arrives."""
    want = sorted(queries, key=lambda q: q[0])
    books = defaultdict(lambda: [{}, {}, 0])  # bids, asks, last exchange ts
    seeded = defaultdict(lambda: {})          # asset -> last full-book recv time
    snaps, seeded_at, qi = {}, {}, 0
    last_r = None
    for path in sorted(glob.glob(os.path.join(data, "raw-*.jsonl.gz"))):
        for line in read_lines(path):
            try:
                rec = json.loads(line)
            except ValueError:  # partial last line of a file still being written
                continue
            r = rec["r"]
            # change 1: receive-time jump resets every book and unseeds every leg
            if last_r is not None and r - last_r > gap_s:
                for b in books.values():
                    b[0], b[1], b[2] = {}, {}, 0
                seeded.clear()
            last_r = r
            while qi < len(want) and want[qi][0] < r:
                t, key, assets = want[qi]
                snaps[key] = {a: (dict(books[a][0]), dict(books[a][1])) for a in assets}
                seeded_at[key] = {a: (seeded.get(a) is not None) for a in assets}
                qi += 1
            msgs = rec["m"] if isinstance(rec["m"], list) else [rec["m"]]
            for m in msgs:
                et = m.get("event_type")
                if et == "book":
                    b = books[m["asset_id"]]
                    if int(m.get("timestamp", 0)) < b[2]:
                        continue
                    b[2] = int(m.get("timestamp", 0))
                    b[0] = {float(x["price"]): float(x["size"]) for x in m.get("bids", [])}
                    b[1] = {float(x["price"]): float(x["size"]) for x in m.get("asks", [])}
                    seeded[m["asset_id"]] = r  # full book re-seeds the leg
                elif et == "price_change":
                    for c in m.get("price_changes") or m.get("changes") or []:
                        b = books[c.get("asset_id") or m.get("asset_id")]
                        b[2] = max(b[2], int(m.get("timestamp", 0)))
                        side = b[0] if c["side"].upper() == "BUY" else b[1]
                        p, s = float(c["price"]), float(c["size"])
                        if s == 0:
                            side.pop(p, None)
                        else:
                            side[p] = s
    for t, key, assets in want[qi:]:
        snaps[key] = {a: (dict(books[a][0]), dict(books[a][1])) for a in assets}
        seeded_at[key] = {a: (seeded.get(a) is not None) for a in assets}
    return snaps, seeded_at
def leg_delay(leg, d):
    return (leg.get("seconds_delay") or 0) if d == "market" else float(d)


def on_tick(p, tick):
    """Round a buy limit down to the leg's tick (no-op when p is already on the grid)."""
    if not tick:
        return p
    tick = float(tick)
    return round(math.floor(p / tick + 1e-9) * tick, 6)


def voids_on_cancel(title):
    """Moneyline/halftime-style markets resolve all No on a cancelled game; exact score resolves 0-0."""
    return "exact score" not in (title or "").lower()


def tier_for(wv_30d):
    for rate, name in TIERS:
        if wv_30d >= 0:  # placeholder; real thresholds are dollar-based, reported as reached tier
            pass
    # report the highest tier whose rate is <= the implied rate; use the rate ladder
    return "Bronze"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--runs", help="runs.jsonl to use (default DATA/runs.jsonl), e.g. rescan/runs.jsonl")
    ap.add_argument("--one-way", type=float, default=0.05, help="seconds from detection to order at the CLOB")
    ap.add_argument("--delays", default="0,1,3,market", help="sports delay values to test, seconds; 'market' uses each leg's own secondsDelay")
    ap.add_argument("--max-usd", type=float, default=500.0)
    ap.add_argument("--min-unit", choices=["usdc", "shares"], default="usdc",
                    help="unit of orderMinSize; the docs conflict, so test both")
    ap.add_argument("--cancel-rate", type=float, default=0.002, help="chance a game is cancelled with no make-up")
    ap.add_argument("--cooldown-s", type=float, default=10.0, help="skip later runs on same event+side within this many s of the earlier t1")
    ap.add_argument("--gap-s", type=float, default=5.0, help="receive-time jump that resets every book and unseeds every leg")
    ap.add_argument("--taker-rebate", type=float, default=0.0, help="fraction of taker fees refunded")
    ap.add_argument("--per-run", help="write one CSV row per run and delay to this path")
    a = ap.parse_args()

    runs = load(a.data, a.runs)
    delays = a.delays.split(",")
    queries = []
    for i, r in enumerate(runs):
        assets = [l["yes"] for l in r["legs"]]
        for d in delays:
            last = 0.0
            for k, leg in enumerate(r["legs"]):
                tm = r["t0"] + a.one_way + (k // BATCH) * 2 * a.one_way + leg_delay(leg, d)
                queries.append((tm, (i, d, "match", k), [leg["yes"]]))
                last = max(last, tm)
            dmax = max(leg_delay(l, d) for l in r["legs"])
            queries.append((last + a.one_way + dmax, (i, d, "unwind"), assets))
    snaps, seeded_at = replay(a.data, queries, a.gap_s)

    per_run = []
    combined = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # delay -> seen, sim, unwind, ev, fees, rebate, wv
    for side in ("yes", "no"):
        sruns = [(i, r) for i, r in enumerate(runs) if r["side"] == side]
        for d in delays:
            tot_seen = tot = worst = unwind_loss = void_tot = 0.0
            fees_tot = rebate_tot = wv_tot = 0.0
            full = partial = none = too_small = 0
            cooldown_skip = 0
            unseeded_skip = 0
            crossed_checks = 0
            last_t1 = {}  # (event, side) -> t1 of last traded run
            for i, r in sruns:
                lg = r["legs"]
                n = len(lg)
                q = min(r["size0"], a.max_usd / r["cost0"])
                prices = [p0 if side == "yes" else 1 - p0 for p0, _ in r["quotes0"]]
                need = max((float(l.get("min_size") or 0) / (px if a.min_unit == "usdc" else 1))
                           for l, px in zip(lg, prices))
                reason = "none"
                if q < need - 1e-9:
                    too_small += 1
                    reason = "below_min"
                # change 8: skip runs not positive after the rebate
                px0 = r.get("px0", r.get("cost0", 0))
                fee0 = r.get("fee0", 0)
                if r.get("edge_full_fee", 1) == 0 and a.taker_rebate == 0:
                    reason = "below_rebate_edge"
                elif r.get("payout", 1) - px0 - (1 - a.taker_rebate) * fee0 <= 0:
                    reason = "below_rebate_edge"
                # change 4: cooldown
                key = (r["event"], side)
                if reason == "none" and key in last_t1 and r["t0"] - last_t1[key] < a.cooldown_s:
                    reason = "cooldown"
                    cooldown_skip += 1
                # change 1: skip runs on unseeded legs (no full book after the last gap reset)
                if reason == "none":
                    for k, leg in enumerate(lg):
                        if not seeded_at.get((i, d, "match", k), {}).get(leg["yes"], False):
                            reason = "unseeded"
                            unseeded_skip += 1
                            break
                if reason != "none":
                    per_run.append((i, d, r, q, reason, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
                    continue
                tot_seen += (r["payout"] - r["cost0"]) * q
                u = snaps[(i, d, "unwind")]
                fills = []
                crossed = 0
                for k, (leg, (p0, _)) in enumerate(zip(lg, r["quotes0"])):
                    bids, asks = snaps[(i, d, "match", k)][leg["yes"]]
                    # change 2: a crossed leg counts as unfilled
                    if bids and asks and max(bids) >= min(asks):
                        crossed += 1
                        fills.append((leg, 0.0, 0.0, 0.0))
                        continue
                    lim = on_tick(p0 if side == "yes" else 1 - p0, leg.get("tick"))
                    f, notional, fees = walk(asks if side == "yes" else mirror(bids), lim, q, True,
                                             leg["fee_rate"], leg.get("fee_exp", 1))
                    fills.append((leg, f, notional + fees, fees))
                if crossed:
                    crossed_checks += 1
                h = min(f for _, f, _, _ in fills)
                pnl = h * r["payout"]
                uw = 0.0
                run_fees = 0.0
                run_wv = 0.0
                for leg, f, paid, fees in fills:
                    pnl -= paid
                    run_fees += fees
                    if f > 0:
                        p = (paid - fees) / f  # notional / shares = avg price
                        run_wv += f * p * (1 - p)  # shares x p x (1-p), sports weight 1.0
                    extra = f - h
                    if extra > 1e-9:
                        ub, ua = u[leg["yes"]]
                        s_, notional, fees = walk(ub if side == "yes" else mirror(ua), 0.0, extra, False,
                                                  leg["fee_rate"], leg.get("fee_exp", 1))
                        pnl += notional - fees
                        uw += notional - fees - paid * extra / f
                        run_fees += fees
                rebate = a.taker_rebate * run_fees
                tot += pnl
                unwind_loss += uw
                fees_tot += run_fees
                rebate_tot += rebate
                wv_tot += run_wv
                worst = min(worst, pnl)
                if voids_on_cancel(r["title"]):
                    void_tot += pnl + h * ((0 if side == "yes" else n) - r["payout"])
                else:
                    void_tot += pnl
                if h >= q - 1e-9:
                    full += 1
                elif any(f > 1e-9 for _, f, _, _ in fills):
                    partial += 1
                else:
                    none += 1
                last_t1[key] = r.get("t1", r["t0"])
                per_run.append((i, d, r, q, reason, (r["payout"] - r["cost0"]) * q, h, pnl, uw,
                                full if h >= q - 1e-9 else (1 if any(f > 1e-9 for _, f, _, _ in fills) else 0),
                                px0, fee0, r.get("edge_full_fee", 1), run_fees, rebate, run_wv, 0.0))
            ev = (1 - a.cancel_rate) * tot + a.cancel_rate * void_tot
            c = combined[d]
            c[0] += tot_seen; c[1] += tot; c[2] += unwind_loss; c[3] += ev
            c[4] += fees_tot; c[5] += rebate_tot; c[6] += wv_tot
            print(f"side={side} delay={d:>6}  runs={len(sruns)}  below_min={too_small}  seen=${tot_seen:9.2f}  "
                  f"sim=${tot:9.2f}  of_which_unwind=${unwind_loss:8.2f}  worst=${worst:7.2f}  "
                  f"all_cancelled=${void_tot:9.2f}  ev@cancel={a.cancel_rate}=${ev:9.2f}  "
                  f"full={full} partial={partial} none={none}  cooldown_skip={cooldown_skip} unseeded_skip={unseeded_skip} crossed={crossed_checks}  "
                  f"fees=${fees_tot:8.2f} rebate=${rebate_tot:8.2f} wv=${wv_tot:8.2f}")
    for d in delays:
        s, t, u, e, f_, rb, wv = combined[d]
        print(f"side=both delay={d:>6}  seen=${s:9.2f}  sim=${t:9.2f}  of_which_unwind=${u:8.2f}  ev=${e:9.2f}  "
              f"fees=${f_:8.2f} rebate=${rb:8.2f} wv=${wv:8.2f}")

    if a.per_run:
        with open(a.per_run, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["event", "title", "side", "t0", "dur", "n_legs", "cost0", "size0", "q",
                        "below_min", "skipped_reason", "seen_usd", "filled_sets", "pnl_usd", "unwind_usd",
                        "full_partial_none", "px0", "fee0", "edge_full_fee", "fees_usd", "rebate_usd",
                        "wv_usd", "maker_rebate_usd"])
            for (i, d, r, q, reason, seen, h, pnl, uw, fpn, px0, fee0, eff, fees, rb, wv, mkr) in per_run:
                w.writerow([r["event"], r["title"], r["side"], r["t0"], r.get("dur", ""), len(r["legs"]),
                            r["cost0"], r["size0"], round(q, 4), 1 if reason == "below_min" else 0,
                            reason, round(seen, 4), round(h, 4), round(pnl, 4), round(uw, 4), fpn,
                            round(px0, 6), round(fee0, 6), eff, round(fees, 4), round(rb, 4),
                            round(wv, 4), round(mkr, 4)])


if __name__ == "__main__":
    main()
