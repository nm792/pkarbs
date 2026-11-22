# IT ROW: NBA recorders on Prime before 23:30Z 22 Nov + TheSports box manifest

From: former gas / NBA / TheSports thread (spec: scan/nba_paper/SPEC-nba-paper-test-2026-11-22.md, branch claude/project-thread-lfb1pf, a983d811). Reviewer orders R-028, R-029, R-030, R-032, R-037, R-039. Read-only capture, NO orders. Run on Prime under your caps.

## Part 1 (needed first, by 14:00Z 22 Nov, read only)
1. TheSports box copy: list BOX_ROOT/stale-20261122/vol2/pkarbs/thesports/ with every file name, size in bytes and sha256 (P101a.log says 10 files, 34,906,107,252 B, checksum_exit=0). Say whether P101b (deleting the VOL2 source) ran and when. Paste under '## TheSports box manifest' in agent/status/nba-books-ws.md.
2. In that tree, for books.jsonl: first and last recv time per day 6-16 Nov, and the count of distinct NBA token ids with rows after 12 Nov 12:39Z (the gamma 406 break). Same for pmws.jsonl: count of rows with "leagueAbbreviation":"nba" per day.
3. Give the Prime path of pm_sport_books.js (NBA tag) and of the live sports-WS logger, and say whether its output file contains NBA frames today (row count of nba frames in the last 24 h).

## Part 2 (recorders; start before 23:30Z 22 Nov; first NBA tip is about 00:00Z 23 Nov)
Start on Prime, same host clock, same OUT dir: (a) pm_sport_books.js with the NBA tag: both tokens' own books by websocket for every NBA moneyline; (b) the sports-WS frame logger with NBA frames written; (c) agent/tasks/nba-feed-delay/books.py auto or equal, plus the NBA liveData scoreboard/play-by-play poller (measurement only). Follow agent/tasks/nba-books-ws.md Part B with 22-23 Nov dates; memory cap as in that task. No deletes.

## Proof to paste (agent/status/nba-books-ws.md), per recorder
- pid; two file sizes and row counts 60 s apart; the committed capture SHA (git sha of the script as run) and the start time.
- R-037 HEALTH READ within 15 min of start: >= 99% of expected snapshots captured (expected = 1 per second per token per live game window), 0 unhandled errors, price source = each traded token's OWN book (name the JSON field/line), disk free, pid. On any FAIL: stop, keep files, fix, restart, new read within 15 min, plain-English meaning.
- If the recorder cannot start before 23:30Z say so here at once with the blocker.
