# P71 — PandaScore raw capture restart (19 Nov 2026)

- The approved recorder was not running: no matching systemd unit, crontab entry, tmux session, or `ll_capture.py` process was found. The existing raw directory's newest file was `pandascore_2026111612.jsonl.gz`, last modified 16 Nov 13:00 UTC. No recorder log was available to confirm why it stopped; the VOL2-floor exit is plausible but unverified.
- Read-only preflight matched the expected source SHA-256 prefix `be437551ef87`; the reviewer-supplied floor wrapper passed all 4 checks. Started the wrapper with `PS_FLOOR_GB=10` in tmux session `pscap2` at approximately 11:20 UTC.
- Live verification: PID 3323067 was running; its log showed connected PandaScore feeds. New output `pandascore_2026111911.jsonl.gz` appeared at 11:22 UTC and grew from 13,249 to 18,130 bytes over 60 seconds. This confirms capture resumed and is writing.
- No original source file was edited. The recorder is using the reviewer-approved wrapper and 10 GB floor; confirm any later floor/config change through the reviewer.

## APPROVALS NEEDED:
None.

## RESULT
- P71 completed: capture restarted and new raw output growth verified.

## DATA
- Live output: `pandascore/raw/pandascore_2026111911.jsonl.gz`; recorder log: `/tmp/pscap2.log`.
- Project status details: `agent/status/pandascore.md`, section `P71 PandaScore capture restart`.

## OPEN / NOT VERIFIED
- Original stop cause is not confirmed because the previous tmux session and recorder log were absent.

Count: notes run 1, outstanding 0, PENDING open 0
