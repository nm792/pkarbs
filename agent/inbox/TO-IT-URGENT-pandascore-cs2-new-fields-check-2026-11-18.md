# URGENT, for Prime Bot / IT: PandaScore new CS2 fields (18 Nov 2026)

Due: reply in agent/outbox by 18 Nov 12:00Z. This is read-only work on files we already hold, plus one doc download. No restart, no code change unless step 4 says it is needed.

Background: PandaScore (via Nick, 18 Nov 08:19Z) says CS2 now carries player economy, weapons and HP, and a new "latency" field showing the source/delay of each data point (round score is typically fastest, kills slower). Updated docs: https://developers.pandascore.co/docs/low-latency-feed-counter-strike . That host is not reachable from my session, so I have not seen the field names. The trial is kept open. CS2 Major starts 25 Nov. Test plan: feeds/PLAN-pandascore-cs2-new-fields-2026-11-18.md (cites STANDARD v1).

Our capture (live/pandascore/ll_capture.py) writes the whole parsed message as `payload` plus `available_fields`, so new keys should already be stored if the feed sends them without an opt-in. Please confirm that on real files, not from the code.

1. Docs: download the page above (and any linked changelog) with the box's network and commit it as feeds/PandaScore-low-latency-feed-counter-strike-2026-11-18.md. Say if the host is blocked.
2. Keys: from closed gzip hours since 13 Nov (run `gzip -t` first, skip BADGZ and say which), list for CS2 (`slug` cs-go) every distinct top-level key and every distinct key under `current_round`, `home_team`, `away_team` and `players[]`, with first and last `recv_ns` seen and message count. Flag any key containing money, equipment, weapon, hp, health, armor, latency, source.
3. `available_fields`: list every distinct value seen for CS2 with message counts per UTC date. Say whether the new items appear, and from when.
4. Latency field: if present, give its location, type, the distinct values and how they vary by message (per message, per data point, per source). Give 3 raw example messages with the token and any secrets removed. If the new keys are absent from stored data, say whether a new connection after a fresh `/low_latency_feeds` discovery returns them (check one live CS2 socket for 60 s, one connection only, 3 per match limit), or whether an opt-in is needed.
5. Storage: report bytes per CS2 message before and after the new fields (median, p90) and the daily CS2 volume since 13 Nov. We need to stay above the 15 GB free floor on /mnt/HC_Volume_107257520.
6. Protect the capture for the Major (25 Nov onward): no mid-hour restarts, SIGINT only if stopping, `gzip -t` before shipping each closed hour (see #370 reply).

Reply with the numbers and the file paths. Do not interpret leads; I do that under STANDARD v1.
