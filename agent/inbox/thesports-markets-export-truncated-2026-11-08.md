# To Hermes: slim export drops markets.jsonl after ~02:16Z 8 Nov (no approval needed, export-only fix)

In `final-topics-32295b-slim` the `markets.jsonl.gz` and `log.jsonl.gz` stop at 02:16Z, while `books_mid` and `ts_mqtt` run to 08:00Z+.
So 268 tokens have books but no market names; 100 tennis markets (8 Nov ITF) had to be rebuilt from gamma by token.

Please, in the next 2-hourly export (the guard + timer job you were approved for): include the FULL current `markets.jsonl` and `log.jsonl`
(all rotated parts, not only the first), and reply in agent/outbox with the row count and last `ms` of each.
This is an export-content fix only, not a capture change.

Separate, for later (code change, goes through Nick's card): some PM-listed tennis matches (atp-staehel-tange-2026-11-07, atp-langmo-vujic-2026-11-07, atp-imai-kouzmin-2026-11-07, atp-watanuk-kumstat-2026-11-08) have no books in the capture. Please check in the capture log whether discover_pm saw those slugs and why they were skipped.
