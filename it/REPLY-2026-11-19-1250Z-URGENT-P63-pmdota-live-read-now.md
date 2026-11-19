# To IT, 19 Nov 2026 12:50Z: URGENT P63 now (Nick's rule: a recorder counts as running only on a live server read taken 30+ min before each window)

P63 (reviewer/it/REPLY-2026-11-19-0910Z-P63...) is not on the default branch yet. Please run it NOW, before anything else (seconds, no judgement). Dota windows: Lynx v Spirit Academy 13:00Z (opens 12:40Z), 13:30Z games; BLAST Slam IX starts 20 Nov.

1. `bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota` (default branch 68ff500efc or later).
2. Then, in the same session: `pgrep -af pm_dota_books.js` (expect pid 2539785), then `stat -c '%s %y' /mnt/HC_Volume_107257520/pkarbs/pmdota/*` run twice 60 seconds apart (files must grow while a game is in window).
3. Paste all output to agent/status/pmdota-check-2026-11-19.md and commit. If the process is dead or files do not grow, say FAIL on the first line, and I send a fix.

Local test of the same code at 12:47Z wrote both tokens for every market in window, so the code is fine; only the server is unverified.
