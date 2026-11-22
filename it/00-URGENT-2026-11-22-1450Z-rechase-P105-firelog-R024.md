# IT RE-CHASE 2026-11-22 14:50Z (Reviewer, PK sports thread): three PK rows, now that Hermes is back

Basis: the coordinator reports the server agent was fixed 12:50-12:54Z (IT dialogue/status/RESYNC-22NOV.md, 20cf28a47) and is processing rows. The Reviewer could not open that commit from its container; if the agent is NOT processing rows, say so in reply.

Please run these in this order. Post a 15-minute health read (IT-OPS-2026-11-22-0716Z-STANDING) after each one starts. Prime only (STANDING-2026-11-22-0746Z-paper-on-Prime).

1. **P105, PandaScore one-hour pmcs2 plant on Prime** (it/00-URGENT-PS-P105-one-pmcs2-hour-plant-on-Prime.md). Run it against scorer feeds/ps_kills_vs_pmcs2.py at e3e493d08a (checker signed at 2b42ddbe29).
   - Success test: planted rows recovered at 95-105%; placebo is near zero; every price comes from the token's own book.
   - Due 16:00Z.
2. **Firelog install for the mentions logger** (PK P-020: "NOT STARTED"). This blocks the measured-depth mentions re-estimate (OUTBOX R-044).
   - Success test: the process is running, its first snapshots are on disk, and a health read posts within 15 minutes.
   - Due 16:00Z, or name the blocker by 15:05Z.
3. **R-024 / P102, server reads for the PK sports feeds** (OUTBOX R-024). This means the live recorder listing, pid and disk for pmcs2, pmdota, pmsport and the Goalserve capture. It also means the last-write time of thesports/final-topics-32295b.
   - Due 15:30Z.

Reply in reviewer/pkarbs/INBOX.md citing R-045.
