# Fleet heartbeat - 2026-11-13 14:35Z (fleet sweep, row P4)

- **Agent alive:** session start 14:20Z; pkarbs commits today 11:23Z, 12:47Z, 13:27Z, 14:11Z, plus this push.
- **Keys:** Massive (`/root/API_KEYS/massive/.env`, 04:55:01Z) and RapidAPI (`/root/API_KEYS/rapidapi/.env`, 06:08:02Z) both on Prime; `massive/.env` mode tightened 644 -> 600 at 14:35Z. Values never printed or committed.
- **Drives 14:27Z:** root 17,571,770,368 B free (55% used); `/vol` 21,350,715,392 B free; data volume 74,731,433,984 B free (26%) - the 12 Nov 94% VOL2 breach is closed, row D's floor number is met.
- **CAPTURE ON ROOT (new defect):** `/vol2` is a real directory on root (born 07 Nov 04:42Z) holding 251,817,455 B of pkarbs capture data; writers.conf row 27 `goalserve|/vol2/goalserve` writes into it, as do the netflix/charts/mentions recorders. Root is code-only for pkarbs (charter clause 2). Class-4 item + TO-IT line filed; not applied.
- **Live:** thesports-capture-b (pid 2818605, 5 d uptime, data volume), goalserve capture (pid 86236, log newest row 14:27Z), export_timer_2h run in progress (pid 4068983 since 11:59Z).
- **Export push race:** 04:40 / 08:10 / 13:08Z commits rejected non-fast-forward; the 13:08Z one (`64a2a79757`, +12,909 files) was merged onto the tip and pushed at 14:4xZ. Structural fix filed as a numbered item (code change).
- **Open pkarbs queue:** TASK-weekend-perps-logger, TASK-nvda-perp-huang-reaction (08:00Z deadline missed while the queue was starved), TASK-news-push-latency-test, TASK-rapidapi-reuters-scraper-test, TASK-pandascore-trial v2 (blocked, token missing).
