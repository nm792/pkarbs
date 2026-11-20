# IT 11:10Z 20 Nov: P94 closed, PS local export queued for 14:11Z

1. **Goal:** measure whether PandaScore and Goalserve live feeds lead Polymarket books enough to trade.
2. **Where it stands:** the 10:41Z PS live read is in pkarbs 81386c3e94 (agent wrote FAIL; your 11:05Z queue-order update, reviewer 81a3ba39, reads it as PASS in substance). IT closed P94 at dialogue a81c8e95 and dropped the 11:41Z repeat to save an agent call.
3. **Most important item:** your 14:11Z export is queued as P95 (dialogue OPEN-WAITING.md, a81c8e95), moved to OPEN at the 14:10Z IT check. One change: the agent uses /mnt/HC_Volume_107257520/tmp/psexp instead of /tmp/psexp (scratch on root is barred; root was 2.78 GB free at 11:00Z, data DISK.tsv 471ed32f), and stops if VOL2 is under 10 GB.

Items:
- Every job's first row is now X5 (root emergency, IT 11:12Z), then X4 (VOL2 growers; writes agent/status/disk-2026-11-20.md for you). P86a is the top P row after X5P; its cron line must be in before 14:50Z.
- If you want the 11:41Z read after all, say so in a REPLY file.
