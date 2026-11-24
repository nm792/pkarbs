# Gate: PK NBA RN1-style maker, Nautilus live paper SPEC v4 (pkarbs 199a6050f5, branch claude/project-thread-lfb1pf). 24 Nov 08:30Z
Verdict: **FAIL (spec)** on 5 items. Paper only. No node code exists yet; this commit has the spec plus the Data API v2 client only. Gating "against the code" therefore covers the client, and the spec against Nautilus 1.231 behaviour.

## What passes
- **Data API v2 client** (scan/nba_paper/pm_data_api_v2.py): fails closed; every row's condition id must equal the request, and rows without the field raise.
  - My rerun of test_pm_data_api_v2.py: the planted wrong params condition_ids / markets / market and the missing-field case all raise.
  - Live: condition_id returned 1,000 on-market rows; param=markets raised WrongMarketRows on row 0.
- Paper client only, never a credential (A7). Fills, queue and P&L are to come from the Nautilus engine, with no custom fill/queue/P&L code (R-081).
- Own-token books (A1). Principles 8, 12, 13 and 14 are written down, with pre-set stops and a held-out first 10 games.

## FAIL items
1. **It cites a superseded fact as its comparator (standing check 1 / 3).**
   - Section 2 gives "RN1 ... NBA maker +10.5% on $42.5K in one night".
   - The same source file, reviewer/pkarbs/rn1-recheck-2026-11-24/README.md (pkarbs reviewer), has a CORRECTION in section B: NBA maker over 3 days **-$1,819 on $270K (-0.7%)**, with daily figures -4,681 / -7,979 / +5,078 / +5,764.
   - The spec's own held-out figure is also negative: -$42/game at 0 s on 39 games in 2026.
   - The spec must carry the corrected figures, and say what in RN1's NBA maker fills (by market type: spreads +4.7%, totals -4.7%) the rule is built from.
2. **The quote rule is not built from measured RN1 placement, and it reads against the settled placement lesson (standing check 3).**
   - "Bid at mid x 0.975, 10 s life" puts us behind a measured median of 6,300 sh. The live dry run had 0 fills on 62 bids, with 1,876 sh ahead (README A).
   - That is the pattern Nick ruled on for MFW (24 Nov 03:15Z): joining behind a deep queue only fills when price runs through us. That is adverse selection by construction, and it fails MODELLING-PRINCIPLES s10.
   - The spec must cite where RN1's NBA maker fills sit against the own-token best bid at fill (above / at / below, with c/sh), as flow_r156 did for MFW, and set the rule from that.
3. **The principles table is incomplete (standing check 2).** It covers s8, 12, 13 and 14 only. It needs:
   - s2 power: a planted maker edge of the target size, which the same pipeline must detect;
   - s4 breadth: independent bets, given games and both tokens;
   - s5 shrunk edge per league / market type;
   - s10 fills not random: who fills us, chaser vs against-move;
   - s11 regime: per day (RN1's NBA days swing ±$5-8K);
   - the informed-trader / HMM check;
   - the s17 citation checklist.
4. **The Nautilus fill mode must be specified, not left to IT.**
   - In 1.231, trade_execution=False fills a resting bid only when the book's ask reaches it (process_trade_tick returns before matching). For a bid below the best bid, that under-fills.
   - trade_execution=True fills on any SELLER print at or below our price. Without queue_position=True it ignores the 6,300 sh ahead, which is an upper bound. Nautilus's queue_position needs trade_execution=True.
   - The spec must name: trade_execution=True + queue_position=True + liquidity_consumption=True; use_message_queue=True with the market's own latency; the Polymarket data client's own trade ticks reaching the sandbox (P106e drops prints, but the node's data client is separate); and the pre-flight fail cases (as MFW maker G/G-, H/H2).
   - **Per the MINT ruling (Nick 24 Nov 03:33Z):** a taker BUY of the other team's token at q >= 1-p may fill our bid on this token. Map it fill-only and de-duplicated, as the MFW maker node does, or label all results a lower bound.
   - **"Joining the single live node" is not allowed:** own-order competition and a shared account (bucket e68e8ca3f FAIL; MFW 23 Nov wallet fault). Use its own TradingNode, trader id and Nautilus account.
5. **The delay class contradicts SETTLED A.3.** The spec says "250 ms is not used for sports" and gives NBA as 0. A.3 (Nick card 23 Nov 13:08Z): 250 ms taker hold on non-weather markets whose own delay reads 0; sports markets use their own 1 s. An NBA market reading 0 therefore gets 250 ms in the engine. Post-only rests are unaffected, but cancels, requotes and any take are not. Use the bucket node's settled_a3 mapping, or bring Nick a primary source.

## Notes
- No sizing statement (NO SIZING FROM PROBES); the spec's quarter-Kelly line should go.
- The $/day basis (sim $70/day, 35% of $200) is labelled unproven. Keep it that way.
- The P106e health read and the per-market feeSchedule / minimum / seconds_delay are still UNVERIFIED, as the spec says. The pre-flight must read them and be able to fail.
