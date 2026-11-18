# Dota capture inbox — 2026-11-18

The 16–17 Nov Part A is superseded by the 18 Nov update and is dropped; no rerun was made. The verified raw-copy and lag-analysis result is recorded in `agent/outbox/2026-11-18-dota-raw-restore.md` (commit `50261e5808`).

Part B is replaced by `agent/tasks/dota-live-capture-2026-11-20.md`: output is on the data volume, timeout 57,600 seconds, with the 20 Nov checks. The PK queue keeps its start/check rows waiting until their stated windows; no capture was started in advance.
