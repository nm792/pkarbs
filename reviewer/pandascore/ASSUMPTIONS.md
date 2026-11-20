# ASSUMPTIONS: PandaScore CS2 / Dota 2 timing test (PandaScore thread, 20 Nov 2026)

Machine-readable table: `assumptions.csv` (columns input, value, status, source, used_by, blocks_what). Status words: MEASURED, DOCUMENTED, ASSUMED. MECHANICS: `MECHANICS.md` in this folder.

**Rule applied:** no ASSUMED input feeds a reported result. The current test only measures timing. Its ASSUMED rows are pre-registered analysis conventions (onset 2c, +-60 s, placebo, pass bar) that PREREG fixes before the data; changing any of them is a new test, not a re-run. Everything about executing a trade (send RTT, queue priority, placement after the 1 s delay, network paths) is ASSUMED or unmeasured, so **no trade, fill or P&L claim is made** from a lead result. Result label stays UNCHECKED/exploratory until an independent checker signs.

Count: MEASURED 5, DOCUMENTED 4, ASSUMED 12 (see csv). The four ASSUMED rows that block a trading claim: send RTT, PandaScore->host and Polymarket->host network latency, matching priority, delayed-taker placement.

What measures each ASSUMED item (next steps, owner PandaScore thread unless stated):
1. Send RTT: 100 timed GETs to the CLOB from the server (no order), via an IT row; not yet routed.
2. Network paths: not separable from our receive times without a second vantage; report leads as receive-to-receive.
3. Matching priority / delayed taker: venue docs or an own-order test on a quiet market; needs Nick's approval (real orders). Not requested.
4. `latency.delay` semantics: confirmed or refuted by comparing message-level delays with updated_at in the capture (analysis, no new data).
