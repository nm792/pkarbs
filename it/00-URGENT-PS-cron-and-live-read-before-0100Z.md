# 00-URGENT to IT, 19 Nov 2026 22:40Z (PandaScore thread): two read-mostly rows BEFORE 01:00Z, ahead of P67/P75/P60c/P68a. One line each.

Why: the Goalserve cron (P68, 07:30Z) runs only esports and tennis. The PandaScore CS2 look (look 1 for 19 Nov) has NO schedule. Nick's rule: no more missed windows. Also nobody has pasted a live probe read since 10:49Z (probe loop, capture `pscap2`, recorder).

1. **Live read (read-only, 60 s):** `git -C /root/pkarbs fetch -q origin reviewer && git -C /root/pkarbs show origin/reviewer:it/pandascore_live_read.sh > /tmp/pandascore_live_read.sh && bash /tmp/pandascore_live_read.sh` then `D=/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe; ls -l --time-style=full-iso $D | tail -8; for f in $(ls -t $D/pandascore-cs2-probe-*.log | head -2); do echo "== $f"; grep -E "PREFLIGHT|events|onset|exit" $f | tail -15; done`. Paste under `## CS2 live read 2 (19 Nov)` in `agent/status/pandascore.md`.
2. **Test and install the PandaScore daily look cron** (tested wrapper, runs the already-signed feeds/run_ps_cs2_daily_look.sh at 01:15Z):
   a. `for f in ps_cs2_daily_look_cron.sh test_ps_cs2_daily_look_cron.sh; do git -C /root/pkarbs show origin/reviewer:it/$f > /tmp/$f; done; bash -n /tmp/ps_cs2_daily_look_cron.sh && bash /tmp/test_ps_cs2_daily_look_cron.sh /tmp/ps_cs2_daily_look_cron.sh` (must end `PASS (4 checks, each able to fail)`; the stub run prints one git "couldn't find remote ref" line, that is the planted-failure check)
   b. only if a. passed and `crontab -l | grep -c ps_cs2_daily_look_cron` prints 0: `install -m 755 /tmp/ps_cs2_daily_look_cron.sh /root/ship/ps_cs2_daily_look_cron.sh; (crontab -l; echo '15 1 * * * ENVFILE=/root/ship/ship.env bash /root/ship/ps_cs2_daily_look_cron.sh') | crontab -; crontab -l | tail -4`
   Paste a and b under `## PandaScore CS2 daily look cron (19 Nov)`. Do not run the look by hand before 00:00Z (the wrapper refuses until the day closes).

The Goalserve thread's list is otherwise unchanged.
