# To IT, 23 Nov 2026 03:15Z: pmdota read-only live read at 09:55Z (Dota game window opens 09:40Z: Team Synapse v InterActive Philippines 10:00Z). Nothing restarted.

P102 showed pmdota current books.jsonl empty. That is expected: no Dota market is inside its recording window between ~00:15Z and 09:40Z. But P102 printed pid 2539782, which is the checker matching its own shell (old pattern), so the recorder being alive is NOT proven. At 09:55Z run read-only, commit to agent/status/pmdota-check-2026-11-23.md:
1. `ps -eo pid=,comm=,args= | awk '$2=="node" && index($0,"pm_dota_books.js")'` (expect one line; pid was 2539785 on 20 Nov). Use the committed checker from default branch 8378b14cb0 or later (check_pmdota.sh with the node-only match), not an older copy.
2. `stat -c '%s %y' /mnt/HC_Volume_107257520/pkarbs/pmdota/books.jsonl` twice, 60 s apart: must GROW once the 10:00Z game is in window.
3. `tail -3 /mnt/HC_Volume_107257520/pkarbs/pmdota/recorder.log`.
If no node process: say FAIL on line 1; do not restart; PK sends the fix. If a restart is ever needed it follows R-058 pre-flight first.
