# TheSports bundle: Polymarket side stale since 12 Nov (priority, blocks Dota locked test D1)

From: TheSports thread, 13 Nov 16:20Z. Measured in export 64a2a79757 (13 Nov 13:08Z build, files in rn1/scores/thesports/final-topics-32295b-slim):

- markets.jsonl.gz: newest row 12 Nov 12:13Z (cs2, tennis), dota2 11:42Z, lol 05:41Z. Rows added per day: 8 Nov 959, 9 Nov 626, 10 Nov 647, 11 Nov 558, 12 Nov 263, 13 Nov 0. So PM market registration for the TheSports capture stopped about 12 Nov 12:13Z for ALL sports.
- pmws.jsonl.gz: newest row 12 Nov 05:36Z (file mtime 12 Nov 08:31Z). The PM websocket recorder in the bundle stopped.
- books_mid and ts_mqtt are still current (to 13 Nov 12:00Z), and TheSports Dota data is flowing (about 93k msgs on 12 Nov, 27k on 13 Nov to 12:00Z).
- Effect: Dota games after 12 Nov 12:13Z cannot be paired to a Polymarket market, so the locked Dota test D1 stays at 39 of 40 games although live Dota matches exist. Also the 4 Dota matches registered on 12 Nov (z10-angryb, p-synaps, redjoh-pckcp, oldblo-xe) did not pair.

## Please do, in this order
1. Find out why market registration and pmws stopped at 12 Nov ~05:36Z / 12:13Z (VOL2 full on 12 Nov? the 06:12Z IT-check wipe on 13 Nov? process died?) and restart both within the existing charter (no new collector). Reply in agent/outbox with the cause and the restart time.
2. After restart, confirm in the next export that markets.jsonl.gz has new rows for Dota, tennis and CS2 and that pmws.jsonl.gz is advancing.
3. If the registered 12 Nov Dota markets can be re-paired from books_mid already on disk, say so (do not change any rule; the locked test D1 is unchanged and needs 40 paired games).

Deadline: status by 17:00Z in agent/status/thesports-trial.md. The TheSports trial ends 16 Nov.
