# Request to Hermes (2026-11-08T02:15Z): arm the standing 2 h TheSports export, verify capture still running

Nick approved the restart (00:00Z) and the record-keeping standing instruction ("keep the records") covers the export; this is routine, no new consent needed. Read-only, no orders, delete nothing, no credentials in git.
1. Verify `final-topics-32295b` is still being written (single instance; row counts per topic now vs 01:00Z).
2. Arm the recurring slim export + commit for `final-topics-32295b` every 2 h (same layout as `final-topics-32295-slim`), and commit the first one now (00:21Z to now). If a new job is needed, write it small and say so.
3. Also commit the 13:15Z-14:00Z stretch of the old chunk `final-topics-32295` if it is not covered by `slim-1102-32295` or `final-topics-32295-slim` (check the boundary; tell me if it is already covered).
Reply in `agent/outbox/thesports-arm-export-2026-11-08.md`.
