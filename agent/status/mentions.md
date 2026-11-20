## Mentions daily scorer (20 Nov)

P92a complete, read-only scorer setup verified on Prime.

- Step 1: scorer checks passed: `PASS (12 of 12 checks)`; cron wrapper tests passed: `PASS (6 checks, each able to fail)`. The wrapper's expected missing-ref test printed `fatal: couldn't find remote ref nosuch` before the PASS summary.
- Step 2: installed `/root/mentions_pm_daily_cron.sh`; Prime crontab contains `20 0 * * * /root/mentions_pm_daily_cron.sh`.
- Step 3: manual run completed all three paper-only scorers. Polymarket: 13 forward events, NET P&L after fees -$25.29. Kalshi arm 1: 2 events, NET -$0.15. Kalshi arm 2: 72 events, 9 bets, NET +$7.60. All three LATEST files include their NET lines; outputs are under `/mnt/HC_Volume_107257520/pkarbs/mentions/daily/`.
- Verification: run logs record exit 0 for all three scorers; `LATEST.txt` and both Kalshi LATEST files are present. The 00:20Z daily cron is installed.
- Scope: P92a steps 1–3 only. Recorder deployment is P92b, not performed in this row.

P92a project commit: pending.
