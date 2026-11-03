# Status: Nepal PL live ball-by-ball capture, 3 Nov 2026 (ESPN feed lag vs Polymarket)

state: PICKED UP — dry run PASS; windows now ACTUALLY SCHEDULED (at jobs 2,3) 3 Nov
last agent write: 3 Nov 01:34Z (recorded real at-jobs; prior outbox had described, not scheduled)

- Task: agent/tasks/TASK-cricket-npl-live-2026-11-03.md.
- Dry run `--minutes 0.2` id 1558592 (2 Nov 15:47Z): polls 3, empty 0, rows 7, exit 0. Feed healthy.
- Windows (one process each, MemoryMax 300M/swap0, timeout 15600 — bounded, in-repo, no P&L):
  - A id 1558593 (Biratnagar v Janakpur) 3 Nov 06:30Z, 255 min — at job 2.
  - B id 1558594 (Lumbini v Pokhara) 3 Nov 10:30Z, 255 min — at job 3 (kills lingering A first).
  - B starts 15 min before A ends; job 3 kills A on result first, confirm stopped.
- Run cmd: systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 15600 python3 -m evrules.live_pbp_logger cricket <id> --minutes 255 --every 5 --out /root/cricket-live --share /root/cricket-live/share
- Outputs: /root/cricket-live/*.jsonl; commit to rn1/scores/cricket/live-2026-11-03/; trades_<id>.json after each.
- Next: run A 3 Nov 06:30Z (at 2); report pass/fail per window + ps/free in this status after each.
