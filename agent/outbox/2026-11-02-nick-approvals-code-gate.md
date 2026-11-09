# Outbox: nick-approvals-code-gate read (2 Nov 2026)

Read and applied both quoted approvals:

1. Rugbyrama 15 s poll as a fourth async task in capture.py (approved 15:44:04Z) — implemented, tested locally (protocol rule 1, 25/25 gates), committed. See outbox/2026-11-02-fix-poll-and-status.md for the test detail.
2. Window AB as one 5 h process (approved 15:50:19Z, low CPU priority nice -n 19, 600M cap, poll intervals unchanged) — reflected in the status harness line and the Next-window line. Run order: AB (7 Nov 13:15-18:05Z) then D then C, one at a time.

Fixture conflict handled per the coordinator (2 Nov 15:47Z): window A covers Toulouse v Clermont 13:30 UTC, window D covers Vannes v Bordeaux 14:00 UTC on 8 Nov. Windows now AB/D/C as above.

No further action gated on me.
