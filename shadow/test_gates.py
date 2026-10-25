#!/usr/bin/env python3
"""Hard gates for the sports MECE shadow rescan. Run these before printing or reporting any P&L.

Synthetic mode (default): builds a tiny data dir with hand-computed answers and checks
  G1  detector: known-answer runs, including two different price changes in the same exchange
      millisecond (new WS format: asset_id and hash live inside each price_changes entry);
  G2  detector and sim see the same book: every run's quotes at t0 equal the sim's book at t0,
      and at delay 0 every leg fills >= 95% of q;
  G3  crossed book opens no run; after a gap reset, a leg rebuilt from deltas only (no full book)
      opens no run;
  G4  sim P&L equals the hand-computed value including the taker rebate, the printed sim= total
      equals the sum of the per-run CSV, and rebate_usd sums to R x fees_usd.

Real-data mode (G5): one raw hour first.
  python3 shadow/test_gates.py --real-data <data dir> --hour 2026102320 [--totals totals.json] [--save DIR]
  Re-detects runs on that hour only, then runs G2, G3 and G4 (reconcile only) on them. One process at a
  time (rescan, then the book check, then the sim); the temp dir is deleted at the end.

Exit code 0 only if every gate passes. Usage: python3 shadow/test_gates.py [-v]
"""
import argparse, csv, glob, gzip, io, json, os, re, shutil, subprocess, sys, tempfile
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shadow_sim  # noqa: E402
from books import Replay, read_lines, CORRUPT  # noqa: E402

T = 1792800000.0
ONE_WAY = 0.0019
FEE = 0.05
results = []


def gate(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""), flush=True)


def leg(tok, delay=0):
    return {"cid": "c" + tok, "yes": tok, "no": "n" + tok, "name": tok, "fee_rate": FEE, "fee_exp": 1,
            "rebate_rate": 0.15, "seconds_delay": delay, "tick": 0.01, "min_size": 5}


def book(tok, r, asks, bids):
    return {"event_type": "book", "asset_id": tok, "timestamp": str(int(r * 1000)),
            "asks": [{"price": str(p), "size": str(s)} for p, s in asks.items()],
            "bids": [{"price": str(p), "size": str(s)} for p, s in bids.items()]}


def pc(ts_ms, changes):
    """New-format price_change: no message-level asset_id or hash."""
    return {"event_type": "price_change", "timestamp": str(ts_ms),
            "price_changes": [{"asset_id": a, "side": sd, "price": str(p), "size": str(s), "hash": h}
                              for a, sd, p, s, h in changes]}


def fee(p):
    return FEE * p * (1 - p)


def build_synthetic(d):
    """Five events, one per check. Records stay < 5 s apart except one deliberate 14 s gap."""
    evs = {"E1": ["a1", "a2", "a3"], "E2": ["b1", "b2", "b3"], "E3": ["c1", "c2", "c3"], "E4": ["d1", "d2", "d3"],
           "E5": ["e1", "e2", "e3"], "E6": ["f1", "f2", "f3"]}
    with open(os.path.join(d, "events.jsonl"), "w") as f:
        for eid, toks in evs.items():
            f.write(json.dumps({"t": T - 100, "id": eid, "title": f"{eid} FC vs. Test FC", "complete": True,
                                "n_markets": 3, "legs": [leg(x, 1 if eid == "E5" else 0) for x in toks]}) + "\n")
    recs = []
    # E1 known answer: all asks 0.30 x 100 at T+0, leg a1 reprices to 0.45 at T+2 -> one YES run, dur 2
    recs.append((T + 0.0, [book(x, T, {0.30: 100}, {0.20: 50}) for x in evs["E1"]]))
    recs.append((T + 2.0, pc(int((T + 2) * 1000), [("a1", "SELL", 0.30, 0, "h1"), ("a1", "SELL", 0.45, 100, "h2")])))
    # E2 same millisecond: asks 0.20/0.40/0.40 (no edge); b2 -> 0.30 opens a run; b1 -> 0.35 in a second
    # message with the SAME exchange timestamp must close it. Expected: one YES run, dur 0.5
    recs.append((T + 3.0, [book("b1", T + 3, {0.20: 100}, {0.10: 50}), book("b2", T + 3, {0.40: 100}, {0.10: 50}),
                           book("b3", T + 3, {0.40: 100}, {0.10: 50})]))
    same_ms = int((T + 3.5) * 1000)
    recs.append((T + 3.5, pc(same_ms, [("b2", "SELL", 0.40, 0, "h3"), ("b2", "SELL", 0.30, 100, "h4")])))
    recs.append((T + 4.0, pc(same_ms, [("b1", "SELL", 0.20, 0, "h5"), ("b1", "SELL", 0.35, 100, "h6")])))
    recs.append((T + 4.5, pc(int((T + 4.5) * 1000), [("b3", "BUY", 0.11, 50, "h7")])))  # touches E2 again
    # E3 crossed: c1 bid 0.35 >= ask 0.30, YES set would be 0.90 -> no run
    recs.append((T + 5.0, [book("c1", T + 5, {0.30: 100}, {0.35: 50}), book("c2", T + 5, {0.30: 100}, {0.10: 50}),
                           book("c3", T + 5, {0.30: 100}, {0.10: 50})]))
    # E4 stale after gap: books at 0.40 (no edge), 14 s gap resets everything, then deltas only add 0.20 asks
    recs.append((T + 6.0, [book(x, T + 6, {0.40: 100}, {0.10: 50}) for x in evs["E4"]]))
    recs.append((T + 20.0, pc(int((T + 20) * 1000), [(x, "SELL", 0.20, 100, "g" + x) for x in evs["E4"]])))
    # full books arrive at T+21 at 0.40 again -> still no edge, so no run on E4 at any time
    recs.append((T + 21.0, [book(x, T + 21, {0.40: 100}, {0.10: 50}) for x in evs["E4"]]))
    recs.append((T + 22.0, pc(int((T + 22) * 1000), [("d1", "BUY", 0.11, 50, "h8")])))
    # E5 partial fill, legs have a 1 s sports delay: asks 0.30 x 100, bids 0.20 x 200; e1's ask moves to 0.50
    # at T+23.5, before the delayed orders match at T+24.0019. e2 and e3 fill 100, e1 fills 0.
    recs.append((T + 23.0, [book(x, T + 23, {0.30: 100}, {0.20: 200}) for x in evs["E5"]]))
    recs.append((T + 23.5, pc(int((T + 23.5) * 1000), [("e1", "SELL", 0.30, 0, "h9"), ("e1", "SELL", 0.50, 100, "h10")])))
    # E6 two records with the same receive time: the first opens a run at 0.30 x 100 on every leg, the
    # second (same r) raises f2's ask size to 150. The t0 book must be the one right after the first.
    recs.append((T + 24.5, [book(x, T + 24.5, {0.30: 100}, {0.20: 50}) for x in evs["E6"]]))
    recs.append((T + 24.5, pc(int((T + 24.5) * 1000), [("f2", "SELL", 0.30, 150, "h12")])))
    recs.append((T + 26.0, pc(int((T + 26) * 1000), [("d1", "BUY", 0.12, 50, "h11")])))
    with gzip.open(os.path.join(d, "raw-2026102500.jsonl.gz"), "wt") as f:
        for r, m in recs:
            f.write(json.dumps({"r": round(r, 3), "m": m}) + "\n")
    expected = {  # event -> (t0, dur, cost0, size0)
        "E1": (T, 2.0, 0.90 + 3 * fee(0.30), 100.0),
        "E2": (T + 3.5, 0.5, 0.20 + 0.30 + 0.40 + fee(0.20) + fee(0.30) + fee(0.40), 100.0),
        "E5": (T + 23.0, 0.5, 0.90 + 3 * fee(0.30), 100.0),
        "E6": (T + 24.5, 1.5, 0.90 + 3 * fee(0.30), 100.0),
    }
    return expected


def run(cmd, verbose):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if verbose or p.returncode:
        print(p.stdout[-4000:], p.stderr[-4000:])
    return p


def detect(data, out, verbose, totals=None):
    os.makedirs(out, exist_ok=True)
    if totals:
        shutil.copy(totals, os.path.join(out, "totals.json"))
    p = run([sys.executable, os.path.join(HERE, "rescan.py"), "--data", data, "--out", out, "--gap-s", "5"], verbose)
    path = os.path.join(out, "runs.jsonl")
    runs = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    return p, path, runs


def same_book(data, runs_path, max_usd=500.0):
    """G2/G3: rebuild the sim's book at t0 and at t0 + one-way for every run's legs."""
    runs = shadow_sim.load(data, runs_path)
    q = []
    for i, r in enumerate(runs):
        for k, lg in enumerate(r["legs"]):
            q.append((r["t0"] + ONE_WAY, (i, "m", k), [lg["yes"]]))
            if "seq0" not in r:  # older runs: fall back to time (can catch later records in the same ms)
                q.append((r["t0"] + 1e-6, (i, "t0", k), [lg["yes"]]))
    snaps, seeded = shadow_sim.replay(data, q, 5.0)
    # t0 book = state right after the record that opened the run, via the same shared replay
    by_seq = defaultdict(list)
    for i, r in enumerate(runs):
        if "seq0" in r:
            by_seq[r["seq0"]].append(i)
    if by_seq:
        rp, seq, last = Replay({}, gap_s=5.0, create=True), 0, max(by_seq)
        for path in sorted(glob.glob(os.path.join(data, "raw-*.jsonl.gz"))):
            for line in read_lines(path):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                seq += 1
                rp.feed(rec["r"], rec["m"])
                for i in by_seq.get(seq, []):
                    for k, lg in enumerate(runs[i]["legs"]):
                        b = rp.books.get(lg["yes"])
                        snaps[(i, "t0", k)] = {lg["yes"]: (dict(b.bids) if b else {}, dict(b.asks) if b else {})}
                        seeded[(i, "t0", k)] = {lg["yes"]: rp.is_seeded(lg["yes"])}
                if seq >= last:
                    break
            if seq >= last:
                break
    rows = []
    for i, r in enumerate(runs):
        side = r["side"]
        qty = min(r["size0"], max_usd / r["cost0"])
        mismatch = crossed = unseeded = 0
        fills = []
        for k, (lg, (p0, s0)) in enumerate(zip(r["legs"], r["quotes0"])):
            bids, asks = snaps[(i, "t0", k)][lg["yes"]]
            best = (min(asks) if asks else None) if side == "yes" else (max(bids) if bids else None)
            size = (asks if side == "yes" else bids).get(best) if best is not None else None
            if best is None or abs(best - p0) > 1e-9 or size is None or abs(size - s0) > 1e-6:
                mismatch += 1
            if bids and asks and max(bids) >= min(asks):
                crossed += 1
            if not seeded[(i, "t0", k)][lg["yes"]]:
                unseeded += 1
            mb, ma = snaps[(i, "m", k)][lg["yes"]]
            lim = shadow_sim.on_tick(p0 if side == "yes" else 1 - p0, lg.get("tick"))
            f, _, _ = shadow_sim.walk(ma if side == "yes" else shadow_sim.mirror(mb), lim, qty, True)
            fills.append(f / qty if qty else 0.0)
        rows.append({"event": r["event"], "title": r["title"], "side": side, "t0": r["t0"], "dur": r.get("dur", 0),
                     "mismatch": mismatch, "crossed": crossed, "unseeded": unseeded, "min_fill": min(fills),
                     "quotes0": r["quotes0"]})
    return rows


def sim(data, runs_path, csv_path, rebate, verbose, delays="0", partial="dump"):
    p = run([sys.executable, os.path.join(HERE, "shadow_sim.py"), "--data", data, "--runs", runs_path,
             "--one-way", str(ONE_WAY), "--delays", delays, "--max-usd", "500", "--min-unit", "usdc",
             "--cooldown-s", "10", "--gap-s", "5", "--taker-rebate", str(rebate), "--per-run", csv_path,
             "--partial", partial], verbose)
    printed = {}
    for m in re.finditer(r"side=(yes|no) delay=\s*(\S+).*?sim=\$\s*(-?[\d.]+)", p.stdout):
        printed[(m.group(1), m.group(2))] = float(m.group(3))
    rows = list(csv.DictReader(open(csv_path))) if os.path.exists(csv_path) else []
    return p, printed, rows


def reconcile(printed, rows, rebate):
    """G4: printed sim= per side equals the CSV sum; rebate_usd sums to R x fees_usd."""
    by_side = {}
    for r in rows:
        by_side[r["side"]] = by_side.get(r["side"], 0.0) + float(r["pnl_usd"])
    has_delay = bool(rows) and "delay" in rows[0]
    ok_sum = True
    for (side, d), v in printed.items():
        if has_delay:
            s = sum(float(r["pnl_usd"]) for r in rows if r["side"] == side and r["delay"] == d)
        elif len({k[1] for k in printed}) == 1:
            s = by_side.get(side, 0.0)
        else:
            gate("G4 CSV has a delay column", False, "cannot reconcile multi-delay output without it")
            return
        ok_sum &= abs(s - v) < 0.006
    gate("G4 printed sim= equals CSV pnl_usd sum", ok_sum and printed, f"printed={printed}")
    fees = sum(float(r["fees_usd"]) for r in rows)
    rb = sum(float(r["rebate_usd"]) for r in rows)
    gate("G4 rebate_usd == R x fees_usd", abs(rb - rebate * fees) < 0.006, f"rebate={rb:.4f} R*fees={rebate * fees:.4f}")


def gz_member(text):
    bio = io.BytesIO()
    with gzip.GzipFile(filename="raw-2026102500.jsonl", mode="wb", fileobj=bio) as g:
        g.write(text.encode())
    return bio.getvalue()


def corrupt_restart(tmp, verbose):
    """G0: the logger was killed mid-write and restarted, so the hour file holds a truncated gzip
    member followed by a new one. The reader must skip the broken member and keep the new one."""
    d = os.path.join(tmp, "data-g0")
    os.makedirs(d)
    shutil.copy(os.path.join(tmp, "data", "events.jsonl"), os.path.join(d, "events.jsonl"))
    junk = "".join(json.dumps({"r": round(T + 1 + i / 1e4, 4), "m": {"event_type": "last_trade_price",
                                                                        "asset_id": "zz", "pad": os.urandom(24).hex()}}) + "\n"
                   for i in range(3000))
    first = gz_member(junk)
    # second member: E2's three records (books at T+3, run opens at T+3.5, closes at T+4.0)
    raw = [json.loads(l) for l in gzip.open(os.path.join(tmp, "data", "raw-2026102500.jsonl.gz"), "rt")]
    e2 = [rec for rec in raw if T + 2.9 < rec["r"] < T + 4.6]
    second = gz_member("".join(json.dumps(rec) + "\n" for rec in e2))
    with open(os.path.join(d, "raw-2026102500.jsonl.gz"), "wb") as f:
        f.write(first[: len(first) // 2] + second)
    p, _, runs = detect(d, os.path.join(tmp, "out-g0"), verbose)
    ok = p.returncode == 0 and any(r["event"] == "E2" and abs(r["dur"] - 0.5) < 1e-3 for r in runs)
    gate("G0 truncated gzip member then a new one: reader recovers the new member", ok,
         f"exit {p.returncode}, runs {[(r['event'], r['dur']) for r in runs]}, "
         f"{(p.stdout.strip().splitlines() or [''])[-2][-60:]}")


def synthetic(verbose):
    tmp = tempfile.mkdtemp(prefix="gates-")
    data = os.path.join(tmp, "data")
    os.makedirs(data)
    expected = build_synthetic(data)
    corrupt_restart(tmp, verbose)

    # G1 + G3 (detector)
    p, runs_path, runs = detect(data, os.path.join(tmp, "out"), verbose)
    yes = {r["event"]: r for r in runs if r["side"] == "yes"}
    no_runs = [r for r in runs if r["side"] == "no"]
    for eid, (t0, dur, cost, size) in expected.items():
        r = yes.get(eid)
        ok = (r is not None and abs(r["t0"] - t0) < 1e-3 and abs(r["dur"] - dur) < 1e-3
              and abs(r["cost0"] - cost) < 1e-9 and abs(r["size0"] - size) < 1e-9)
        got = None if r is None else (round(r["t0"] - T, 3), r["dur"], round(r["cost0"], 6), r["size0"])
        gate(f"G1 known-answer run {eid}", ok, f"expected t0=T+{t0 - T:.1f} dur={dur} cost0={cost:.6f} q={size}; got {got}")
    n_e1e2 = sum(1 for r in runs if r["event"] in ("E1", "E2", "E5", "E6"))
    gate("G1 no extra runs on E1/E2/E5/E6 (same-millisecond update not dropped)", n_e1e2 == 4, f"{n_e1e2} runs")
    gate("G1 no NO-side runs (NO sets cost > payout)", not no_runs, f"{len(no_runs)} NO runs")
    gate("G3 crossed book opens no run (E3)", not any(r["event"] == "E3" for r in runs))
    gate("G3 deltas after a gap reset open no run until a full book (E4)", not any(r["event"] == "E4" for r in runs))

    # G2 on whatever the detector produced
    rows = same_book(data, runs_path)
    gate("G2 detector quotes == sim book at t0, every leg", all(x["mismatch"] == 0 for x in rows),
         f"{sum(x['mismatch'] > 0 for x in rows)} of {len(rows)} runs differ")
    gate("G2 delay-0 fill >= 95% of q on every leg", all(x["min_fill"] >= 0.95 for x in rows),
         f"min fills {[round(x['min_fill'], 3) for x in rows]}")

    # G4 on a hand-made runs file (tests the sim alone, whatever the detector does)
    toks = {"E1": ["a1", "a2", "a3"], "E2": ["b1", "b2", "b3"], "E5": ["e1", "e2", "e3"]}
    px = {"E1": [0.30, 0.30, 0.30], "E2": [0.20, 0.30, 0.40], "E5": [0.30, 0.30, 0.30]}
    hand = os.path.join(tmp, "hand-runs.jsonl")
    with open(hand, "w") as f:
        for eid, (t0, dur, cost, size) in expected.items():
            if eid not in toks:
                continue
            f.write(json.dumps({"event": eid, "side": "yes", "title": f"{eid} FC vs. Test FC", "t0": t0, "t1": t0 + dur,
                                "dur": dur, "cost0": cost, "px0": sum(px[eid]), "fee0": sum(fee(x) for x in px[eid]),
                                "edge_full_fee": 1, "payout": 1, "size0": size,
                                "quotes0": [[x, 100.0] for x in px[eid]], "assets": toks[eid]}) + "\n")
    R = 0.10
    # hand values, 100 sets each. Full fill: 100 x (1 - cost0) + R x fees.
    full = {e: 100 * (1 - expected[e][2]) + R * 100 * sum(fee(x) for x in px[e]) for e in toks}
    # E5 at its 1 s delay: e2, e3 filled 100 at 0.30 (cost 2 x 31.05 = 62.10, fees 2.10); e1 unfilled.
    #   dump: sell e2, e3 at bid 0.20: 2 x 100 x (0.20 - 0.008) = 38.40, sell fees 1.60
    #         -> 38.40 - 62.10 = -23.70, rebate 0.1 x 3.70 = 0.37, total -23.33
    #   complete: buy e1 100 at ask 0.50: 50 + 1.25 fee = 51.25; 100 sets pay 100
    #         -> 100 - 62.10 - 51.25 = -13.35, rebate 0.1 x 3.35 = 0.335, total -13.015
    want = {
        ("dump", "0"): full["E1"] + full["E2"] + full["E5"],
        ("dump", "market"): full["E1"] + full["E2"] - 23.33,
        ("best", "market"): full["E1"] + full["E2"] - 13.015,
        ("complete", "market"): full["E1"] + full["E2"] - 13.015,
    }
    for mode in ("dump", "best", "complete"):
        p, printed, csv_rows = sim(data, hand, os.path.join(tmp, f"hand-{mode}.csv"), R, verbose,
                                   delays="0,market", partial=mode)
        for (m, d), v in want.items():
            if m != mode:
                continue
            got = printed.get(("yes", d))
            gate(f"G4 sim P&L == hand value incl. rebate (partial={mode}, delay={d})",
                 got is not None and abs(got - v) < 0.006, f"want {v:.4f}, got {got}")
        reconcile(printed, csv_rows, R)
        hedged = re.search(r"side=yes delay=market.*?sim=\$\s*(-?[\d.]+)\s+hedged_sets=\$\s*(-?[\d.]+)\s+"
                           r"of_which_unwind=\$\s*(-?[\d.]+)\s+rebate=\$\s*(-?[\d.]+)", p.stdout)
        ok = hedged and abs(float(hedged.group(1)) - sum(float(hedged.group(k)) for k in (2, 3, 4))) < 0.016  # four 2-dp printed values
        gate(f"G4 sim == hedged_sets + unwind + rebate (partial={mode})", ok, hedged.groups() if hedged else "no match")
    if not verbose:
        shutil.rmtree(tmp, ignore_errors=True)


def real(data_dir, hour, totals, verbose, save=None):
    tmp = tempfile.mkdtemp(prefix=f"gates-{hour}-")
    data = os.path.join(tmp, "data")
    os.makedirs(data)
    src = os.path.join(data_dir, f"raw-{hour}.jsonl.gz")
    if not os.path.exists(src):
        sys.exit(f"missing {src}")
    os.symlink(os.path.abspath(src), os.path.join(data, os.path.basename(src)))
    # only the event snapshots this hour needs: the last refresh before it (every event is written at each
    # refresh, all with the same t) plus every refresh inside it. Streamed twice, never loaded whole.
    h0 = datetime.strptime(hour, "%Y%m%d%H").replace(tzinfo=timezone.utc).timestamp()
    ev_path = os.path.join(data_dir, "events.jsonl")
    t_before = max((t for t in (json.loads(l).get("t", 0) for l in open(ev_path)) if t < h0), default=None)
    kept = 0
    with open(ev_path) as src, open(os.path.join(data, "events.jsonl"), "w") as dst:
        for line in src:
            t = json.loads(line).get("t", 0)
            if t == t_before or h0 <= t <= h0 + 3600:
                dst.write(line)
                kept += 1
    print(f"events.jsonl: kept {kept} snapshot lines for hour {hour}")
    p, runs_path, runs = detect(data, os.path.join(tmp, "out"), verbose, totals)
    print(f"hour {hour}: {len(runs)} runs detected; rescan said: {p.stdout.strip().splitlines()[-3:]}")
    rows = same_book(data, runs_path)
    long_ = [x for x in rows if x["dur"] > 0.05]
    bad = [x for x in long_ if x["min_fill"] < 0.95]
    gate("G2 detector quotes == sim book at t0", all(x["mismatch"] == 0 for x in rows),
         f"{sum(x['mismatch'] > 0 for x in rows)} of {len(rows)} runs differ")
    gate("G2 delay-0 fill >= 95% on every leg, >= 95% of runs with dur > 0.05 s",
         long_ and (len(long_) - len(bad)) / len(long_) >= 0.95,
         f"{len(long_) - len(bad)} of {len(long_)} pass; all runs: {sum(x['min_fill'] >= 0.95 for x in rows)} of {len(rows)}")
    gate("G3 no run opened on a crossed leg", all(x["crossed"] == 0 for x in rows), f"{sum(x['crossed'] > 0 for x in rows)} runs")
    gate("G3 no run opened on an unseeded leg", all(x["unseeded"] == 0 for x in rows), f"{sum(x['unseeded'] > 0 for x in rows)} runs")
    for x in bad[:10]:
        print("  low fill:", x["event"], x["title"][:50], x["side"], round(x["t0"], 3), "dur", x["dur"],
              "min_fill", round(x["min_fill"], 3), "quotes0", x["quotes0"])
    p, printed, csv_rows = sim(data, runs_path, os.path.join(tmp, "hour.csv"), 0.03, verbose, delays="0,market")
    reconcile(printed, csv_rows, 0.03)
    if save:
        os.makedirs(save, exist_ok=True)
        shutil.copy(runs_path, os.path.join(save, f"runs-{hour}.jsonl"))
        shutil.copy(os.path.join(tmp, "hour.csv"), os.path.join(save, f"per-run-{hour}.csv"))
        with open(os.path.join(save, f"fills-{hour}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["event", "title", "side", "t0", "dur", "mismatch", "crossed", "unseeded", "min_fill", "quotes0"])
            for x in rows:
                w.writerow([x["event"], x["title"], x["side"], x["t0"], x["dur"], x["mismatch"], x["crossed"],
                            x["unseeded"], round(x["min_fill"], 4), json.dumps(x["quotes0"])])
        print("saved to", save)
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-data", help="raw data dir (raw-*.jsonl.gz + events.jsonl)")
    ap.add_argument("--hour", help="raw hour to test, e.g. 2026102320")
    ap.add_argument("--totals", help="totals.json from an earlier rescan (event -> market count)")
    ap.add_argument("--save", help="real mode: copy runs, per-run CSV and per-run fill check here")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if a.real_data:
        real(a.real_data, a.hour, a.totals, a.verbose, a.save)
    else:
        synthetic(a.verbose)
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)} of {len(results)} gates pass" + (f"; FAILED: {failed}" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
