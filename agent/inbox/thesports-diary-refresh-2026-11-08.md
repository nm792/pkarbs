# Request to Hermes (2026-11-08T03:25Z): refresh the TheSports team-name diary

Signal-vs-noise analysis is limited by pairing: only 24 of 75 tennis games and 29 of 38 CS2 maps (23 Dota games, 19 with names) pair to a Polymarket market by names. `rn1/scores/thesports/diary/` has files only to 7 Nov. Nick, 8 Nov 02:33Z: "keep going".
Read-only, no orders, delete nothing, no credentials in git:
1. Refresh the diary/schedule lookup for every tennis, csgo, dota2 (and lol) match id seen in `final-topics-32295-slim` and `final-topics-32295b-slim` (home/away names, start time), same JSON layout as the existing `diary/*.json` (tennis-*.json etc.), and commit them to `rn1/scores/thesports/diary/`.
2. Repeat with each 2 h slim export.
Reply in `agent/outbox/thesports-diary-refresh-2026-11-08.md`.
