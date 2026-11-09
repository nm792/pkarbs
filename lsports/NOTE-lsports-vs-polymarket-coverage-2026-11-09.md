# LSports coverage vs Polymarket in-play sports (9 Nov 2026)

Confidence: 7/10. What would lift it to 9 is at the end.

## What this is
Every sport Polymarket lists with in-play markets, ranked by in-play dollars, against what LSports says it covers live. Polymarket numbers: in-play $/day from `sports-volume/ADV-2026-10-20_11-04.md` (gamma volume of closed events, in-play share measured from v2 trades), plus a gamma snapshot of open events on 9 Nov 00:55Z (gamma `/events?series_id=`, 229 leagues, 6,463 open events). LSports: its public sport pages, Scouts Feed / Hyper Livescore pages and blog posts (read 9 Nov via TinyFish), and the reply LSports sent Nick on 6 Nov (memory `lsports-feed`). Nobody contacted LSports for this.

## How to read the LSports columns
- **Public page**: LSports names the sport and league on its own site. Marketing, not a delivery promise.
- **Reply (6 Nov)**: what LSports wrote to Nick about the HYPER feed: p95 latency is against "officials", NOT against the Polymarket price. Timestamps to the second only, no event_ts, no sequence number. Source undisclosed. Trial 10 days, any sport can be added.
- **Scouts Feed**: only product with venue scouts ("as low as 1 s"). Covers 11 sports, 60+ competitions, 10,000+ events a month, listed sports: table tennis, cricket, handball, baseball, volleyball, soccer, ice hockey, basketball, tennis, American football (+ horse racing in the sport footer). No esports, rugby, MMA, golf, darts or chess on that list.
- **TheSports** (our current trial): NBA, tennis, CS2, Dota 2, a trickle of LoL. No cricket, NHL, NFL.

## Ranked table (all sports with Polymarket in-play volume, nothing left out)

| # | Sport / league | PM in-play $/day (20 Oct-4 Nov) | LSports live coverage | LSports event depth and claimed latency | TheSports has it? | Verdict for the trial |
|---|---|---|---|---|---|---|
| 1 | Soccer, 166 leagues (UCL $2.75M, Serie A $2.28M, EPL $1.96M, LaLiga $1.96M, MLS $1.13M, ...) | $19.15M | Yes, 2,000+ leagues, scouts at venues | Goals, cards, subs, incidents. "close to zero" (no number) | No | Deprioritised (efficient). Only tested as a free side-product of the trial |
| 2 | NBA | $13.79M | Yes, NBA, NCAA, EuroLeague, 900+ leagues; Scouts | "real-time scores, stats and incidents"; reply p95 3 s | Yes | Dropped by Nick |
| 3 | LoL | $10.16M | Yes (reply: kills, towers, Baron etc.); esports API "23 titles, 950,000 fixtures" | Kills/objectives; reply says esports p95 3-7 s vs officials, and ahead of broadcast | Barely (LoL not activated) | **Test first, but the window is short: Worlds final 14 Nov, then off-season to mid-Jan** |
| 4 | CS2 | $8.72M | Esports API yes; blog covers round winners and first kills. But the 6 Nov reply listed no CS2 events | Unknown | Yes (price leads feed 15-30 s) | Only worth it if LSports shows a source ahead of the broadcast. Major 25 Nov is after the trial ends |
| 5 | ATP | $7.83M | Yes. Tennis "Premium", exclusive ATP package; scouts log every point | Per point (who served, who won the point). Reply p95 2-3 s | Yes (point messages being timed) | Test: needs to beat TheSports and the price |
| 6 | Dota 2 | $5.80M | Esports API, blog names Dota hero kills and Roshan. Reply listed no Dota events | Unknown | Yes (towers/barracks/Roshan unknown) | Unknown, confirm event list when the feed opens |
| 7 | NFL | $5.58M | Yes (NFL, NCAA, CFL, UFL) | Scores and incidents; reply p95 3-5 s | No | Deprioritised |
| 8 | WTA | $5.00M | Yes, exclusive WTA package | As ATP; reply 2-3 s | Yes | Test with ATP |
| 9 | College football | $1.99M | Yes (NCAA Men's Football) | As NFL | No | Deprioritised |
| 10 | Baseball (MLB $0.88M) | $0.88M | Yes (MLB, KBO, NPB, NCAA) | Scores and incidents | No | Off-season until Mar 2027; nothing open on PM now |
| 11 | UFC / MMA | $0.78M | **No MMA page, not on Scouts list.** Unknown | Unknown | No | Gap. Check sport list once credentials exist |
| 12 | NHL | $0.54M | Yes (NHL, AHL, KHL, 250+ leagues) | Goals, penalties; reply p95 3-5 s | No | The one NHL add vs TheSports; NHL is parked |
| 13 | Cricket (intl $0.44M) | $0.44M | Page says IPL, T20, ODI, T10, Test, 750+ leagues, on Scouts list. Reply called cricket "less relevant" | Ball-by-ball not stated | **No** | **Biggest add vs TheSports.** ESPN is ~30 s behind the price, so any feed under ~10 s is a step up. BBL 12 Dec, IPL Mar |
| 14 | ITF (tennis) | $0.30M | Yes, official ITF distributor since 2025; reply ITF p95 1.5-2 s | Per point | Unknown | Free add on the tennis test |
| 15 | Valorant | $0.16M | Esports API, round and first-kill markets in blog | Unknown | No | Tiny. Ride along |
| 16 | Rugby (union and league) | ~$0 in the table; $3.1M a year, Six Nations $128k per match | **No rugby page, not on Scouts list.** Unknown | Unknown | No | Gap. We capture rugby from another source |
| 17 | Chess | ~$0 (no per-game markets since May; World Championship 24 Nov-~11 Dec) | **No evidence at all** | Unknown | No | Gap. Lichess broadcast is the source |
| 18 | Golf, darts, F1, handball, volleyball, table tennis, other esports (MLBB, R6, CoD, PUBG, Rocket League) | ~$0 in-play (tiny) | Handball, volleyball, table tennis yes; golf, darts, F1 not named; MLBB on esports blog | n/a | No | Ignore: no PM depth |

Note on outrights: golf is a $174M-a-year market, but it trades pre-play on futures (Masters Winner $126M), not in-play, so there is nothing for an in-play feed to do.

## Open on Polymarket right now (9 Nov 00:55Z snapshot, 24h volume)
LoL $24.3M (12 open events, Worlds semis; last event 11 Nov), NBA $8.7M (100), NFL $6.6M, CFB $1.2M, NHL $0.87M (100), WTA $0.82M (WTA Finals), UFC $0.11M (Contender Series, 14-21 Nov), ATP $0.09M, Dota 2 $0.05M (53 open, last 13 Nov), international cricket $34k, Abu Dhabi T10 $5k (64 events, to 15 Nov), Valorant $2k, KHL/SHL/AHL/Liiga/DEL/NL hockey: $10-26k liquidity each and ~$0 volume. CS2 shows 100 open events with $0 (pre-created, no live Tier 1 event this week). No open AFL, IPL, BBL, chess, rugby or MLB events.

## What falls inside a 10-day trial (assume start ~11 Nov, end ~21 Nov: an estimate)
- LoL: Worlds final 14 Nov only (one series, about $10M in-play a day at Worlds level).
- Dota 2: PGL event to 15 Nov, BLAST Slam from 17 Nov (to 29 Nov), DreamLeague 2 Dec.
- CS2: IEM Beijing and BLAST Rivals dates unconfirmed; PGL Major starts 25 Nov, after the trial.
- Tennis: WTA Finals to ~15 Nov, Nitto ATP Finals 15-22 Nov (ATP site), Challenger and ITF every day.
- Cricket: Afghanistan v Sri Lanka T20 series 9-13 Nov and Abu Dhabi T10 to 15 Nov (both tiny on PM); BBL is 12 Dec, after the trial.
- NHL, NBA, NFL (Sundays), CFB (Saturdays): continuous.

## Gaps and opportunities (what LSports adds that TheSports cannot)
1. **Cricket** (not on TheSports). PM in-play $0.44M/day now, IPL and BBL are the big windows. Needs a ball-level event list from the feed.
2. **LoL** (barely on TheSports). Biggest in-play market after NBA, but only 14 Nov inside the trial. Everything else waits for mid-January.
3. **NHL** (not on TheSports). PM $0.54M/day in-play, rn1 present, parked.
4. **Tennis ITF/Challenger**: extra tour coverage, small on PM.
5. **Soccer, NFL, CFB, MLB**: LSports covers them, TheSports does not. Efficient markets, so no reason to test first.
6. Not covered or unconfirmed: MMA, rugby, chess, golf, darts. For rugby and chess we already have other sources.

## What to test first when the trial opens
1. Tennis (ATP/WTA Finals, Challenger): does the LSports point message land before the PM price move, against a random-time placebo (design in `LSports-trial-test-design-2026-11-07.md`)? This is the largest in-play market where the feed could lead.
2. LoL Worlds final 14 Nov: kill and tower events versus price. One series only, so this is a timing sample, not a verdict.
3. Cricket: first ball-by-ball message seen on any match (T10, T20 internationals) and its delay versus the PM price. Passes if the feed lands inside ~10 s of the price, since ESPN is ~30 s.
4. Dota 2 and CS2: list which event types arrive at all. If none, stop.
5. Print the sport and event list the feed actually sends in the first hour (settles MMA, rugby, chess, golf, darts in one go).

## Caveats
- LSports latency claims are against "officials", not against Polymarket's price. They carry no placebo and no millisecond timestamps. None of the "close to zero" or "1 s" figures is a measured lead.
- Per the 6 Nov reply, source is undisclosed; "aggregated from 100+ live feeds, AI and computer vision" means part of the feed may be no faster than free sources.
- PM in-play $/day is from 20 Oct-4 Nov and includes the Worlds QFs; Dec and Jan will be lower for LoL.
- The gamma snapshot is a single moment (Monday 00:55Z, a quiet hour); 24h volume undercounts weekdays' typical activity for tennis.

## What would raise confidence to 9
- The sport and event-type list LSports actually sends on the HYPER feed (settles rows 4, 6, 11, 13, 16, 17). Not available before the feed opens.
- Measured delay of any LSports message against the PM price (the trial itself).
- LSports technical docs (not public).
