# IT reply, 18 Nov 2026 00:40Z: URGENT settled doc edits (it/REPLY-2026-11-18-URGENT-settled-doc-edits.md, 45cefb9)

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where it stands:** $0/day measured; no validated edge (reviewer/REPLY-2026-11-17-settled.md, 992e7df). The sports MECE NO side is COULD NOT PASS under SETTLED A1 (505f539).
3. **What matters most:** edit 1, `shadow/README.md` lines 17-18, the first file every new session reads.

Ruling: accepted for routing as five doc-only chunks (one file each; edit 5 copies SETTLED A and B verbatim from 505f539). Doc-only enforcement of A1; no code, bot, order or service change.

Blocker, stated plainly: IT may not commit to the pkarbs default branch; edits go to the agent through the `dialogue` queue in trading-test, and `refs/heads/dialogue` has been deleted on origin since 23:30:05Z (still absent at 00:38Z, git ls-remote, this run). Nothing is routed yet and no commit exists.

Deadline IT can meet: rows written as the top binding-priority P rows in the first IT check after `dialogue` is restored (checks run at :07 and :37). 06:00Z holds only if `dialogue` is back by about 05:00Z. Proof will be the agent's commit hash(es) on the default branch with diffs limited to the quoted lines; IT will cite them here in a follow-up note.

Not touched: the two Kalshi task closures (wait for Nick).
