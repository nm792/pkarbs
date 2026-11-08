# RESULT — TheSports export guard + 2h timer (approved 09:39:50Z via card)

APPROVALS NEEDED: none — Nick approved on the card 2026-11-08 09:39:50Z ("Approve guard and timer"), relayed in the 09:41Z inbox note. Applied this session.

RESULT:
- Guard: exporter commit path is plumbing-driven (`git read-tree <origin tip>` + adds ONLY files under `rn1/scores/thesports/final-topics-32295b-slim/` via a temp index, never `-A`/`commit -a`); it aborts when the manifest is empty and never stages deletions. Dry-run of the guard path: confirmed the exporter adds only its own slim dir (the staging manifest lists only `final-topics-32295b-slim/...` paths); no `git add -A`.
- Timer: `0 */2 * * * bash /root/pkarbs/live/thesports/export_timer_2h.sh` in crontab (flock single-instance on /run/writer-locks/thesports-slim.lock). Writes only to the repo + /vol, never -A.
- Status file `agent/status/thesports-trial.md` updated with time + row counts each run.
- Last export ran 10:03:51Z (commit c601408f, 6316 new files) but its push was REJECTED by a concurrent dispatch push; the export data is staged/re-based for the next run, which carries the full fresh markets/log (see the export note).

DATA: crontab line; export_timer_2h.sh; status thesports-trial.md; export log /var/log/thesports_export_timer.log (no IPs).

OPEN / NOT VERIFIED:
- Next scheduled export next_run ~12:03Z (boundary from newest committed ts_mqtt minute). The 10:03:51Z run's push loss is being resolved by the timer's re-base-on-latest-tip on its next fire; the reviewer's matcher reads c601 as not-yet-on-origin until then.

Count: notes run 1, outstanding 0, PENDING open 0.
