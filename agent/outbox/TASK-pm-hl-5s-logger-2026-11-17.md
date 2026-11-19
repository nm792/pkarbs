# P6 — 5 s Polymarket/Hyperliquid divergence logger boot persistence

Task code commit: `722e6ab53b147744b3de9c9fcb17fd39575ce3cd`.

- The logger is live as a transient unit, PID 3618574, started 2026-11-17 04:11:50 UTC. Its transient definition has the requested `ExecStart`, `Restart=always`, and `RestartSec=5s`; `UnitFileState=transient`, so it is not enabled across reboot. No persistent unit file existed.
- Current read-only output: `<data-volume>/pmhl5s/pmhl5s_20261117.jsonl.gz`; 864 rows, 7,307,927 bytes, first row 04:11:50.725720Z, last row 05:25:46.324720Z; 11.69 polls/min. NVDA-USD, MU-USD, AMD-USD, TSLA-USD, and SP500-USD books are present in every row; 0 rows have book errors.
- Root free space measured 15,855,411,200 bytes; data-volume free space 43 GB. No process was stopped and no data was removed.
- A persistent unit definition was staged and passed `systemd-analyze verify` (exit 0; unrelated pre-existing unit warnings only). Installing it under `/etc/systemd/system/` was blocked by the unattended terminal safety gate before any copy or unit change. The persistent unit remains absent; the existing transient logger remains active. No `daemon-reload`, enable, or restart occurred.

Status: waiting for the terminal's on-box consent to install the persistent unit and enable it. The requested `is-enabled=enabled` and post-switch row proof are not yet established.
