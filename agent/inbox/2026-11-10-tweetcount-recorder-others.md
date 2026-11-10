# Task for Hermes (from the forecast-edges thread): start a second recorder, same rules as the Elon one

Why: Trump's past windows cannot be rebuilt (the tracker's post list shows about 60% of its own count), so we record the tracker's own hourly totals and the books going forward for the 7 non-Elon accounts.

1. Probe (one shot, read-only): `python3 agent/tasks/tweetcount-recorder-others.py --out /tmp/x --probe`. Write the result to agent/outbox/tweetcount-others-probe-2026-11-10.md.
2. If the probe passes, run it under `systemd-run --scope -p MemoryMax=300M python3 agent/tasks/tweetcount-recorder-others.py --out /vol2/pkarbs/tweetcount-others`, one process, nothing else started. It writes about 1 file per window, a few MB per day. Status line to agent/outbox/tweetcount-others-status.md every few hours.
3. Both recorders are paper-test only: no orders, no keys. Nick pre-authorised recorders for this thread.
Priority: the Nov 3-10 windows end 17:00Z today; the Nov 6-13 windows end 13 Nov.
