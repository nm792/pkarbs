# QUEUE ORDER (updated 20 Nov 04:27Z; Nick 03:23Z, read-only, minutes). Do in this order, before every other row:
0. it/00-URGENT-PS-both-stopped-on-floor-0648Z-restart-floor-3GB.md (both recorders stopped 06:48Z, 07:00Z match missed) -- Nick-blocking
1. it/00-URGENT-P88-export-goalserve-match-samples-NICK-WANTS-IT-NOW.md (Goalserve, P88)
2. it/00-URGENT-PS-export-ALL-cs2-matches-since-1920.md (needs the storage-box copy of the PandaScore raw hours)
Then P87 etc. Paste results to agent/status/pandascore.md and the Goalserve file.

UPDATE 07:50Z (PandaScore): 
- P91 (restart both CS2 recorders) stays first. In the P91 row also ship the idle folders named in IT-2026-11-20-0522Z-vol2-ship-idle-folders.md (pkarbs/from-vol 6.8 GB, pkarbs-ps-step2 3.4 GB) so VOL2 has margin above the 10 GB floor (12.07 GB free leaves only 2 GB).
- NEW: it/00-URGENT-PS-T0k-BOX-session-export-pandascore-hours.md is addressed to the session that can read the storage box (T0k5 or equivalent). IT routes it there; Nick is not asked to.

UPDATE 08:20Z (PandaScore): it/00-URGENT-PS-LIVE-MATCH-read-0911Z.md = the ONE exact live-match read IT asked for (09:11Z and 09:41Z sessions; four CS2 matches at 09:00Z). It proves the capture writes. Run it; it is read-only.

UPDATE 09:55Z (PandaScore, TIME-CRITICAL): ROW 1 for the 10:11Z dispatch session = it/00-URGENT-PS-LIVE-MATCH-read-0911Z.md (read-only, one command). The four 09:00Z CS2 matches end at about 11:00Z; the read proves whether the PandaScore capture wrote a `connected` line and a new pandascore_2026112009 hour file. It takes about 90 seconds. Do it before P93 and P86a.
FALLBACK schedule (same command, same paste heading): run it again in the 10:41Z session (before the 11:30Z windows) and in the 11:41Z session (before the 12:00Z windows). If a session skips it, write a REPLY file naming the exact blocker (token, tmux, permission, row not found) instead of silence.

UPDATE 11:05Z (PandaScore): P94 read-only live read read as PASS in substance (see my note in the paste): the capture IS writing. Next PandaScore row for the 14:11Z session: it/00-URGENT-PS-export-LOCAL-hours-at-1411Z.md (read-only export of today's local raw hours, one more commit of sample files).

UPDATE 15:10Z (PandaScore): P95 (read-only export, under 5 MB) runs with a 2 GB gate, not 10 GB: see it/REPLY-2026-11-20-1510Z-P95-gate-waived-readonly-export.md. P95 first, then P97.

## UPDATE 22 Nov 04:15Z: put it/00-URGENT-PS-R022-live-read-listing-coverage-by-0700Z-22Nov.md FIRST (read-only, three commands, due 07:30Z). P95/P97 exports are done.

## UPDATE 22 Nov 04:20Z: R022 row runs at the 05:41Z dispatch, merged with the Dota 0730Z read in one session.
