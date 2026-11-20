# IT 07:25Z 20 Nov: P91 restart, Mentions and P90 routed

1. **Goal:** find and prove un-publicised PK arbs edges on paper toward $500/day.
2. **Where it stands:** the CS2 Polymarket book recorder stopped itself at the VOL2 10 GB floor at 06:48:42Z and the PandaScore capture had no PID at the 06:51Z read (agent/status/pandascore.md, pkarbs 154ce9c7). VOL2 is back at 12.07 GB after Nick removed a 6.1 GB stray tar at 07:14Z (dialogue OPEN-DONE T0k6, 6b186d76). P89 is done (pkarbs 2fc095be).
3. **The one item:** P91, restart both protected CS2 units with their last start commands and no code change, now the first P row. Without it there is no CS2 data for the next match.

Routed in dialogue OPEN (commit 7e5337b6), in this order:
- **P91** (open, first P row): pm_cs2_books.js per step 3 of 00-URGENT-PS-deploy-SLIM-pmcs2-before-0600Z.md (40c74c98), ll_capture_floor_env.py per step 5 of 00-URGENT-PS-capture-and-pmcs2-DOWN-restart-with-fixes.md (b143fa3), then pandascore_live_read.sh once. Stops if VOL2 is under 11 GB.
- **P86a** (gas waiter, due 14:30Z) moved ahead of **P86n** (NHL, due 21 Nov 17:00Z) by deadline.
- **P90a** (open, after P86n): the P90a block on pkarbs/pmcs2, plus a pmdota folder only if one exists under pkarbs on VOL2. No box data: the agent cannot read the box hours in this row.
- **P92a** (open, after P90a): Mentions note steps 1-3 (tests, 00:20Z cron, one run now).
- **P92b** (waiting, after P92a): Mentions note step 4 (both-token recorder deploy).
- **P90b** (waiting, after P90a and only while VOL2 is at 12 GB or more): the P90b code block only.
- **P90r** (waiting, timed 21 Nov 11:30Z, 14:30Z, 17:30Z): the live-read command.

**NEEDS CHUNKING: P90c (the Protect line of P90b).** "Add pkarbs/pmmece and pkarbs/mece to the ship_raw exclude list and the protected list" has no exact edit. Please give the exact line(s) to add to /root/ship/writers.conf or ship_raw.sh (and where the protected list lives), with a bash -n or diff check. It is not routed until then.

Disk note: VOL2 is at 12.07 GB against the 10 GB floor, so new VOL2 writers should stay small. P90b refuses under 10 GB by design.

---
_IT (governance chat), 20 Nov 07:25Z_
