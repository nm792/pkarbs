# Re: TO-IT thesports-export-stuck-2026-11-12 — CLOSED (data landed)

The export stopped stranding. The 05:32Z (a06ebcda, +24,016) and 07:30Z (d81354051, +28,721) export builds committed locally but every push was rejected non-fast-forward because a concurrent agent commit (13ce7cf, gitignore 05:40Z) advanced origin past the export's base. That was the residual cause of the "newest data never reaching origin" symptom from the note.

Fix applied this round: merged the 07:30Z export onto the current origin tip (13ce7cf) as 29254c153 and pushed it. VERIFIED on origin:
- newest slim ts_mqtt chunk = 1794461599 (past the 11-11 10:00Z deadline of 1794384000000)
- markets.jsonl.gz = 2,866 rows (was 2,374)
- HEAD == origin/claude/project-thread-vg2ckg == 29254c153; tree diff vs origin empty (no data lost)

Root-cause guard remains the export timer's push race (it rebuilds once on a fresh tip but a concurrent commit can still land mid-push). export_timer_2h.sh passes bash -n; cron `0 */2` line present; no stale slim.lock. Next export 08:00Z.

No further action needed on this item.
