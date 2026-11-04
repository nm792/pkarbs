# GameScorekeeper (GSK) as a faster esports feed — 4 Nov 2026

Source: gamescorekeeper.com (/coverage, /esports-data, /esports-betting-industry, /terms) and docs.gamescorekeeper.com,
read 4 Nov 12:20Z via TinyFish (gamescorekeeper.com and api.gamescorekeeper.com are NOT on the sandbox allowlist). Raw page text in raw/.

| Question | Finding |
|---|---|
| Company | GameScorekeeper ApS, Aarhus, Denmark, founded 2016. Clients quoted: Pinnacle (trading director), DraftKings, PrizePicks. |
| Titles | CS2, LoL, Dota 2, CoD, HoK, AoV, MLBB, Wild Rift, R6, Valorant, Overwatch, Rocket League. CS2 7,800+ matches/600+ tournaments a year; LoL 13,000+/500+; Dota 5,000+/300+. No tournament list; live data exists only for fixtures that carry a "v2live" link, so IEM/BLAST/LCK live coverage can't be confirmed without a key. |
| Live detail, CS2 | Push events: map/half/round start-end-void, every kill (killer, victim, weapon, headshot), assist, flash assist, suicide, bomb plant/defuse/explode, end-of-round equipment; optional full state every 10 s. Kill-level. |
| Live detail, LoL | Kills, towers, inhibitors, dragons (type), baron, map winner; full state (gold, kills, CS, HP per player) every 10 s. |
| Live detail, Dota | Only map started/ended/winner plus full state every 10 s. No kill events. |
| Delivery | WebSocket push, one connection per fixture (wss://api.gamescorekeeper.com/v2/live/{fixtureId}); REST 1,000 req/h. |
| Stated latency | None. Only "fast speeds". No number anywhere on site or docs. |
| Data source | Not an official partner. "Our automated data platform continually monitors and collects data from a wide range of online sources... cross-checked between sources." Fixture metadata exposes hltvMatchId/hltvMapIds and demoUrl, which points to HLTV scorebot for CS2. LoL official data is GRID-exclusive, so GSK LoL must come from public sources (lolesports livestats ~55 s behind PM price, or broadcast). Dota likely Valve's delayed spectator API (5-15 min behind PM price, measured 4 Nov). |
| Betting use | Allowed: it is their main market ("market creation, odds modelling and bet settlement"); Pinnacle is a client. Terms: Danish law, strict no refunds on activated subscriptions. |
| Price / trial | No published price (Datarade also says unpublished). Terms mention a "free trial account". Account only via contact@gamescorekeeper.com / sales@gamescorekeeper.com. |

## Verdict
- Dota: no use (no kill events; source is the delayed feed we already measured).
- LoL: unlikely to beat the price; best public source is PM's own sports stream (12 s) and Riot's official feed is GRID-only.
- CS2: the only possible value. If it is HLTV scorebot speed, kills arrive roughly when PM bots see them, so at best par with price, not ahead. (Correction 12:20Z: the later queue study found bots reprice within ~1 s of the event, so the queue is not stale and a feed AHEAD of the price would help; the queue is not a separate blocker. HLTV's own kill-vs-price delay is measured 4 Nov 13:00-16:00Z in thread "Time HLTV live scoreboard on CS2"; GSK's CS2 speed is likely the same.)
- Worth one free-trial email at most, to time CS2 kills vs PM price on one match; not worth paying for. Confidence 6/10.
