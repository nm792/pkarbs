# Status: lol-live-capture (Worlds 3-6 Nov 2026)

State: OPEN (scheduled) — ready, not yet runnable
Last heartbeat: 2026-11-03 06:05Z (NTP sync confirmed for TES-IG feed-delay capture)

## Task
Within each of the four Game-1 windows (22:00Z each, 3-6 Nov: TES-IG, GEN-LYON, DK-BLG, T1-KC), measure how much later the Polymarket Game-1 winner price moves after each Riot livestats event, on the book (1 s REST polls) and on trades.

## Prep state (done, on disk)
- agent/tasks/lol-live-capture/config.json — 4 matches, esports_match_id + game1_id, PM condition + token IDs, scheduled_start_utc (22:00Z). Slug/date mismatches noted (config keys off scheduled_start_utc).
- capture.js + watchdog.sh present; node v22.23.1 available.
- Local 60 s test (2 Nov) passed against a completed game: frames 10 lines, book 7 changed rows.
- Known limits: WS market channel non-101 from sandbox -> books are REST 1 s polls; livestats timestamps may trail broadcast (report lag distribution, do not call it broadcast latency).

## Not run yet
- Match windows start 3 Nov 22:00Z (TES-IG). Capture runs only inside each window (start-90 min to +150 min), memory-capped 600 MB, one process per match, cleanup + `ps`/`free -m` confirm after.
- Blocked/cap: none for the capture itself (no API key needed); the esports key (LOL_API_KEY env) only re-resolves game IDs.

## Next
- Bootle capture for TES-IG on 3 Nov ~20:30Z (90 min before 22:00Z). Copy outputs to /mnt/project-files/rn1/scores/lol/live-2026-11/ every 10 min; post status to the thread every 10 min; never go silent.

## 2026-11-03 07:3xZ sweep
- timedatectl: System clock synchronized: yes; NTP service: active (confirmed for TES-IG 20:30Z window).
- capture.js merged per 06:06Z update (2s polls for all five game ids; live-2026-11/feed_delay.py analysis; 15 bids/asks depth levels). Ready for TES-IG window 20:30Z.

## 2026-11-04 02:36Z (inbox 2026-11-04 items 2 + 3)
- TES-IG (3 Nov 20:30Z window): capture found in shared folder /mnt/project-files/rn1/scores/lol/live-2026-11/tesig/ (books 789 KB, frames, polls, capture.log). Committed to rn1/scores/lol/live-2026-11/server-TES-IG/ in this repo.
- GEN-LYON (4 Nov ~20:30Z window): capture.js on disk (agent/tasks/lol-live-capture/capture.js, mtime 2026-11-04T00:00Z) CARRIES the PR#39 startingTime fix — confirmed. Copy output to rn1/scores/lol/live-2026-11/server-GEN-LYON/ every 10 min during the window.
