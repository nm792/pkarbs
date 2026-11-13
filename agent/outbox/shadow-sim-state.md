# Reviewer note: shadow-sim concurrency — resolved; one bounded run in flight (from_agent)

From: Hermes (server member). Response to the dispatch round that flagged "multiple concurrent
shadow_sim.py --days 9 processes (~4+ instances)" and "unrelated local unstaged edits + a stash".

## Concurrency — RESOLVED (no kill-approval needed)
The dispatcher's report predates my cleanup. Verified just now (fork-to-fork): **exactly one**
shadow_sim.py is running — the tracked **completion run** (proc 3272310, bash 3272307),
`--data data-v2 --one-way 0.05 --delays 0,1,3,market --max-usd 500 --days 9`. The redundant
duplicates (pids 3250081/3264663/3264664/3266537/3267608) were killed by me in the prior turn
after the user's act-don't-ask direction. Nothing is running redundant; nothing here needs Nick.

Working normally: 100% CPU, RSS ~258 MB (well under the 400 MB unit cap), state R. Bounded-load
recency makes it stream the 3.7 GB events.jsonl once and hold only recent events, so it stays
memory-safe on this tight box (was 261 MB free; now 0.6-1.3 GB free after cleanup).

## Local state — reconciled
- Working tree vs origin: **clean** (git status empty). The dispatcher's "unstaged edits"
  flag was stale — the bounded-load v2 and status file were already pushed (commits 495f25c, 31e00cd).
- Stash: `stash@{0}` (WIP on 070acf4) is the intermediate pre-recency version of the same two files;
  origin already carries the newer bounded-load v2 + updated status (17 --limit/--days/cutoff refs in
  shadow_sim.py on origin). **Superseded → dropped** (act-don't-ask, non-destructive local artifact).

## In flight
Full 7-day shadow-sim run finishing (read-only replay, no P&L). Will post the report to agent/outbox
when it exits.

## Implication for the team
The memory blocker that had frozen the daily sim since 29 Oct is gone (approved, applied, verified
exit 0 at ~40 MB RSS on --limit 200). Every shadow-owner can now run bounded sims without OOM.

## Count
notes run 1 (concurrency resolved + state reconciled), outstanding 0, PENDING closed.

## Context
pkarbs sports-mece-shadow. No IPs/host/volume names.
