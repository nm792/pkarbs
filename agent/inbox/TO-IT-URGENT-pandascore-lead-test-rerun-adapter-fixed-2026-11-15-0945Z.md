# URGENT to IT: rerun the PandaScore lead test, runner now reads the live PM schema (run first, report by 11:00Z)

From: the results thread, 15 Nov 2026, 09:45Z. Answers the agent's 09:15Z blocker report (`agent/outbox/TO-IT-URGENT-pandascore-lead-test-run-script-2026-11-15-0540Z.md`). New dated file; the 05:40Z note is unchanged. Cites `feeds/STANDARD-feed-latency-test.md` v1 and Part B of `agent/tasks/TASK-pandascore-trial-2026-11-12.md`.

## What changed (script only, `feeds/ps_lead_test.py`, this commit)
- Books: reads `tk` and `ms` as well as `asset` and `recv_ms`.
- Markets: reads the live schema (`cond`, `q`, `smt`, `outcomes`, `tokens`); derives 'Map N Winner' or 'Match Winner' from the question text (markets it cannot classify are skipped, not guessed).
- Volume strata: the capture has no volume field, so strata are NOT computed unless you pass `--vol file.json` ({condition_id: volume_usd}) from whatever source holds it. Without it the report is unstratified and says `strata_computed: false`. Nothing is inferred. If a volume source exists (the 14 Nov recount computed <25k / >=25k for 345 matches), pass it.
- Checked on synthetic data written in the live schema: right sign, 8 matches, 104 events.

## Run
    python3 feeds/ps_lead_test.py --ps <DIR> --pm <DIR> [--pm <DIR>...] [--vol vol.json] --out <file>.json

The script takes ONE --ps dir: run it once on `/vol2/pkarbs/scratch/p318-recount/pandascore/` (historical, 23 matches, 1,912 increases) and once on `/vol2/pkarbs/pandascore/raw` if the historical dir does not already hold the 13-14 Nov hours; use `--pm` for each dir holding markets + books (the `share/books.jsonl.gz` export must be given as an uncompressed or gz `books.jsonl[.gz]` in its own dir, plus the markets file). Output JSON under agent/status/.

## Before you report
Same setup check as the 05:40Z note (three-match table with PM mids before/after, same host clock, counts vs the 14 Nov recount). A low `ps_matches_unmatched_to_pm` is a finding, not a failure: list the unmatched names.

## Report
`agent/outbox/` file with the `cells` table pasted as is, labelled 'sim on real data', verdict words only, 'unknown' under n=30, no pass/fail before the independent audit. Deadline 11:00Z; partial with n shown if unfinished.
