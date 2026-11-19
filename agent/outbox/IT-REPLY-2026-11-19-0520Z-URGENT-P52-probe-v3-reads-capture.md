# P52 Goalserve probe v3 — 19 Nov 2026

- Reviewer offline test: `ALL PASS` (28 checks).
- Launched capture-source probe at 05:39:25Z, PID 2867115, for esports, tennis, hockey_nhl and basketball; 180-minute run. It reads stored payloads and makes no Goalserve requests.
- First preflight at 05:39:48Z: clock offset 0.000200 s; Polymarket lag p10/p50/p90 0.018/0.018/0.023 s; 27,198 PM messages.
- Tennis: all preflight checks passed; 14 live games, 9 matched; 49 polls, 0 errors; accepted market `To Win`.
- Hockey NHL: all preflight checks passed; 2 live games, 2 matched; 49 polls, 0 errors; accepted market `Home/Away`.
- Esports: no live games; 35 polls, 0 errors; no accepted market or match, so preflight did not pass.
- Basketball: 8 live games and 1 match; 49 polls, 0 errors; no accepted winner market, so preflight did not pass.
- Probe remained running at last check; the final JSON and 07:30Z checkpoint are not yet available. No final result is claimed.
- Detailed preflight output is in `agent/status/goalserve.md` under `Goalserve live probe v3 (19 Nov)`.
