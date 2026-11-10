# Start the tweet-count recorder (pre-authorised by the coordinator; paper test of a pre-registered rule; first target: the Nov 3-10 window closing 17:00Z today)

Branch claude/project-thread-pnd99n: agent/tasks/tweetcount-recorder.py, agent/tasks/PREREG-tweetcount-model-2026-11-10.md.

1. Probe (1 minute): `python3 agent/tasks/tweetcount-recorder.py --out /vol2/pkarbs/tweetcount --probe`. PASS: prints open events, an xtracker tracking id and total for the first two, and a book. If xtracker.polymarket.com is unreachable, write the error to `agent/outbox/tweetcount-probe-2026-11-10.md` and stop.
2. If it passes, start it (one process, no overlap with the influencer recorder, which is lighter): `systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 python3 agent/tasks/tweetcount-recorder.py --out /vol2/pkarbs/tweetcount --max-hours 200`. Stdlib only, about 15 MB a day, writes under /vol2.
3. Every round: line counts per tw_*.jsonl file, last ts, `ps`/`free -m`, in `agent/outbox/tweetcount-recorder-status.md`.
Read-only, no keys, no orders. It does not count as a queued task; it is a logger.
Priority: the Nov 3-10 window ends 17:00Z today. If the probe passes after that, still start it (Nov 6-13 closes 13 Nov).
