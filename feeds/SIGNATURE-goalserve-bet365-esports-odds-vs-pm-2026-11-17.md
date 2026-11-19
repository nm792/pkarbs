# Signature record: Goalserve esports odds vs Polymarket rule-to-code table

Table: feeds/RULE-TO-CODE-goalserve-bet365-esports-odds-vs-pm-2026-11-17.md (v2). Code and amendments at commit c82acb04af6f64c1b281c20cf71331ba3c7b7b87 (PR #395): feeds/goalserve_odds_vs_pm.py, feeds/test_goalserve_odds_vs_pm.py, feeds/AMENDMENT-goalserve-odds-prereg-2026-11-17.md (items 1 to 10).

Signed by: the "Audit CS2 model" project thread (not the author), 17 Nov 2026 about 11:01Z, as relayed to the Goalserve thread. Source of record: that thread's v2 sign-off file, reviews/SIGNOFF-goalserve-odds-vs-pm-rule-to-code-2026-11-17.md (details at its end). This file only records the relay; the checker's own file is the primary record.

Result: all 21 rows MATCH. Row 21 (cells per game, not pooled across CS2, Dota and LoL) was added by the checker on 17 Nov 10:53Z. Row 5 was found DIFFERS at 10:53Z (market names) and re-checked MATCH after PR #395: market_kind() maps "Home/Away" and "Home/Away (map N)" correctly and excludes "Odd/Even", "Map-match" and "Round Winner". Self test re-run by the checker: ALL PASS, false pass 0 of 20 and 0 of 20.

Conditions that travel with any result:
1. State "bookmaker not identified (bm empty; vendor docs say bet365)". The Pinnacle absence covers 3 files only (17 Nov 08 to 10Z).
2. Game cells come from the info.league prefix; only dota2 is confirmed. Print league_prefixes_seen.
3. The map-N alignment with Polymarket is assumed.
4. The real run needs the 13 to 16 Nov files, a true --clock-note and --poll-log, the real-series 5, 15 and 25 s plant in the same report, and the power limit (about 25 s at n of about 120) stated beside each verdict.
5. An independent audit is done before anything is relayed.

Status of any result until condition 5 is met: UNCHECKED.
