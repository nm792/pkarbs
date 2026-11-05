# Technical requirements for a TheSports trial (5 Nov 2026)

Text to send to TheSports is in section A. Section B is our internal reasoning (do not send).

---

## A. To send to TheSports

Thank you for the quote. Before we commit we would like the free trial, and we will judge it on **speed** (time from the real event to your message reaching our server). Our requirements:

### 1. Delivery (all sports)
- **Push only** (your MQTT over WebSocket/TLS, or a WebSocket). We will not use HTTP polling for live data.
- **One message per event.** No batching, conflation or throttling (for example, not "latest state every 2 s").
- Each message must carry:
  - `event_ts`: when the event happened, UTC, **milliseconds**, from your source (scout entry, official feed or game server);
  - `send_ts`: when your server published it, UTC, milliseconds;
  - a match id, a per-match **sequence number**, and a flag when a message corrects or deletes an earlier one.
- Reconnect with replay of missed messages (by sequence number).
- We connect from one server with a **fixed IP** (we will send it for your whitelist). Please tell us where your broker is hosted.

### 2. Speed we need (event to delivery at our server)
| Sport | Median | 95th percentile |
|---|---|---|
| Tennis (ATP, WTA, Challenger) | 1 s or less | 2 s |
| League of Legends | 2 s or less | 4 s |
| Counter-Strike 2 | 2 s or less | 4 s |
| Dota 2 | 3 s or less | 6 s |
| NBA | 2 s or less | 4 s |
| NFL | 1 s or less | 2 s |

### 3. Events we need, per sport
- **Tennis:** every point (point winner, full score after the point: sets, games, points, tiebreak points), server, plus match start, end, retirement/walkover and suspensions.
- **League of Legends:** every kill (killer, victim, team, game time), towers, inhibitors, dragons, Baron, Herald/other epic monsters, team gold at least every 5 s, game start and end. Pro leagues: LCK, LPL, LEC, LCS, Worlds/MSI.
- **CS2:** every kill (killer, victim, side, weapon, headshot), bomb plant/defuse/explosion, round start and end (winner and reason), players alive per side, team money or equipment value at round start, map start and end. Tier 1 and tier 2 events.
- **Dota 2:** every kill, towers, barracks, Roshan, team net worth at least every 5 s, game start and end. Tier 1 and tier 2 leagues.
- **NBA:** every play (made and missed shots, free throws, fouls, turnovers, timeouts) with game clock and score.
- **NFL:** every play (down, distance, yard line, play type and result, score, game clock).

### 4. Questions
1. **Source, per sport:** where does the data come from: your own scouts at the venue, an official data feed, the game server (esports), or a TV/stream broadcast? Esports broadcasts usually run on a delay of minutes; do you get data ahead of the broadcast?
2. **Measured latency, per sport:** your median and 95th-percentile time from the real event to `send_ts`, and how you measured it.
3. Do your messages already carry `event_ts` and `send_ts` in milliseconds? If not, can you add them for us?
4. Does MQTT push cover **all** the events above (point-by-point tennis, kill-by-kill esports, play-by-play NBA/NFL) during the trial, or are some only on HTTP polling?
5. Where is your MQTT broker hosted (country/city, cloud)? Do you have a broker in Europe?
6. Is your data licensed for **automated trading on prediction markets**? Any restriction?
7. Trial: 15 days from which date? Which endpoints and topics are included? Can it start when we send our IP, and can it run to at least **18 November** so it covers BLAST Slam (Dota 2) and the Worlds final (LoL)?
8. Can we buy single sports (for example tennis only, or LoL only) at the prices you quoted?
9. Do you sell **historical** point-by-point / kill-by-kill data with millisecond event timestamps?
10. Uptime commitment, and what happens during an outage (status page, notifications)?

---

## B. Internal: why these numbers (do not send)

Every figure is measured against the **Polymarket price**, never the play. A feed only earns if it reaches us before the price moves, because the queue at our price fills within about 1 s after the move (CS2 queue study, 4 Nov).

| Sport | What we have now (vs PM price) | Value by feed delay (sim / upper bound) | Pay $/mo (= $/day) | Worth paying if |
|---|---|---|---|---|
| Tennis | Cito ~20 s after the price; Pinnacle only ~2.4 s before PM onset | Upper bound $3.97/match 5 s before onset, $1.99 at onset, $1.29 at +2 s, ~$0 by +5 s; ~$120-260/day at 0 s, optimistic (no queue) | $300 ($10) | point arrives at or before the price move |
| LoL | PM free stream 10-12 s after the price; Riot ~45 s | Kills-only sim ~$43/game at 2 s vs ~$20/game at 12 s (free) | $200 ($6.7) | under ~3 s; Worlds ends 14 Nov, then offseason to Jan |
| CS2 | Our feed 16.5-23 s behind; price moves on kills ~32 s before round updates | ~$250-300/day estimate at +20 s (PR #49, now at risk from queue result) | $200 ($6.7) | kill-level under ~2 s |
| Dota 2 | Valve 5-15 min behind on PM leagues (~$0) | Sim ~$430/day at 0 s, ~$270/day at 20 s, $0 by 90 s | $200 ($6.7) | under ~30 s would already help |
| NBA | PM WS 5.8 s after the play (free) | Sim ~$290/day at 0 s, ~$240 at 2 s, ~$125 at 5 s (PROVISIONAL, timed vs play not price) | $200 ($6.7) | under ~3 s |
| NFL | PM WS every 5 min; ESPN play time ~17 s after price | ~$15/day upper bound even at 0 s; real money only 5-10 s BEFORE the price | $200 ($6.7) | effectively never; trial only, don't buy |

Notes:
- Each sport's price is under $10/day, so cost is not the question; **speed is**. One sport that meets its target pays for the whole $1,300.
- LoL is per game and NBA/tennis/CS2/Dota are per day; don't add them.
- TheSports is AiScore's supplier (a livescore-app feed); our prior is that it's about as fast as Cito (6/10). The trial decides.
- The targets in section A are tighter than the "worth paying if" column on purpose, so we learn their real speed.
