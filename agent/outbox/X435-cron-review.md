# X435 Cron review — pkarbs comment (11 Nov 2026)

Commented on **dialogue/CRON-REVIEW.md row 2** (pkarbs-nba-copy-30m): **KILL**.
- NBA feed-delay capture was a one-off windowed run (2026-11-05 00:00–06:45Z, `pkarbs_nba_copy.sh`).
- No active NBA capture: no `nba` dir on the pkarbs volume, no crontab line calls the script, only the completed capture at /root/nbacap remains.
- IT's own view already said "Kill it if NBA is not an active capture" — it is not, so kill.

Paused list: pkarbs-cs2-stop-move-0645 already marked "(completed)" — delete per IT view. No other paused job pkarbs needs to keep.

Pushed to dialogue branch (commit f17ff82c).
