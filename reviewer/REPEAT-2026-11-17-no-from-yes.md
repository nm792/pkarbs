# REPEAT: NO priced from YES, 17 Nov 2026. Verdict: COULD NOT PASS

For: the PK arbs project (not the box agent). Reviewer note, read-only. Reply in `reviewer/REPLY-2026-11-17-no-from-yes.md`.

## The claim (17 Nov, corrected by Nick at 09:23Z)
"On the 8 markets checked, the NO prices are exact mirrors of the YES prices, so pricing NO from YES shouldn't have hidden any arbs."

## The rule (fixed by Nick)
Each Polymarket token is its own order book and is priced only from its own asks. A NO buy fills against the NO token's asks, never 1 - YES. Mirroring holds for resolved books. It does not hold for open books. A check on resolved books says nothing about open ones, so this check cannot pass.

## Prior instances in this repo (same assumption, written down as fact)
| # | Date | File | Text |
|---|---|---|---|
| 1 | 24 Oct | `shadow/README.md:17` | "The NO book is the mirror of the YES book (NO ask = 1 - YES bid; checked live on 24 Oct, 92 of 92 ...)" |
| 2 | 24 Oct | `agent/TASK-rescan-both-sides.md:14-15` | "The NO book is the exact mirror of the YES book ... so the YES books in the raw files already hold both sides" |
| 3 | 25 Oct | `reports/sports-mece/all-hours-2026-10-25.md:21` | "NO legs read from the mirrored book" |
| 4 | 4 Nov | `live/cs2_feeds/NOTE-cs2-queue-after-events-2026-11-04.md:18` | "YES and NO books mirror exactly: NO bid = 1 - YES ask" |
| 5 | 17 Nov | project chat (Nick's correction) | the 8-market claim above |

Count: 5 written instances in this repo or chat (24 Oct to 17 Nov). Nick says he has corrected this at least a dozen times. The other corrections are not in this repo.

## Required before any arb result that uses NO prices is used again
1. List the 8 markets checked, with market id, check time (UTC), and whether each was resolved or open at that time.
2. Say the same for the 24 Oct "92 of 92" check: were those books open or resolved?
3. Re-run the check on open books only. Read each token's own asks from its own `/book` call at the same timestamp. Report mismatches per level, not only at the top.
4. Until then, every arb count or P&L in the files above that read NO from YES (items 1 to 4) is unverified.

5. Likely cause of the recurrence: `shadow/README.md:17` and `agent/TASK-rescan-both-sides.md:14` still state the wrong rule as fact, and new work reads them. Correct both at the source, in your own branch (the Reviewer does not edit them), and confirm the corrections in your REPLY with the commit SHA.

## Discussion (answer in the reply file)
- Why does this rule keep being forgotten? Name the step that lets it back in: a README that still states the mirror as fact, a rescan design built on it, or something else.
- What will you put in your own instructions so it cannot come back? State the exact wording.
