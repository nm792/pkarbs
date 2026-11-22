#!/usr/bin/env python3
"""PAPER run of the `post` rule (and shadow rules) against the LIVE recorded books, under the Reviewer's conditions (reviewer/REVIEW-RESPONSE-2026-11-20-gas-daily-and-mechanics.md e5648c5e):
 1. a decision may only be taken AFTER the first logged AAA page row that shows the event date D (not at a fixed 03:30);
 2. fills come ONLY from the own-token asks in the book snapshot logged at the decision moment, at the displayed size (A1, A8): never from prints or later books;
 3. settlement from the Polymarket resolution (gamma outcomePrices), cross-checked against the page value;
 4. $/day with an event-clustered CI against $200/day (A9), rebates separate; fee rate is a parameter (0.05 from 20 Nov 23:59Z, SETTLED);
 5. sanity check within 15 minutes of the first live day (sanity()).
No orders are ever sent (A6/A7). Inputs: books JSONL from pm_gas_books.py, page JSONL from aaa_watch.py. yes_fav / no_out are SHADOW only (logged, never counted)."""
import argparse, datetime as dt, json, math, os, random, sys
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import rule as R, nowcast as N
ET = ZoneInfo("America/New_York")
def page_date_str(D): return f"{D.month}/{D.day}/{D.strftime('%y')}"            # AAA shows e.g. 11/21/26
def read_jsonl(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            try: out.append(json.loads(line))
            except ValueError: pass          # a half-written last line must not stop the run
    return out
def page_change(page_rows, D):
    """First page row that is a good fetch (status 200) AND shows date D. Returns (recv_ns, price) or None. Failed fetches (403 etc.) never count."""
    for r in page_rows:
        if r.get("status") == 200 and r.get("price_as_of") == page_date_str(D) and r.get("regular_current") is not None:
            return r["recv_ns"], r["regular_current"]
    return None
def token_buckets(snapshot):
    """token_id -> (bucket_index_by_lower_edge, outcome, bounds) from the labels of one snapshot."""
    toks = {}
    for tid, v in snapshot["tok"].items():
        q, out = v["label"].rsplit("|", 1); toks[tid] = (N.bucket_bounds(q), out)
    edges = sorted({b for b, _ in toks.values()}); return {tid: (edges.index(b), out, b) for tid, (b, out) in toks.items()}
def run(books, page, D, prm, nowcast=None, clock_end=None, latency_s=2.0, max_stale_s=2.0, hold_s=0.25, max_wait_s=5.0):
    """Returns decisions (list of dicts). Counted decisions have shadow=False and kind 'post'. clock_end: ns cut-off (10:00 ET on D).
    Decision moment = the logged page read (recv_ns). Fill book = the LATEST own-token book snapshot received at or before decision time + latency_s (R-006 a); latency_s is an ASSUMED page-read-to-order delay of at most 2 s, NOT measured (paper: no order path exists).
    The snapshot must also be received at or after the page RESPONSE (max_stale_s = latency_s = 2 s, so the window is [response, response + 2 s]; R-020: a book older than the response was seen before the page value was known), else there is no decision (a stale book is not a decision-time book). One decision, one snapshot: a better ask in any LATER snapshot, or in an earlier snapshot that a newer one superseded, is never filled (A8).
    SETTLED A3 taker hold (R-007): a post decision counts as filled only if the SAME level (token, price) is still shown with at least the decided size in the first snapshot at or after page read + latency_s + hold_s (hold_s = 0.25 s, not later than max_wait_s); otherwise it is logged as shadow kind 'post_unfilled_hold', status 'unfilled (hold)', and not counted. hold_s=None switches the check off (tests only)."""
    chg = page_change(page, D); decisions = []; spent_tok = {}; spent_rule = {}; level_taken = {}; level_max = {}
    dec_snap = None
    if chg:
        cand = [b for b in books if chg[0] + (latency_s - max_stale_s) * 1e9 <= b["recv_ns"] <= chg[0] + latency_s * 1e9 and not (clock_end and b["recv_ns"] > clock_end)]
        dec_snap = cand[-1] if cand else None
    for snap in books:
        ns = snap["recv_ns"]
        if clock_end and ns > clock_end: break
        tb = token_buckets(snap)
        if chg and snap is dec_snap:
            val = chg[1]; bounds = {}
            for tid, (i, out, b) in tb.items(): bounds[i] = b
            win = next((i for i, (lo, hi) in bounds.items() if lo <= val < hi), None)
            if win is None: continue                                          # page value outside every bucket: no decision
            for tid, (i, out, b) in tb.items():
                if (i == win) != (out == "Yes"): continue                      # YES of the page bucket, NO of every other bucket
                v = snap["tok"][tid]
                for p, sz in sorted(map(tuple, v["asks"])):
                    key = (tid, p); level_max[key] = max(level_max.get(key, 0.0), sz)
                    avail = level_max[key] - level_taken.get(key, 0.0)          # never count the same displayed size twice across snapshots
                    if avail <= 0: continue
                    sh = R.take("post", prm.post_q, p, avail, spent_tok.get(tid, 0.0), spent_rule.get("post", 0.0), prm)
                    if sh <= 0: continue
                    cost = sh * p; level_taken[key] = level_taken.get(key, 0.0) + sh; spent_tok[tid] = spent_tok.get(tid, 0.0) + cost; spent_rule["post"] = spent_rule.get("post", 0.0) + cost
                    decisions.append(dict(shadow=False, kind="post", recv_ns=ns, page_change_ns=chg[0], token=tid, label=v["label"], price=p, size_shown=sz, shares=sh, cost=cost, fee=R.fee_per_share(p, prm.fee_rate) * sh, page_value=val))
        elif nowcast and (not chg or ns < chg[0]) and ns < dt.datetime(D.year, D.month, D.day, 3, 0, tzinfo=ET).timestamp() * 1e9:
            mean, sd = nowcast; bounds = {i: b for i, o, b in tb.values()}
            q = {i: N.norm_cdf((hi - mean) / sd) - N.norm_cdf((lo - mean) / sd) for i, (lo, hi) in bounds.items()}; s = sum(q.values()); q = {i: x / s for i, x in q.items()}
            fav = max(q, key=q.get)
            for tid, (i, out, b) in tb.items():
                kind = qq = None
                if out == "Yes" and i == fav: kind, qq = "yes_fav", q[i]
                elif out == "No" and q[i] <= prm.out_q: kind, qq = "no_out", 1 - q[i]
                if not kind: continue
                v = snap["tok"][tid]
                for p, sz in sorted(map(tuple, v["asks"])):
                    key = (tid, p, "s"); level_max[key] = max(level_max.get(key, 0.0), sz); avail = level_max[key] - level_taken.get(key, 0.0)
                    if avail <= 0: continue
                    sh = R.take(kind, qq, p, avail, spent_tok.get((tid, "s"), 0.0), spent_rule.get(kind, 0.0), prm)
                    if sh <= 0: continue
                    level_taken[key] = level_taken.get(key, 0.0) + sh; spent_tok[(tid, "s")] = spent_tok.get((tid, "s"), 0.0) + sh * p; spent_rule[kind] = spent_rule.get(kind, 0.0) + sh * p
                    decisions.append(dict(shadow=True, kind=kind, recv_ns=ns, token=tid, label=v["label"], price=p, size_shown=sz, shares=sh, cost=sh * p, fee=R.fee_per_share(p, prm.fee_rate) * sh, q=qq))
    if chg and hold_s is not None:
        t_chk = chg[0] + (latency_s + hold_s) * 1e9
        chk = next((b for b in books if b["recv_ns"] >= t_chk), None)
        if chk is not None and chk["recv_ns"] - t_chk > max_wait_s * 1e9: chk = None
        out = []
        for d in decisions:
            if d["shadow"]: out.append(d); continue
            lvl = None
            if chk is not None and d["token"] in chk["tok"]:
                lvl = next((s for p, s in chk["tok"][d["token"]]["asks"] if abs(p - d["price"]) < 1e-9), None)
            if lvl is not None and lvl >= d["shares"] - 1e-9: out.append(dict(d, status="filled", hold_check_ns=chk["recv_ns"]))
            else: out.append(dict(d, shadow=True, kind="post_unfilled_hold", status="unfilled (hold)", hold_check_ns=chk["recv_ns"] if chk else None))
        decisions = out
    return decisions
def settle(decisions, gamma_markets, prm=None):
    """gamma_markets: list of gamma market dicts (clobTokenIds, outcomes, outcomePrices). A token wins when its outcomePrice is >= 0.99 (resolved). Returns (rows with pnl, unresolved count)."""
    win = {}
    for m in gamma_markets:
        toks = json.loads(m["clobTokenIds"]); pr = json.loads(m["outcomePrices"])
        for t, p in zip(toks, pr): win[t] = float(p)
    out = []; unresolved = 0
    for d in decisions:
        w = win.get(d["token"])
        if w is None or 0.01 < w < 0.99: unresolved += 1; out.append(dict(d, pnl=None)); continue
        won = w >= 0.99; out.append(dict(d, won=won, pnl=(d["shares"] * (1 - d["price"]) if won else -d["cost"]) - d["fee"]))
    return out, unresolved
def day_pnl(rows, shadow=False):
    return sum(r["pnl"] for r in rows if r["pnl"] is not None and r["shadow"] == shadow)
def report(day_pnls, target=200.0, n_boot=4000, seed=1):
    """day_pnls: one P&L per event day (the cluster). Bootstrap over days; returns mean, 95% CI, and whether the lower bound clears the target (A9)."""
    n = len(day_pnls); rnd = random.Random(seed); means = sorted(sum(rnd.choice(day_pnls) for _ in range(n)) / n for _ in range(n_boot))
    lo, hi = means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]
    return dict(days=n, mean=sum(day_pnls) / n, ci95=(lo, hi), clears_target=lo >= target, target=target)
def sanity(page_path, books_path, decisions_path, now_ns, max_age_s=120):
    """15-minute sanity check: page log has rows and the newest is recent; book log newest recent; decisions file exists (may be empty before the page changes)."""
    res = {}
    for name, path in (("page", page_path), ("books", books_path)):
        rows = read_jsonl(path) if os.path.exists(path) else []
        res[name + "_rows"] = len(rows); res[name + "_fresh"] = bool(rows) and (now_ns - rows[-1]["recv_ns"]) / 1e9 <= max_age_s
        res[name + "_good_fetches"] = sum(1 for r in rows if r.get("status", 200) == 200)
    res["decisions_file"] = os.path.exists(decisions_path); res["ok"] = res["page_fresh"] and res["books_fresh"] and res["page_good_fetches"] > 0 and res["decisions_file"]
    return res
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--books", required=True); ap.add_argument("--page", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--fee-rate", type=float, default=0.05); ap.add_argument("--latency-s", type=float, default=2.0); ap.add_argument("--nowcast", help="mean,sd of the AAA print for D (enables SHADOW rules)")
    a = ap.parse_args(argv); D = dt.date.fromisoformat(a.date); prm = R.Params(fee_rate=a.fee_rate, rule_caps=(("yes_fav", 0.10), ("no_out", 0.05), ("post", 0.10)))
    nc = tuple(float(x) for x in a.nowcast.split(",")) if a.nowcast else None
    end = dt.datetime(D.year, D.month, D.day, 10, 0, tzinfo=ET).timestamp() * 1e9
    dec = run(read_jsonl(a.books), read_jsonl(a.page), D, prm, nc, end, a.latency_s)
    with open(a.out, "w") as f:
        for d in dec: f.write(json.dumps(d) + "\n")
    print(f"decisions {len(dec)} counted {sum(1 for d in dec if not d['shadow'])} shadow {sum(1 for d in dec if d['shadow'])} page_change {page_change(read_jsonl(a.page), D)}")
if __name__ == "__main__": main()
