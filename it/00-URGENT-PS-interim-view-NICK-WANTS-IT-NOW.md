# 00-URGENT to IT, 20 Nov 2026 00:55Z (PandaScore thread; Nick 00:43Z: "we need an interim view"). READ-ONLY. Ahead of everything else for PK arbs.

Order: step 1, 2, 3, 4 below, one command per line. Paste each output under `## PS interim view (20 Nov)` in `agent/status/pandascore.md`. Nothing is edited, restarted or deleted.

1. `git -C /root/pkarbs fetch -q origin reviewer; for f in ps_interim_view.py test_ps_interim_view.py; do git -C /root/pkarbs show origin/reviewer:it/$f > /tmp/$f; done; python3 -I /tmp/test_ps_interim_view.py /tmp/ps_interim_view.py` (must end `PASS (4 checks, each able to fail)`; if not, paste and stop)
2. `D=/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe; ls -l --time-style=full-iso $D/*.json 2>&1 | tail -15; ls $D/*.json | wc -l`
3. `D=/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe; nice -n 10 timeout 1500 python3 -I /tmp/ps_interim_view.py /mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl $D/pandascore-cs2-probe-*.json 2>&1 | cut -c1-1200` (scans the 3+ GB books file once, can take several minutes; paste the whole output; if `ls` in step 2 shows 0 json files, say so and paste step 4 instead)
4. `D=/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe; for f in $(ls -t $D/pandascore-cs2-probe-*.log | head -40); do grep -H -E "PREFLIGHT all|events:|FINAL" $f | cut -c1-700; done | tail -12; ls -l --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | tail -8`

Why: probe json files are written only when a cycle ends with a measurable match; the script turns those rows into per-match events, onsets, median lead and ask depth. Output is EXPLORATORY, UNCHECKED.
Separately, after the 01:15Z cron: `tail -c 3000 /mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-daily-logs/LATEST-cs2.tail` and `ls -l /mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-daily-cs2/` under `## PS look 1 (20 Nov)`.
