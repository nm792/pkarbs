# P34 — Dota PandaScore lead run (P38 rerun, 18 Nov)

State: partial; reader fix handled malformed/live-written gzip as PARTIAL FILE. Outputs exist, but Dota verdict remains unchecked because only 2 matches were available (<12).

- Export commit: `c45a5bc60e2e88d685ee12b9572047c07dc46e37` (required fix present).
- Reused PM inputs: markets 42 lines; books 100676 lines. Planted tests: six PASS; exit 0.
- Lead: exit 0. `ps_events_total=302`, `ps_matches_seen=10`, `ps_matches_unmatched_to_pm=7`; strata not computed. Dota map/match: n_events=74, n_with_onset=0, onset share=0.0, n_matches=2 (<12, unknown), after-feed denominator unavailable (`pct_price_after_feed=null`), verdict `no lead (needs audit)` (not a conclusive verdict).
- Audit: exit 0. Dota map/match all-events: n_events=74, n_matches=2, onset share=0.0, after-feed denominator unavailable (`null`), `no lead reproduced` (insufficient matches); isolated >=60s: 4 events, 2 matches, `unknown (n<30)`. Clock note: feed uses `recv_ns` on capture host; PM price uses book-row `ms` on same host; exchange `sent` is logged only.
- PARTIAL FILE (both runs): `pandascore_2026111612.jsonl.gz` — invalid block type; `pandascore_2026111821.jsonl.gz` — compressed file ended before end-of-stream (the live writer was still appending). These files were read-only and not repaired. At 21:52Z listing: 2026111612 (216915 bytes), 2026111820 (870868 bytes), 2026111821 (111608 bytes; live-growing). The 21-file size changed during this session, so its partial warning is expected; no rerun against it was attempted.
- `systemd-run` exit codes: lead 0; audit 0. No Dota verdict is claimed.

Evidence: `agent/status/pandascore-lead-test-2026-11-18-dota.json`, `agent/status/pandascore-lead-test-2026-11-18-dota-audit.json`; logs `agent/status/pandascore-lead-test-2026-11-18-dota-run.txt` and `agent/status/pandascore-lead-test-2026-11-18-dota-audit.txt`.
