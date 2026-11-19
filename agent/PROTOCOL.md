# Protocol for server work (standing rule, from Nick, 25 Oct 2026)

The server is a shared resource. Every task in agent/ follows these rules. A task that breaks them
should not be run; report back instead.

1. **Local first.** Everything that can be tested without the server is tested without it first
   (synthetic books with hand-computed answers, small public samples). Code changes ship with tests:
   `python3 shadow/test_gates.py` must end with "N of N gates pass" before any server task uses that code.
2. **Small and bounded.** A server task gets at most 1-2 hours of data, streams files (no loading a
   whole data set into memory), runs one process at a time, and runs under a memory cap and a time
   limit on resident memory, e.g. `systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 timeout 1800 python3 ...`
   (`ulimit -v` caps virtual memory and kills Python early; do not use it). No overlapping jobs.
3. **One question, pass/fail fixed in advance.** Each task states the single question it answers and
   the pass/fail criterion before it runs. If a gate fails, stop, report the failure and the examples,
   and do not report P&L.
4. **Clean up.** When done, kill every process the task started, delete its temp files, and say so in
   the report (`ps` and `free -m` after).
5. **No queue.** Never start new server work while an earlier task's results are still unreviewed.
   Only one task in agent/ is OPEN at a time, apart from the always-on logger.
6. **Label every number.** Each figure in a report says whether it was computed by the sim on real
   data, computed on synthetic data, or estimated. Estimates are never reported as measured.
7. **Feed tests follow one standard.** Any feed trial or latency test cites feeds/STANDARD-feed-latency-test.md (v1) and does not restate it. The benchmark is always the Polymarket price, never another feed. Only Nick changes it.
8. **Settled facts.** The facts and decisions in reviewer/SETTLED.md sections A and B (commit 505f539672cdcb39b640958e61c2f9e72c321fcc) are standing rules for every task, copied here verbatim:

## A. Fixed facts (Nick)

1. **Each Polymarket token is its own order book and is priced only from its own asks.** NO is never priced as 1 - YES bid/ask. Mirroring holds only for resolved books, never for open ones (Nick 17 Nov 09:23Z; he has corrected this at least a dozen times).
2. **Tail NO books never get asks.** A leg that needs asks on tail NO books cannot fire by construction. This is known, not a finding.
3. **Taker hold:** non-weather markets hold marketable orders 250 ms (Nick). Primary doc wording: "Taker delay: used on selected crypto and finance up/down markets. The order is held for 250 ms" (docs.polymarket.com/concepts/order-lifecycle; copy in nm792/mfw-clone `results/rule-rebuild-2026-11-05/primary/concepts_order-lifecycle.md:62`). Sports markets also carry their own seconds delay (`secondsDelay`).
4. **Taker Rebate tiers run 0-50% by 30-day volume.** The starting tier is not an issue for a strategy that trades volume: volume earns the tier. Do not report a 0% starting tier as a finding.
5. **MECE gaps appear at transitions** (data releases, deciding events, score changes). A scan on a fixed time grid cannot pass; it samples between transitions.
6. **Kalshi is not relevant here.**
7. **Never trade or stage orders.** Ask Nick before any code or bot change.

## B. Settled decisions and agreed lessons

1. REPEAT (register, 17 Nov): NO priced from YES. Five written instances 24 Oct to 17 Nov. Any new instance is refused unread.
2. Missing own-book rows are excluded and counted, never filled from the other token (register row "token priced from the other token's book").
3. Sports MECE recorder streamed YES tokens only (`shadow_logger.py:279-283`), so every past sports-MECE NO result is COULD NOT PASS until NO tokens are recorded (register, false-negative audit 17 Nov).
4. Every lock carries a cost-term table (term, value, source, measured/published/assumed); "not published" means search sibling projects first; unsourced results are COST UNCHECKED (your own REPLY-2026-11-17-platform-rules.md, accepted).
5. A locked rule protects a test only if a non-author maps each rule line to file:line before the run, and the code recovers a planted edge and returns ~0 on a no-edge series (register row 7).
