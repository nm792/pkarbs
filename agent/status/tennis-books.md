# status: tennis-books (TASK-tennis-books-2026-11-05, note 04:10Z)
state: READY awaiting disk headroom (Nick Go 04:43Z honored; root 80% / 7.36G free < 10G gate)
last_heartbeat: 2026-11-05T05:02Z UTC
- Task: 1 s Polytope tennis order-book logger + OddsPapi latency probe, 12 h. Script exists: `live/tennis_books/capture.py`.
- NOT started: not running (pgrep empty), no /root/tennis-books dir. New collector at time of disk-freeze standing rule (root / 80%, 7.4 G free); daemon start held for Nick's explicit Go.
- On Go: `cd <repo> && git pull; mkdir -p /root/tennis-books/2026-11-05; systemd-run --scope -p MemoryMax=500M timeout 43500 python3 live/tennis_books/capture.py /root/tennis-books/2026-11-05 12 --share /root/tennis-books/2026-11-05/share`; hourly gzip+commit to `rn1/scores/tennis/books-2026-11-05/`; status updates; delete /root/tennis-books after final commit.
- Revert: kill the systemd scope, remove /root/tennis-books.
errors: none
output_paths: (none yet)
