APPROVALS NEEDED:
- None. This is read-only count work.

RESULT
- Completed #318 follow-up through 2026-11-14 13:25Z; count-only per `feeds/STANDARD-feed-latency-test.md` v1. No lead or verdict computed.
- PandaScore: 26 matches; Dota increases — kills 1,069, towers 243, barracks 76, Roshan 38. CS2: 702 round-score changes, 6,052 alive flips.
- Goalserve: 24 matches, 11,867 distinct odds-change payloads (Dota 2 4,596; CS2 6,964; other esports 307). One malformed body skipped; complete surrounding rows retained.
- `payloads` counts match observations; distinct odds-change events count each payload once if any participant value/suspension changed. Participant-field changes count individual fields; hence they may exceed payloads. For match 140832465: 6,063 payloads, 705 distinct changed payloads, 8,478 participant-field changes.
- PM-book overlap within ±60s: CS2 <$25k 225/378 events (5 matches); CS2 >=$25k 266/266 (5); Dota <$25k 550/776 (4); Dota >=$25k 78/78 (1). These are counts, not lead measurements.

DATA
- `agent/status/p318-recount-2026-11-14.json` — all per-match counts, receive gaps, close codes, and priced-event buckets.
- Script: `/vol2/pkarbs/scratch/p318-recount/full_recount_1325.py` (exit 0); bounded raw inputs; no code or rule changes.

OPEN / NOT VERIFIED
- 5,322 code-4004 closes map to match 1789154, which has zero status rows in this interval; per-match gap alignment is not measurable. Four additional close-error rows had no code. No data loss is inferred.
- The 13:00Z hour was append-streamed at cutoff; complete rows through 13:25Z were retained, incomplete gzip tail ignored. The 12:00Z completed hour decoded cleanly.

Count: notes run 1, outstanding 0, PENDING open 0
