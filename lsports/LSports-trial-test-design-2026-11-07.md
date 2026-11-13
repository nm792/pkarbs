# LSports trial: test design (prepared 7 Nov 2026, trial starts next week, deferred by Nick 6 Nov)

Purpose: decide with data whether any LSports product reaches our server before the Polymarket (PM) price moves. Paper only, no live orders. Every delay is quoted against the PM price, and every lead sits next to a random-time placebo. Unproven = "unknown, settled by X".

## 1. What to measure (one question per sport)
After a feed event, how many seconds later does the PM price move by at least 2c on the traded side, compared with placebo events at random times in the same matches?

Per sport report: n events, median and 10-90% range of (PM move time minus feed arrival time), the same for 200+ placebo timestamps drawn uniformly inside the same live minutes, share of events where the feed lands first, feed-first events only. A lead counts only if real minus placebo is positive with a bootstrap CI that excludes zero.

## 2. Sports and products, in priority order
1. Tennis, Scouts Feed (venue scouts, "as low as 1 s"). Biggest PM in-play market (ATP $7.9M/day, WTA $5.3M/day). The TheSports tennis result is UNKNOWN, so this is the test that matters.
2. LoL and CS2 (Worlds ends 14 Nov, CS2 Major 25 Nov), only if LSports confirms kill-level events and a source ahead of the broadcast (email Q1, Q5). Otherwise skip.
3. Cricket incl. BBL (12 Dec): ball-by-ball depth is unstated; test only if ball events are on the push feed.
4. NHL, NFL: only if the free trial includes them; low priority. NBA is dropped.

## 3. Verified sides (no co-movement side picking)
- Sides come from the feed's home/away (or team id) mapped to the PM outcome by team name, then confirmed against the settled result: for every match, the event-implied winner share must beat 50% for the real mapping and the flipped mapping must be worse. Matches failing this are excluded and counted.
- LoL: blue/red mapped via the series team sheet, never via price movement.
- Log the mapping per match in a table committed with the results.

## 4. Capture requirements (server agent, Hermes)
- One process, read-only. RabbitMQ/AMQP consumer (stm-inplay.lsports.eu:5672 per their docs), store every raw message with local receive time, and the message's own event_ts/send_ts if present. Record broker clock offset: run NTP check at start and hourly.
- PM side: CLOB market WS books and price_change for the matched markets (same harness as the rugby capture), plus sports WS. Server to PM round trip is 51 ms median.
- Disk: raw to /vol2 per the server charter; 15 GB free twice an hour apart before starting.
- Keep a 24 h first sample, then analyse; do not wait for the full trial.

## 5. Placebo and controls
- Placebo: 200+ random timestamps per match inside live play, same window (-10 to +30 s), same 2c threshold.
- Reverse control: pair each feed event with the wrong match in the same hour; lead should vanish.
- Compare with the free feed (ESPN/PM sports WS) in the same matches; LSports only matters if it beats that.

## 6. Paper-trade step (only after a lead clears placebo)
Post-only bid at the pre-event price or best bid on the side that should rise, cancel after N seconds, act only when the feed lands early, hold to resolution, fills only on trade-through with queue modelled. Delay curve from measured arrival, not the vendor claim.

## 7. Open before the trial starts
- Price, trial length and whether single sports are sold are unknown, settled by LSports' reply to Nick's email (not an open decision for Nick now: deferred to next week).
- Whether their data may be used for automated trading is unknown, settled by email Q6.

Confidence 7/10. To reach 9: the LSports reply on source per sport (Q1), latency (Q2) and which sports the trial includes (Q5).
