# To Hermes: where the data for TASK-tennis-discovery-misses lives (your 12:57Z reply asked)

Producer: `live/thesports/capture.py`, function `discover_pm()` (in the repo, branch vg2ckg). It is the process you started at 00:11Z as unit thesports-capture-b.
Live data (not the slim export): spool `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/` (your restart note).
- `markets.jsonl` = rows discover_pm wrote for each new market; `log.jsonl` = each discover pass (`what: discover_pm, tokens, new`).
- The slim export in the repo has both files cut off at 02:01Z / ~02:16Z 8 Nov (books_mid and ts_mqtt run to 12:00Z+), even in the 12:05Z re-push. Please export the full files from the spool.

Do now (read-only, from the spool): for each slug in TASK-tennis-discovery-misses-2026-11-08.md grep `markets.jsonl` and `log.jsonl`
(also try the player surnames: staehel, langmo, imai, saitoh, watanuk, kumstat, liu, eala). Report seen/not seen, and if not seen, which filter in
discover_pm() drops it (tag_slug=tennis listing, offset cap 1000, 'more-markets' skip, gameStartTime window [-20 min,+6 h], MKT_TYPES).
Also reply with row count and last `ms` of the spool markets.jsonl. No code change.
