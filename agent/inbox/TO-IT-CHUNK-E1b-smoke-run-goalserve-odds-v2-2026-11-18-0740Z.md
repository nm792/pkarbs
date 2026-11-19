# CHUNK E1b: smoke run (replaces the run line of chunk E1, which exited 1 with "look K=-1 ... outside 1..20" because 16 Nov files are before the first look day). Read-only. 18 Nov 2026 07:40Z

**1. Goal.** First daily Goalserve odds look on 19 Nov ~01:00Z; the smoke proves the code does not crash on the real file and Polymarket formats.
**2. Position.** Self test ALL PASS with the new `--smoke` flag. Real runs never use the flag. Do not read or post any cell or verdict.
**3. One item.** Same as E1 (agent/inbox/TO-IT-CHUNK-E1-smoke-run-goalserve-odds-v2-2026-11-17-2230Z.md) with the clean export from it/REPLY-2026-11-18-URGENT-goalserve-ruling-clean-tree-no-stash.md instead of `git pull`, and with `--smoke` added to the run line:
`... python3 -I feeds/goalserve_odds_vs_pm_v2.py --smoke --files "$T/gs/esports_20261116*.jsonl.gz" --pm $V/pkarbs/thesports/final-topics-32295b --poll-log "$V/pkarbs/goalserve/goalserve_2026111*.jsonl" --clock-note "smoke run only, result not read" --out $S/smoke.json > $S/smoke.log 2>&1`
Also print `smoke_not_a_result` from the JSON. Post under `## E1b smoke (18 Nov)`.
**Done check:** `ALL PASS`, `smoke exit 0`, `NO_TRACEBACK`, `files` > 0, `smoke_not_a_result True`.
