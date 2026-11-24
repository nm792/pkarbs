# Gate: PK NBA maker paper spec v5 (pkarbs 448c2130bd, spec 7a49c18640). 24 Nov 09:20Z
Verdict: **FAIL (spec)** on item 4 (fill mode and trade feed). Item 3 is partly met. Items 1 and 5 PASS. Item 2 PASSES as a rule, with a condition. Paper only. No node code exists; this gates the spec.
Checked against my own wording of the 5 points (ea259ebda), not the relay. I could not read the owner's INBOX P-NBA-13 from here, so the item-by-item reply is not checked.

## Item 1: superseded comparator. PASS
- v5 sec. 0 withdraws the one-night +10.5% and cites the 3-day NBA maker figure -$1,819 on $270K (-0.7%). I verified this in pkarbs origin/reviewer rn1-recheck README section E (line 44), and the 56% share and +4.69% entry gap at line 54.
- Open, not blocking: section 0 does not say which RN1 NBA market types the rule is built from (the README gives totals/spreads/moneylines $ at line 9, but no per-type P&L for the 3 days).

## Item 2: placement. PASS as a rule, with conditions
- Rule: quote at best bid + 1 tick only when the spread is >= 2 ticks, so the bid opens a new level with 0 shares ahead. That is the settled placement lesson (MFW, Nick 24 Nov 03:15Z), not a join.
- Condition A: the "joining" baseline arm re-tests the settled finding that joining loses. It may run only as a labelled comparison arm, never as a candidate strategy, and its results are reported as a re-test of a settled fact.
- Condition B: the RN1 placement pull (rn1_placement.py on Prime, against P106e books) must run and be reported BEFORE any start. Until then the spec's "RN1 joins / improves" statements stay UNKNOWN (v5 says so).
- Condition C: "fair value from the pre-registered jump model" (sec. 3) has no definition in this spec. It must be defined, with its frozen SHA, or the cell is untestable.

## Item 3: principles table. PARTIAL
- Present and specific: s2 power (planted edge plus null), s4 breadth (games as the independent unit), s5 shrinkage per cell, s8, s10 (fill-conditional markout against the unmatched counterfactual), s11 (per game, day and week; top-5 share), s12 (10-min markout primary), s13 (stops; first 10 games blind), s14 capacity, and the informed-trader check. All pass.
- MISSING: the s17 citation checklist. The standing rule requires a row-by-row citation of the project's ledger for each rule. v5 cites README sections and SETTLED A-rules in places, but not ledger rows for each rule (e.g. the NBA feed-delay rule, the 0.206 s latency, and the queue measurement each cite a file, not a ledger row).
- Required: an s17 table with one line per rule, citing the ledger row.

## Item 4: Nautilus fill mode and feed. FAIL
- Good: trade_execution=True and queue_position=True named; own node and account; MINT matches count as fills (Nick 03:33Z); LOWER BOUND label if one token's prints are missing.
- **FAIL 4a, the default is a test that can only say no.** v5 sec. 2: "default if Nick does not answer: LOWER BOUND label, books-only". With no trade prints in the node's feed, the trade-tick matching that every fill depends on never runs. Only the book can fill, so the test can show no fill for a bid at an inside level, the same failure as MFW's trade_execution=False (r157). The books-only default is not allowed to start a run. The node needs a live trade-print feed for BOTH tokens before it starts. The Data API v2 pull is a REST backfill, not a live feed, so it cannot serve the node as a live source.
- **FAIL 4b, the settled mapping rules are missing.** The MINT rule (Nick 03:33Z) as the MFW gate applied it: other-token BUYER prints mapped fill-only, with the mapped tick never reaching pricing, mid, markout or signals; and de-duplicated against our own token's prints by (token, price, size, ts_event). v5 has neither.
- **4c, not specified:** liquidity_consumption, use_message_queue, the latency model (its sensitivity cells are listed, but not the engine setting), and the pre-flight fail cases (a planted same-token SELL fills; a planted other-token BUY fills, with mapping off gives no fill; a post-only accepted at or above the real ask is FAIL).
- "Joining the single live node": v5 now says "own node and own account, joining the single live node supervised". Those two phrases conflict. The node must be its own TradingNode with its own trader id and account; it may be supervised with the live node, but it must not share an account or engine with it (bucket e68e8ca3f and MFW 23 Nov).

## Item 5: delay class. PASS
- Hold = the market's seconds_delay if > 0, else 250 ms (sec. 3). That matches SETTLED A.3 (Nick card 23 Nov 13:08Z). The claim that NBA reads 0 is cited (R-065, 2 games, 23 Nov) and the write-up of that as UNVERIFIED for the wider league is honest.
- Open, not blocking: whether secondsDelay adds to or replaces the 250 ms is UNVERIFIED, and both cells run.

## Notes
- The standing check 3 applies: no settled fact of PK's (SETTLED.md) is contradicted. A.1 (own books, NO never from YES) is respected. A.7 (no orders) is respected.
- Confidence and sizing: the spec's confidence 6/10 and its "no $/day before a lower CI" line are consistent with NO SIZING FROM PROBES. Keep it.

## To clear (resubmit v6)
1. A LIVE two-token trade-print feed for the node, named and tested (not a REST backfill, and no books-only default).
2. The MINT fill-only and de-duplication rules, with the planted cases.
3. The engine settings named: trade_execution, queue_position, liquidity_consumption, use_message_queue, latency model.
4. The s17 table, with ledger rows per rule.
5. Condition B run (RN1 placement pull) and the jump-model definition with its SHA.
