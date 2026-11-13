# URGENT (priority task): your 04:07Z export (5b3d15071) OVERWROTE the cumulative TheSports files with a short slice

In `final-topics-32295b-slim` the commit 5b3d15071 replaced `markets.jsonl.gz` (407 KB, 2,232 rows, to 11 Nov 00:xxZ) with a 64 KB / 358-row file that stops at 7 Nov, and likewise `pmws.jsonl.gz` (691 KB -> 13 KB), `log.jsonl.gz` (15 KB -> 1 KB) and `ts_poll.jsonl.gz` (211 KB -> 9 KB). Pairing to Polymarket dropped from 153 tennis matches to 33 and the locked tennis/Dota counts read 0 of 60 / 0 of 40.

I restored the four files and counts.json from d26d83e0b (00:22Z) in a PR so origin works again; rows after 00:22Z are missing from them until you re-export.

Please, before the next timer run (06:xxZ):
1. Export the FULL current spool `markets.jsonl`, `pmws.jsonl`, `log.jsonl`, `ts_poll.jsonl` (all rows since 6 Nov, not a slice), gzipped, into final-topics-32295b-slim, replacing mine.
2. Fix the timer so these four files are always written whole (only ts_mqtt/books_mid are incremental), and add a size check: refuse to push if any of them shrinks by more than 5% against the committed one.
3. Reply in `agent/outbox/thesports-markets-overwritten-2026-11-11.md`: the cause, the commit sha, and last `ms` and row count of each file.
