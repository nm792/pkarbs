# SETTLED: PK arbs (nm792/pkarbs)

Written by the Reviewer, 17 Nov 2026 ~22:50Z. For the PK arbs project (Nick's Claude project), not for the box agent.
Source for every fact and decision below: Nick's own rulings as recorded in the Reviewer project memory, and the agreed rows of the Reviewer register (`register-lessons.md`). Only Nick changes a fixed fact.

Why this file exists: each new session rebuilds its picture from this repo, and this repo still says things Nick has corrected many times. The code was fixed (`shadow/shadow_sim.py:10-16` now prices NO from the NO token's own book), but the README and the task file that describe it still say the opposite, so the next session re-learns the wrong rule.

## A. Fixed facts (Nick)

1. **Each Polymarket token is its own order book and is priced only from its own asks.** NO is never priced as 1 - YES bid/ask. Mirroring holds only for resolved books, never for open ones (Nick 17 Nov 09:23Z; he has corrected this at least a dozen times).
   - **Platform mechanics, recorded 18 Nov 17:50Z from primary docs and the venue's own data. This corrects the description, not the pricing rule.** Polymarket's docs (docs.polymarket.com/concepts/prices-orderbook, saved in mfw-clone docs/primary/polymarket-docs/prices-orderbook.html, sha256 4546e68d…, fetched 6 Nov) say that a buy of Yes at $0.60 and a buy of No at the complementary $0.40 match, because $0.60 + $0.40 = $1.00. 1 pUSD then mints a complete set, and the reverse operation merges it. So an open market's YES and NO orders sit in one matching book, and the book published for the NO token is the YES book seen from the other side. Reviewer probe at 14:51Z: `clob.polymarket.com/book` for both tokens of all 11 open London 20 Nov markets. YES and NO were identical up to complement at every level, in price and size, with equal server timestamps (raw JSON: trading-test reviewer/temperature/evidence/polymarket-open-books-london-2026-11-20.json; pkarbs saw the same, 92/92 legs, on 24 Oct). **What stands:** price each token only from its own published asks, read from that token's book at the decision moment. Never take a price from another source or from a hand-kept copy. **What is withdrawn:** "NO is never 1 - YES" and "mirroring holds only for resolved books", as statements about the published open book. A NO ladder equal to 1 - YES is not a defect in itself, and findings that rested only on it are withdrawn.
2. **Tail NO books never get asks.** A leg that needs asks on tail NO books cannot fire by construction. This is known, not a finding.
3. **Taker hold:** non-weather markets hold marketable orders 250 ms (Nick). Primary doc wording: "Taker delay: used on selected crypto and finance up/down markets. The order is held for 250 ms" (docs.polymarket.com/concepts/order-lifecycle; copy in nm792/mfw-clone `results/rule-rebuild-2026-11-05/primary/concepts_order-lifecycle.md:62`). Sports markets also carry their own seconds delay (`secondsDelay`).
4. **Taker Rebate tiers run 0-50% by 30-day volume.** The starting tier is not an issue for a strategy that trades volume: volume earns the tier. Do not report a 0% starting tier as a finding.
5. **MECE gaps appear at transitions** (data releases, deciding events, score changes). A scan on a fixed time grid cannot pass; it samples between transitions.
6. **Kalshi is not relevant here.** Update (Nick 18 Nov 07:51Z): Kalshi cannot be traded for now but is a future target. Kalshi data may be used for analysis (e.g. gas series); no Kalshi trading.
7. **Never trade or stage orders.** Ask Nick before any code or bot change.
8. **Never infer availability or edge from a book read after resolution or after the decision moment (Nick, 18 Nov 07:32Z).** A book read once the outcome is decided, or at any time after the decision, says nothing about what was available at the decision. It cannot support "no asks", "can never fill" or "no edge". Any such claim is refused as a REPEAT. The only valid evidence is the book logged at the decision moment.

9. **Pass bar: a strategy that can reliably deliver $200 per day is worth pursuing (Nick, 18 Nov 08:18Z).** Every candidate's sizing reports $/day on qualifying strikes with realistic fills (decision-time depth, own-token prices, fees), with a confidence interval, against this bar. "Reliably" means the CI lower bound, not the point estimate. Stacking (Nick 18 Nov 08:21Z): the plan is to stack many such strategies. Each candidate is judged on its own reliable $200/day, and also reports (a) the correlation of its daily P&L with the other candidates/live strategies, (b) the capital it ties up and shares with them, and (c) its worst-day loss, so a stack's combined worst day can be bounded. Rebates (Nick 18 Nov 08:22Z: some may also qualify for rebates): report P&L before rebates and rebate/incentive income separately, citing the venue's fee and rebate docs; report the tier the combined stack volume would reach. The $200 bar is judged before rebates; rebates are upside (same rule as Nick's MFW milestone, 18 Nov 07:37Z: break even before rebates, rebates on top).
## B. Settled decisions and agreed lessons

1. REPEAT (register, 17 Nov): NO priced from YES. Five written instances 24 Oct to 17 Nov. Any new instance is refused unread.
2. Missing own-book rows are excluded and counted, never filled from the other token (register row "token priced from the other token's book").
3. Sports MECE recorder streamed YES tokens only (`shadow_logger.py:279-283`), so every past sports-MECE NO result is COULD NOT PASS until NO tokens are recorded (register, false-negative audit 17 Nov).
4. Every lock carries a cost-term table (term, value, source, measured/published/assumed); "not published" means search sibling projects first; unsourced results are COST UNCHECKED (your own REPLY-2026-11-17-platform-rules.md, accepted).
5. A locked rule protects a test only if a non-author maps each rule line to file:line before the run, and the code recovers a planted edge and returns ~0 on a no-edge series (register row 7).

6. **Ideas log (Nick, 18 Nov 08:26Z: the projects never keep track of ideas discussed).** Every idea Nick raises or the project proposes gets a row in `reviewer/IDEAS.md` the day it comes up: idea, date, source, status, next step. Rows are never deleted. Status changes are appended with a date and commit. An idea is never dropped silently: "parked" names who parked it, when and why. Every REPLY that changes an idea's status updates its row.
## C. Contradictions found in this repo (default branch `claude/project-thread-vg2ckg` at 371480a7d7)

Searched: `agent/PROTOCOL.md`, `agent/TASK-*.md`, `agent/tasks/`, `agent/inbox/`, every `README.md`, `notes/`, `evrules/`, plus a repo-wide search of `.md`/`.txt` for the mirror wording. There is no CLAUDE.md, AGENTS.md or wiki/ in this repo.

| # | File:line | What it says | Contradicts |
|---|---|---|---|
| 1 | `shadow/README.md:17-18` | "The NO book is the mirror of the YES book (NO ask = 1 - YES bid; checked live on 24 Oct, 92 of 92 legs identical at full depth), so the NO side is computed from the YES books." | A1. Also contradicts the current code it documents (`shadow/shadow_sim.py:10-16`, "Nothing is derived from the other token's book"). **Worst item:** it is the description of the sim every new session reads first. |
| 2 | `agent/TASK-rescan-both-sides.md:14-15` | "The NO book is the exact mirror of the YES book (checked live on 24 Oct: 92 of 92 legs identical at full depth), so the YES books in the raw files already hold both sides." | A1. Agent-read task file. |
| 3 | `live/cs2_feeds/NOTE-cs2-queue-after-events-2026-11-04.md:18` | "YES and NO books mirror exactly: NO bid = 1 - YES ask" | A1. |
| 4 | `reports/sports-mece/all-hours-2026-10-25.md:21` | "NO legs read from the mirrored book" | A1; the result in that table is COULD NOT PASS. |

## D. Fixed facts missing from the instruction files

`agent/PROTOCOL.md` (the standing rule file) states none of A1-A7. Missing: own-asks rule (A1), tail NO (A2), taker hold (A3), rebate tier (A4), MECE transitions (A5), never trade or stage orders (A7). The "no orders" rule appears only task by task (e.g. `agent/tasks/TASK-mention-books-2026-11-10.md:14`).

## E. Needs a project answer (not counted above)

Kalshi (A6) is used in `agent/tasks/TASK-mention-books-2026-11-10.md:1,14` and `agent/tasks/TASK-netflix-data-2026-11-10.md:1,6,9,11` (Kalshi books and trades as model inputs). State whether these are still live; if they are, explain why A6 does not apply, or drop them.

## F. What the project must do

1. Correct each file in section C at source (or replace the line with "SUPERSEDED, see reviewer/SETTLED.md"), on your own branch. Agent-read files go through your normal note route, not through the Reviewer.
2. Copy sections A and B verbatim into the file every new PK arbs session reads first (`agent/PROTOCOL.md` or a new top-level instructions file), citing this file's commit.
3. Reply in `reviewer/REPLY-2026-11-17-settled.md`: for each item in C, D and E, either "fixed at <commit>" or "disputed" with a primary source. Open the reply with the goal, the measured position with a cited artifact, and the single most important item (REPLY-RULES.md).
4. Every later reply cites the SETTLED.md commit in its first lines.
5. Any claim that contradicts this file is a REPEAT and is returned unread. To change a settled item, bring a primary source to the Reviewer; fixed facts change only on Nick's word.
6. Tests: a test built on the same assumption as the code cannot find that assumption. Every test that touches A1 must contain a case where the NO book differs from 1 - YES and must fail if NO is read from YES.
