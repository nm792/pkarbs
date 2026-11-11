# Nick APPROVED CHANGE-BATCH #6 (10 Nov 05:12Z: "2. yes")

Approved: add the cricket capture's ts_mqtt rows (/mnt/HC_Volume_107257520/pkarbs/thesports-cricket/2026-11-10) to the 2-hourly slim export by editing the export timer's topic list, as in your outbox thesports-cricket-separate-capture-2026-11-10.

Please:
1. Apply the edit (same slim layout, cricket under its own dir name, e.g. `final-topics-cricket-slim`, parts under 5 MB, deletion guard as before).
2. Make a one-off cricket export now (all cricket ts_mqtt, pmws and log rows since 04:05Z).
3. Reply in `agent/outbox/thesports-cricket-export-2026-11-10.md`: commit sha, row counts per file, and the first and last `ms`.
