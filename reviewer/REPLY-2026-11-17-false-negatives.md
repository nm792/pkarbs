# Reply to REVIEW-2026-11-17-false-negatives (incl. addenda 07:23Z, 07:29Z)

## 1. Goal
Find and build automated Polymarket edges worth $500/day with no catastrophic loss.

## 2. Where we stand against it (measured)
No automated edge is validated at any size yet. Cited artifacts, all at `claude/project-thread-vg2ckg` head 80859479873d:
- Perps, funding windows (xyz, sourced cost 0.9 bp): no cell has a CI lower bound above 0; liquid weekend +8.8 bp (CI -9.4 to +25.3, n 411). `weekend-perps/RESULT-divergence-rerun-2026-11-17.md`. Run ID: none recorded in the file; raw output under `followups-2026-11-17/rerun-2026-11-17/` (not opened by me).
- Perps, metals/Brent around the reopen: NOT PASSED/unknown, costed at 9 bp (wrong, see item 1). Even at full 5 bp size the file's own capacity bound is about $440/week from silver, with the wrong held-out sign. `weekend-perps/RESULT-metals-brent-oos-2026-11-16.md`.
- Sports MECE in-play: YES side saw 66 positive-edge runs in 12 h (+$96.93 after fee at detection), none surviving a 1 s delay (`reports/sports-mece/all-hours-2026-10-25.md:12`, quoted by the Reviewer; I did not open this file). NO side: could not pass as run (item 3 below).
- Position in one line: measured daily profit against the $500/day target is $0; the only gap actually seen is in sports MECE YES sets, and it did not survive delay.

## 3. The one item that matters most
Reviewer items 8 to 10, the sports MECE NO side. It is the only place in this repo where gaps were seen on live books, and half of that test (NO sets) could not see a pass. I verified in the code at head 80859479873d:
- `shadow/shadow_logger.py` docstring: "the NO book mirrors the YES book (NO ask = 1 - YES bid)". The WebSocket streams only `leg["yes"]` tokens (`asset_event`, `refresh()` chunks built from `leg["yes"]`). The NO token id is stored in the event but never subscribed to.
- `shadow/shadow_sim.py` docstring and code: NO books are `mirror()` of the YES book, and NO legs are filled by walking `mirror(bids)`.
So no NO-token price exists in any recorded raw file. A NO-book arb could not have been detected or simulated. "No NO-side arb" is therefore not a result; it is unknown. (I verified content, not the Reviewer's exact line numbers.)

## 4. Items

**Item 1 (metals/Brent at 9 bp): AGREE, with the arithmetic checked.** `RESULT-metals-brent-oos-2026-11-16.md` line 3 charges "2 x (9 bp fee + stressed half-spread)". Moving to 0.9 bp is a constant 16.2 bp per round trip (2 x 8.1), so the shifted nets the Reviewer lists follow. I did not open `growth.json` or the cost table, so the 0.9 bp applicability to SILVER/COPPER/PLATINUM/BRENTOIL rests on the Reviewer and on `RESULT-divergence-rerun-2026-11-17.md` ("xyz growth-mode 0.9 bp (sourced)"). The shifted numbers are the Reviewer's arithmetic, not a rerun; I have not rerun them. The result's capacity conclusion (far below $500/day) should be recomputed after the rerun; not recomputed here, so unsupported.
Step that let it through: the result was written 16 Nov, before the cost table existed (17 Nov), and a high cost was labelled "conservative" so no one checked it. Nothing required a cost source on a negative verdict.

**Item 2 (sports MECE NO leg priced from the YES book): AGREE on the fact** (see section 3). Platform mechanic not settled: I could not open docs.polymarket.com from this session (host not in the allowed network domains), so I cannot say from docs whether a NO ask can differ from 1 - YES bid, or how `secondsDelay` applies to in-play sports takers. This needs that host allowed, or NO books recorded and compared to the mirror. Until then both are UNKNOWN. The taker-rebate point (R = 0.03 in the sim against a 0% starting tier) is agreed in principle; not verified by me against the all-hours run.

**Item 3 (funding-window 1x spread sensitivity): AGREE, not done.** The rerun prints only the 3x-half-spread cost. A 1x row should be printed so the reader can see whether liquid cells are zero or zero because of the stress. Plan: add it as a sensitivity row (no verdict change) in the next run of the rerun script; the date depends on the IT/coordinator queue, so no date is committed here.

**Item 7 (CS2 event-only, 20 matches): NOT VERIFIED.** I have no evidence a rerun at 100 matches exists or is planned. The file's own plan said a firm verdict by about 12 Nov, before the PGL Major on 25 Nov. I will treat the verdict as UNKNOWN (n = 20) and ask the coordinator whether it is still planned.

Items 4 to 6 (stand): no objection; not rechecked.

## 5. Which step applies the cost-table check to a negative result?
None did. Every control we added (cost-term table with sources, rule-to-code table, planted-edge check) was triggered by a positive or by a lock. Changes:
1. A negative verdict ("fails", "no edge", "could not pass") carries the same gates as a positive: a sourced cost-term table, a rule-to-code table signed by someone other than the author, and the planted-edge check.
2. Every test states "can this test see a pass?" before it runs: which inputs it needs (e.g. NO-token books) and a planted-edge series that proves it detects one. A test that cannot see the thing it tests is reported as UNKNOWN.
3. Any "No X" statement in a report names the data it was based on (token books, fee source, sample n) or is labelled unsupported.
4. Wording: a result file that rests on a withdrawn input is edited to say REOPEN at the top, not left standing.

## 6. For the coordinator (working rules)
- A negative verdict is not relayed to Nick without cost sources and a "can the test see a pass" line.
- Sports MECE NO side is UNKNOWN, not "no arb". NO-token books need to be recorded (logger change, an IT task) before any NO claim.
- docs.polymarket.com must be allowed in the cloud session network to settle mechanics from docs as Nick's rule requires.

Confidence 7/10 that these answers are correct and complete. Held down by: item 1 numbers are the Reviewer's constant shift, not a rerun; the platform mechanic in item 2 and the CS2 status in item 7 are unverified; `growth.json` and the cost table were not opened. To reach 9: allow docs.polymarket.com, open growth.json and the cost table, and run the 1x sensitivity and the metals rerun.

## Addendum 09:30Z: platform mechanics settled from Polymarket docs (item 2 follow-up)

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** unchanged from the reply above: no validated automated edge. This addendum adds two platform facts, no new strategy result.
3. **The one item that matters most:** the "NO = mirror of YES" assumption in `shadow/shadow_sim.py:13-14` is mostly right for NO *prices*, so the false-negative is smaller than feared. The remaining defect is that the recorder never streamed NO tokens and the delay used was 1 s while the sports value is 3 s (below). Both are checkable, neither was checked.

**Q1: one combined book, or separate YES/NO books?**
- Docs: each outcome token has its own book fetched by its own id (`GET /book?token_id=`; "Select both outcome IDs"): https://docs.polymarket.com/market-data/prices-order-books.md . Orders in the two books match by minting a complete set: "Someone places a limit order to buy Yes at $0.60 ... buy No at $0.40 ... the orders match ... 1 pUSD creates a complete set": https://docs.polymarket.com/concepts/prices-orderbook.md . Market-making page: "Buying NO at 0.48 ... is economically equivalent to selling YES at 0.52": https://docs.polymarket.com/trading/market-making.md . The docs do NOT state in words that the NO book is a literal mirror, so I measured it.
- Measured 17 Nov 2026 ~09:25Z, live `clob.polymarket.com/book`, the 8 highest-24h-volume active markets with all four sides populated (7 negRisk, 1 not; script and output not committed, recomputable): in all 8, the lowest 5 NO ask prices equal 1 minus the highest 5 YES bid prices, and the best NO bid/ask equals 1 minus best YES ask/bid (e.g. YES 0.123/0.125, NO 0.875/0.877). n = 8 markets at one instant, not a sports in-play sample, sizes not compared.
- Conclusion: on these markets the two books are the same liquidity shown two ways, so deriving NO ask = 1 - YES bid gives the NO token's own ask price. Pricing NO from YES books should not by itself hide an arb. Reviewer's item 8 stays valid as a *data* point (no NO-token book was ever recorded, so equality was never verified for sports MECE) but the likely effect on the verdict is small. Caveat: I did not test sports in-play books or negRisk tail legs with empty books (Nick's fact, separate issue). Confidence the mirror holds for sports markets: unsupported until a sports pair is compared.

**Q2: secondsDelay for sports**
- Docs: `secondsDelay` = "Delay, in seconds, before a newly placed marketable order can match" (https://docs.polymarket.com/market-data/market-details.md, Market Timing). Order lifecycle: "Sports/game delay: enabled on configured sports markets around live game conditions. The order waits for the market's configured delay window before matching. During either delay, the order is pending and cannot be canceled. If the market, balance, allowance, or risk checks fail when the delay expires, the order is rejected instead of matching": https://docs.polymarket.com/concepts/order-lifecycle.md . Status `delayed`; place-orders page says to read `market.trading.secondsDelay` before ordering: https://docs.polymarket.com/trading/place-orders.md .
- Not a "250 ms" taker delay: that is a separate mechanism for crypto/finance up/down markets (`itode: true` on `GET /clob-markets/{condition_id}`).
- Value: Gamma API `GET gamma-api.polymarket.com/markets?...tag_id=1` returned `secondsDelay` = 3 on 7 of 100 sports markets (Bundesliga 2 football, returned markets dated Nov 2025, so possibly stale; the other 93 had null). I did not find a docs page that states 3 s as a rule. So: the delay is per market, 3 s observed, not the 1 s the sim used. A delayed order is a held taker: the price can move during the wait and it is then matched or rejected, so a gap must survive the full delay, which makes a 3 s delay harsher than 1 s.
- Implication for item 2: re-running at 1 s understates the delay; the YES-side "none survive 1 s" verdict is, if anything, firmer at 3 s. Re-check `secondsDelay` per live market at order time.

Confidence 7/10. Q2 definition and Q1 docs statements are quoted from the docs; Q1 equality is measured but n = 8, non-sports, one instant; the 3 s value is from Gamma on possibly stale rows. To reach 9: compare YES/NO books on 20+ live sports in-play markets and read secondsDelay for current live games.

## Addendum 2, 09:25Z: the two checks needed to reach 9 (YES/NO books on sports markets, current secondsDelay)

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** unchanged: no validated automated edge. This addendum measures two platform facts only. Inputs: Gamma `GET /markets?closed=false&active=true&order=volume24hr&end_date_min=2026-11-17&end_date_max=2026-11-19` (600 markets, 201 with `gameStartTime` or `secondsDelay`), then `clob.polymarket.com/book` for both tokens of each, fetched 17 Nov ~09:22Z. Scripts not committed (recomputable); no run ID.
3. **The one item that matters most:** `secondsDelay` is **1 s** on today's sports and esports markets (not 3 s), and 0 on NBA, so the 1 s delay in the shadow sim matches the platform. My 3 s in the earlier addendum came from stale Nov 2025 Bundesliga rows and is withdrawn.

**secondsDelay today (201 markets, by slug prefix):** 1 s on 173 (fif/soccer 47, unl 42, cs2 25, afcq 14, dota2 12, nhl 10, cbb 7, val 6, conl 5, and one each bra, cfb, clf, euroleague, uwcl); 0 s on 28 (all `nba`). Mechanism and docs links as in the first addendum (order held for the delay, not cancellable, then matched or rejected).

**YES/NO books, sports and esports (184 markets with all four sides populated):**
- Best NO ask and best NO bid equal 1 minus best YES bid and best YES ask in **184 of 184**.
- Every price level and size mirrors on both sides (full depth) in **175 of 184**. I did not inspect the 9 that differ; likely cause is books moving between my two sequential fetches, unverified.
- 8 of the 184 have a `gameStartTime` already passed (soccer, Valorant, CS2). That is "started per schedule", not confirmed in-play; it is a small in-play sample.
- Conclusion: for sports markets, deriving NO ask = 1 minus YES bid gives the NO token's own top-of-book price. The NO-side "could not pass" finding stands as a recorder gap, but the mirror assumption in `shadow/shadow_sim.py` is supported at top of book. Not tested: negRisk tail legs with empty NO asks (Nick's fact), and a NO-token book recorded over a full game.

Confidence 9/10 on the mirror at top of book (184/184, sports and esports, one instant) and on today's secondsDelay values. Held back from 10 by: single snapshot, 8 started-per-schedule markets, 9 full-depth mismatches not inspected.

## WITHDRAWAL 09:25Z (Nick, 09:21Z): the "NO mirrors YES" conclusion is withdrawn
Nick's fact: NO mirrors YES only on resolved books, not on open ones. My addendum and addendum 2 concluded that deriving NO from YES gives the NO token's own price, on the strength of 184/184 top-of-book matches from `GET clob.polymarket.com/book` on open markets. **That conclusion is withdrawn.** It is UNKNOWN whether the real resting NO orders differ from 1 minus the YES book, and my snapshot cannot tell, because REST `/book` for the complement token may be a derived view and not the resting NO orders (cause under investigation, next addendum). Consequence: Reviewer items 8 to 10 stand in full; the sports MECE NO side is COULD NOT PASS, and nothing in my two addenda reduces that. The secondsDelay findings (1 s today, 0 s NBA; docs quotes) are unaffected.
