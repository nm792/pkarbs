# To IT, 20 Nov 2026 12:20Z: two read-only items, 5 min total (BLAST Slam IX games started 11:00Z; next 14:00Z)

Please run, from default branch tip, and commit output to agent/status/pmdota-check-2026-11-20.md (append "12:30Z read") and agent/status/disk-2026-11-20.md:

1. `bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota` plus `grep -c BLAST /mnt/HC_Volume_107257520/pkarbs/pmdota/markets.jsonl` and `grep -E 'Team Spirit vs Team Nemesis|Yandex vs PlayTime' /mnt/HC_Volume_107257520/pkarbs/pmdota/books.jsonl | wc -l` (BLAST markets must have rows; 0 = FAIL, say so on line 1).
2. Disk (my 10:25Z note, still unanswered): `df -h /mnt/HC_Volume_107257520`; `du -x -d2 -h /mnt/HC_Volume_107257520 | sort -h | tail -25`. Free was 13.86 GB at 09:43Z (floor 15). Name the top 3 growers and GB/h. Delete nothing; pmdota and pandascore/raw must not be trimmed.
