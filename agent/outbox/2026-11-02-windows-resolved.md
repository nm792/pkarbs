# Outbox: Top 14 windows + Nick approvals resolved (2 Nov 2026)

From: Hermes (server member). Replying to the inbox chain in one consolidated note:
`fixture-windows`, `windows-c-d-ready`, `windows-d-and-overlap`, `nick-approvals-code-gate`,
`window-ab-confirmed`. All five are the same window-resolution thread and read together below.

## Current window state (matches config + task v2)
- Windows are now **AB, D, C** — one bounded process at a time, in time order:
  - **AB**: 7 Nov 13:15-18:05 UTC, 6 matches, 36 tokens, run under `nice -n 19`, 600M cap,
    18000 s runtime limit (merged from A+B; Nick approved the 5 h single process 15:50Z).
    Toulouse v Clermont appears once. Coordinator settled the fixture conflict 15:47Z.
  - **D**: 8 Nov 13:45-16:30 UTC, Vannes v Bordeaux (Rugbyrama 61243, 14:00 UTC), 6 tokens.
  - **C**: 8 Nov 19:50-22:35 UTC, La Rochelle v Bayonne (Rugbyrama 61238, 20:05 UTC), 6 tokens.
- Config `agent/tasks/rugby-top14-config-2026-11-07.json` carries keys AB / C / D; verified on disk.
- The task file (v2) already reflects the merged AB and the AB/D/C order.

## Gate checks
- **CLOB market WS connects from the server** (was 403 from the sandbox) — the live probe
  received the first market book on the window-A token; CLOB stream will be the price clock.
- Sports WS connects, 0 `rutopft` now (off-hours). ESPN rugby 270559 is the score cross-check.
- Rugbyrama widget poll: config key present; will be added as the fourth async task (already in
  the task's procedure, Nick approved the code change 15:44Z).

## What I cannot run yet (by design, not a miss)
The windows are 7-8 Nov; none is due today. Each starts only after the prior window is reviewed
and its process is gone, and AB does not start until the coordinator re-checks the gamma start
times on 6 Nov. No code change, merge, restart or kill pending on Nick.

## Count
notes run 5 (window chain, one consolidated reply), outstanding 0 (window runs are scheduled
for 7-8 Nov, not blocked).

## Context
pkarbs rugby Top 14 capture, windows 7-8 Nov, one question: score-change -> moneyline lag (CLOB).
No P&L. No IPs/host/volume names.
