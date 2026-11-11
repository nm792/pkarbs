# RESULT — rugby CLOB WS probe (bounded, read-only, ~160 s)

APPROVALS NEEDED: none.

RESULT:
- Ran the probe as given (`nice -n 19 python3 agent/tasks/rugby-clob-ws-probe.py`) against window C tokens. All FOUR subscribe variants delivered frames from this box:
  - A_default_ua: 4 frames (1 snapshot len 4014 + 3 PONG)
  - B_custom_ua:  4 frames (2 snapshots + 2 PONG)
  - C_initial_dump: 4 frames (snapshots + PONG)
  - D_yes_only:    4 frames (snapshots + PONG)
- Every "snapshot" frame is a real booked market (bids present), not an empty heartbeat. So a snapshot MUST arrive and DOES arrive for all four subscribe variants over the same window-C tokens that the capture connects to and gets 0 frames from.
- => The custom `user_agent_header` (variant B) is NOT the cause: B receives frames exactly like the library default (A). The 7 Nov 0-frame capture is not explained by the UA.
- First frame head (A and B identical market): market 0x800d27… / asset_id 1063059783398… / ts 1794127438914 (booked bids listed).

DATA: rugby/probe_clob_variants.jsonl (16 lines), rugby/probe_clob_variants_stdout.txt (4 summary lines). No IPs/hostnames.

OPEN / NOT VERIFIED: none for the probe question. The capture's 0-frame root cause remains open — UA ruled out; likely the capture process env or subscription construction (patch 4's watchdog/REST-fallback approach would still cover a silent WS regardless of cause). Apply the approved patch per approval when granted.

Count: notes run 1, outstanding 0, PENDING open 0.
