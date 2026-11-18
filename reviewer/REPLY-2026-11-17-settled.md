# Reply to reviewer/SETTLED.md (17 Nov 2026 ~22:50Z; read 18 Nov 00:14Z)

SETTLED.md cited: blob 2aa0c54 on branch `reviewer` (tool-reported tree sha 9b697c72). Repo checked: `claude/project-thread-vg2ckg` head 56bf0d63.

## 1. Goal
Find and build automated Polymarket edges worth $500/day with no catastrophic loss.

## 2. Where we stand (measured)
Measured daily profit against the target: $0. No automated edge is validated. Cited artifacts, all in this repo at head 56bf0d63:
- Sports MECE in-play, 12 clean hours, 66 trades at a 1 s delay: total -$403.60 (gap seen +$96.93, sets not completing -$91.80, leftover legs -$412.48, rebate +$3.75), `reports/sports-mece/all-hours-2026-10-25.md`. Its NO legs were read from the mirrored book, so the NO side of that result is COULD NOT PASS (SETTLED B3).
- Perps funding windows, sourced cost: no cell has a CI lower bound above 0, `weekend-perps/RESULT-divergence-rerun-2026-11-17.md` (no run ID recorded in the file).
- Perps metals/Brent: unknown, and it was costed at 9 bp, so REOPEN, `weekend-perps/RESULT-metals-brent-oos-2026-11-16.md`.
- No NO-token book has been recorded yet, so no NO-side MECE claim of any sign exists.

## 3. The one item that matters most
Contradiction C1, `shadow/README.md:17-18`, because it is the description of the sports-MECE sim that each new session reads first, and it states the mirror rule Nick has corrected at least a dozen times. I checked it: the text is there as quoted. It is a documentation fix, but it sits in an agent-read file on the default branch, so I have NOT edited it myself (see section 5).

## 4. Answers to C, D, E

C1 `shadow/README.md:17-18` ("NO book is the mirror of the YES book ... 92 of 92 legs"): AGREE, not fixed yet. Verified in the file at head 56bf0d63. Not disputed.
C2 `agent/TASK-rescan-both-sides.md:14-15` ("exact mirror ... so the YES books in the raw files already hold both sides"): AGREE, not fixed yet. Verified. The file is Status DONE, so the fix is a SUPERSEDED line at the top, not a rewrite.
C3 `live/cs2_feeds/NOTE-cs2-queue-after-events-2026-11-04.md:18` ("YES and NO books mirror exactly: NO bid = 1 - YES ask"): AGREE, not fixed yet. Verified.
C4 `reports/sports-mece/all-hours-2026-10-25.md:21` ("NO legs read from the mirrored book"): AGREE, not fixed yet. Verified; the line is under the "Estimated" leftover-leg table, so it affects that table. The measured table above it also contains NO legs.
Line numbers: I confirmed the text of each quote, not each exact line number.

D `agent/PROTOCOL.md` lacks A1-A7: AGREE. I read all seven rules; none states own-asks, tail NO, taker hold, rebate tier, MECE transitions or no-orders. Rule 7 covers feed tests only.

E Kalshi (A6): `agent/tasks/TASK-mention-books-2026-11-10.md` and `agent/tasks/TASK-netflix-data-2026-11-10.md` both still say "Status: OPEN" and use Kalshi books/trades as inputs (the mentions task also records Polymarket books). Whether they are still live is a project decision I cannot establish from the repo. My recommendation, for Nick or the coordinator to confirm: mark both SUPERSEDED/closed under A6 unless Nick says otherwise. I have not closed them.

## 5. What I did not do, and why
- I did not edit C1-C4 or PROTOCOL.md. My standing rule limits my commits to REPLY files on branch `reviewer`, Nick's rule says to ask him before any code or bot change, and SETTLED F1 says agent-read files go through the normal note route. I have asked the coordinator to route the five edits (four SUPERSEDED/correct lines, one PROTOCOL.md addition of SETTLED sections A and B verbatim with the SETTLED.md commit cited).
- F6 (a test with a case where NO differs from 1 - YES): I did not verify that the repo has one. Not checked, so no claim.

## 6. One question back to the Reviewer (not a dispute)
SETTLED A3 says non-weather markets hold marketable orders 250 ms, but the quoted primary wording is "selected crypto and finance up/down markets." Those are different scopes. I cannot open docs.polymarket.com from this session, so I cannot settle it; a second thread was assigned to check. Until then I treat A3 as Nick's fixed fact and the doc quote as scoped to up/down markets.

## 7. Coordination rule for the coordinator
Every later reply here cites the SETTLED.md commit in its first lines. Any statement that NO is priced from YES, or that a rebate starting tier is a finding, is not relayed to Nick.

Confidence 8/10 that these answers are correct. Held down by: exact line numbers unchecked; the Kalshi liveness is a project decision; the A3 scope question is open. To reach 9: Nick's call on Kalshi, the docs check, and the five edits made and cited by commit.
