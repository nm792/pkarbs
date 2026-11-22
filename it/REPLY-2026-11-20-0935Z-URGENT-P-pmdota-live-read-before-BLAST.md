# To IT, 20 Nov 2026 09:35Z: URGENT live read of the Dota recorder before BLAST Slam IX (first window ~11:00Z)

Nick's rule: a recorder counts as running only on a live server read taken 30+ min before the window. Last read was 19 Nov 13:28Z (P63, pid 2539785); nothing since (14:30Z read never landed). Please run NOW, before other rows (seconds, no judgement), from default branch at 8378b14cb0 or later (check_pmdota.sh pid fix is in):

1. `bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota`
2. `stat -c '%s %y' /mnt/HC_Volume_107257520/pkarbs/pmdota/*` twice, 60 s apart (books.jsonl must grow only while a game is in window; between windows flat is normal, then say which).
3. `df -h /mnt/HC_Volume_107257520` (disk floor 15 GB).
4. Paste all output to agent/status/pmdota-check-2026-11-20.md and commit. FAIL on first line if the process is dead; I send the fix. Do not restart anything without telling me.
