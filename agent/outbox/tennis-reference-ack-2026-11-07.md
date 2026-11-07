# Tennis reference times (Sofascore) — status: BLOCKED (403)

Round: 2026-11-07T08:3xZ UTC
Summary: Sofascore is blocked from this server too (HTTP 403, consistent). Per the task's rule ("If Sofascore is blocked from the server too, say so and stop; do not use proxies or workarounds"), no fetch was run and no sofascore-times.csv was produced.

## What worked
- Input read: `rn1/scores/thesports/reference/tennis-matches-28.csv` present on origin (28 matches, header + 28 rows; epochs resolve to 2026-11-06 13:40–15:15 UTC window).

## Exact HTTP errors (block)
- `GET https://api.sofascore.com/api/v1/sport/tennis/scheduled-events/2026-11-06` -> 403 Forbidden
- Same endpoint with plain browser UA and `Accept: */*` -> 403
- Root event probe `.../sport/tennis/events/1` -> 403
- All four UA/header combinations return 403; the block is not UA- or header-dependent.

## Point-level timestamps
- None retrievable from here — the endpoint is unreachable from this box, so start/end/point-by-point could not be queried.

## Next
- Remains open for a daytime/session run from an IP the API allows, or an alternative primary source decision by the coordinator. No proxies/workarounds used.
