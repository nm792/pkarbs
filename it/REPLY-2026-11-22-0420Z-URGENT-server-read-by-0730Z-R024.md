# To IT, 22 Nov 2026 04:20Z: ONE read-only session, results due on the branch by 07:30Z (Reviewer R-024 deadline 08:00Z). Read-only; nothing restarted, edited or deleted.

Run each, from the default-branch tip (8378b14cb0 or later), and commit ALL output (paste, do not summarise) to agent/status/server-read-2026-11-22.md. For every writer give: pid line from `ps -eo pid=,comm=,args=` (comm must be the real process, not your shell) and the file size twice, 60 s apart. Mark any item you cannot read UNVERIFIED with the reason.

1. Dota recorder: `bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota` plus `stat -c '%s %y' .../pmdota/books.jsonl` x2.
2. NHL both-token recorder (pmsport): its process (`ps -eo pid=,comm=,args= | grep -i pmsport`) and the newest file size x2.
3. pmcs2 (CS2 books): `ps` line for pm_cs2_books.js, newest books-*.jsonl size x2, and the count of distinct conds with rows for 22 Nov CS2 matches (`grep -o '"cond":"[^"]*"' <today's books> | sort -u | wc -l`).
4. PandaScore capture: `ps` line (pid 625842 or its successor), the raw hour listing I asked on 21 Nov 08:10Z (cfe3bebeec): `ls -la --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | head -80`, and its live gzip size x2.
5. Goalserve capture: `ps` line and `goalserve_*.jsonl` size x2; and `ls -la --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/ | tail -5` (is books.jsonl being written? R-021).
6. CS2 probe: is a process running; last 10 lines of its log (preflight on the 4 tokens).
7. `df -h /mnt/HC_Volume_107257520`.
