# IT: live pid-and-growth reads now, at the agent's next session (URGENT, read-only)

Goal: automated, measured edges toward $500/day; Nick asks whether the tests are running and only a live server read can say yes.
Measured position: gas listing-book capture is running (my read 14:58:35Z, then LISTED 15:01:02Z, books20 file growing); everything below is UNVERIFIED since its last dated read. SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.
Single most important item: the PandaScore RAW capture has not written since 16 Nov (your 10:54Z note); P71 restart is queued. Say whether it is writing now.

One block, one paste, each line with its own UTC timestamp. For each item print: `pgrep -af <process>` (pid), then two `stat -c '%s %y' <file>` readings 60 s apart, and PASS or FAIL on the first line.
1. PandaScore RAW capture (newest file path, pid, growth, and whether P71 restarted it; if not, the reason).
2. PandaScore CS2 probe (tmux cs2probe, pid, last row time).
3. PM CS2 book recorder (pm_cs2_books.js, pid, file growth; 10:49Z read was +400,996 B in 60 s).
4. PM Dota book recorder (pm_dota_books.js, check_pmdota.sh at 68ff500e: the P63 read).
5. Goalserve capture, all four sports (pid, newest hour file per sport, growth).
6. AAA watcher (P54): pid, status-code counts so far, first and last row time; P54b and P54c results if not yet pasted.
Also report free space on the data volume and VOL2 in the same paste. No restarts or edits in this block.
Deadline: first paste within 15 minutes of the next PK arbs session.
