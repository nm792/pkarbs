# agent/status/cricket-npl-live

state: RUNNING — window A (id 1558593, Biratnagar Kings v Janakpur Bolts) live since 06:30Z,
255 min; window B (id 1558594) due 10:30Z, 255 min.
- procs: 450231 (timeout wrapper) / 450232 (live_pbp_logger), started 06:30Z, etime growing.
- out /root/cricket-live, share /root/cricket-live/share.
- After window A ends, launch window B via the same systemd-run/scope wrapper; never overlap.
heartbeat: 2026-11-03T08:2xZ
