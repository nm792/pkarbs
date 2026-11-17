# 5 s Polymarket/Hyperliquid divergence logger — 17 Nov

Task code commit: `722e6ab53b147744b3de9c9fcb17fd39575ce3cd`. The live script SHA-256 matches the file at that commit.

- Unit: `pm-hl-5s-logger.service`; active since 2026-11-17 04:11:50 UTC, PID 3618574; `Restart=always`, `RestartSec=5s`. `systemctl cat` shows a transient `systemd-run` unit (not a persistent boot-enabled unit).
- Read-only output: `<data-volume>/pmhl5s/pmhl5s_20261117.jsonl.gz`. At 05:06:13 UTC: 644 rows, 5,382,939 bytes; first 04:11:50.725720 UTC, last 05:06:13.856356 UTC; 11.84 polls/min.
- Required order books all present: NVDA-USD, MU-USD, AMD-USD, TSLA-USD, SP500-USD. Book error records: 0.
- Free space at verification: root 15,912,370,176 bytes; data volume 43,399,786,496 bytes. No keys used or written.

Open: the running unit is transient, so persistence across a system reboot is not established.
