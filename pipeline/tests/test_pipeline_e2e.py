"""End-to-end: synthetic family with a planted momentum edge vs a null family. The pipeline must
find the planted one (OOS, after BH over all cells) and must NOT find the null."""
import json, os, random, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import screen


def make(planted, seed, n=150):
    rnd = random.Random(seed); evs, trades = [], {}
    H = 3600
    for i in range(n):
        end = 1_760_000_000 + i * 20000 + rnd.randint(0, 5000)
        q = rnd.uniform(0.25, 0.75); win = 1 if rnd.random() < q else 0
        cond = f"c{seed}_{i}"; toks = [f"t{seed}_{i}_0", f"t{seed}_{i}_1"]
        rows = []
        t = end - H  # decision time for horizon 1h
        # token0 own prints: baseline q, then (planted) leaked move in the last hour before decision
        lead = (0.25 if planted else 0.0) * ((1 if win else 0) - q)
        for k in range(12):
            tt = t - 4 * H + k * 900
            rows.append((tt, "BUY" if k % 2 else "SELL", toks[0], round(min(.97, max(.03, q + rnd.gauss(0, .02))), 3), 10, 0))
        for k in range(6):
            tt = t - H + 60 + k * 500
            rows.append((tt, "BUY", toks[0], round(min(.97, max(.03, q + lead * (k + 1) / 6 + rnd.gauss(0, .01))), 3), 10, 0))
        # after decision: prints at the last price level (so fills are at the signal-time price)
        last = rows[-1][3]
        rows.append((t + 30, "BUY", toks[0], last, 10, 0))
        # token1 own prints, independent noise around its own level
        for k in range(10):
            rows.append((t - 3 * H + k * 1000, "BUY" if k % 2 else "SELL", toks[1], round(min(.97, max(.03, 1 - q + rnd.gauss(0, .03))), 3), 10, 1))
        rows.append((t + 40, "BUY", toks[1], round(min(.97, max(.03, 1 - last)), 3), 10, 1))
        trades[cond] = rows
        evs.append(dict(id=f"e{seed}_{i}", title="x", endDate=None, volume=1e5, series=[{"slug": f"fam{seed}", "recurrence": "daily"}],
                        markets=[dict(conditionId=cond, outcomes='["A","B"]', outcomePrices=json.dumps(["1", "0"] if win == 1 else ["0", "1"]),
                                      clobTokenIds=json.dumps(toks), volumeNum=1e5, endDate=None, closedTime=None)]))
        import datetime as dt
        iso = dt.datetime.fromtimestamp(end, dt.timezone.utc).isoformat()
        evs[-1]["endDate"] = iso; evs[-1]["markets"][0]["endDate"] = iso
    return evs, trades


def run(planted):
    evs, trades = make(planted, seed=7 if planted else 8)
    d = tempfile.mkdtemp(); ev_path = os.path.join(d, "ev.jsonl")
    with open(ev_path, "w") as f:
        for e in evs: f.write(json.dumps(e) + "\n")
    screen.get_trades = lambda cond: {"rows": trades[cond], "trunc": False}

    class A: pass
    a = A(); a.events = ev_path; a.window_days = 40; a.out = os.path.join(d, "out"); a.max_families = 5
    a.n_events = 150; a.min_median_vol = 1000; a.seed = 1
    scr, fam, cells = screen.run(a)
    return cells


def test_planted_found_and_null_not():
    c1 = run(True)
    hit = [c for c in c1 if c["h"] == "1h" and c["signal"] == "mom1"][0]
    assert hit["ic_test"] > 0.1 and hit["bh_discovery_q10"], hit
    c0 = run(False)
    assert not any(c["bh_discovery_q10"] for c in c0), [c for c in c0 if c["bh_discovery_q10"]]
