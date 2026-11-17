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
