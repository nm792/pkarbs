# URGENT (deadline-bound): TheSports diary fetch and stalled 2h export

From: TheSports thread, 13 Nov 20:10Z. Follows abb9c671 (row P10) and IT reply 055e448c62.

The TheSports trial ends 16 Nov. After that the diary cannot be fetched, and the locked Dota test D1 (39 of 40 games) cannot finish. P10 must not wait behind non-deadline work. Please move it to the top of Hermes's queue now.

1. Diary: read-only fetch of the TheSports diary for dota2 for 2026-11-12 and 2026-11-13 (then csgo, lol, tennis if cheap), same format as rn1/scores/thesports/diary/dota2-2026-11-11.json (including results_extra.team). Save under rn1/scores/thesports/diary/ and push. Rerun daily until 16 Nov. As of 20:07Z the repo has no diary file after 11 Nov.
2. Export: the 2h slim export has not pushed a TheSports commit since 64a2a79757 (13 Nov 13:08Z), over 6.5 hours. agent/status/thesports-trial.md still shows push_rc 1 and last export 14:38:44Z. Please find why (the 950 KB pmws gate with the split ruling, or the push race) and push an export so the diary and the new Polymarket markets (registered since the 17:06Z gamma fix) reach the repo.
3. Reply in agent/outbox with the fetch time and the export commit. Status in agent/status/thesports-trial.md within 60 minutes.
