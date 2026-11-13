# Reply to inbox #305 — PandaScore Dota 2 coverage report, due 16:15Z

Posted 16:10Z, inside the deadline: section `## Dota 2 coverage 16:15Z` in `agent/status/pandascore.md`.
No rule, threshold or socket behaviour was changed.

1. **13 matches touched since 15:12:29Z (13 `hello` + 2,804 `status` rows); 5 are Dota 2, 8 CS2.**
   **4 of the 5 Dota matches have a Polymarket Game-N-Winner / Match-Winner market** (matched by team names):
   Froglings vs PuckChamp, PARIVISION vs Yellow Submarine, Team Allied vs potn9ki, Team Liquid vs LGD Gaming.
   **`Team Synapse vs Time to Sleep` has no PM listing — 80% pairing observed.** TheTheSports side has had no new
   PM-paired Dota game since 11 Nov, so the bottleneck stands on the PM-listing side, not the socket side.
2. **State changes (diffed per `match_id`, `game_timer`/net-worth drift excluded):** PARIVISION vs Yellow
   Submarine — 61 kills / 12 towers / 4 barracks / 1 roshan; Froglings vs PuckChamp — 38 / 17 / 11 / 9;
   Team Allied vs potn9ki — 58 / 14 / 6 / 9; the two 15:45Z sockets (Liquid vs LGD, Synapse vs Time to Sleep)
   show 0 changes in the window. Totals: 3 matches with real changes, 157 kill-side, 43 tower, 21 barracks,
   19 roshan. Counts only — not analysed, so not "sim on real data".
   **PM price coverage within +/-60 s: NOT COMPUTED — no PM price row source for esports markets was found on
   Prime (the task names "the PM recorder" without a path). Blocker stated, not guessed: name the path and the
   pass runs in minutes.**
3. **ESTIMATE: ~10 PM-paired distinct Dota matches in ~2-3 h of continued evening slate, ~30 priced events at
   ~3 priced markets per BO3** — assumptions: PM keeps listing 4/5 in-play Dota matches, slate rate holds,
   price coverage satisfied (unverified, blocker above). **BLAST Slam from 17 Nov** named as the dependable
   tier-1 source for the match-clustered CI. Rate rests on 54 minutes of observation — thin.

Also owed and delivered: first-hour MB — hour-15 file 330,887 B / 2,500 rows -> ~7.9 MB/day gz.

**Micro-choice recorded (clause 20):** the `/vol2`-on-root bug (P7) was not repointed here — code/config change,
filed as class 4, `dialogue/APPROVALS.md` open approval #20, for the daily report. Root 17.56 GB free (above the
floor). Revert: restore the pre-edit copy and point the paths back.
