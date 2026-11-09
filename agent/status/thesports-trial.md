# thesports-trial status
state: running (capture-b scope active, writing ts_mqtt/books)
last heartbeat (UTC): 2026-11-09 01:40Z (server-member sweep)
export: 2h timer cron '0 */2 * * *' armed; slim-export loop running; all slim exports on origin (last 22:24Z eca4c7cc0 + continuing).
process: thesports-capture-b.scope active; python capture pid alive; RSS 276 MB < 650 MB cap, VmSwap 0 — no OOM (monitor 'oom' flag is stale noise).
errors: none this round (a prior non-ff push was resolved by rerun).
output: slim final-topics-32295b-slim on origin (ts_mqtt/ markets/ log full); diary json under rn1/scores/thesports.
rugby: C ended ~23:31Z; C+D raw export to /mnt/project-files/rugby/live-2026-11/ COMPLETE 01:38Z (10 files). schedule_captures --run-due is a no-op (empty schedule; waits Nick card).
