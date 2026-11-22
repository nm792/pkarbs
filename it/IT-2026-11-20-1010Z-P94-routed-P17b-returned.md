# IT 10:10Z 20 Nov: P94 PandaScore live read routed, P86a reopened, P17b returned

1. **Goal:** measure whether CS2/Dota live data (PandaScore, Polymarket books) leads the market enough to trade, with the protected recorders writing continuously.
2. **Where it stands:** P93 pmdota live read done (report 890c7de68e, 09:43Z). VOL2 13,667,217,696 bytes free after the root syslog archive (trading-test dialogue status/X3-syslog.md, 3e94254c). pkarbs/from-vol: see IT-2026-11-20-1006Z note.
3. **Most important item:** your 09:55Z queue update (806f1b1a) asked for the PS live-match read as row 1 at 10:11Z, but no OPEN row carried it, so the 10:11Z session could not see it. Routed now as **P94**, first P row, for the 10:41Z and 11:41Z sessions (dialogue c1006d22). The 10:11Z read is missed.

Items
- P94 (open): run it/00-URGENT-PS-LIVE-MATCH-read-0911Z.md command plus pandascore_live_read.sh at 10:41Z and 11:41Z; paste under `## PS live match read (20 Nov)` in agent/status/pandascore.md.
- P86a (open, after P94): VOL2 is above the 10 GB gate; step 3 only (crontab line for 14:50Z), since steps 1-2 passed (agent/status/gas.md, 1c1f9270).
- **P17b returned, NEEDS A RULING:** its window was 10:00-10:30Z and its own task gate needs VOL2 at 15 GB or more; VOL2 is 13.67 GB. Reply with either a new start window and a lower gate (10 GB is the IT floor), or "skip P17b". P17d and P17c wait on it.
- Still unanswered: it/00-URGENT-IT-0925Z-delete-final-topics-yes-or-no.md (34.9 GB). Nothing is deleted without your YES.
