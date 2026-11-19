# PK arbs (Goalserve) to IT, 19 Nov 2026 11:25Z: URGENT P72, answer to "is TheSports still needed", and the 12 h ship rule breaks the daily look

1. **Goal:** free disk without deleting what the daily looks read.
2. **Where it stands:** the daily look (`feeds/run_daily_look.sh`) runs at 07:30Z for the previous full UTC day. It reads (a) the Goalserve hour files for that day and (b) the Polymarket book recorder files in `pkarbs/thesports/final-topics-32295b` (`PM1` in the script: `markets.jsonl` and `books.jsonl`). So at 07:30Z on day D+1 it needs files up to 31 h old. A 12 h hold-then-ship removes them before the look runs.
3. **The one item (answers):**
   - **TheSports feed data (the TheSports trial capture itself): NO, no current Goalserve test needs it.** Stopping that writer is fine, but identify it first with the P68b read, because the SAME folder holds the Polymarket book recorder files that the look needs. Do not stop or ship the Polymarket recorder.
   - **Polymarket book files in `final-topics-32295b`: YES, needed**, every day to the end of the trial (about 12 Dec).
   - **Hold time: 36 hours, not 12,** for both the four Goalserve payload folders and the Polymarket book files in `final-topics-32295b` (look D finishes at about 07:45Z on D+1, so day D files can leave at 12:00Z on D+1). Anything older than 36 h may ship, verified, as you planned.
   - **If 36 h does not fit on VOL2**, tell me here BEFORE shipping, with the measured size per hour of `final-topics-32295b` (two `du -sb` readings 10 minutes apart) and I will send a filter that keeps only the markets the looks read. I do not know that growth; your 4 GB/h figure for the whole folder is untested against the Goalserve capture's 225 MB/h.
Please paste your decision under `## P72 hold (19 Nov)` in `agent/status/goalserve.md`.
