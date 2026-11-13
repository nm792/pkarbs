# Reply to inbox #304 — Goalserve Dota 2 status, due 16:15Z

Posted 16:10Z, inside the deadline: section `## Dota 2 coverage 16:15Z` in `agent/status/goalserve.md`.

- **3 distinct Dota 2 matches in the stored payloads (15:09:30Z-16:08:06Z)**, each with a Polymarket
  Game-N-Winner market: PARIVISION vs Yellow Submarine (1,299 payloads), Froglings vs PuckChamp (1,821),
  Team Liquid vs LGD Gaming (237, from 16:00:03Z). **14:04:31-15:09:35Z has no bodies (hash/size/changed only:
  2,135 polls / 2,015 changed), so that window cannot be counted by match — stated, not estimated.**
- **bet365 odds moves: 474 total** — PARIVISION vs Yellow Submarine 221, Froglings vs PuckChamp 253,
  Team Liquid vs LGD Gaming 0. Method: consecutive stored payloads whose odds block (`value_eu`/`suspend`) differs.
- **ESTIMATE: ~10 distinct matches and ~30 priced Dota events in 3-4 h of continued slate** (observed rate 3
  matches/59 min, 2-3 priced PM markets per BO3; assumptions listed in the status section).
  **BLAST Slam from 17 Nov** named as the tier-1 source; 13-15 Nov is the thin pre-tournament window.
- Payload-parse check done: team names in `info.name` + `team_info`, per-game counters (`kills`, `towers`,
  `roshans`, `barracks`) in `stats`. **Verdict wording kept: Goalserve has no Dota game events — no timestamped
  kill/tower stream, only per-poll stat counters plus bet365 odds. No round field. Not an edge.**

Report was late-proofed against the clock at 16:10:01Z (`date -u` on the box).

**Micro-choice recorded (clause 20):** the `/vol2`-on-root bug (P7) was NOT repointed in this pass — a path
repoint is a code/config change, so it is filed as class 4, `dialogue/APPROVALS.md` open approval #20, for the
daily report. Root 17.56 GB free (above the 15 GB floor) and the payload store self-stops at the floor, so
waiting loses nothing. Revert for #20: restore the pre-edit capture copy and point the paths back.
