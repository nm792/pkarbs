# Outbox: Top 14 rugby capture — picked up, harness built, connectivity PROVEN (from_agent)

From: Hermes (server member). Replying to the inbox nudge (rugby-top14-capture-nudge-2026-11-02).
Task: agent/tasks/TASK-rugby-top14-capture-2026-11-07.md. Status: OPEN -> being prepared.

## What I can run (and have run today)
1. **capture.py written** (agent/tasks/rugby-top14-capture.py, py 3, websockets-only, one bounded
   process per window A/B/C, MemoryMax=600M/swap0 via the task's systemd-run wrapper, timeout
   10500). Three concurrent async tasks: sports WS (rutopft filter), CLOB market WS (reconnect max
   3, REST 5 s fallback), ESPN 30 s + trades 10 s polls. Outputs rugby/<win>_{sports,clob,espn,
   trades}.jsonl + <win>_log.txt; 10-min copy to /mnt/project-files/rugby/live-2026-11/.
2. **CLOB market websocket CONNECTS from the server.** Live probe just now (16.0 websockets, honest
   UA) opened `wss://ws-subscriptions-clob.polymarket.com/ws/market`, subscribed window A on
   clobTokenId 1145090600…, and received the first market book message immediately. This was the
   task's open risk (403 from the sandbox 2 Nov); from the server it connects, so the CLOB stream
   will be the price clock, not the 5 s REST fallback.
3. **Sports WS connects** (4 msgs in a 15 s probe; 0 `rutopft` now, off-hours — the window decides
   whether the sports WS carries Top 14 at all, else ESPN is the lone score clock; stated).
4. **ESPN rugby scoreboard (league 270559):** 200 OK on the 2 Nov probe per the task; will re-verify
   in-window.

## What I cannot run yet (by design, not a miss)
The three capture windows are 7 Nov 13:15Z / 7 Nov 15:20Z / 8 Nov 19:50Z. Those are bounded
in-repo runs I will start on schedule under the same systemd-run wrapper. Each window after the
prior is reviewed and its process gone (task rule). No restart, no kill, no code change pending
on Nick.

## Decision I need from the thread (ask only if it changes the plan)
None — everything in the task runs per its own procedure. If the thread wants outputs pushed more
often than every 10 min, say so.

## Count
notes run 1 (rugby pick-up), outstanding 0 (windows are scheduled, not blocked), status created.

## Context
pkarbs rugby Top 14 capture, windows 7-8 Nov, one question: score-change -> moneyline lag (CLOB).
No P&L. No IPs/host/volume names.
