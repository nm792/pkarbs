# TASK (URGENT): run the 5 s divergence logger on the server, continuously, starting today

Why: Nick wants the divergence between each perp and its oracle/index tested at real order-book prices (LOCKED-RULE-divergence-followups-2026-11-17.md, Test 1). Hourly history cannot show intra-hour gaps; a container-side copy is running but dies with the session.
1. Run `weekend-perps/pm_hl_5s_logger.py --out /mnt/HC_Volume_107257520/pmhl5s --interval 5` as a restarting service (systemd, Restart=always). It is read-only, no keys. Expected size 150-250 MB per day compressed; check free space first and keep the 15 GB floor (rotate/ship daily, delete nothing without a note).
2. Verify after 30 minutes: polls per minute about 12, no errors, books present for NVDA-USD, MU-USD, AMD-USD, TSLA-USD, SP500-USD.
3. Post a short note in agent/outbox with the unit file, first/last timestamps, row count and file size. Deadline: today 17 Nov 06:00Z. Keep it running through the weekend 21-23 Nov and the Monday reopen.
