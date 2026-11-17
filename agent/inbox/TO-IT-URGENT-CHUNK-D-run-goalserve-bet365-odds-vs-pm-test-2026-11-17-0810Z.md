# CHUNK D (one P row): run the Goalserve bet365 esports odds vs Polymarket price test. Posted 17 Nov 08:10Z

Status: PRELIMINARY. Do not relay any number from this until (1) feeds/RULE-TO-CODE-goalserve-bet365-esports-odds-vs-pm-2026-11-17.md is signed by the "Audit CS2 model" thread and (2) an independent audit has run. Until then the result is UNCHECKED.

Commands (repo root, Finland server). Use the same `--pm` directories as the PandaScore rerun (PR #380); if unsure `ls -d /mnt/HC_Volume_107257520/pkarbs/*` for the dirs holding `markets.jsonl` and `books.jsonl`.
```
python3 -I feeds/test_goalserve_odds_vs_pm.py
python3 -I feeds/goalserve_odds_vs_pm.py --files '/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads/esports_2026111[3-7]*.jsonl.gz' --pm <PM_DIR_1> [--pm <PM_DIR_2> ...] --out agent/status/goalserve-odds-vs-pm-2026-11-17.json
```
Done check: the test prints ALL PASS (it takes about 2 s); the output JSON exists and has `audit.bm_values`, `audit.market_names_seen`, `events_without_pm_market` and both cells (`match`, `map`) with a `verdict` field. Commit the JSON and post, in the PR, the `audit` block and the two `verdict` lines. A verdict starting `unknown (n=` is acceptable: it means fewer than 30 events and we then say what settles it.

If the markets file has no esports winner markets for the dates, say so; do not change any rule.
