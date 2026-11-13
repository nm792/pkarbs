# TheSports export: markets.jsonl still ends 21:42Z 8 Nov (request, no approval needed)

The 07:25Z one-off export (aefed1cee) has topic data to 07:2xZ but `final-topics-32295b-slim/markets.jsonl.gz` still ends at 2026-11-08 21:42Z (last row ms 1794174137570). Tennis matches after that cannot be paired to Polymarket tokens, so the post-01:00Z locked tests have 0 qualifying matches.

Please, in the next export and in the 2 h timer copy: (1) write the full current spool `markets.jsonl` (all rows to now, not a clipped copy) and `log.jsonl`; (2) say in the outbox the last `ms` in each file. The diary request for 9 Nov is in thesports-diary-9nov-2026-11-09.md. Nick's approval for the timer re-fetch/rebuild fix is being asked on a card now; do not wait on it for this export.
