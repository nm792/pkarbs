# Pause lifted by Nick (14:19Z 5 Nov): restart order, under charter 383

Nick told the project thread directly that the pause is lifted. Please also post your own `from_agent/381-pause-lifted.md` as the dialogue procedure requires. If the charter disk gate (`/root/bin/disk_gate.sh`) refuses any item, the refusal is final: log the figures and skip it, do not work around it.

Order of work, one at a time:
1. **LoL DK-BLG dry run, 22:00Z today (highest priority, time-boxed).** Confirm the watchdog/run.flag is armed and the capture will start at 22:00Z, dry only, memory-capped, timeout-bound. Output goes to /vol2, not `/`. Raw ships to the storage box hourly; git gets a manifest only. Report armed/not armed in agent/status/lol-live-capture.md by 15:00Z.
2. **tennis-books restart on /vol2** (the 12:33Z run was on the old HC volume path). Same task file, same stop limits adapted to /vol2. Stop by 21:30Z so DK-BLG starts clean. One task toward the 2/day budget.
3. **cricket-feeds capture restart on /vol2**, same rules. It ended 13:49Z; the cricket thread wants continuous capture until ~17:15Z.
4. **Post fresh numbers** in agent/status/heartbeat.md: `df -h` for `/`, /vol, /vol2, which captures run, and what the gate said for each item.

Do not commit raw data to this repo (charter 383). Commit computed results and manifests. Never commit keys. Reply in the existing status/outbox files.
