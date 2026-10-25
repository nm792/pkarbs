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
- Fees/volume out: per side and delay, print fees, rebate and wv.

Fill-check fixes (TASK-rescan-fillcheck):
- replay() uses books.Replay, the same book replay as rescan.py (gap reset, seeding, per-change dedup).
- The taker rebate is added to P&L. sim = hedged_sets + of_which_unwind + rebate, each dollar once:
  hedged_sets is the complete sets filled at t0 prices held to payout; of_which_unwind is everything
  done with the legs left over (dump or completion).
- --partial dump|complete|best: on a partial fill, sell the extras at the bid, or buy the missing legs at
  the ask (a full set is MECE, so completing it locks the payout), or per run whichever pays more.
- CSV gains delay, t0_iso, partial_exit, a per-run full_partial_none (0 none, 1 partial, 2 full), and every
  leg's best bid/ask at t0, match and unwind time plus its fill.

Usage: python3 shadow_sim.py --data data/ --runs rescan/runs.jsonl --one-way 0.05 --delays 0,1,3,market
"""
import argparse, glob, gzip, json, math, os, csv
from datetime import datetime, timezone
from books import Book, Replay
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
    """queries: list of (t, key, assets). Returns (snaps, seeded_at): snaps[key][asset] is (bids, asks)
    after every record received at or before t, and seeded_at[key][asset] says whether the leg had a
    full book since the last gap reset. Uses books.Replay, the same replay as rescan.py."""
    want = sorted(queries, key=lambda q: q[0])
    rp = Replay({}, gap_s=gap_s, create=True)
    snaps, seeded_at, qi = {}, {}, 0
    empty = Book()

    def take(t, key, assets):
        snaps[key] = {x: (dict(rp.books.get(x, empty).bids), dict(rp.books.get(x, empty).asks)) for x in assets}
        seeded_at[key] = {x: rp.is_seeded(x) for x in assets}

    for path in sorted(glob.glob(os.path.join(data, "raw-*.jsonl.gz"))):
        for line in read_lines(path):
            try:
                rec = json.loads(line)
            except ValueError:  # partial last line of a file still being written
                continue
            r = rec["r"]
            while qi < len(want) and want[qi][0] < r:
                take(*want[qi])
                qi += 1
            if qi >= len(want):
                break
            rp.feed(r, rec["m"])
        if qi >= len(want):
            break
    for q in want[qi:]:
        take(*q)
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
    ap.add_argument("--partial", choices=["dump", "complete", "best"], default="dump",
                    help="partial fill exit: sell extra legs at the bid, buy the missing legs at the ask, "
                         "or per run whichever pays more (both priced on the same unwind-time book)")
    a = ap.parse_args()

    runs = load(a.data, a.runs)
    delays = a.delays.split(",")
    queries = []
    for i, r in enumerate(runs):
        assets = [l["yes"] for l in r["legs"]]
        queries.append((r["t0"] + 1e-6, (i, "t0"), assets))
        for d in delays:
            last = 0.0
            for k, leg in enumerate(r["legs"]):
                tm = r["t0"] + a.one_way + (k // BATCH) * 2 * a.one_way + leg_delay(leg, d)
                queries.append((tm, (i, d, "match", k), [leg["yes"]]))
                last = max(last, tm)
            dmax = max(leg_delay(l, d) for l in r["legs"])
            queries.append((last + a.one_way + dmax, (i, d, "unwind"), assets))
    snaps, seeded_at = replay(a.data, queries, a.gap_s)
    max_legs = max((len(r["legs"]) for r in runs), default=0)

    per_run = []
    combined = defaultdict(lambda: defaultdict(float))
    for side in ("yes", "no"):
        sruns = [(i, r) for i, r in enumerate(runs) if r["side"] == side]
        for d in delays:
            T = defaultdict(float)  # totals for this side and delay
            worst = 0.0
            last_t1 = {}  # (event, side) -> t1 of last traded run
            for i, r in sruns:
                lg = r["legs"]
                n = len(lg)
                q = min(r["size0"], a.max_usd / r["cost0"])
                prices = [p0 if side == "yes" else 1 - p0 for p0, _ in r["quotes0"]]
                need = max((float(l.get("min_size") or 0) / (px if a.min_unit == "usdc" else 1))
                           for l, px in zip(lg, prices))
                px0 = r.get("px0", r["cost0"])
                fee0 = r.get("fee0", 0.0)
                row = {"i": i, "d": d, "r": r, "q": q, "reason": "none", "seen": 0.0, "h": 0.0, "pnl": 0.0,
                       "uw": 0.0, "fpn": 0, "exit": "", "fees": 0.0, "rebate": 0.0, "wv": 0.0, "fills": [0.0] * n}
                if q < need - 1e-9:
                    row["reason"] = "below_min"
                    T["below_min"] += 1
                elif r.get("payout", 1) - px0 - (1 - a.taker_rebate) * fee0 <= 0:
                    row["reason"] = "below_rebate_edge"  # at R=0 this is exactly edge_full_fee == 0
                elif (r["event"], side) in last_t1 and r["t0"] - last_t1[(r["event"], side)] < a.cooldown_s:
                    row["reason"] = "cooldown"
                    T["cooldown_skip"] += 1
                elif not all(seeded_at[(i, d, "match", k)][leg["yes"]] for k, leg in enumerate(lg)):
                    row["reason"] = "unseeded"
                    T["unseeded_skip"] += 1
                if row["reason"] != "none":
                    per_run.append(row)
                    continue
                row["seen"] = (r["payout"] - px0 - (1 - a.taker_rebate) * fee0) * q
                u = snaps[(i, d, "unwind")]
                useed = seeded_at[(i, d, "unwind")]
                fills, crossed = [], 0
                for k, (leg, (p0, _)) in enumerate(zip(lg, r["quotes0"])):
                    bids, asks = snaps[(i, d, "match", k)][leg["yes"]]
                    if bids and asks and max(bids) >= min(asks):  # crossed leg counts as unfilled
                        crossed += 1
                        fills.append([leg, 0.0, 0.0, 0.0])
                        continue
                    lim = on_tick(p0 if side == "yes" else 1 - p0, leg.get("tick"))
                    f, notional, fees = walk(asks if side == "yes" else mirror(bids), lim, q, True,
                                             leg["fee_rate"], leg.get("fee_exp", 1))
                    fills.append([leg, f, notional, fees])
                T["crossed"] += 1 if crossed else 0
                buy_cost = sum(nt + fe for _, _, nt, fe in fills)
                buy_fees = sum(fe for _, _, _, fe in fills)
                wv = sum(f * (nt / f) * (1 - nt / f) for _, f, nt, _ in fills if f > 0)
                h = min(f for _, f, _, _ in fills)
                if any(not useed[leg["yes"]] for leg, f, _, _ in fills if f - h > 1e-9):
                    T["unwind_unseeded"] += 1

                def dump(sets, held):
                    """Sell each leg's holding above `sets` at the unwind-time bid. Returns (proceeds, fees)."""
                    pr = fs = 0.0
                    for leg, f in held:
                        extra = f - sets
                        if extra > 1e-9:
                            ub, ua = u[leg["yes"]]
                            _, nt, fe = walk(ub if side == "yes" else mirror(ua), 0.0, extra, False,
                                             leg["fee_rate"], leg.get("fee_exp", 1))
                            pr += nt - fe
                            fs += fe
                    return pr, fs

                # exit A: dump the extras
                pr_a, fs_a = dump(h, [(leg, f) for leg, f, _, _ in fills])
                pnl_a = h * r["payout"] - buy_cost + pr_a
                fees_a = buy_fees + fs_a
                # exit B: buy the missing legs up to the largest fill at the unwind-time ask, dump what is left over
                top = max(f for _, f, _, _ in fills)
                held, extra_cost, fs_b, wv_b = [], 0.0, 0.0, 0.0
                for leg, f, _, _ in fills:
                    g = nt = fe = 0.0
                    if top - f > 1e-9:
                        ub, ua = u[leg["yes"]]
                        g, nt, fe = walk(ua if side == "yes" else mirror(ub), 1.0, top - f, True,
                                         leg["fee_rate"], leg.get("fee_exp", 1))
                        if g > 0:
                            wv_b += g * (nt / g) * (1 - nt / g)
                    held.append((leg, f + g))
                    extra_cost += nt + fe
                    fs_b += fe
                h_b = min(x for _, x in held)
                pr_b, fs_b2 = dump(h_b, held)
                pnl_b = h_b * r["payout"] - buy_cost - extra_cost + pr_b
                fees_b = buy_fees + fs_b + fs_b2
                use_b = a.partial == "complete" or (a.partial == "best" and pnl_b > pnl_a + 1e-12)
                if top - h <= 1e-9:
                    use_b = False  # nothing partial
                pnl, run_fees, sets = (pnl_b, fees_b, h_b) if use_b else (pnl_a, fees_a, h)
                if use_b:
                    wv += wv_b
                rebate = a.taker_rebate * run_fees
                pnl += rebate  # the taker rebate is part of P&L
                # unwind_usd: P&L of everything that is not a complete set bought at t0 prices
                hedged = h * r["payout"] - sum((nt + fe) * h / f for _, f, nt, fe in fills if f > 0)
                uw = pnl - rebate - hedged
                fpn = 2 if h >= q - 1e-9 else (1 if top > 1e-9 else 0)
                T["full" if fpn == 2 else "partial" if fpn == 1 else "none"] += 1
                T["seen"] += row["seen"]; T["sim"] += pnl; T["unwind"] += uw; T["hedged"] += hedged
                T["fees"] += run_fees; T["rebate"] += rebate; T["wv"] += wv
                T["exit_complete"] += 1 if use_b else 0
                T["dump_total"] += pnl_a + a.taker_rebate * fees_a
                T["complete_total"] += (pnl_b + a.taker_rebate * fees_b) if top - h > 1e-9 else (pnl_a + a.taker_rebate * fees_a)
                worst = min(worst, pnl)
                if voids_on_cancel(r["title"]):
                    T["void"] += pnl + sets * ((0 if side == "yes" else n) - r["payout"])
                else:
                    T["void"] += pnl
                last_t1[(r["event"], side)] = r.get("t1", r["t0"])
                row.update(h=sets, pnl=pnl, uw=uw, fpn=fpn, exit=("complete" if use_b else "dump") if fpn == 1 else "",
                           fees=run_fees, rebate=rebate, wv=wv, fills=[f for _, f, _, _ in fills])
                per_run.append(row)
            ev = (1 - a.cancel_rate) * T["sim"] + a.cancel_rate * T["void"]
            for k in ("seen", "sim", "hedged", "unwind", "fees", "rebate", "wv", "dump_total", "complete_total"):
                combined[d][k] += T[k]
            combined[d]["ev"] += ev
            print(f"side={side} delay={d:>6}  runs={len(sruns)}  below_min={int(T['below_min'])}  seen=${T['seen']:9.2f}  "
                  f"sim=${T['sim']:9.2f}  hedged_sets=${T['hedged']:8.2f}  of_which_unwind=${T['unwind']:8.2f}  "
                  f"rebate=${T['rebate']:8.2f}  worst=${worst:7.2f}  "
                  f"dump_total=${T['dump_total']:9.2f}  complete_total=${T['complete_total']:9.2f}  "
                  f"all_cancelled=${T['void']:9.2f}  ev@cancel={a.cancel_rate}=${ev:9.2f}  "
                  f"full={int(T['full'])} partial={int(T['partial'])} none={int(T['none'])} exit_complete={int(T['exit_complete'])}  "
                  f"cooldown_skip={int(T['cooldown_skip'])} unseeded_skip={int(T['unseeded_skip'])} "
                  f"unwind_unseeded={int(T['unwind_unseeded'])} crossed={int(T['crossed'])}  "
                  f"fees=${T['fees']:8.2f} wv=${T['wv']:8.2f}")
    for d in delays:
        c = combined[d]
        print(f"side=both delay={d:>6}  seen=${c['seen']:9.2f}  sim=${c['sim']:9.2f}  hedged_sets=${c['hedged']:8.2f}  "
              f"of_which_unwind=${c['unwind']:8.2f}  rebate=${c['rebate']:8.2f}  dump_total=${c['dump_total']:9.2f}  "
              f"complete_total=${c['complete_total']:9.2f}  ev=${c['ev']:9.2f}  fees=${c['fees']:8.2f} wv=${c['wv']:8.2f}")

    if a.per_run:
        def quotes(key, assets):
            out = []
            for x in assets:
                bids, asks = snaps[key][x] if key in snaps else ({}, {})
                out += [max(bids) if bids else "", min(asks) if asks else ""]
            return out

        legcols = []
        for k in range(max_legs):
            legcols += [f"leg{k}_{w}" for w in ("bid_t0", "ask_t0", "bid_match", "ask_match", "bid_unwind",
                                                  "ask_unwind", "filled")]
        with open(a.per_run, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["event", "title", "side", "delay", "t0", "t0_iso", "dur", "n_legs", "cost0", "size0", "q",
                        "below_min", "skipped_reason", "seen_usd", "filled_sets", "pnl_usd", "unwind_usd",
                        "full_partial_none", "partial_exit", "px0", "fee0", "edge_full_fee", "fees_usd",
                        "rebate_usd", "wv_usd", "maker_rebate_usd"] + legcols)
            for x in per_run:
                r, i, d = x["r"], x["i"], x["d"]
                assets = [l["yes"] for l in r["legs"]]
                t0q = quotes((i, "t0"), assets)
                legs = []
                for k, aid in enumerate(assets):
                    mq = quotes((i, d, "match", k), [aid])
                    uq = quotes((i, d, "unwind"), [aid])
                    legs += [t0q[2 * k], t0q[2 * k + 1]] + mq + uq + [round(x["fills"][k], 4)]
                legs += [""] * (len(legcols) - len(legs))
                w.writerow([r["event"], r["title"], r["side"], d, r["t0"],
                            datetime.fromtimestamp(r["t0"], timezone.utc).isoformat(timespec="milliseconds"),
                            r.get("dur", ""), len(r["legs"]), r["cost0"], r["size0"], round(x["q"], 4),
                            1 if x["reason"] == "below_min" else 0, x["reason"], round(x["seen"], 4),
                            round(x["h"], 4), round(x["pnl"], 4), round(x["uw"], 4), x["fpn"], x["exit"],
                            round(r.get("px0", r["cost0"]), 6), round(r.get("fee0", 0.0), 6),
                            r.get("edge_full_fee", 1), round(x["fees"], 4), round(x["rebate"], 4),
                            round(x["wv"], 4), 0.0] + legs)


if __name__ == "__main__":
    main()
