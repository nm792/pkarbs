# IT 2026-11-22 10:20Z: PK arbs routing (R-024 server read, Mentions firelog, P99 perps crons)

1. **Goal:** find and build automated Polymarket edges toward $200-500/day, each judged on measured own-token depth (pkarbs it/00-URGENT-MENTIONS-install-firelog-R031.md).
2. **Where it stands:** the last agent commit here was P101a at 07:25:15Z (pkarbs 30f0ba45). The R-024 server read never ran. The Hermes agent has made no commit on any repo since 07:36Z (trading-test dialogue d518aefc).
3. **The item that matters most:** the agent stall. P102 (your server read) is the top open P row, but it runs only when dispatch fires again. That is in NEEDS-NICK (dialogue 5e14955f).

Routed (dialogue 5e14955f; exact blocks in trading-test dialogue/status/ROWS-22NOV.md). PK runs once an hour, one row at a time, in this order:
1. **P102:** your 04:20Z server read (it/REPLY-2026-11-22-0420Z), read-only, all 7 items, into agent/status/server-read-2026-11-22.md. It includes the PandaScore raw listing, so P99a is closed as superseded.
2. **P103:** firelog steps 1-3. Scratch goes to VOL2 tmp, not /tmp (SCRATCH RULE). Otherwise as written.
3. **P103b:** firelog health read (step 5). Hourly dispatch cannot meet "16 minutes after step 2". It runs about 1 h later.
4. **P104:** P99 perps crons, to be installed before 2026-11-22T22:30Z. I changed your cron lines in three ways: (a) analyze output goes to run-2026-11-22/analyze_<label>.txt, so it is not lost to cron mail; (b) the snap file is copied to perpsnap-out inside the cron line; (c) a VOL2 10 GB guard and nice -n 10. With these, no session is needed at run time.
5. **P100b:** gas books sanity, read-only.
6. **P104b:** read of the two Sunday runs, NOT BEFORE 2026-11-22T23:25Z. **The Monday 14:20Z read is not routed yet.** IT adds it after P104b lands.
7. **P103c:** firelog step 6, the depth backtest on Prime. /tmp is replaced by VOL2 tmp.
8. **P92b:** Mentions both-token deploy. Its VOL2 dependency has landed (61.65 GB free at 10:00:18Z, data 0efe91d7). It is queued after P103c.

**NEEDS CHUNKING:** the Goalserve restart that the Reviewer's 0808Z chase mentions is not in your 04:20Z note. If you want it, send the SHA and the exact start command as a separate row.
