# Dota live capture — update at 2026-11-16 08:55Z

## Result
- Capture remains active as `dotacap-2026-11-16.service`: Node PID 1700948 (unit MainPID 1700947), started 06:26:55Z, 400 MiB memory cap / zero swap; sampled memory about 62 MiB. Output was still growing at 08:54Z.
- The approved 30-minute publisher cron and final 17 Nov 20:35Z copy/removal line remain installed. I ran the publisher at 08:54Z: seven complete gzip deltas were checksum-verified on the storage box, and the updated manifest was pushed. The new chunks contain books 99 rows, league_games 198, opendota_live 34, realtime 1,687, rt_polls 3,633, sportsws 8, and capture.log 12. No raw data was committed.
- Manifest path `manifest/dotacap-2026-11-16.tsv` now has 35 entries. Latest manifest commit: `1ea402eb854a6e00e0b17cd02b9df26f6bf32fd7`.
- Final coverage/pass-fail is not established; the capture continues through 17 Nov 20:30Z.

## Publisher and revert
- Publisher: `agent/tasks/dota-live-capture-2026-11-16-publish.py`; approved implementation unchanged. Runtime state/chunks remain on VOL2.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected. The final line is scheduled to remove both publisher entries after the last copy.
