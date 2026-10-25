# Task for the server agent: fix detector/sim book mismatch, then report fill rate before any P&L

From: Claude in the "PK arbs" project (25 Oct 2026), after verifying
`reports/sports-mece/rescan-clean-2026-10-24.md` (commit b5527a0).
Status: OPEN

## Hard rules
- Shadow mode only. Do not place, sign or cancel any orders. Do not use wallet keys.
- Public Polymarket endpoints only.
- Do not stop or restart the v2 logger on `shadow/data-v2/`. Replay files already on disk.
- Keep raw files out of git.

## Why
The clean rescan's sim cannot fill quotes the detector has just seen. In
`rescan-clean-2026-10-24-usdc-cd10.csv`, at delay 0 (one-way 1.9 ms), 36 of the 51 traded runs complete
zero sets, and 23 of those runs were open longer than 0.1 s. A quote that stays on the book for 100 ms
should not vanish within 2 ms that often. Almost all of the −$901 at 1 s is unwind loss from those
runs (complete sets +$24.56, unwinds −$925.90), so the total is not a valid measurement.

Bugs found by reading the code:
1. **Raw dedup key is wrong, and only the detector dedups.** `rescan.py` keys on
   `(m["asset_id"], m["timestamp"], m["hash"])`. Current WS `price_change` messages carry `asset_id` and
   `hash` inside each entry of `price_changes`, so the key becomes `(None, timestamp, None)`, and
   different price changes that share a millisecond are dropped as duplicates. `shadow_sim.replay()` does
   no dedup, so the detector and the sim replay different books.
2. **No unseeded tracking in the detector.** `rescan.py` clears books at gaps but never marks legs
   unseeded, so a run can open on a leg rebuilt from deltas only. The sim checks seeding at match time
   only, not at unwind time.
3. **Rebate never reaches P&L.** In `shadow_sim.py`, `rebate = a.taker_rebate * run_fees` is computed and
   totalled but never added to `pnl`. Example: the rb18 CSV's P&L of −954.68 leaves out the $19.91 rebate.
4. **Per-run CSV gaps.** No `delay` column, no leg quotes (task change 5), `t0` is not ISO, and
   `full_partial_none` writes the running `full` counter instead of a per-run 0/1/2.

## What to change (shadow/)
1. **One replay for both.** Move the book replay into one shared function (raw record → book update,
   with dedup, gap reset and seeding) and use it in both `rescan.py` and `shadow_sim.replay()`, so the
   detector and the sim cannot drift apart.
2. **Correct dedup.** For `price_change`, dedup per change on `(asset_id, timestamp, hash)` taken from the
   change entry (falling back to the message fields only if the entry lacks them). For `book`, dedup on
   `(asset_id, timestamp, hash)` from the message. If there is no hash, compare the full entry instead.
   Print how many records and changes were dropped.
3. **Seeding in the detector and at unwind.** After a gap reset, a leg is unseeded until a full `book`
   message arrives. Do not open or extend runs while any leg is unseeded. In the sim, check seeding at
   match time and at unwind time; if an unwind leg is unseeded, count it in `unwind_unseeded=` and carry
   it at the next seeded bid (do not value it at $0).
4. **Rebate in P&L.** Add `rebate` to `pnl` for every traded run, so the printed `sim=` and the CSV's
   `pnl_usd` are after the rebate.
5. **Complete the set, as an option.** A full negRisk set is mutually exclusive and collectively
   exhaustive, so on a partial fill there are two ways out: sell the extra legs at the bid (current), or
   buy the missing legs at the ask at unwind time (FAK, up to the extra size) and hold the full sets.
   Add `--partial complete|dump|best` (default `best`: per run, take whichever has the higher P&L after
   fees). Print both totals for each side and delay.
6. **CSV.** Add `delay`, ISO `t0`, a per-run `full_partial_none` (0 none, 1 partial, 2 full),
   `partial_exit` (complete / dump), and for each leg the YES best bid and ask at t0, match time and
   unwind time (`leg{k}_bid_t0`, `leg{k}_ask_t0`, … as in TASK-rescan-clean change 5), plus `leg{k}_filled`.

## Self-check first: fill rate at delay 0 (report this before any P&L)
Run the sim at `--delays 0` on the same data with `--min-unit usdc --cooldown-s 10`. For every traded run,
compute each leg's fill fraction `filled / q`. Report:
- the number of traded runs, and how many have every leg filled >= 95% of q;
- the same, only for runs with `dur > 0.05` s;
- for the first 10 runs with `dur > 0.05` s where any leg fills < 95%: event, title, t0 (ISO), dur,
  and every leg's quote at t0 against its best ask (YES side) or best bid (NO side) at match time.

**Pass:** at least 95% of the runs with `dur > 0.05` s have every leg filled >= 95%. If it fails, stop:
commit the report with the self-check and the 10 examples only, no P&L, and set Status to BLOCKED.

## What to run (only if the self-check passes)
1. `python3 shadow/rescan.py --data <rescan-data dir> --out shadow/rescan-fix/ --fetch-totals --gap-s 5 --max-taker-rebate 0.5`
2. The sim at `--min-unit usdc` and `--min-unit shares`, each with `--cooldown-s 10`, `--delays 0,1,3,market`,
   `--partial best`, `--taker-rebate 0`, writing `reports/sports-mece/rescan-fix-2026-10-25-<unit>-cd10.csv`.
3. The same at `--min-unit usdc --cooldown-s 10 --delays market --taker-rebate 0.03`, writing `...-usdc-cd10-rb03.csv`.

## Report (commit to this repo)
`reports/sports-mece/rescan-fix-2026-10-25.md`, in this order:
1. Self-check result (the fill-rate numbers above). Nothing else goes before it.
2. Dedup counts, resets, unseeded skips at match and unwind, crossed checks.
3. Simulator output as printed (yes, no, both), for `dump`, `complete` and `best`.
4. For delay=market, USDC, cooldown 10, `best`, an additive breakdown, each dollar counted once:
   seen edge after full fee; edge lost to incomplete sets; = P&L on complete sets; P&L of partial exits
   (split into dump and complete); rebate; total. State fees paid as an "of which" line, not an addend.
   Leave void games out of the total (show them in a footnote only).
5. For each CSV: sum of `pnl_usd` per side and delay equals the printed `sim=` total to the cent, and the
   sum of `rebate_usd` equals R x the sum of `fees_usd`.
6. Label every number as computed by the sim. Do not add estimates.

Set Status above to DONE (or BLOCKED if the self-check fails) and commit.
