SETTLED.md cited: reviewer/SETTLED.md at commit e2a25c41beffd3f4438590a691fc2ed07402838b (A8, A9 apply). Part of the answer to reviewer/CHASE-2026-11-19-gas-and-perp-open-HARD.md; locked rule in reviewer/REPLY-2026-11-19-gas-and-perp-open.md (89a146df).

# Gas sizing run: 15-minute plausibility check, 19 Nov 02:30Z. RESULT: FAILED, restarted

**1. Goal.** Strategies that reliably make $200/day before rebates (A9).
**2. Where we stand.** No gas sizing number yet. First full run (60 days, 47 series, code blob ad96c371, committed in PR #440 squash 1271afdc, `scan/gas_sizing/`) started 02:16Z.
**3. The item that matters most.** At 02:30Z the run had produced **zero output lines and zero result files and the process no longer existed** (`full.log` empty, `full/` empty, no python process). That is implausible: the 20-day single-series smoke run on the same code had finished in about 3 minutes. Per the standing rule I treated it as failed, not "slow".

Cause (inferred, not proven): the process was lost when the cloud sandbox was restarted or snapshotted between my turns; `dmesg` shows a fresh boot and the new process id is low (223). The run had no checkpointing, so nothing was kept. I cannot show a code fault: the 8 can-fail tests pass (`scan/gas_sizing/test_gas_sizing.py`, 8 of 8) and the smoke run (series KXAAAGASD, 20 days, 270 API calls, 49 HTTP 429 retried) returned plausible counters (368 markets, 20 events, 216 near-print strikes, 474 entries out of band, 158 beyond life).

Fix (committed after the run, see below): per-series checkpoint files (`full/cache/<series>.json`, each finished series reloaded after a restart, window pinned by `--now` so a resumed run uses the same 60 days), cache writes guarded so a write error cannot kill a worker, detached start (`setsid`), 6 workers at 8 requests/second. Code blob 9ff59e77 (local, tests 8 of 8 pass); I will push it to `scan/gas_sizing/gas_sizing.py` in a follow-up PR and cite that commit with the result.

Restart: 02:31Z, window end `--now 1795055463` (stored in `now.txt`). Next check due 02:46Z: series completed, rows, events per series, calls, 429s, failures. Same expectations as the locked rule (1 + 12 + 35 series, about 60 events each, 2-5 qualifying strikes per event-day). Result still targeted for 06:00Z; the estimate is about 38,000 API calls at 8 requests/second, about 80 minutes, so about 03:55Z if nothing else breaks. This is an estimate, not measured.

Confidence 8/10 on the diagnosis of the lost process; 6/10 that the 06:00Z target holds (Kalshi rate limits are unmeasured at 8 requests/second).
