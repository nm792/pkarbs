# Reply to inbox #288 (2026-11-13-goalserve-use-v2-task-only.md): v2 running, trial task not run

Reply time: 2026-11-13 14:35Z (Prime).

- **`TASK-goalserve-trial-2026-11-12` was NOT run and is treated as superseded** (assumptions wrong per this note). Nothing from it was executed.
- **`TASK-goalserve-v2-2026-11-12` is in progress, esports first:** the esports capture started **14:04:31Z** (commit `9739c3d24d`), 0.5 s `inplay-esports.gz` polling, log `/vol2/goalserve/goalserve_20261113.jsonl` (24,339,080 B, newest row 14:27Z, pid 86236). Tennis and NHL WebSocket legs and the cricket/rugby 1 s livescore legs follow after it, one process at a time.
- **Auth shape confirmed 13:09-13:19Z** (`agent/status/goalserve-probe.md`): `gettoken` 200 with the `apiKey` field; esports/basket/volleyball 200 with data. No WebSocket is used for esports, cricket or rugby, per the note.
- **Status file:** `agent/status/goalserve.md` written 13:25Z and updated at capture start; next update within 30 min of start, then every 30 min while anything is blocked.
- **No key and no server address** written anywhere in this reply; the key lives only in `/etc/pkarbs/goalserve.env` (mode 600).

LoL Worlds final is 14 Nov, so esports stays first.
