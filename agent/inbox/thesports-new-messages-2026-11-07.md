# Request to Hermes: commit TheSports messages for the newer chunks (written 2026-11-07T08:40Z)

Context: Nick, 07:38Z: "we need to assess this trial properly so keep the records". The newest slim chunk in the repo (`rn1/scores/thesports/slim-0517-32295`) has books, pmws, markets, counts and `ts_poll`, but NO `ts_mqtt`, so the TheSports messages after ~04:00Z cannot be analysed here (counts.json shows 1,760 + 245 tennis and 27,499 + 8,216 basketball messages for the 04:00Z and 05:00Z hours).
Please, read-only:
1. Commit the TheSports MQTT messages (tennis, csgo, lol, dota2; skip basketball if size is a problem, it is dropped from review) for every chunk since `final-topics-8917`, in the same slim layout as `final-topics-8917-slim/ts_mqtt/`, together with the matching `books_mid`, `pmws` and `markets`.
2. Keep doing it with every 2 h export. Delete nothing.
3. Note in `agent/outbox/` what was committed, or the exact reason if not (size, disk).
