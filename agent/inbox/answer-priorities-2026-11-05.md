# Answer to your priority question (outbox/2026-11-05-request-priorities-for-open-inbox.md), 14:50Z

From the project thread, for Nick (he asked us to deal with you in the repo, not through him).

Do NOT work the ~40-item inbox oldest-first. Most of it is stale. The priority list is the one in `agent/inbox/pause-lifted-restart-order-2026-11-05.md` (commit f09715ac, written 14:19Z, just after your 14:20Z pause-lift commit, so you may not have read it). In order:

1. LoL DK-BLG dry run 22:00Z: confirm armed, report in agent/status/lol-live-capture.md by 15:00Z. Output to /vol2.
2. Cricket-feeds capture restart on /vol2 (wanted until ~17:15Z).
3. tennis-books restart on /vol2, stop by 21:30Z.
4. Fresh `df -h` for /, /vol, /vol2 in agent/status/heartbeat.md.

Everything else in the inbox stays queued and untouched until Nick releases items one by one. Exceptions you may do now, because they are read-only and cheap: none required. Do not start CS2, Dota, HLTV, cross.bet, rescan or gates tasks. If a charter disk-gate refusal blocks an item above, log the figures and move to the next; do not ask the owner again.

Never commit raw data or keys.
