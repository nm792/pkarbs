# pkarbs sports-MECE shadow logger — STOPPED, all data on the storage box (step 4/5)

Per `agent/inbox/2026-11-03-stop-shadow-logger-approved.md` (Nick OK 3 Nov 14:15Z). All steps done.

## Stop (step 2)
- `systemctl stop pkarbs-shadow-logger.scope` executed; **unit now `inactive`**.
- **Confirmed: no `shadow_logger.py` process remains** (pid 2951556 gone; `ps` clean; nothing writing to `data-v2/`).
- Not restarted; no replacement started.

## Data on the box (step 1 + step 3, sha-verified three-way, manifest committed)
| phase | files | span | note |
|---|---|---|---|
| step 1 (offload >48h) | 85 | 23 Oct - 26 Oct | sha-verified, local deleted after verify |
| step 3 (last-48h tail) | 188 | 26 Oct - 4 Nov 00:00 | incl. events.jsonl 4.1 GB; local KEPT till verified |
| **total** | **273** | | **0 sha mismatches, 0 skipped** |

- Manifests: `agent/status/storage-offload-manifest.csv` (step 1), `agent/status/storage-offload-step3-manifest.csv` (step 3), each committed per file.
- Box holds **95 GB** under `pkarbs/`; box df 929 GB avail (10%).

## Disk
- `/dev/sdc` (`/mnt/HC_Volume_107257520`): **28 GB free** (was 0 / 100% before offload; now 68%).
- `/`: **8.6 GB free** — **satisfies the >=5 GB requirement** for the LoL QF capture at 20:30Z.

## Status
`agent/status/sports-mece-shadow.md` flipped to **STOPPED (data on the storage box)**.

## Rests
No tb IPs, host names outside the manifest, volume names, or keys written. No external cost.
