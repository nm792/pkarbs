# Nick APPROVED the exporter guard and the 2 h timer (written 2026-11-08T09:41Z)

Nick tapped "Approve guard and timer" on the approval card (8 Nov 09:39:50Z): "Approve Hermes adding a deletion guard to the TheSports export and a 2-hourly timer?" This clears the two consent-gated items in your 07:04Z reply (`thesports-commit-deleted-files`).
Do (read-only for PM/TheSports, no orders, nothing deleted, no credentials in git):
1. Guard: the exporter commit path adds ONLY its own slim output dir (`git add <dir>`, never `-A`/`commit -a`) and aborts the commit if `git diff --cached --diff-filter=D --name-only` is non-empty. Test it once on a dry run and show the output.
2. Timer: a systemd timer or cron line that runs the slim export + commit for the live chunk every 2 h (one instance), updating `agent/status/thesports-trial.md` with time and row counts.
3. Reply in `agent/outbox/thesports-guard-timer-2026-11-08.md`: the guard diff, the dry-run output, the timer definition, first and next run times.
