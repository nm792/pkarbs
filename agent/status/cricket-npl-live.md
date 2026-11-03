# agent/status/cricket-npl-live
state: PREP — window A (id 1558593, Biratnagar Kings v Janakpur Bolts) not yet open; starts 2026-11-03 06:30Z, 255 min. Window B (id 1558594) 10:30Z, 255 min.
- logger script evrules/live_pbp_logger.py present on origin, py_compile OK.
- launch command per task: systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 15600 python3 -m evrules.live_pbp_logger cricket <id> --minutes 255 --every 5 --out <cricket dir> --share <cricket dir>/share
- nothing to run yet this round (window opens 06:30Z); will be launched as a tracked bound capture when due.
heartbeat: 2026-11-03T04:20Z
