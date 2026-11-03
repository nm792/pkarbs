# To Hermes: lol-live-capture update before tonight (3 Nov, TES-IG window opens 20:30Z)

From thread "Build LoL game-state win model". Nick asked (05:37Z) that tonight's capture measures the livestats feed delay.
Changes merged in agent/tasks/lol-live-capture/ (capture.js, config.json):
1. Frames are polled every 2 s (was 10 s) for ALL five game ids of each series (config game_ids; ids checked against getEventDetails).
2. New output <label>_polls.jsonl: one line per poll {recv_ms, sent_ms, game, status, newest_ts, n}. Copy it with the other outputs every 10 min to /mnt/project-files/rn1/scores/lol/live-2026-11/ and commit it.
3. The log now records whether the host clock is NTP-synced. Please confirm `timedatectl` shows NTP synchronized before 20:30Z and write the result in agent/status/lol-live-capture.md.
Same bounds as before (one process per match, 600 MB cap, start-90 to +150 min). Use the merged capture.js; no other change.
Analysis: rn1/scores/lol/live-2026-11/feed_delay.py <label>_polls.jsonl.

## Update 06:06Z
capture.js now also writes 15 price levels per side in each book row (`bids`, `asks`), to measure queue depth at our resting bid. Tested live against the TES-IG book. Use this merged version tonight.
