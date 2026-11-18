# IT to PK arbs, 18 Nov 2026 20:10Z: P34 amended, P35 recorder and N2 routed, CS2 and PandaScore-hours returned

1. **Goal.** Checked PandaScore and Goalserve lead results (STANDARD v1) for Nick, each Polymarket token priced from its own book (SETTLED A1).
2. **Where it stands.** dialogue/OPEN.md at IT check 20:10Z (trading-test dialogue 14566621): P34 is the one open row; no agent commit on P34 since routing at 19:40Z, and no agent output on P30 since 18:41Z. Last agent model commit 19:31Z (P33, pkarbs ebc30b60). Data disk free 21.4 GB at 20:00Z (dialogue/status/DISK.tsv).
3. **The item that matters most: one agent session now runs P34, P35, P30 in that order** (3 items per session). Rows are chained (`waiting: after ...`) rather than all `open`, because every open row wakes the paid agent (budget nearly gone). Nick's 20:00Z readout will be late; if L is not posted by 21:30Z the agent is told to say so.

## Routed
- **P34 amended** (your 19:55Z reply 96943c66): the symlink is replaced by `feeds/dotacap_books_adapter.py` (3a9149cc) writing into the scratch PM dir; rows_in/rows_out/dropped are pasted; step C's `asset` row count must equal rows_out, else stop.
- **P35 new** (your 20:00Z reply 4daaf741): starts `feeds/pm_dota_books.js` (a7a2e761) as you wrote, with three IT changes: (a) the script is copied to `$O` and run from there, because P30's export does `rm -rf $X`; (b) END = 2026-11-20T09:30:00Z (the script's own 2nd argument) so it stops before P17b's 15 GB free check at 10:00Z; extend it with a new note giving an MB/h budget; (c) start only if 20 GB or more is free. The 15-min check is an exact one-liner: conds seen and conds with both tokens, line counts, log tail, df.
- **P30, P31, P32** unchanged; now `waiting: after P35 / P30 / P31`.
- **P36 = your chunk N2** (c9beeb3c, squash 02a4838a), after P32, as written.

## NEEDS CHUNKING (not routed)
1. P34 extra questions a) and b) (second `--ps`/PM store for 13-15 Nov; where the 13-16 Nov PandaScore hours are): open-ended searches. Name exact paths to `ls -l`/`du -sb`.
2. P34 c) and 20:00Z note a)-c) (PandaScore hourly files, socket per live match, conditional restart of `ll_capture.py`): no exact commands; the restart is conditional on a judgement. Send exact read-only commands (e.g. `ls -l` of named dirs, a named log path with a grep pattern), and a separate restart row with its gate.
3. P35 hourly gzip and storage-box copy: give the exact cron or command lines (paths, schedule) as a separate chunk.
4. CS2 tonight run (#422, late note 58adb456) and CS2 smoke: still returned (IT 19:10Z note): name the exact `--ps` and `--pm` dirs and the full command lines for steps 1, 3a, 3b and 4.
5. CS2 PM token coverage (228505cf, c8282b46): point 1 has no command; N2 (P36) may already answer it per sport for `final-topics-32295b`. Points 2-3 (find the recorder, change it to both tokens) are code work: they come back to you. Send a tested recorder or patch plus an exact start line, like P35.

Confidence 8/10 that P35's both-token count works on the script's row layout (read from a7a2e761 lines 5 and 44; not run).
