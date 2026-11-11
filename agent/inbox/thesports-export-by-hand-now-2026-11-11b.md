# Run one TheSports export by hand now, with the 19:26Z fix (11 November 2026, 20:50Z)

On origin/claude/project-thread-vg2ckg the newest ts_mqtt chunk is still 1794384000000 (10:00Z) and markets.jsonl.gz is still 2,374 rows. Nothing with TheSports data has landed for over 10 hours. Tennis is one match short of its target, and the trial ends 16 November.

Please do this now, ahead of every other task:

1. Run the export by hand: build the slim export for final-topics-32295b-slim, then fetch the CURRENT origin tip, put the files on it, and push fast-forward (your 19:26Z CB15 fix, de0517c84).
2. Before committing, check `git diff --cached --stat` is NOT empty and shows ts_mqtt chunks after 1794384000000, books_mid after 10:00Z, markets.jsonl.gz, pmws.jsonl.gz and diary/tennis-2026-11-11.json. If it is empty, do not push; write the reason in agent/outbox.
3. After the push, run `git show --stat <hash> | tail -5` and check on origin that the newest ts_mqtt chunk is later than 1794384000000. Put the hash and that check in agent/outbox/thesports-export-by-hand-now-2026-11-11b.md.
4. If the push is rejected again, say so in agent/outbox with the exact error, and retry once on the fresh tip.
