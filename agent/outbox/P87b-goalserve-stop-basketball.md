# P87b — Goalserve basketball removal preflight

- **State: NOT RUN.** No restart or live-file edit was made; `basketball_payloads` was left intact.
- The live tmux session `goalserve` has PID 4045212 running `python3 live/goalserve/capture.py` (started 17 Nov 09:00Z). The merged PR 455 changes `live/goalserve/capture_store_all.py`; that file is not the process's current script path. The checked-out `live/goalserve/capture.py` also differs from the fetched thread version and has local uncommitted basketball polling/storage changes. I did not infer a deployment mapping or overwrite it.
- No safe between-match gap was established: the latest basketball payload contains events marked in progress (including second-quarter and overtime records) with provider update times around 05:30Z, while the current source timestamp is stale. This does not establish current match state, so the required quiet-gap condition is unverified.
- Disk preflight: VOL2 has 9.0 GB free, below the 10 GB floor. No storage was moved or deleted.
- The three required post-restart folder freshness checks and the three-minute verification were not run because no restart occurred. Existing folder mtimes are not post-restart evidence.
- `basketball_payloads` remains on disk. No deletion or cleanup was attempted.
- Blocker routed to IT in dialogue/TO-IT.md: clarify the live deployment target/source and resume only after a verified quiet gap and disk-floor handling.
