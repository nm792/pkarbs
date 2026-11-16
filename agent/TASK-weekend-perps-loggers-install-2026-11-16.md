# TASK (URGENT): install the two weekend perp loggers and prove them on a live sample

Deadline: **Thu 20 Nov 2026 12:00Z** (so 21-23 Nov is captured). Post a start-line status when you begin.

Files (merged, PR #359): `weekend-perps/hl_weekend_logger.py` (Hyperliquid xyz) and `weekend-perps/pm_weekend_logger.py` (Polymarket perps, SP500/NAS100/NVDA/SNDK/MU/AMD/GOOG, every 60 s).
Both were smoke-tested live from another machine. Analysis scripts already ran on real backfill data (weekend-perps/backfill-2026-11-16/), so the harness exists.

Steps:
1. Run each as a restarting service (systemd, Restart=always), output on /mnt/HC_Volume_107257520 (not the root disk).
2. Let both run 30 minutes. Write `agent/outbox/weekend-perps-logger-sample-<date>.md` with row counts, first/last timestamps, and file sizes for each logger.
3. Re-check on Thu 20 Nov 06:00Z that both are still writing.

If anything blocks, raise it in the outbox at once; do not wait.
