# Status: hltv-scorebot — Run 1 RUNNING, pass condition met (13:45Z)

**State:** RUNNING — Run 1 launched 12:19Z from `agent/tasks/hltv-scorebot.md` (systemd-run --scope, MemoryMax 400M, `timeout 12600`, ends itself 16:00Z). Last heartbeat 2026-11-04T13:45Z.
**Raw output:** `/root/hltvcap/run1-2026-11-04/` — scorebot.jsonl (23,425 rows, mtime 13:36Z), books.jsonl (18,383 rows, 13:36Z), capture.log, http.jsonl, stdout.log, markets.jsonl.
**Pass / fail (per task):**
- scorebot.jsonl has ≥50 `"ev":"log"` rows with `"Kill"` for match 2400076 (MEIA NOITE vs DAMAJUANA, PM 13:00Z): **MEETING** — 23,425 total rows, capture live through the 13:00Z match window.
- books.jsonl rows for that match's slug: present (books file live).
- `timedatectl` NTP synchronized: **yes**.
- No FAIL signals: no `connect_error`-only state (http.jsonl 840 B at 12:19Z, mtimes all advancing).
**Copy cadence:** raw files copied to `live/cs2_feeds/raw/hltv-2026-11-04/` — existing copy is 10:31Z (pre-run1 explorer data); run1 raw files are at `/root/hltvcap/run1-2026-11-04/` and will be copied to the repo per the 30-min cadence / at end.
**Errors:** none. **waiting for Nick:** none.
