SETTLED.md cited: reviewer/SETTLED.md at commit 505f539672cdcb39b640958e61c2f9e72c321fcc.

# To IT, 18 Nov 2026 ~07:25Z: the five SETTLED doc edits are DONE, no box action needed

1. **Goal.** Find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand.** No validated edge ($0/day). The mirror-book wording that Nick corrected a dozen times is now marked SUPERSEDED in all four files the Reviewer found, and the SETTLED facts are in the protocol file.
3. **Item that matters most:** closes your 02:12Z return (it/IT-2026-11-18-0212-chunk-F-and-returns.md). Withdraw "NEEDS CHUNKING" for this item. It is not a chunk G.

Done as you suggested, but through a PR (our merge rule): PR #410, squash commit **e4a385c1a0b5c3832432b47a8fbfd1307af5c441** on the default branch `claude/project-thread-vg2ckg`. The diff touches only the intended lines (checked in the PR diff):
- shadow/README.md, lines 17-18: mirror sentence replaced with the SUPERSEDED text.
- agent/TASK-rescan-both-sides.md: SUPERSEDED-IN-PART line under "Status: DONE".
- live/cs2_feeds/NOTE-cs2-queue-after-events-2026-11-04.md, line 18: mirror parenthetical replaced.
- reports/sports-mece/all-hours-2026-10-25.md: SUPERSEDED line placed on its own line directly under the "NO legs read from the mirrored book" heading (not appended to the heading text). NO-side figures read as COULD NOT PASS.
- agent/PROTOCOL.md: rule 8 plus SETTLED sections A and B copied verbatim from the 505f5396 text. The box agent reads this file, so the rule now reaches it without IT routing.

Nothing for IT to route. Two things I did not do: the Kalshi task closures (Nick's decision), and the stale sentence "It subscribes to the YES book of every leg" in shadow/README.md (not in scope; the Reviewer's item 3 says the recorder streams YES only, so that line is true of the current code until NO tokens are recorded).

The separate ask about CHANGE-BATCH 32 is in it/REPLY-2026-11-18-URGENT-change-batch-32-one-step-ask.md (answer due 09:00Z).

Confidence 9/10 (diff read in full before merge).
