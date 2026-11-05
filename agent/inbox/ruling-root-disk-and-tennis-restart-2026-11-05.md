# Ruling on your tennis-books restart question (outbox/2026-11-05-tennis-books-stop-executed-restart-check.md)

From the project thread, 12:40Z 5 Nov, answering for Nick (he asked us to fix the data-management problem; settle it here, not through him). Thanks for stopping cleanly and keeping everything committed. The stop was correct.

**Answer on restart: (b) for now, with a fix first.** Do not relaunch while root is the only place it writes. The real problem is that `/` is small and nearly full (5.9 GB free, 84%), and tonight's LoL DK-BLG dry run (22:00Z) needs >= 5 GB free on `/` (ruling 3 Nov item 7). Tennis must not compete with it.

Do these in order. Each is bounded; stop and log at any mismatch.

1. **Find what fills `/`.** One command, nice/ionice: `du -xh --max-depth=2 / 2>/dev/null | sort -rh | head -30`. Write the table into `agent/outbox/2026-11-05-root-disk-breakdown.md` with `df -h` for `/` and the HC volume. Include sizes of: cricket-feeds output, /root/oddspapi*, /root/tennis-books, CS2/LoL/Dota/NBA logger dirs, journald, apt/pip caches, /tmp.
2. **Free space on `/` using only safe cleanup:**
   - Delete: anything already committed to the repo AND gzip-verified (same delete-after-commit rule as the ruling 05:25Z), apt/pip caches, `journalctl --vacuum-size=200M`, /tmp files older than 1 day that no process has open.
   - Move (not delete): large data NOT in the repo goes to the storage box or the HC volume with the three-way sha256 check from the 3 Nov offload ruling (local sha, box sha, committed manifest line), then delete local only after all match. Skip anything modified in the last 48 h or open (`lsof`).
   - NEVER delete: anything uncommitted and not copied, the OddsPapi key, logger data for tonight's capture, or cricket-feeds output while it is running.
3. **Target:** `/` at >= 12 GB free before 20:00Z. Report the number.
4. **Tennis restart (new route):** if the HC volume has >= 20 GB free, relaunch tennis-books writing to the HC volume (not `/`), with the old stop limits adapted: kill and keep what is committed if its dir exceeds 2 GB, OR HC free < 10 GB, OR `/` free < 6 GB (so tennis never starves the 22:00Z capture). Hourly gzip+commit then delete committed raw, as before. Split any file over 90 MB before committing (you already do this). Run it until 21:30Z at the latest, then stop it so the 22:00Z capture starts clean. If HC cannot take it, stay stopped (option c); 965,778 rows is enough for the backtest to continue.
5. **cricket-feeds:** leave running. If after step 2 it is itself the main consumer, say so in the breakdown and propose a cap; do not stop it without a note back.
6. **Confirm at 20:00Z** in `agent/status/heartbeat.md`: `/` free GB, HC free GB, which captures are running, and that LoL/CS2 loggers write to `/`.

Nick can overrule any of this by telling you directly. Reply in your existing outbox files. Never commit keys.
