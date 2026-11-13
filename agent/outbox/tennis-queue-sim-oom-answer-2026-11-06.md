# OUTBOX — tennis-queue-sim step 3 re-run after fix: still OOM at 1.5 GB cap

Addresses: agent/inbox/tennis-queue-sim-oom-answer-2026-11-06.md (reviewer answer, 6 Nov 01:05Z)
From: server member. Round 2026-11-06T01:5xZ.

## RESULT
- Ran step 3 exactly as released: fixed `queue_sim.py` (1faba85f/26d12382, stream-twice + top-12)
  under `systemd-run --unit=qsim-nov5-3 -p MemoryMax=1600M -p MemorySwapMax=0`, venv python
  (numpy present), all three recorder runs + first root-run books/markets added.
- Input: 1,705,382 book rows (v2 1,048,467 + HC 130,759 + root rn1 526,156) / 12,871 market rows.
- Outcome: **kernel OOM-kill again** (systemd 'oom-kill', exit 143). Unit consumed **1.5G memory peak**
  over 51.4 s wall / 46.4 s CPU, then the kernel killed it — the fixed script still exceeds the
  1.5 GB cap on the full merged input.
- Per the release line ("If it still OOMs at 1.5 GB, stop and report the peak; do not raise the cap")
  I stopped and did NOT raise the cap.

## DATA
- Unit: `qsim-nov5-3.service` (failed, oom-kill). Launcher: /root/pkarbs/run_qsim_nov5.sh.
- Prior attempt at same cap before the fix also OOM'd (same peak) — so the stream-twice fix did not
  get the full merge under 1.5 GB.

## OPEN / NOT VERIFIED
- The >=20 Pinnacle-match full-merge run has NOT produced output; the box cannot fit it at the
  approved 1.5 GB cap.

## Need (owner decision, no Nick button — not a code change / restart)
- Option A: raise MemoryMax for this one bounded run (box 7.7 GB total, ~4.8 GB free; prior 7-match
  run used a smaller set and succeeded — the full merge is the >=20 attempt).
- Option B: scope books input down (one or two runs, or a time window) and accept fewer matches.

Count: notes answered 1 (re-run attempted, still gated), outstanding 1 (step 3 result).
