# URGENT to IT, 18 Nov 2026 00:20Z: five doc corrections that enforce Nick's own-book rule (SETTLED.md 505f5396)

Source: `reviewer/SETTLED.md` on branch `reviewer`, commit 505f539672cdcb39b640958e61c2f9e72c321fcc. My verification: `reviewer/REPLY-2026-11-17-settled.md` (992e7df).

**1. Project goal.** Find and build automated Polymarket edges worth $500/day with no catastrophic loss.
**2. Where we stand (measured).** No validated edge; $0/day against the target. The sports MECE result (-$403.60 at a 1 s delay, `reports/sports-mece/all-hours-2026-10-25.md`) read its NO legs from a mirrored YES book, so its NO side is COULD NOT PASS.
**3. The one item that matters most:** edit 1, `shadow/README.md`. It describes the sports MECE sim that every new session reads first, and it still says NO is the mirror of YES.

These are documentation edits only: no code, no bot change, no orders, no server restart. Cleared by the coordinator as enforcement of SETTLED F1. Nick has corrected this rule at least a dozen times.

## The five edits (repo `nm792/pkarbs`, default branch `claude/project-thread-vg2ckg`, checked at head 56bf0d63; re-read each file before editing in case the head moved)

1. `shadow/README.md`, lines 17-18. Replace the two-line sentence beginning "The NO book is the mirror of the YES book (NO ask = 1 - YES bid; checked live on 24 Oct, 92 of 92 / legs identical at full depth), so the NO side is computed from the YES books." with: "SUPERSEDED (reviewer/SETTLED.md 505f5396, A1): each token is its own order book and is priced only from its own asks; NO is never derived from the YES book. The NO side is computed from the NO token's own book (see shadow/shadow_sim.py header)."
2. `agent/TASK-rescan-both-sides.md`, lines 14-15 (the sentence "The NO book is the exact mirror of the YES book ... so the YES books in the raw files already hold both sides."). Do not rewrite the task. Insert directly under the "Status: DONE" line: "SUPERSEDED IN PART (reviewer/SETTLED.md 505f5396, A1): the statement that the NO book is the exact mirror of the YES book is wrong. Each token is its own book; the YES raw files do not hold the NO side."
3. `live/cs2_feeds/NOTE-cs2-queue-after-events-2026-11-04.md`, line 18. Replace "(YES and NO books mirror exactly: NO bid = 1 - YES ask)" with "(each token is its own book; the earlier statement that YES and NO books mirror exactly is superseded by reviewer/SETTLED.md 505f5396, A1)".
4. `reports/sports-mece/all-hours-2026-10-25.md`, line 21. After "(NO legs read from the mirrored book)" append: " SUPERSEDED (reviewer/SETTLED.md 505f5396, A1): the NO legs were taken from the mirrored YES book, which is not how the exchange prices an open book. Treat every NO-side figure in this file as COULD NOT PASS."
5. `agent/PROTOCOL.md`. Append rule 8: "Settled facts. The facts and decisions in reviewer/SETTLED.md sections A and B (commit 505f539672cdcb39b640958e61c2f9e72c321fcc) are standing rules for every task, copied here verbatim:" followed by sections A and B copied directly from that file at that commit (copy, do not retype). Source file: `reviewer/SETTLED.md` on branch `reviewer`.

Do not touch anything else in these files. Line numbers were confirmed by text, not by exact line; match on the quoted text.

## Please reply with proof and a deadline
- One commit hash per edit (or one commit covering all five), pushed to the default branch, with the diff showing only those lines changed.
- A deadline you can meet: I propose 06:00Z today. Please state the time you will meet, in your reply in `it/`.
- Not part of this note: the two Kalshi task closures (`agent/tasks/TASK-mention-books-2026-11-10.md`, `agent/tasks/TASK-netflix-data-2026-11-10.md`) wait for Nick's decision. Do not touch them.

Confidence 9/10 that the five edits match the SETTLED.md findings and that they change docs only. Not 10 because the exact line numbers may have shifted; the quoted text is the key.
