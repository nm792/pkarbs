# thesports-trial status
state: running (capture-b scope active, writing ts_mqtt/books)
last heartbeat (UTC): 2026-11-09 02:20Z (server-member dispatch round)
export: 2h timer cron '0 */2 * * *' armed; slim-export loop running; all slim exports on origin (last 22:24Z eca4c7cc0 + continuing).
process: capture pid 2818605 alive (systemd-run thesports-capture-b.service absent by that name; scope runner start_writer.sh); RSS 276 MB < 650 MB cap, VmSwap 0 — no OOM (monitor 'oom' flag is stale noise). ts_mqtt.jsonl 1.85 GB, last write 02:18:58Z (live).
rugby: C+D 10 raw files gzipped and committed to claude/project-thread-vg2ckg under rugby/live-2026-11/ (commit 0844e739 / bd969718 + reply 0308e7a2f) — D_espn split into 4 pieces per 1MB gz hook. Reviewer's lag pass can proceed.
errors: none this round.
output: slim final-topics-32295b-slim on origin (ts_mqtt/ markets/ log full); cricket slim pending export-approval. cricket capture OUT /mnt/HC_Volume_107257520/pkarbs/thesports-cricket/2026-11-10
cricket: SEPARATE cricket-only capture started 2026-11-10 04:05:18Z (unit thesports-capture-cricket, mqtt_suback QoS0, live match zp5rzpcdx6n4q82; ts_mqtt 38 rows by 04:15Z). 2h-export inclusion = APPROVALS item (code change).

