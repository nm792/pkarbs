# reply: mention-books recorder — RUNNING (11 Nov 2026, 09:30Z)

Per `agent/inbox/2026-11-11-mention-books-confirm.md`. Recorder confirmed live and PASS.

1. **RUNNING.** systemd timer `pkarbs-mentions-recorder.timer` (OnCalendar=*:0/5, Persistent=true); unit `pkarbs-mentions-recorder.service` (oneshot, MemoryMax=200M) last ran 2026-11-11 09:25:04Z, exit 0/SUCCESS. Every 5 min. Reset: `systemctl start pkarbs-mentions-recorder.service`.
2. **Test:** `python3 live/mentions/test_record_mention_books.py` → `8 of 8 checks pass`.
3. **Last run log** (journald, no run.log file; unit writes to journal):
   `{"ev": "done", "targets": 0, "books": 0, "file": "/vol2/pkarbs/mentions/books_20261111.jsonl.gz"}` (09:25:06Z). DeprecationWarning on utcnow() is cosmetic.
4. **First sample committed:** `rn1/mentions/books/books_20261111.jsonl.gz` — newest file, **1176 lines, all Kalshi, 0 Polymarket** (0 targets is normal when no new Polymarket mention market opened in the window; task PASS allows it). 149 KB, under the 5 MB hook.

Note: actual output dir is `/vol2/pkarbs/mentions` (unit ExecStart arg), not `/root/mentions/books` as in the inbox text. Daily commit at 00:50Z via `pkarbs_recorder_commit.sh mentions` → `rn1/mentions/books/`.

Status: `agent/status/mention-books.md` = RUNNING.
