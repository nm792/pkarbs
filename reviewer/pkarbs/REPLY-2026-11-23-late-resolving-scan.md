# REPLY to R-056 item (2): R-036 item 1 / OPEN-ITEMS 6, status 23 Nov ~02:00Z

**Goal:** find and build un-publicised Polymarket edges that reliably deliver $500/day (bar $200/day per strategy on the CI lower bound).
**Where we stand (measured):** $0/day; the late-resolving scan has no MEASURED cell, only FLOORs: causal $53/day summed over 81 families (26% of $200) and a hindsight ceiling of $868/day (pipeline/R036-late-winner-scan-2026-11-22.md, late_leader.py 3364acc6d3, tapes to 19 Nov); wti-15m +$29.05/day, lower bound +$5.52, 11 bets, UNPROVEN.
**The one item that matters:** decision-time own-token books for these series exist nowhere until IT restarts the resolving-books recorder on commit 131c2c6200 and posts a health read; without them every $/day stays a FLOOR.


STATUS: FINAL NOT POSSIBLE AS MEASURED BY 12:00Z; delivered as FLOOR (22 Nov numbers) plus two exact blockers. Confidence 6/10.
Numbers (unchanged, interim P-019 text in pipeline/R036/INBOX-row-P-019.md; the INBOX ID P-019 was also used by the perps thread, so rename mine P-R036-1): causal FLOOR $53/day summed = 26% of $200 (T-1h; T-3h -$167, T-30m -$14), CEILING $868/day hindsight, no MEASURED cell.
BLOCKER 1 (measured depth): decision-time own-token books exist for nothing. Recorder code is done and tested (pipeline/forward/resolving_books.py, 7 tests, health read per R-037). IT row it/IT-2026-11-22-resolving-books-recorder.md (commit 1d46eb258b on claude/project-thread-o5rbz8) was never picked up: it is not in the reviewer tree. Renamed from late_books to resolving_books today because "late-books" is also the gas runner's name (pid 2259571). Needed from IT: run steps 1-5 of that row and post the health read; first usable depth table needs about 4 weeks (20 events per daily family).
BLOCKER 2 (fresh data): R-039 forbids rerunning backtests in the container. Prime rerun row: it/IT-2026-11-23-prime-late-leader-final.md (data 49 MB in /mnt/project-files/pipeline/R036/pk_cache_min.tgz). It reproduces 53.07 / 867.7 / 81 first, then extends the sample to 23 Nov. If IT runs it before 11:00Z I write the final table from the CSV by 12:00Z.
BLOCKER 3 (my push): rows are on my branch only; Nick has not answered the push card (open since 22 Nov 06:00Z).
OPEN-ITEMS row 6 update (not yet on reviewer): status "REPLIED interim; FINAL = FLOOR; MEASURED blocked on IT rows resolving-books recorder + Prime rerun"; stays OPEN.
