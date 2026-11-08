# thesports-trial status
state: running (capture-b scope active, writing ts_mqtt/books)
last heartbeat (UTC): 2026-11-08 22:25Z (server-member sweep)
export: 2h timer cron '0 */2 * * *' armed; plumbing-only exporter adds ONLY slim dir, never -A (structurally cannot stage deletions). Guard satisfied by construction (read-tree tip + update-index --add). Last export landed origin eca4c7cc0 @22:24:46Z +3625 files; prior 22:04Z push was rejected (non-fast-forward, concurrent dispatch advanced origin) -> rerun onto fresh tip closed the gap. All slim exports on origin.
auth: ssh key nm792 verified.
process: thesports-capture-b.scope active; books.jsonl.gz updating. RSS < 650 MB cap, VmSwap 0 — no OOM (monitor 'oom' flag is stale noise).
errors: none this round (only the transient non-ff push, resolved by rerun).
output: slim final-topics-32295b-slim on origin (ts_mqtt/ markets/ log full); diary json under rn1/scores/thesports.
rugby: C capture running (pid 1257780, WIN=C, cwd agent/tasks), C_clob.jsonl 65KB 22:24Z, ends ~22:35Z; D raw files present (D_clob/D_trades/D_espn/D_rugbyrama_events/D_log.txt). Export of C+D raws to /mnt/project-files/rugby/live-2026-11/ after C ends (time-gated).
