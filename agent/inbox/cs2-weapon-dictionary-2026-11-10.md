# Fetch the TheSports CS2 weapon dictionary (read-only, routine, one call)

Why: CS2 player snapshots carry `weapon_id` as a hashed id (about 30 distinct values). Our own win model needs equipment value per team, so we need the id to weapon name mapping. Our price regression from cash drops failed (R2 0), so only the dictionary can fix it.

Do:
1. Using the existing TheSports credentials (read-only, no secrets in git), find the CS2/csgo basic-info dictionary that lists weapons (check docs.thesports.com for the csgo "weapon" list endpoint; if the exact path is unclear, try `/v1/csgo/weapon/list` and the nearest documented dictionary endpoints for csgo: map, weapon, team, player).
2. Save the raw JSON responses as `rn1/scores/thesports/reference/csgo-weapons.json` (and `csgo-maps.json` if a map dictionary exists) and commit to `claude/project-thread-vg2ckg`.
3. Reply in `agent/outbox/cs2-weapon-dictionary-2026-11-10.md`: endpoint(s) used, HTTP status, number of weapon rows, and whether player-level rating or per-player historical stats exist in the API (name the endpoint only; do not pull bulk data).
No orders, no purchases, no deletions.
