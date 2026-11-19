"""Render screen output (families.json, cells.json) into a markdown report with citations."""
import json, sys, subprocess


def rank(vals, rev=True):
    order = sorted(range(len(vals)), key=lambda i: -vals[i] if rev else vals[i]); r = [0] * len(vals)
    for k, i in enumerate(order, 1): r[i] = k
    return r


def main(outdir, meta):
    fam = json.load(open(f"{outdir}/families.json")); cells = json.load(open(f"{outdir}/cells.json"))
    scr = fam["all_screen"]; fs = [f for f in fam["families"] if f.get("n_late", 0) >= 15 and f["mean_gap_10m"] is not None]
    r1, r2, r3 = rank([f["events_per_day"] for f in fs]), rank([f["median_vol"] for f in fs]), rank([f["mean_gap_10m"] for f in fs])
    for f, a, b, c in zip(fs, r1, r2, r3): f["r_freq"], f["r_vol"], f["r_late"], f["rank_sum"] = a, b, c, a + b + c
    fs.sort(key=lambda f: f["rank_sum"])
    L = [f"# Stage-1 screen: {meta['run']}", "", f"Run `{meta['run']}`, commit `{meta['commit']}`, events file `{meta['events']}` "
         f"({len(scr)} families with >=5 closed events, window {meta['window']} days), out `{outdir}`.", "",
         f"Passed freq (>=1/day, active >=50% of days) and vol (median >= $20k): {sum(1 for f in scr if f['pass_freq'] and f['pass_vol'])} families; "
         f"top {len(fam['families'])} by events/day x median volume were sampled.", "",
         "## Families ranked on all three criteria (rank sum, lower is better; late-move = mean of 0.95 minus winner's own-token price 10 min before T*)", "",
         "| family | ev/day | median vol $ | late gap | winner<0.5 at 1h | rank f/v/l | sampled mkts | late n |", "|---|---|---|---|---|---|---|---|"]
    for f in fs:
        L.append(f"| {f['family']} | {f['events_per_day']:.1f} | {f['median_vol']:,.0f} | {f['mean_gap_10m']:.2f} | "
                 f"{(f['share_winner_below_50_at_1h'] if f['share_winner_below_50_at_1h'] is not None else float('nan')):.2f} | "
                 f"{f['r_freq']}/{f['r_vol']}/{f['r_late']} | {f['n_markets_sampled']} | {f['n_late']} |")
    L += ["", "Caution: T* uses hindsight, and a live market that resolves in play is expected to be uncertain until late. "
          "A large late gap alone is not evidence of mispricing; the ex-ante IC table below is the test.", ""]
    n = len(cells); disc = [c for c in cells if c["bh_discovery_q10"]]
    L += [f"## Signal IC (ex-ante, decision = end time minus H, fill = first BUY print after)", "",
          f"Cells tried: {n}. Benjamini-Hochberg q=0.10 discoveries on out-of-sample p: {len(disc)}.", "",
          "Top 15 cells by out-of-sample IC with >=6 test buckets (sign chosen on train only):", "",
          "| family | H | signal | n events | IC all | IC train | IC test | t test | p test | BH |", "|---|---|---|---|---|---|---|---|---|---|"]
    ok = [c for c in cells if c["n_test_days"] >= 6 and c["ic_test"] == c["ic_test"]]
    for c in sorted(ok, key=lambda c: -c["ic_test"])[:15]:
        L.append(f"| {c['family']} | {c['h']} | {c['signal']} | {c['n_events']} | {c['ic_all']:+.3f} | {c['ic_train']:+.3f} | "
                 f"{c['ic_test']:+.3f} | {c['t_test']:+.2f} | {c['p_test']:.3f} | {'yes' if c['bh_discovery_q10'] else 'no'} |")
    open(f"{outdir}/REPORT.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], json.loads(sys.argv[2]))
