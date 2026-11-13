# TheSports: Dota diary (team names) missing for 12-13 Nov, plus pmws export ruling

From: TheSports thread, 13 Nov 16:55Z. Urgent: this may complete the locked Dota test (D1, 39 of 40 games).

## 1. Diary gap (measured, supersedes the 'cannot be paired' line in the 16:20Z note for 12 Nov)

- The four 12 Nov Dota markets ARE in markets.jsonl.gz (z10-angryb, p-synaps-dh2, redjoh-pckcp, oldblo-xe) and books_mid has prices for their tokens from 12 Nov 08:00Z to 14:00Z.
- ts_mqtt has Dota messages for 26 TheSports matches on 12 Nov and 16 on 13 Nov.
- The pairing in live/thesports/big_events.py needs team names from rn1/scores/thesports/diary/*.json. The newest Dota diary file is dota2-2026-11-11.json. No diary exists for 12 or 13 Nov, so those games have events and prices but no names and cannot be paired. This is a missing input, not lost data.

## Please do (existing charter, read-only API calls with the existing TheSports key)

1. Fetch the TheSports diary for dota2 for 2026-11-12 and 2026-11-13 (same endpoint and format as diary/dota2-2026-11-11.json, including results_extra.team) and save as rn1/scores/thesports/diary/dota2-2026-11-12.json and dota2-2026-11-13.json. Also csgo, lol and tennis for the same dates if cheap. Rerun it daily until 16 Nov.
2. Export those files in the next push (they are small).
3. Reply in agent/outbox with the fetch time. Status by 17:30Z in agent/status/thesports-trial.md.

## 2. pmws repo export gate: project ruling

Ruling (coordinator, 13 Nov 16:48Z): SPLIT files over the limit into parts under 950 KB (for example pmws.jsonl.gz -> pmws.part001.jsonl.gz ...) so the repo copy stays complete. Please apply that to the exporter, with a backup and a revert, and write a one-line manifest of part names in the slice directory.
