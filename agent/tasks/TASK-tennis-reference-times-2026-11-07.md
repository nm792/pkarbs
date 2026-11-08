# Task for Hermes: independent timestamps for the 28 tennis matches (written 2026-11-07T07:47Z)

Why: we need official or third-party start/end times (and point-level times if any exist) to judge whether TheSports tennis or the Polymarket price is late. Request relayed by the project coordinator; read-only, no orders, no money, no credentials printed.

Input: `rn1/scores/thesports/reference/tennis-matches-28.csv` (TheSports match id, home, away, scheduled start epoch, first/last TheSports message epoch).

Do, from the server (its IP may be allowed where the cloud container gets 403):
1. Sofascore (`api.sofascore.com`): for each match find the event (tennis scheduled-events for 2026-11-06 and 2026-11-07, or search by player names). Save raw JSON: `event/<id>` (startTimestamp, time.*, currentPeriodStartTimestamp), `event/<id>/incidents`, `event/<id>/point-by-point`, `event/<id>/statistics` if present. Save under `rn1/scores/thesports/reference/sofascore/<match_id>-*.json`. Keep it to those 28 events, one request each endpoint, polite pace.
2. Write `rn1/scores/thesports/reference/sofascore-times.csv`: match_id, sofascore_event_id, startTimestamp, and any end/last-period timestamp present (say "none" if absent).
3. Say in `agent/outbox/tennis-reference-ack-2026-11-07.md` this round what worked, the exact HTTP errors if blocked, and whether any point-level timestamps exist. If Sofascore is blocked from the server too, say so and stop; do not use proxies or workarounds.
Commit and push to the default branch. Do not delete anything under `rn1/scores/thesports/` (records kept for the whole trial).
