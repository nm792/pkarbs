# status: tennis-books (TASK-tennis-books-2026-11-05)
state: STOPPED (HARD-STOP 2026-11-05T12:18Z)
reason: root free 4.9G < 5.0G hard-stop (ruling-disk-gate 05:25Z + Nick 04:43Z). Scope killed, data kept committed.
last commit: 6a2f3b6d 12:18Z - books split 2 parts (part1 41MB, part2 70MB; single gz 109MB >100MB GH limit), 965,778 rows. log/markets/probe .gz committed.
raw files: /root/tennis-books/2026-11-05/share/*.raw deleted per delete-after-commit ruling; raw books.jsonl (766MB) reclaimed.
df at stop: / 4.9G free / 88% used. tennis-books dir was 1.5G.
next: do NOT restart unless a new reviewer note clears disk. cricket-feeds still running separately.
last heartbeat: 2026-11-05T12:18Z UTC
