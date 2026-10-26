# Read-only book capture around three macro releases: pre-registered rule

Written 26 Oct 2026, before any capture. Approved by Nick 26 Oct 05:44Z. Follows agent/PROTOCOL.md.
Builds on [macro-pickoffs-12m-2026-10-26.md](macro-pickoffs-12m-2026-10-26.md) (addendum of 06:00Z).

## Question

The 12-month scan measured a printed 0-30 s pickoff pool worth $38/day (net, 30% capture, largest day
excluded). Nick's view is that prints undercount the stale depth a fast taker could reach. Break-even
for the $50/day bar needs the reachable pool to be at least **1.31x** the printed pool. This capture
measures the reachable stale depth directly, at 1 s after the release.

## What runs, where, and for how long

- Where: the Composio remote sandbox (1 CPU, 976 MB). Not the project server.
- What: `scripts/bookcap/capture.py`. It reads public endpoints only and places no orders. It needs no keys.
  - REST `POST /books` for every YES and NO token, every 0.25 s.
  - The WebSocket market channel for the same tokens, logged with local receive time.
  - 5 samples of `GET /time` for the clock check.
- Bounds: one process; `RLIMIT_AS` 700 MB; `timeout 900`; capture window R-120 s to R+60 s.
- Cleanup: the output directory is analysed, the summary numbers go into the repo, and the raw files are
  deleted from the sandbox the same day.
- No new capture until the previous one is reported and reviewed.

| Release | Polymarket events | R (UTC) | Window (UTC) |
|---|---|---|---|
| FOMC, 28 Oct | 606422 | 2026-10-28 18:00:00 | 17:58:00-18:01:00 |
| Jobs (Oct), 6 Nov | 1120074 payrolls, 1120075 unemployment | 2026-11-06 13:30:00 | 13:28:00-13:31:00 |
| CPI (Oct), 10 Nov | 1189083, 1189074, 1189688, 1189689 | 2026-11-10 13:30:00 | 13:28:00-13:31:00 |

Release dates checked on bls.gov (CPI 10 Nov 08:30 ET, Employment Situation 6 Nov 08:30 ET) and the
Polymarket FOMC event (decision 28 Oct, 2 pm ET).

## Dry run (26 Oct 05:48Z, event 606422, 35 s, measured)

- 131 polls, 0 errors. Largest gap between polls: 0.25 s. Median round trip: 0.19 s.
- Payload: about 1.5 KB of gzip per poll for 10 tokens. A 180 s window is about 1 MB.
- WebSocket: connected, gave book snapshots, price changes and PONG; 0 errors.
- **The YES and NO books mirror each other exactly.** Each NO bid at q is the YES ask at 1-q with the
  same size. So only the YES book is counted, to avoid double counting.
- **The book `timestamp` field is the time of the last change, not the snapshot time.** It lagged
  local time by up to 56 s. So it cannot be used to time snapshots. Snapshot time is the local send time
  `t0`, and the clock is checked against `GET /time` instead.
- Clock: `/time` returns whole seconds. Local minus server was 0.56-0.94 s over 3 samples, which is
  what a correct clock gives (server floors the second). So the local clock is right to within about 0.5 s.

## Definitions (fixed now)

For each market (one outcome bracket) the winner is read from the resolved `outcomePrices` after the
event settles. v = 1 for the winning YES token, v = 0 for a losing one. Fee f(p) = 0.05·p·(1-p) per share.

- **Stale value S at one snapshot** (YES book only, net of taker fee):
  - Winning YES: sum over asks at price p of (1 - p - f(p)) × size, where that is positive.
  - Losing YES: sum over bids at price p of (p - f(p)) × size, where that is positive.
- **S_pre**: S at the last snapshot with t0 < R.
- **S_reach**: S at the first snapshot with t0 ≥ R + 1.0 s. This is the depth a taker who acts 1 s after
  the release could still reach, before anyone else's fills are subtracted.
- **P**: the printed 0-30 s pool for the same release, from data-api trade prints, net of fees, computed
  the same way as in the 12-month scan (scripts/macro12m).
- **RP** = max(P, S_reach). Prints that happened are reachable by definition; resting stale depth at 1 s is
  added only where it is larger.

## Pass/fail

- **Pass:** ΣRP ≥ 1.31 × ΣP, summed over the captured releases. Per-release ratios are reported too.
- **Fail:** ΣRP < 1.31 × ΣP.
- After FOMC alone, the ratio is reported as a partial result; the verdict waits for all three.
- If a release has P = 0 and S_reach = 0 (no surprise), it is reported and kept in the sums.

## Data gates (if any fails for a release, that release gives no number)

1. Median snapshot rate ≥ 2 Hz and no gap over 2 s between R-10 s and R+30 s.
2. Every token of the event appears in every snapshot used.
3. Clock: local minus `/time` within [-0.5, 1.5] s for all 5 samples.
4. Sanity: S_pre ≥ S_reach. If this fails the snapshot is suspect and is checked by hand.
5. The process stayed under its memory cap and ended before its time limit.

## What fails if the capture fails

- Sandbox recycled or unreachable at the wake: the script is re-uploaded at each wake, so only a
  sandbox outage loses the release. That release is then missing and the verdict uses the others.
- Rate limit (HTTP 429) or errors: gate 1 fails and that release gives no number.
- Polymarket changes market ids or adds brackets: the script reads them at start, 2 min before R.

## Limits of the method (estimated, not measured)

- S_reach counts all stale depth at 1 s as reachable by us. Other bots take from the same depth at the
  same time, so it is an upper bound on what one taker gets. The 30% capture share from the scan still
  applies on top.
- 4 Hz polling cannot see orders placed and cancelled within 0.25 s. The WebSocket log is kept to check
  this later; it is not part of the pass/fail.
- Three releases is a small sample. A pass is a reason to keep going, not a go-live signal.
