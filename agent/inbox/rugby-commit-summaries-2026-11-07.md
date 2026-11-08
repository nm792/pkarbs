# Rugby AB: commit the 5-minute summaries every round (project thread, 7 Nov 13:30Z)

The project thread cannot see the server's /mnt/project-files (your status says it sits on the server's root disk), so rugby/live-2026-11/AB_summary.md never reaches Nick. Nick asked for a 5-minute data summary during every match, so route it through the repo.

Each cron round, while a rugby window runs, and again at window end:
1. Copy rugby/AB_summary.md (or `tail -n 60` of it if long) to reports/rugby-capture/AB_summary.md, plus `tail -n 20 rugby/AB_log.txt` to reports/rugby-capture/AB_log_tail.txt, and commit to the branch you use for status. These two small files are all that is needed in-window; the raw jsonl stays on the server until the window ends.
2. Before the 13:17Z kill, five processes each wrote a summary block, so early blocks are duplicated. After the approved kill (rugby-ab-kill-duplicates-approved-2026-11-07.md) there is one writer; just note the kill time in the status file.
3. If AB_summary.md has no block in the last 10 minutes, say so in the status file and in the commit message.
Pre-authorised, no tap needed (committing outputs only).
