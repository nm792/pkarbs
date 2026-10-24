# Task for the server agent: clean rescan (book resets at gaps, crossed books, dedup, per-run results, rebates)

From: Claude in the "PK arbs" project (24 Oct 2026), after an independent audit of
`reports/sports-mece/rescan-2026-10-24.md`. Updated the same day to add Polymarket taker rebates
(changes 6 to 10 below).
Status: OPEN

## Hard rules
- Shadow mode only. Do not place, sign or cancel any orders. Do not use wallet keys for this task.
- Public Polymarket endpoints only: gamma-api.polymarket.com, clob.polymarket.com/books,
  wss://ws-subscriptions-clob.polymarket.com/ws/market.
- Do not stop or restart the v2 logger on `shadow/data-v2/`. This task only replays files already on disk.
- Keep raw files out of git.

## Why
The audit found the rescan's +$122 (1 s delay, USDC min-size) is driven by fake runs:
- **Stale books at gaps.** The corrupt 01Z, 04Z and 06Z files were left out, but `rescan.py` and
  `shadow_sim.replay()` carry the books straight across the hole. At 02:00 and 05:00 the books still held
  the 00:59 and 03:59 state, and deltas only overwrite the levels they touch. 13 runs in the first 60 s of
  02Z and 05Z make up $615 of the $1,054 deduplicated "seen", including the top Atlante v San Luis and
  Tigre v Tucumán runs. Public price history confirms the quotes were hour-old (Atlante NO run at
  05:00:00 used YES bids 0.36 and 0.35; the real prices were about 0.0005 and 0.02). The sim fills from
  the same stale book, so these count as profit at 1 s delay too.
- **Crossed books.** Tigre at 02:00:01 showed a YES set at 0.62 and a NO set worth 1.54 at once, which
  is impossible unless a leg's bid is at or above its ask.
- **Duplicates.** 60 runs in `shadow/rescan/runs.jsonl` are exact copies (same event, side and t0).
- **Same liquidity counted again.** 445 runs restart within 10 s of the previous run on the same event
  and side. Many reuse the identical leg quote, and the sim treats each as a new full-size trade.
- **No per-run output.** The sim prints only totals, so nobody can check which runs drive the result.
- **Rebates left out.** The sim charges the full sports taker fee (0.05 x p x (1 - p)) on every buy and unwind,
  with no taker rebate. Polymarket pays takers a tiered rebate on fees, set by 30-day Weighted Volume
  (Bronze 3%, Silver 8%, Gold 18%, Platinum 32%, Diamond 44%, Obsidian 50%; no backfill). For sports,
  Weighted Volume = shares x p x (1 - p) per buy, which is 20 x the fee. The logger also opens a run only
  when the set is positive after the full fee, so sets that a rebate would make positive are never logged.
  On the clean runs, fees ($504) are larger than the edge ($441), so this matters. Makers pay no fee and get
  15% of the market's taker fees back (`feeSchedule.rebateRate`), but every order in this strategy is a taker,
  so maker rebate stays 0 here.

Full audit: the project file `sports-mece/audit-rescan-2026-10-24.md`. Rebate notes, with quotes from the
Polymarket docs: `sports-mece/rebates-2026-10-24.md`.

## What to change (shadow/)
Make these changes in `shadow/rescan.py` and `shadow/shadow_sim.py`, plus `Logger.check` in `shadow/shadow_logger.py` for change 6 (share helpers where sensible).
Commit the code with the report.

1. **Book reset at gaps.** While replaying raw records in time order, if the receive time `r` jumps by
   more than `--gap-s` seconds (default 5) from the previous record, or a new file starts after a
   missing, excluded or truncated file, clear every book. After a reset, mark every leg "unseeded".
   A leg becomes seeded again only when a full `book` message for it arrives (WS or REST resync).
   Do not open runs on an event, and do not fill or unwind sim orders on a leg, while any of its legs
   is unseeded. Print the number of resets and the seconds skipped.
2. **Crossed-book check.** At every check, if any leg has best bid >= best ask, do not open or extend a
   run on that event (close any open run). In the sim, if a leg's book is crossed at match or unwind
   time, count that leg as unfilled and count the event in a `crossed=` tally. Print the count of
   checks rejected for crossing.
3. **Dedup.** Drop raw records that repeat an earlier one with the same (asset_id, exchange
   `timestamp`, `hash` if present, else the full message). Drop runs that repeat (event, side, t0).
   Print how many of each were dropped.
4. **One trade per opportunity.** Add `--cooldown-s` (default 10) to the sim. After the sim trades a
   run on an event and side, skip later runs on the same event and side that start within that many
   seconds of the earlier run's `t1`. Print the count skipped. Report results with cooldown 10 and 0.
5. **Per-run results.** The sim writes `--per-run OUT.csv` with one row per run and delay:
   event, title, side, t0 (ISO UTC), dur, n_legs, cost0, size0, q, below_min (0/1),
   skipped_reason (below_min / cooldown / unseeded / crossed / none), seen_usd, filled_sets, pnl_usd,
   unwind_usd, full/partial/none, and the YES best bid and ask of every leg at t0, match time and
   unwind time. Also add the columns from change 9.
6. **Price and fee stored apart, looser threshold.** In `Logger.check` (`shadow/shadow_logger.py`), add
   `px0` (sum of leg prices paid) and `fee0` (sum of leg taker fees) to each run, next to `cost0`
   (keep `cost0 = px0 + fee0`). Add a `max_taker_rebate` setting: a run opens when
   `payout - px0 - (1 - max_taker_rebate) x fee0 > min_edge`, and store `edge_full_fee` (0/1: still positive
   at the full fee). Default 0, so the running logger behaves the same if it is ever restarted. `rescan.py`
   takes `--max-taker-rebate` and passes it in. Do not restart the v2 logger for this.
7. **Rebate rate per leg.** Store `rebate_rate` (`feeSchedule.rebateRate`, 0 if fees are off) next to
   `fee_rate` in the leg lists the logger writes. For the rescan, older `events.jsonl` lines lack it; fill
   0.15 for sports legs with `fee_rate` 0.05 and say so in the report. The sim does not use it yet
   (all orders are takers); it is for a later maker-leg sim.
8. **Taker rebate in the sim.** Add `--taker-rebate R` (fraction of taker fees refunded, default 0). Apply it to
   every taker fee: leg buys and unwind sales. Skip runs whose `payout - px0 - (1 - R) x fee0 <= 0`, with
   `skipped_reason = below_rebate_edge`, and compute `seen_usd` at the same R. Runs without `px0`/`fee0`
   (old format) count as `edge_full_fee = 1`.
9. **Fees and volume out.** For each side and delay, print `fees=$` (taker fees paid before rebate),
   `rebate=$`, and `wv=$` (Weighted Volume, buys only: shares x p x (1 - p) per fill, sports weight 1.0).
   Also print `wv_30d=$`, which is wv scaled from the hours of raw data covered to 30 days, and the tier it
   reaches. Per-run CSV gains `px0, fee0, edge_full_fee, fees_usd, rebate_usd, wv_usd`, and
   `maker_rebate_usd` (always 0 in this mode).
10. **Trade prints.** Count the `last_trade_price` messages per raw hour file and how many legs have any.
    Only count them; this tells us whether a later sim of resting orders is possible.

## What to run
1. Run the rescan on the same restored data as before (`rescan-data/`, without the corrupt 01Z, 04Z
   and 06Z files):
   `python3 shadow/rescan.py --data <rescan-data dir> --out shadow/rescan-clean/ --fetch-totals --gap-s 5 --max-taker-rebate 0.5`
2. Run the sim four times: `--min-unit usdc` and `--min-unit shares`, each with `--cooldown-s 10` and
   `--cooldown-s 0`:
   `python3 shadow/shadow_sim.py --data <rescan-data dir> --runs shadow/rescan-clean/runs.jsonl --one-way 0.0019 --delays 0,1,3,market --max-usd 500 --min-unit usdc --cooldown-s 10 --gap-s 5 --per-run reports/sports-mece/rescan-clean-2026-10-24-usdc-cd10.csv`
   (and the same for the other three combinations, with matching CSV names). These four use
   `--taker-rebate 0`, so they stay comparable with the old report.
3. Run the sim three more times at `--min-unit usdc --cooldown-s 10 --delays market`, with
   `--taker-rebate 0.03`, `0.08` and `0.18`, writing `...-usdc-cd10-rb03.csv`, `-rb08.csv` and `-rb18.csv`.

## Checks before you commit
- None of the 13 old runs that start in the first 60 s of 02Z or 05Z on 24 Oct should survive with the
  same quotes. List any that do, with their leg bids and asks at t0.
- Zero duplicate (event, side, t0) in `shadow/rescan-clean/runs.jsonl`.
- Zero runs opened while a leg was crossed or unseeded.
- For each per-run CSV, the sum of `pnl_usd` per side and delay equals the printed `sim=` total to the cent.
- At `--taker-rebate 0`, the runs the sim trades are exactly those with `edge_full_fee = 1` (the relaxed
  threshold adds runs to the log but not to the 0-rebate result).
- For each CSV, the sum of `rebate_usd` equals R x the sum of `fees_usd` to the cent.

## Report (commit to this repo)
Commit `reports/sports-mece/rescan-clean-2026-10-24.md` and the four per-run CSVs in
`reports/sports-mece/`. Include:
- all four simulator outputs, as printed (yes, no and both lines);
- resets (count, seconds skipped), dedup counts (raw records, runs), crossed checks rejected, runs
  skipped by cooldown;
- the result of each check above;
- for each side at delay=market (USDC and shares, cooldown 10): **the fraction of gross that comes from
  the top 10 runs**, where gross = sum of positive `pnl_usd`. Also give the same for `seen_usd`.
  Then list those 10 runs with title, t0, dur, cost0, q, seen_usd, pnl_usd and leg quotes at t0;
- the number of distinct matches contributing positive P&L, and the share of gross from the single
  biggest match;
- the hours of raw data covered, and which hours are missing;
- rebates: the three `--taker-rebate` outputs as printed; how many runs the relaxed threshold added (with
  `edge_full_fee = 0`) and their `seen_usd` at R = 0.08 and 0.18; fees paid, wV and `wv_30d` with the tier it
  reaches; and the 1 s (`market`) delay result at R = 0, 0.03, 0.08 and 0.18 side by side;
- the `last_trade_price` counts from change 10.

## When done
Set Status above to DONE and commit.
