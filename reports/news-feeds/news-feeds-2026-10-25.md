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

---

## Addendum (12:40Z): "choose where to scan", not "be faster"

Nick's reframe: if we know a big stimulus is coming and volume in those contracts is rising,
larger gaps that can fill at scale are more likely there, so the calendar should decide where
the scanner looks.

### A. Does more activity mean bigger, deeper, fillable gaps? (measured on our 12-hour shadow)

Data: `reports/sports-mece/hours/*/per-run-*.csv` (24 Oct 21Z to 25 Oct 08Z), 533 gap runs on
93 in-play soccer events, each run at delay 0 and at the real 1 s delay. Events split into
thirds by how many gap runs they produced (a proxy for how busy the book was; it is ex post,
see C).

| Third (31 events each) | Gap runs | Median size at the gap (shares) | Edge per run at delay 0 | Seen $ at delay 0 | Sets traded | Full fills at 1 s | P&L at 1 s |
|---|---|---|---|---|---|---|---|
| Busiest | 414 (78%) | 14.8 | $0.38 | $79.0 | 48 | 8 | **-$287.1** |
| Middle | 88 | 12.5 | $0.18 | $14.5 | 15 | 1 | -$106.8 |
| Quietest | 31 | 10.0 | $0.46 | $3.5 | 3 | 1 | -$9.7 |

**[ours, measured]** Busy events do hold most of the gaps (78% of runs, 82% of seen $), and
size at the gap is a little larger (median 14.8 vs 10-12.5 shares, +20-50%). But the loss
per traded set at 1 s is about the same (-$6.0 busy, -$7.1 middle, -$3.2 quiet). Pointing the
scanner at busy events would give more of the same trade, not a better one: the sign stays
negative.

### B. Would priority polling raise executable size per alert?

- **Sports (Polymarket):** no. The logger already takes every book update over the WebSocket,
  so every gap is seen. What loses money is the 1 s order delay, not missed gaps. **[ours]**
- **Cross-venue and Kalshi (REST polling):** in principle yes, but the 20 Oct pass found quotes
  unchanged across two passes 25 minutes apart (193/195 kept). Polling faster is not what
  limits us there either; the gap is negative after fees. **[ours]**
- Where it could matter: scheduled spikes on markets we only poll (Kalshi CPI/FOMC, election
  night). There, volume and spread both jump at the release second, and the makers who
  reprice are faster than a 1 s taker **[estimate]**. A calendar that raises the polling rate
  for those windows costs nothing, but I can't size the gain without data from a release
  window.

### C. What this does not measure

Run counts are known only after the fact. The useful version needs a signal we have
*beforehand*: event volume, `volume24hr`, time to kickoff, league. That needs gamma metadata
for these 93 events, a cheap public pull. The remote sandbox used for earlier public pulls
failed on every call today, and pulling it through the page fetcher costs about 20 KB per
event, so I left it out. Not done.

### Sizing against $50/day

On the sports data, focusing on busy events changes nothing that would reach $50/day: about
-$24/hour in the busiest third versus about -$34/hour in all events (12 hours, -$403.6 total, matching the all-hours report). A calendar plus volume
ranking is free and worth having inside the scanner once something is positive, but it does not
make a negative trade positive. For a non-sports scheduled event we have no data: the
election-night (midterms) and a CPI or FOMC window would be the tests. Logging one CPI or FOMC
release on Kalshi or Polymarket (public trades or prices) is a desk-sized check.

**Confidence 6/10** that calendar or volume targeting does not lift P&L to the bar (the sports
result is measured; whether we can rank events in advance, and non-sports, are estimates). To
reach 9:
(1) gamma volume and kickoff for the 93 events, to check whether ranking in advance matches the
after-the-fact split;
(2) public trades and price history around one CPI or FOMC release and one big match kickoff, to
measure depth and gap size in the event window against quiet hours.

---

## Addendum 2 (13:05Z): the two open checks, run

Data access: the Composio sandbox failed on every call again ("Failed to execute bash command in
sandbox", 5 tries, 12:15-12:30Z), and this container's proxy refuses Polymarket hosts. Pulled
instead through the TinyFish page fetcher, which writes large responses to disk:
gamma `/events?id=...` for the 93 matches, and data-api `/v2/trades?event_id=..&limit=500`
for release events. Scripts and inputs: `reports/news-feeds/scripts/`.

### Check 1: can we pick the busy matches before kick-off? **[measured]**

Target: the 31 matches (of 93) with the most gap runs in the 12-hour shadow (78% of runs).
Pick 31 matches with each rule and count how many are in the busy third.

| Rule (31 picks) | Known before kick-off? | Busy matches caught | Share of all gap runs | P&L at 1 s on picks |
|---|---|---|---|---|
| Random pick (10,000 draws) | yes | 10.3 on average (95th pct 14) | 33% (95th pct 45%) | n/a |
| Minutes of the match inside the scan window | yes | 15 | 48% | -$261 |
| League prior: median volume of other matches in the same league | yes | 16 | 50% | -$157 |
| League prior x minutes in window | yes | 15 | 49% | -$188 |
| Total match volume | **no** (includes in-play volume) | 22 | 67% | -$311 |
| Busiest third itself | no | 31 | 78% | -$286 |

- Pre-game rules do better than random, a little above the random 95th percentile: they catch
  about half the gaps where a random pick catches a third. MLS (18 matches, 143 runs) and
  Brazil Serie A (9, 109) are where the gaps were.
- Total volume catches more (22/31), but most of it trades in play, so it is not known before
  kick-off. True pre-game volume would mean paging all trades before kick-off for each match
  (data-api has no windowed volume route); not pulled.
- Every pick still loses at the 1 s delay. Ranking changes where the losses happen, not the sign.

### Check 2: scheduled releases on Polymarket **[measured, 4 release days]**

Each release market's public trades by seconds after the official time. "Pickoff edge" is
profit to the takers who hit quotes still resting at pre-release prices, valued at the
settled outcome. That is the stale-gap pool a release creates. Timestamps are on-chain
settlement times, a few seconds after the match, so "0-10 s" means the first few seconds.

| Release (official time) | Polymarket event | Notional, first 30 s | Pickoff edge 0-10 s | 11-30 s | 31-300 s |
|---|---|---|---|---|---|
| Sep CPI, 14 Oct 12:30Z | Annual CPI | $14.1k | $219 | $428 | $0 |
| | Monthly CPI | $3.5k | $222 | $87 | $0 |
| | Core CPI MoM | $11.9k | **$4,707** | **$2,142** | $0 |
| Aug CPI, 11 Sep 12:30Z | Core CPI MoM | $2.0k | $257 | $1 | $0 |
| | Core CPI YoY | $1.8k | $118 | $0 | $0 |
| FOMC, 16 Sep 18:00Z | Fed decision | $33.5k | $199 | $229 | $101 |
| Sep jobs, 2 Oct 12:30Z | Payrolls | inconclusive (could not infer the winners for most brackets) | | | |

What this shows:
- **Volume spikes 20-100x at the release second.** For example, annual CPI did $736 in the
  half hour before and $15.1k in the half hour after, almost all of it in the first 30 s.
- **The release creates real gaps, and they are gone within about 30 s.** Nothing after
  30 s except FOMC ($101).
- **The size is lumpy.** One release (Sep core CPI) held $6.8k because a resting ask at 0.32
  on the winning bracket ("0.3%") kept being bought from +8 s to +20 s, 4,000+ shares. The
  other five events held $0.1-0.6k each.
- Before the release: no leak. Trades in the 10 minutes before were small ($0-100 each) and
  at pre-release prices.
- This is a speed race again: whoever reads the number first (BLS posts at 8:30:00 ET) takes
  it. These markets have no sports delay **[estimate: `secondsDelay` was set only on sports
  markets in our earlier reads]**. The first fills settle at +6-8 s, so the fastest takers
  matched within a few seconds.

### Sizing against $50/day **[estimate]**

- Scheduled US macro releases with Polymarket markets: CPI 12, jobs 12, FOMC 8, plus PPI and
  others, so about 35-40 per year.
- Pool per release day from this sample: median about $0.4-0.7k, one outlier at $7.8k.
- If we caught 10-30% of the 0-10 s pool with a sub-second taker that reads the release
  source directly: about $40-200 per release, or roughly **$5-20/day averaged over a year**.
  It comes in a few lumpy days, and the fastest bots already take most of it.
- It needs no paid feed: the BLS, BEA and Fed pages and the calendar file are free. It does need
  a parser per release and a pre-armed order per bracket. The losing risk is a parse error at
  release time, which is a catastrophic-loss risk.

### Updated recommendation

1. Sports: don't use calendar or league ranking to rescue the in-play set arb. It picks about
   half the gaps from a third of the matches, but they still lose at 1 s (measured).
2. Scheduled macro releases are where Nick's thesis holds: volume and executable gaps both jump
   at a known second. It is a small, lumpy, speed-bound pool (about $5-20/day, estimated),
   below the bar on its own. It is the most promising lead in this thread. The next desk step,
   no server: run the same trade scan over the last 12 months of CPI, jobs, FOMC and PPI
   events to get a real distribution per release, and check how many of the first fills went to
   one wallet (data-api rows carry the taker wallet).

**Confidence:** Check 1 **8/10** (measured; one 12-hour sample; true pre-game volume not pulled).
Check 2 **6/10** on the size (4 release days, high variance, timestamps are settlement times,
winners inferred from post-release prices, jobs inconclusive). To reach 9: (a) 12 months of
release events through the same script, about 40 fetches; (b) one bounded live test that times
our order against a release (needs Nick's go-ahead and the Polymarket account active).
