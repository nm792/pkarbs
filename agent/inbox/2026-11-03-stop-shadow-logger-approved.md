# Nick approved: stop the sports-MECE shadow logger after its data is moved (3 Nov 14:15Z)

Nick, in project chat at 14:15:00Z, replying "OK" to: "That strategy is dead at a 1 s delay, so I recommend stopping the logger once its old data is moved to the storage box. Shall Hermes go ahead?"

Do, in this order:
1. Run the offload in `agent/inbox/2026-11-03-storage-offload-ruling.md` (sha-verified copy to the storage box, manifest committed, then delete the local copy).
2. Then stop `pkarbs-shadow-logger.scope` (shadow/shadow_logger.py writing to /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/). Confirm with `ps` that no shadow_logger.py process is left. Do not restart it, and do not start any replacement.
3. Then copy the files the logger wrote last, including those from the last 48 h, to the box the same verified way. Keep the local copies until verified.
4. Report in `agent/outbox/2026-11-03-stop-shadow-logger-approved.md`: GB moved, mismatches, stop time, `df -h` for / and /dev/sdc. Also confirm that / has at least 5 GB free before the LoL QF capture at 20:30Z.
5. Update agent/status/sports-mece-shadow.md to STOPPED (data on the storage box).
