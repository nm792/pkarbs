# thesports-trial status
state: running (capture-b active pid 2818605; capture-cricket active pid 1829238); export timer cron `0 */2` live, no stale slim.lock
last export on origin (UTC): 2026-11-12 07:30Z merge (29254c153) — newest slim ts_mqtt 1794461599, past 11-11 10:00Z deadline
data gap: CLOSED (was ~16h stranding; export commits 05:32Z/07:30Z were NFF-rejected on a stale base; merged onto origin tip 13ce7cf and pushed 07:5xZ)
markets.jsonl.gz: 2,866 rows on origin (was 2,374)
volume: /dev/sda1 50% / 19.3G free; VOL2 handled by the concurrent dispatch (OPEN row D)
errors: export push race (non-fast-forward) resolved by merge; export_timer_2h.sh bash -n OK
next scheduled export: 08:00Z cron
