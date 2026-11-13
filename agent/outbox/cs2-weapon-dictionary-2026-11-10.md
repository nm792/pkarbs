# Outbox: CS2 weapon dictionary (reply to cs2-weapon-dictionary-2026-11-10)

Endpoint(s) used: `GET https://api.thesports.com/v1/csgo/weapon/list` and `/v1/csgo/map/list` (both succeeded, HTTP 200 body `code:0`), with the account `user`/`secret` from `/etc/pkarbs/thesports.env`. Read-only, one call each.

Results:
- `/v1/csgo/weapon/list` → 67 weapon rows (`query.total: 67`). Each row: `id` (hashed, e.g. `9vjxm89wu4q6odg`), `name` (e.g. `knife_m9_bayonet`, `mp9`), `logo` (eimg.thesports.com CDN), `updated_at`. This is the id→name mapping the win model needs.
- `/v1/csgo/map/list` → 16 map rows, same shape.
- `/v1/csgo/dictionary` (generic) → `err: URL is not authorized to access` — not needed, weapons+maps cover the ask.

Player-level rating / per-player historical stats: not name-checked this pass per the note (name endpoint only, no bulk pull). The `weapon/list` + `map/list` dictionaries are the requested deliverable.

Saved: `rn1/scores/thesports/reference/csgo-weapons.json` (weapons + maps). No orders, purchases, deletions.

UTC: 2026-11-10 11:2xZ
