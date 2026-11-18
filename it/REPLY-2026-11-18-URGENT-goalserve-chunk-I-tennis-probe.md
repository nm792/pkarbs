# URGENT: Goalserve feeds to IT, 18 Nov 2026 10:15Z: tennis probe (chunk I) and P21

1. **Goal:** run a tennis look in parallel with esports (Nick, 08:04Z); tennis data should count from 19 Nov 00:00Z.
2. **Measured position:** chunk H (4908eea2a6): capture PID 4045212 running since 17 Nov 09:00:06Z; tennis hour files present for 18 Nov, keys `body` and `recv_ns`. The 18 Nov poll rows sit in `goalserve_20261117.jsonl` (log name fixed at capture start), so the poll-log glob must include that file; my daily chunk already uses `goalserve_2026111*.jsonl`.
3. **Most important item:** please route chunk I (agent/inbox/TO-IT-CHUNK-I-probe-goalserve-tennis-payloads-2026-11-18-1010Z.md, squash 322d8129): read-only, prints market names and league strings from two tennis hours. I need it by 12:00Z to write the tennis pre-registration today. Also please confirm P21 (chunk F, esports) is open for 19 Nov ~01:00Z.
