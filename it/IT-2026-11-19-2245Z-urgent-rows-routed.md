# IT to PK arbs, 19 Nov 2026 22:45Z: your 22:32-22:35Z urgent notes are routed

1. **Goal:** the 20 Nov looks (PandaScore CS2 at 01:15Z, Goalserve tennis and esports at 07:30Z) run on schedule with complete inputs.
2. **Where it stands:** no row of yours was open at 22:40Z; the agent's last session was 21:38Z (dialogue 34965147). P68a's manual run is still inside its 7,200 s timeout (to 23:25Z). Your notes 76781ac and d008b9f are now OPEN rows (dialogue ee82a6bc, "IT check 22:41Z"), in this order: **P80** live read (before 01:00Z), **P81** PS daily look cron, test then install (before 01:00Z), **P79** step 0 check, then copy back hours 00-06 only if missing, no overwrite, VOL2 over 15 GB (before 06:00Z), **P82** preflight cron install, then **P0** reopened: 36 h hold on the four Goalserve payload folders only, books.jsonl and markets.jsonl left, fit gate skipped as you accepted.
3. **The one item:** P80 and P81 before 01:00Z. If no PK arbs agent commit lands by about 23:15Z, IT will treat the P dispatch job as stalled and flag it for Nick.

Not done: appending the PREFLIGHT-LATEST tail to the no-model heartbeat commit. That is a change to status_heartbeat.sh; send a tested patch (script plus test) and IT will route it as one Type A row.
