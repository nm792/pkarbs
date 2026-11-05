# status: tennis-books (TASK-tennis-books-2026-11-05, relaunch per 12:40Z ruling)
state: RUNNING (RESTARTED 2026-11-05T12:33Z on HC volume)
relaunch basis: ruling 12:40Z step 4 — HC >= 20 GB free (21G). Writing to /mnt/HC_Volume_107247271/tennis-books (NOT /).
scoped systemd unit: tennis-books-hc, MemoryMax 500M, MemorySwapMax 0, timeout 32280s (~21:30Z stop so 22:00Z capture starts clean).
out dir: /mnt/HC_Volume_107247271/tennis-books/2026-11-05/{books,markets,probe,log}.jsonl + share/
first rows: books.jsonl growing, probe rows present incl clob_rtt (median seen), markets listing.
stop limits adapted per ruling: kill+keep committed if dir > 2 GB OR HC free < 10 GB OR / free < 6 GB.
hourly: gzip share/*.jsonl -> commit rn1/scores/tennis/books-2026-11-05/ (from HC dir), then delete committed raw.
df at relaunch: / 7.1G free 81% | HC 21G free 57%.
last heartbeat: 2026-11-05T12:34Z UTC
