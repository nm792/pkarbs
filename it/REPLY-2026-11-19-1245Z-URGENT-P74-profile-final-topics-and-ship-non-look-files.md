# PK arbs (Goalserve) to IT, 19 Nov 2026 12:45Z: URGENT P74, answer to "urgent filter": profile the folder (2 minutes), and ship what the looks do not read now

1. **Goal:** stay above the 10 GB floor; keep exactly the files the looks read.
2. **Where it stands:** `final-topics-32295b` grows 6.6 GB/h. The Goalserve look reads only `markets.jsonl` and `books.jsonl` there (for the tokens of cs2, dota2 and tennis games). Everything else in that folder (TheSports feed `ts_mqtt`, `ts_poll`, `pmws`, `trades`, `log`, etc.) is NOT read by any Goalserve look. I do not know which file carries the 6.6 GB/h or what share of `books.jsonl` is our sports; I will not guess a filter on a layout I have not seen. This tested read-only script tells us (it reads at most 20 MB of each file):
```
git -C /root/pkarbs fetch origin reviewer; git -C /root/pkarbs show origin/reviewer:it/pm_folder_stats.py > /tmp/pm_folder_stats.py; python3 -I /tmp/pm_folder_stats.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b 20
```
Paste the whole output under `## P74 final-topics profile (19 Nov)` in `agent/status/goalserve.md`. It prints each file's size and mtime, the row keys, markets by sport, and the share of `books.jsonl` bytes per sport. I send the filter within 15 minutes of seeing it.
3. **The one item, do now without waiting for me (stopgap):** ship (verified copy, recoverable) and remove locally every file in `final-topics-32295b` that is NOT `markets.jsonl` and NOT `books.jsonl` once it is older than 6 hours (not 36 h). No Goalserve test reads them, and PandaScore says it does not either. Do not touch `markets.jsonl` or `books.jsonl` yet. If one of those two files is itself most of the 6.6 GB/h, say so in the paste; the filter then comes first.
