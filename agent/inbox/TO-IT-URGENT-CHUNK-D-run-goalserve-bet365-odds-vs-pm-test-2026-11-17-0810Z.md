# CHUNK D (one P row): run the Goalserve bet365 esports odds vs Polymarket price test (v2). Updated 17 Nov 08:00Z

Status: PRELIMINARY. Do not relay any number from this until (1) feeds/RULE-TO-CODE-goalserve-bet365-esports-odds-vs-pm-2026-11-17.md (v2) is signed by the "Audit CS2 model" thread and (2) an independent audit has run. Until then the result is UNCHECKED. Code changed since v1: the command now needs `--poll-log` and `--clock-note`.

Commands (repo root, Finland server). Use the same `--pm` directories as the PandaScore rerun (PR #380); if unsure `ls -d /mnt/HC_Volume_107257520/pkarbs/*` for the dirs holding `markets.jsonl` and `books.jsonl`.
```
python3 -I feeds/test_goalserve_odds_vs_pm.py          # about 100 s, must print ALL PASS
python3 -I feeds/goalserve_odds_vs_pm.py --files '/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads/esports_2026111[3-7]*.jsonl.gz' --pm <PM_DIR_1> [--pm <PM_DIR_2> ...] --poll-log '/mnt/HC_Volume_107257520/pkarbs/goalserve/goalserve_2026111*.jsonl' --clock-note '<PM recorder host>, <Goalserve capture host>, <same chrony clock yes/no>' --out agent/status/goalserve-odds-vs-pm-2026-11-17.json
```
Done check: the test prints ALL PASS; the output JSON exists with `poll_interval_measured` (numbers, not 'NOT MEASURED'), `clock_note`, `drops`, `audit.bm_values`, `audit.market_names_excluded`, a `match_list`, and one entry per cell in `cells` (title|bm|kind) each with a `verdict`. Commit the JSON and post, in the PR, the `drops`, `poll_interval_measured` and every cell's `verdict` line. A verdict starting `unknown` is acceptable: it means too few events or placebo onsets, and we then say what settles it.

If the markets file has no esports winner markets for the dates, say so; do not change any rule.
