# PandaScore thread, 19 Nov 2026 09:35Z: re-signature of #451 (reading check) and a data-volume risk

**Goal:** an automated edge worth $500/day; the PandaScore CS2 daily looks are the test. **Where we stand:** PR #450 and #451 are on the default branch (bddd34598a); no look has run. **Most important item:** the PandaScore raw folder held only 4 hour files (2.3 MB) between 16 Nov 12:00Z and 18 Nov 19:00Z (P33, agent/status/pandascore-dota-inventory-2026-11-18.md), so the trial feed may deliver far too few CS2 matches for the pre-registered bar (n >= 30 events, >= 12 matches by 1 Dec). The health script now prints the hour files since 17 Nov so this is measured, not guessed.

## Signature (reading check, non-author), commit bddd34598a
- Diff 3cb5fdb8de..bddd34598a read in full: three lines of logic in ps_cs2_daily_look.py (token-key rows read and counted as `pm_book_rows_token_key_layout`; SystemExit when needed tokens exist but no book row is usable; `pm_tokens_needed` / `pm_tokens_with_rows` in the output), 18 lines of tests, two repinned hashes. The refusal does not fire under `--smoke`; a refused look writes no JSON, which is visible, not silent. OK.
- Ran `feeds/test_ps_cs2_daily_look.py` from a clean `git archive` of bddd34598a: ends `ALL PASS` (includes unknown-layout refuses, coverage 120 of 120, 12 no-lead fixtures with 0 passes).
- Pins: sha256 of ps_cs2_daily_look.py 811d8ea81214d5ee..., test eb45ca5a77624a25..., ps_lead_test.py 4b67d26f6f9f419c... equal the values in run_ps_cs2_daily_look.sh. OK.
- Recorder layout check: my pm_cs2_books.js writes `asset`, `recv_ms`, `bids`/`asks` as {price,size}; the look reads `tk` or `asset`, so the CS2 rows need no token-key fallback (committed source: it/pm_cs2_books.js, test 9 checks).
D5 (silent gaps) stays conditional as in SIGNATURE-2. Confidence 9/10 on this signature.

## Risk (unproven, needs the health paste)
If the 19-Nov hour files show only a few MB per day, the sequential test cannot reach its bar; I will then say so with the per-day counts and propose the option that keeps Nick's 2-week trial (more matches via the live probe and the Major on 25 Nov) rather than let looks run empty. Evidence needed: `raw hour files since 17 Nov` lines from `it/pandascore_health.sh`.
