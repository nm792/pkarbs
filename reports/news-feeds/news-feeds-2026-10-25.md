# News and sports feeds as scanner triggers (desk research, 25 Oct 2026)

Question (Nick, 25 Oct 12:04Z): do we need an event calendar or a major news/sports feed
(e.g. Reuters) to warn us of large plunges or jumps in betting markets?

Short answer: **not as a trading signal; yes as a cheap free guard.** A paid wire cannot be
first on the markets we trade, and its cost alone is close to the whole $50/day target. A free
calendar plus Polymarket's own free score feed is worth a small module, but only once we run
resting (maker) orders or the midterms watcher, because today's taker-only scanner has nothing
for it to protect. No server use; nothing here is measured by us unless marked **[ours]**.

Labels: **[ours]** = our own earlier data; **[source]** = read from the vendor's or agency's own
docs; **[secondary]** = press or blog, unverified; **[estimate]** = my reasoning, not measured.

## 1. Kill test: is a feed ever faster than the market?

Three kinds of event, which together cover everything we trade:

| Event kind | What moves the price | Can a wire beat it? |
|---|---|---|
| A. In-play sports (goals, cards) | In-venue scouts / official data, sub-second | **No.** Our 1 s sports delay already loses. **[ours]** The stale-leg pool (~$17.1k over 80 games) was picked off inside the first second; ~$2.4k after it, in a dozen shocks. All 73 unfilled legs in the 12-hour shadow repriced against us. Sportradar markets venue-to-client under 1 s **[source, marketing]**; TV is 3-8 s behind **[secondary]**. A wire headline is slower than TV. |
| B. Scheduled releases (CPI, jobs, FOMC, court opinion days, election-night counts) | The official publication itself, at a known time | **No, and no need.** Everyone watches the same official page at the same second; a wire relays it later. The one case a wire "wins" is an accidental early release, e.g. BLS posted April 2024 CPI ~30 min early and markets did not move until the scheduled time **[secondary: Bloomberg/Benzinga]**. Rare and not repeatable. |
| C. Unscheduled news (resignations, rulings without a docket date, injuries, deaths) | Whoever sees it first: X/Telegram, insiders, then wires | **Sometimes slower markets, but not reachable cheaply.** A secondary write-up claims a median ~80 min for Polymarket to fully reprice after news (Vera Research, 90,633 moves of 2c+, Apr-Jun 2026) **[secondary, could not open source]**. Even if true, the first move happens in seconds-to-minutes and the "slow tail" is the long-dated markets we already found pay below the ~4% interest rate. To capture it you need a feed faster than X plus a model that maps headline → market, for every market. |

Verdict: for A and B the market is at least as fast as any feed (A from our data, B by
construction). C is the only place a feed could lead, and it is a news-trading business, not an
arb add-on. **Kill test fails for trading.** (8/10; the C-case lag figure is unverified.)

## 2. Feeds, cost, latency, licensing

| Feed | Cost | Latency | Licensing / notes |
|---|---|---|---|
| LSEG Headlines Direct (Reuters, machine-readable) | Quote only, not published **[source]** | Built for event trading, delivered at Equinix NY4 **[source]**; no news latency number published | Enterprise contract; co-location implied. Assume four to five figures per month **[estimate]**, i.e. at or above the $50/day ≈ $1.5k/month target before any edge. |
| AP Elections API (race calls, vote counts) | Quote only **[secondary]** | Not published | Newsroom licence. Relevant only to midterms night; Kalshi midterms pay on swearing-in (3 Jan 2027), so a call matters for price, not settlement. |
| Benzinga Pro / squawk | ~$99-457/month by tier, sources disagree **[secondary]** | "Sub-second" claimed, unverified **[secondary]** | Equity-focused; weak on sports and politics. |
| Sportradar / Genius live data | Enterprise, operator-only **[estimate]** | <1 s venue-to-client **[source, marketing]** | Not sold to individuals for betting use. |
| **Polymarket sports WebSocket** `wss://sports-api.polymarket.com/ws` | **Free** **[source]** | Not stated; docs say data "may be delayed" and is not for trading decisions **[source]** | Streams score, period, elapsed, live/ended for every game, with a `sportradarGameId`; no subscription frame, ping/pong every 5 s. Best free shock signal for our sports work. |
| Polymarket `gameStartTime` (gamma market field) | Free **[source]** | Schedule | PM **auto-cancels resting sports orders at game start** **[source: concepts/markets-events]**, but early starts can beat the cancel. |
| Kalshi `GET /milestones` (start_date, end_date, linked event tickers) | Free **[source]** | Schedule | Venue-canonical event times. Nick's Kalshi profile is locked, but this is public data. |
| BLS iCalendar `bls.gov/schedule/news_release/bls.ics`; Fed FOMC calendar | Free **[source / secondary for Fed JSON]** | Schedule | Covers CPI, jobs, PPI, FOMC; release at 8:30 ET / 14:00 ET. |
| Free news (Google News RSS, GDELT, X lists) | Free | Minutes for RSS/GDELT; X is fastest but no clean API tier for this **[estimate]** | Useful as a "something happened, pause" flag, not as a trigger. |

## 3. The cheaper use: a calendar that tells the scanner to widen or pause

What it would do:
1. **Pre-event:** flag markets whose underlying event starts within N minutes (kickoff, 8:30 ET
   release, FOMC 14:00 ET, poll close). Pull or widen any resting order; tag any gap seen there
   as "pre-event stale quote, likely to be taken by the release, not by us".
2. **At event:** pause taking for the release minute; a gap that appears at the exact
   publication second is the release, not an arb.
3. **Post-event:** resume after the book has stabilised (e.g. spread back under its pre-event
   median).

Is it worth building now? **Small, yes; urgent, no.**
- Sources are free (rows above), the build is a few hours, and it uses no server.
- Today's scanner is taker-only and the sports set arb is closed; the calendar would mostly
  *remove* trades, so the P&L effect now is ~$0 **[estimate]**.
- It becomes useful the day we rest orders (any maker leg, pre-kickoff reward farming, the
  midterms watcher on election night). Then it is the cheapest insurance against the
  "catastrophic loss" leg of the goal.

## 4. The other direction: news to avoid adverse selection

This is the better use, and it is the same machinery as section 3 plus the free score feed:
- **Sports:** a score change on the Polymarket sports WebSocket marks a goal moment. Our own
  data says every taker gap in those seconds was a goal moment and lost under the 1 s delay
  **[ours]**. Rule: no new taker set and cancel any resting quote for X s after a score change.
  This would have avoided most of the -$412 unwind loss in the 12-hour shadow **[estimate]**,
  but it also removes almost all trades, so the net is "don't lose", not "earn".
- **Maker quotes:** cancel-on-shock is exactly what the maker idea needs, but the earlier upper
  bound already assumed near-perfect cancels and still needed 3-8% of all in-play maker volume
  for $50/day **[ours]**. The free feed does not change that verdict; its latency is unknown and
  likely behind Sportradar-fed market makers.
- **Non-sports:** a free "headline keyword hit on a market's subject" flag (RSS/GDELT) can pause
  quoting in that market. Value depends on running resting orders there.

## Recommendation and sizing against $50/day

| Option | Expected $/day | Cost | Call |
|---|---|---|---|
| Paid wire (Reuters/AP/Benzinga) as a trading trigger | ≤0 net: no lead on A/B, C needs a separate news-trading model | $100s to $1,000s+/month | **Don't buy.** |
| Free calendar (PM gameStartTime, Kalshi milestones, BLS ics, FOMC) | ~0 now; protective once resting orders exist | Few hours, no server | **Build when the first resting-order strategy or the midterms watcher goes live.** |
| Free PM sports score WebSocket as a shock guard | ~0 now (avoids losses, not a profit source) | Free | **Log it alongside books in the next approved job** so we can measure its lag vs the book. |

None of these gets closer to $50/day; they lower tail risk. The profit question is still the
one in project memory (midterms MECE one-offs, maker ideas), not the trigger.

**Confidence: 7/10.** To reach 9:
1. Measure the Polymarket sports WebSocket's lag vs the first book move on a few games (one
   bounded logging job, needs Nick's go-ahead under agent/PROTOCOL.md). If the feed leads the
   book by more than ~1 s, section 4 becomes a possible edge and needs re-sizing.
2. An LSEG Headlines Direct quote (sales contact) to replace the cost estimate.
3. The primary source for the ~80 min Polymarket repricing claim (could not be opened from here).

Sources:
- Polymarket docs (local copy `/mnt/project-files/polymarket-docs/`): sports WebSocket, `gameStartTime`, auto-cancel at game start.
- [LSEG Headlines Direct fact sheet](https://www.lseg.com/content/dam/data-analytics/en_us/documents/fact-sheets/lseg-headlines-direct-fact-sheet.pdf)
- [Kalshi targets and milestones](https://docs.kalshi.com/getting_started/targets_and_milestones)
- [BLS dissemination / schedule](https://www.bls.gov/about-bls/dissemination.htm)
- [Bloomberg: BLS posted April 2024 CPI early](https://www.bloomberg.com/news/articles/2024-05-16/us-bls-says-april-cpi-data-inadvertently-posted-30-min-early); [Benzinga on the same](https://benzinga.com/economics/macro-economic-events/24/05/38873168/us-inflation-data-prematurely-released-by-accident-yet-traders-missed-golden-oppo)
- [Sportradar sports data](https://sportradar.com/betting-gaming/products/betting/sports-data/?lang=en-us)
- [Crypto Briefing on Polymarket repricing lag](https://cryptobriefing.com/polymarket-repricing-lag-80-minutes/) (secondary, not opened)
- [Benzinga Pro pricing tracker](https://subger.com/en/service/benzinga-pro-sub) (secondary)
- Our data: /mnt/project-files/sports-mece/intragame-edges-2026-10-25.md (branch claude/project-thread-fzn6mu), reports/sports-mece/all-hours-2026-10-25.md
