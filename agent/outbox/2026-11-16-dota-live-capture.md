# Dota live capture — update at 2026-11-16 10:23Z

- Capture is active as `dotacap-2026-11-16.service` (Node PID 1700948; unit MainPID 1700947), started 06:26:55Z; 400 MiB cap and zero swap. Output advanced through 10:22Z.
- The scheduled publisher failed at 09:00Z, 09:30Z, and 10:00Z with storage-box authentication errors. Manual execution of the existing approved publisher at 10:22Z succeeded: seven complete gzip deltas were transferred and checksum-verified, then the manifest was pushed. Row counts: books 5,210; league_games 1,008; opendota_live 175; realtime 7,614; rt_polls 18,604; sportsws 332; capture log 47.
- Manifest `manifest/dotacap-2026-11-16.tsv` has 42 entries; manifest commit `4d76d5dbc8bf496c7c34d1c07f88cbec6e42a641`. Raw data remains on `<box>`, not Git.
- Final coverage/pass-fail is not yet established. Capture continues through 17 Nov 20:30Z.
