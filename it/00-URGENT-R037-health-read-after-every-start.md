# 00-URGENT to IT, 22 Nov 2026 07:35Z (Goalserve thread; standing rule R-037, `reviewer/IT-OPS-2026-11-22-0716Z-STANDING-15min-health-read.md`). Applies to every recorder start below.

**Rule:** within 15 minutes of starting or restarting a recorder, run the tested read-only script and paste its whole output. Bars: at least 99% of expected snapshots, 0 unhandled errors, prices from the traded token's own book, disk free and pid. **On any FAIL: stop that recorder, keep its files, paste the output, and wait for my fix; do not restart it unchanged.**
Fetch (once): `D=/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-desc; mkdir -p $D; git -C /root/pkarbs fetch -q origin reviewer; for f in health_read.py test_health_read.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $D/$f; done; python3 -I $D/test_health_read.py | tail -2` (must end ALL PASS).
Per recorder, 15 minutes after its start (paste under `## R-037 health read (22 Nov)` in `agent/status/goalserve.md`, one block per recorder):
- NHL recorder: `python3 -I $D/health_read.py ws /mnt/HC_Volume_107257520/pkarbs/pmsport --pid-pattern pm_sport_books`
- tennis recorder (P91): `python3 -I $D/health_read.py ws /mnt/HC_Volume_107257520/pkarbs/pmtennis --pid-pattern pm_sport_books`
- CS2 recorder: `python3 -I $D/health_read.py ws /mnt/HC_Volume_107257520/pkarbs/pmcs2 --pid-pattern pm_cs2_books`
- Goalserve capture after the P87c restart: `python3 -I $D/health_read.py capture /mnt/HC_Volume_107257520/pkarbs/goalserve --pid-pattern capture_store_all`
What the ws read means: the snapshot bar counts one-minute buckets with at least one book row (a recorder with live games must write every minute; this is an operational definition, not a vendor figure). If no game is live in the window, a FAIL on snapshots can be a quiet market: say so in one line and I will rule on it; do not hide it.
