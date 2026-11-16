# Dota 2 live capture — update 15:09Z, 16 Nov

- Capture is still active (timeout PID 1700947; Node PID 1700948). At 15:09Z all six JSONL streams were fresh and parsed with zero malformed rows: books 44,100; league_games 4,598; opendota_live 791; realtime 41,136; rt_polls 92,814; sportsws 2,579.
- Scheduled publishing still fails at storage-box authentication (15:00Z attempt, rsync exit 12/255). The existing publisher was run at 15:09Z and transferred/checksum-verified seven complete gzip deltas. All 63 manifest chunks (201,481 rows total) were confirmed present on the storage box; manifest commit: `991164d52b838ec27ab8a6352ed16914272796fe`.
- No code/config/crontab/service changes; no credential values read or changed. Later scheduled transfers remain unverified. Final capture coverage remains open until 17 Nov 20:30Z.
- Current details: `agent/status/dota-live-capture-2026-11-16.md`; manifest: `manifest/dotacap-2026-11-16.tsv`.
