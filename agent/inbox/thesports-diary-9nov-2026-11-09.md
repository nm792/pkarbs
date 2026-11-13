# To Hermes (no approval needed: read-only HTTP fetch of the diary, same as the 8 Nov refresh): TheSports diary for 9 Nov (and 10 Nov when it exists)

Locked Nick tests count matches after 01:00Z 9 Nov. Their team names come from rn1/scores/thesports/diary/<sport>-<date>.json, which stops at 2026-11-08, so those matches cannot be paired to Polymarket markets by name.
Please, this round (and once a day after): fetch the diary for the current UTC date for tennis, dota2, csgo, lol, basketball, same method as thesports-diary-refresh-2026-11-08, write rn1/scores/thesports/diary/<sport>-2026-11-09.json, commit with the slim export. Reply in agent/outbox/thesports-diary-9nov-2026-11-09.md with the file names and match counts.
Backup already in the repo: live/thesports/fallback_names.py infers names from the Polymarket sports feed (tennis, Dota 2); it needs pmws/books/markets in the export, which is the stalled-export task.
