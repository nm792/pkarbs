# Dota live capture — update at 2026-11-16 08:36Z

## Result
- The approved capture is running as `dotacap-2026-11-16.service`; Node PID 1700948, 400 MiB cap, zero swap. It started 06:26:55Z, began its scheduled window 08:30Z, and is writing output on VOL2.
- Installed the approved Prime crontab publisher. Recurring line: `*/30 * * * * /usr/bin/python3 /root/pkarbs/agent/tasks/dota-live-capture-2026-11-16-publish.py >> /vol2/pkarbs/dotacap/run-2026-11-16/publisher/cron.log 2>&1`. A final 17 Nov 20:35Z run also removes both publisher lines.
- Ran the publisher four times during validation; each sent only complete new JSONL lines, gzip-compressed each delta, checksum-verified the storage-box copies, and pushed a manifest. Latest manifest commit: `d7f87d527f211f451782aa8c257ea277881373a6`; manifest: `manifest/dotacap-2026-11-16.tsv`. Raw files were not committed.
- The capture remained active during publishing; the 08:35Z check showed 400 MiB cap / 0 swap and output files growing. Current feed/pass result is not yet established; this is capture delivery, not the final feed-delay analysis.

## Implementation and revert
- Publisher: `agent/tasks/dota-live-capture-2026-11-16-publish.py`; SHA-256 `a737778639b387ec83434b65a8dfc0549bdd0a89268b0e147619649d081e366c`; `python3 -m py_compile` passed. State/chunks and logs stay under the VOL2 capture directory. It uses the existing ship credentials at runtime without printing them.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; this stops future copies. The active capture is unchanged. Do not remove the task publisher file while either cron line remains.
- First successful manifest push was `3038c9d59156437c64692a38ca43a6125a2eff71`; later manifest checkpoints include `847019448abd37514bade77d952d10e58c92c718`, `3312c57d726dce1f3769d7fb18b432709af6b347`, and `d7f87d527f211f451782aa8c257ea277881373a6`.
