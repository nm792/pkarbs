APPROVALS NEEDED:
- None. Read-only readback.

RESULT
- **URGENT — missing raw hours:** requested post-restart closed-hour files for 13:00–15:00Z are absent. The 12:00Z gzip is present but fails `gzip -t` (invalid compressed data); no complete rows can be certified from that file. The full interval is incomplete.
- Available closed hours: 16:00Z — 2,511 status rows across 9 matches; 17:00Z — 2,297 rows across 7 matches. Measured directly from the gzip files.
- Close errors since restart at 12:25:21Z: 0, including code 4004: 0. Available raw data has 24 receive gaps >60s across 9 matches; maximum 2,735.8s (match 1791808). None contains a logged close_error/reconnect event. Gap coverage is limited to available 16:00–18:00 raw data, not missing hours.
- Since restart: 17 socket tasks started and 17 connected by the event-log snapshot; 12 ended with normal server close code 1000 (match finished); 5 sockets remained established at the live process check. No early/error close was logged.
- No BLAST-specific book/event input was identified in inspected capture paths by 18:18Z; the 20:00Z cutoff had not arrived, so the requested BLAST recount is not yet measurable.

DATA
- Prime: `/mnt/HC_Volume_107257520/pkarbs/pandascore/raw/` (hour files); `/mnt/HC_Volume_107257520/pkarbs/pandascore/events.jsonl.gz` (lifecycle events).
- Read-only counts; no process, files, or data changed.

OPEN / NOT VERIFIED
- Full 12:25:21Z–20:00Z readback, including missing 13:00–15:00Z hours, 12:00Z corruption, and any BLAST recount at the 20:00Z cutoff.

Count: notes run 1, outstanding 0, PENDING open 0
