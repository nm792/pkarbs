# outbox: rugby-script-changes-approved-2026-11-07 (approved code applied)

Nick approved both changes 15:04:27Z. The patch is merged to this branch. Verified on origin:
- #186 (f4ad8719) CLOB read: lists/dicts/PONG handled, unparsable text recorded, PING every 10s, retries >3.
- #187 (ce3166ab) single-instance flock guard + log no longer truncated by relaunch; summariser reads AB_clob_rest.jsonl.
Per note: AB left running on OLD code with REST fallback (no restart mid-match), Windows C/D 8 Nov start on new code.
OPEN: the 5-min safe-point CLOB probe (read_clob → rugby/probe_clob.jsonl, first-message type + rows/min) has NOT been run/recorded yet. It is the remaining verification of the stream fix; running it is a bounded single-process read-only probe. Status: applied, probe outstanding.
