# Outbox: keep all sports-WS messages — Gated on Nick (restart required)

Round ~07:05Z, 2 Nov. Re: agent/inbox/2026-11-02-ws-keep-all-messages.md (07:00Z).

The running CS2 logger writes raw frames only for `leagueAbbreviation === 'cs2'` (logger.js line ~24:
`if (g.leagueAbbreviation !== 'cs2') return;`). To keep EVERY sports-WS message (cricket incl. Nepal
Premier League on 3 Nov, WTA, college basketball) the league filter must be removed and the node
process restarted. It runs as `cs2-logger.scope` (systemd-run, MemoryMax=512M, timeout 43200) and will
not read source changes until restarted.

Per the note itself ("do not restart the logger… if the change needs a restart, tell us in outbox
first") and protocol (code change + restart/kill → Nick), I am NOT touching the running logger.

Ask to Nick (one line): "Approve removing the league filter from cs2-ws-logger logger.js and
restarting cs2-logger.scope so the raw capture keeps all sports-WS messages (incl. NPL cricket 3 Nov)?"

The capture is byte-identical until then: no messages are lost now, only non-CS2 frames are not
persisted. The CS2 run continues on the original config; pass/fail per its 12 h fixed gate.

Status: agent/status/cs2-ws-logger.md updated to note this pending gated item.
