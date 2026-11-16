# Dota live capture — update at 2026-11-16 08:37Z

## Result
- The approved capture is running as `dotacap-2026-11-16.service`; Node PID 1700948, 400 MiB cap, zero swap. It started 06:26:55Z, began its scheduled window 08:30Z, and writes output on VOL2.
- Installed the approved Prime crontab publisher. Recurring line: `*/30 * * * * /usr/bin/python3 /root/pkarbs/agent/tasks/dota-live-capture-2026-11-16-publish.py >> /vol2/pkarbs/dotacap/run-2026-11-16/publisher/cron.log 2>&1`. A final 17 Nov 20:35Z run also removes both publisher lines.
- Ran the publisher five times; it shipped complete new JSONL lines in gzip deltas, verified each storage-box copy by checksum, and pushed a manifest. Latest manifest commit: `a508ef9cceeb65bc78ff2a3b55bc19e5b260c665`; manifest path: `manifest/dotacap-2026-11-16.tsv`. Raw data was not committed.
- Capture was active during publishing; at 08:36Z the unit remained within its 400 MiB limit and output files were growing. Feed coverage and the task's final pass/fail are not established yet.

## Implementation and revert
- Publisher: `agent/tasks/dota-live-capture-2026-11-16-publish.py`; SHA-256 `e6c046b10b179ae940b6d9c96e29f0a1904709f14f4355f2a5e9a27f3e467476`; `python3 -m py_compile` passed. Runtime state/chunks/logs stay under the VOL2 capture directory. The script reads existing ship credentials at runtime and does not print them.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; this stops future copies. Capture is unchanged. Keep the publisher file until both cron lines are removed.
- First manifest push `3038c9d59156437c64692a38ca43a6125a2eff71`; latest checkpoint `a508ef9cceeb65bc78ff2a3b55bc19e5b260c665`.
