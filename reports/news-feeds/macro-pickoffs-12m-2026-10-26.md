# Stale-quote pickoff at US macro releases, 12 months of Polymarket trades (26 Oct 2026)

Follow-up to addendum 2 of `news-feeds-2026-10-25.md` (Sept CPI left about $7.8k, mostly one stale core
CPI ask at 0.32). Question: across 12 months of CPI, jobs, FOMC and PPI releases, how much did takers
earn by hitting quotes still resting at pre-release prices in the first 30 s, how steady is it, and what
is a realistic $/day for us after competing bots? Desk research only, no server use.

Labels: **[measured]** = computed by our script on Polymarket's public trade prints; **[estimate]** =
my reasoning on top of those numbers. Nothing here is our own fills.

## Answer

**Kill as a standalone route to $50/day; keep as a small, lumpy add-on.** Over 34 release days
(24 Oct 2025 to 15 Oct 2026) takers earned **$82.0k** in the first 30 s **[measured]**, about
**$225/day** averaged over the year, but 41% of it came from one FOMC day. A new, well-built bot taking
20-30% of the rest would make about **$25-38/day**; a 1-3 s bot about **$8-21/day** **[estimate]**. The
fast end of the race is getting faster: since May 2026 the first winning prints land 4-6 s after the
release (on-chain time), against about 11 s before.

**Confidence 7/10.** What would raise it to 9 is at the end.

## Kill condition (written after the first 11 release days were in, before the other 23)

Kill as a standalone strategy if the 12-month pool, net of today's taker fee, times a 30% capture
share (optimistic for a new entrant), averages under $50/day once the single largest release day is
removed.

Result: $46.4k net without the largest day × 30% / 365 = **$38/day → kill.** With that day included it
is $65/day, but that rests on one FOMC meeting.

## Method

- Events: every closed Polymarket event for US CPI (headline monthly and annual), core CPI (MoM, YoY),
  payrolls, unemployment rate, FOMC decision and PPI whose first market closed between 20 Oct 2025 and
  26 Oct 2026: 69 events. Found with gamma `public-search`, markets and winners from gamma `events?id=`.
- Trades: data-api `/trades?market=<all condition ids>`, newest first, paged back to 2 days before the
  first close (taker side, as the API returns it).
- Release second R: the 8:30 ET slot (12:30Z or 13:30Z) for BLS, 2:00 pm ET (18:00Z or 19:00Z) for
  FOMC, picking the slot with the most trades in its first 60 s. Every detected time is a scheduled
  release time; those I can check against the published 2025-26 BLS and Fed calendars (through mid-2026)
  match, including the shutdown-delayed ones (Nov CPI on 18 Dec, Oct+Nov jobs on 16 Dec).
- Pickoff edge of a taker print = (settled value − price) × size for a buy, (price − settled value) ×
  size for a sell; the pool is the sum of positive edges. Once the number is out, the settled value is
  known, so this is what a correct reader of the release locked in. Net = after today's Economics taker
  fee, 0.05 × p × (1 − p) per share.
- Timestamps are Polygon block times, a few seconds after matching. The earliest prints after a release
  land at +3-5 s even on FOMC days, so "+6 s" means roughly 1-3 s after the release in matching time
  **[estimate]**.
- A release day groups the events of one family on one date (e.g. headline and core CPI together).

Gates: (1) reproduces addendum 2: Sept core CPI $4,716 (0-10 s) and $2,142 (11-30 s) vs $4,707 and
$2,142 then (winners now from gamma, not inferred) **[pass]**. (2) Every included event has all markets
resolved 0/1 and trades back to at least R − 10 min **[pass]**. (3) No event left at the API row cap
**[pass after re-pull, see Data access]**.

Excluded release days (no Polymarket trading at the release second): Sept 2025 jobs (markets closed
7 Nov; the report came out 20 Nov after the shutdown), Oct 2025 CPI (never published), May 2026 jobs
(5 Jun: no trades at 12:30Z, a burst at 12:49Z, cause not checked).

## Results

### By release family (MECE: the four rows sum to the total) **[measured]**

| Family | Release days | 0-30 s pool | Median day | Largest day |
|---|---|---|---|---|
| CPI (headline + core) | 11 | $24,675 | $1,457 | $8,856 (14 Oct 2026) |
| Jobs (payrolls + unemployment) | 10 | $10,339 | $708 | $2,636 (16 Dec 2025) |
| FOMC | 8 | $46,515 | $1,275 | $33,851 (29 Jul 2026) |
| PPI | 5 | $509 | $79 | $268 (15 Oct 2026) |
| **Total** | **34** | **$82,039** (net of fee $78,767) | **$902** | |

The Polymarket PPI markets found start in May 2026 and are thin. Nothing was left after 30 s on most days; 31-300 s
added $11.9k in total, mostly on early-2026 days when the race was slower.

### Lumpy versus steady **[measured]**

- **Lumpy: 4 of 34 days, $53.4k, 65% of the year**, defined as a pool of at least 3× the median
  ($2.7k): FOMC 29 Jul 2026 $33.9k, CPI 14 Oct 2026 $8.9k, FOMC 16 Sep 2026 $5.9k, CPI 14 Jul 2026
  $4.8k. The top day alone is 41%, the top 3 are 59%, the top 5 are 68%.
- **Steady: the other 30 days, $28.6k**, typically $100-2,600 a day, median about $700.
- Within a day the pool is also concentrated: on 16 of 34 days a single resting price level gave more
  than half of it. The July FOMC case: asks for "No change" at 0.83-0.85 (about 150k shares across several
  levels) were still resting at the decision and were bought out at +5-6 s for about $27k.

### How fast it goes **[measured]**

Share of the pool by on-chain second after the release:

| Period | Days | Pool | ≤ 6 s | 7-10 s | 11-30 s | First winning print (median) |
|---|---|---|---|---|---|---|
| Oct 2025 - Apr 2026 | 15 | $17.6k | 6% | 10% | 84% | +11 s |
| May 2026 - Oct 2026 | 19 | $64.4k | 58% | 21% | 21% | +6 s |
| May - Oct without 29 Jul FOMC | 18 | $30.6k | 33% | 42% | 25% | +6 s |

So the bots arrived over 2026: before May almost everything was taken 11-30 s after release; since May the
first prints come at +4-6 s.

### Who takes it **[measured]**

- On the median day the top wallet took 53% of the pool and the top three took 88%; a median of 14 wallets
  took something.
- One wallet (0x2f633efb…) took a share on 14 of the 34 days, $11.5k (14% of the year); another
  (0x97276d1b…) took $12.0k on 4 days, mostly the two big FOMC days. The next six took 4-8% each.
  That is a small, repeat set of release bots, not one monopolist.

## Realistic $/day for us after competing bots **[estimate]**

Base: $78.8k net per year = $216/day, or $127/day without the July FOMC outlier. Capture shares are
my estimates from the wallet concentration above, not measured.

| Our setup | Pool we can reach | Our share | $/day without the outlier | With it |
|---|---|---|---|---|
| A. Fast: reads the BLS/Fed page directly, orders armed per bracket, sub-second | all of it | 20-30% | $25-38 | $43-65 |
| B. Medium: 1-3 s to order | the ≥ 7 s part, about 67% recently | 10-25% | $8-21 | $9-23 |
| C. Slow: 5 s or more | the 11-30 s part, 25% and shrinking | 10-30% | $3-10 | $5-14 |

Central case: **about $10-25/day**, earned on 2-4 days a month, with most months near $0-500 and the
occasional $5-10k day. The three rows are alternatives, not additive.

What it would take, all estimates:
- A parser per release (BLS CPI, Employment Situation, PPI; Fed statement) mapped to every bracket of
  every Polymarket event that day, plus orders signed and ready before 8:30:00 ET.
- The real risk is a wrong parse or a wrong bracket at release time: a taker buying the wrong bracket
  at 0.8 loses 0.8 a share. That is the catastrophic-loss leg of the goal, and it needs a hard
  per-release size cap and a two-source check (e.g. BLS page plus the BLS API), which costs speed.
- Size is limited by what is resting, not by our capital: the largest steady day was $2.6k for all
  takers together.

## What this does not cover

- **Kalshi.** Kalshi lists CPI, jobs and Fed markets too, probably with more volume; not pulled
  (Kalshi trades were not tried from here). If Kalshi's release-second pool is several times
  Polymarket's, the answer could change.
- **Other releases** with Polymarket markets (GDP, PCE, retail sales, jobless claims) were not in the
  brief and are not counted.
- **FOMC events** were re-pulled with trades of $10 or more only (see below), so their small fills are
  missing; the effect is small next to their pool.
- **Contamination:** a print matched just before the release can settle just after it. From the
  pre-release edge rate this is at most about $300 on the largest FOMC day and less elsewhere.
- Today's fee was applied to all trades; some older trades paid less.

## Data access (what failed and the workaround)

- This repo's container: the proxy refuses Polymarket hosts (`CONNECT tunnel failed, response 403`).
- Composio remote sandbox: **worked today** (it failed on every call on 25 Oct). Its MCP endpoint
  answered "403 Forbidden" to commands with some URL strings (gamma `events?` and `&` query strings), so
  scripts were sent base64-encoded.
- data-api answers 403 to Python's default User-Agent; a curl User-Agent works.
- data-api refuses offsets above 10,000 (HTTP 400), so 6 FOMC events stopped at 10,500 rows before
  reaching the release. Re-pulled one market at a time with `filterType=CASH&filterAmount=10`; all then
  reached the release.
- The Goldsky orderbook subgraph URL from older docs returns 404; not used.
- TinyFish was not needed this time.

Scripts: `reports/news-feeds/scripts/macro12m/` (README gives the run order). The raw trade files sat
in the remote sandbox and are not kept; the scripts rebuild them in about 20 minutes.

## Per release day **[measured]**

Pool = positive taker edge 0-30 s; net = after today's fee; top wallet = share of that day's pool.

| Day | Family | Events | Notional 0-30 s | Pool 0-10 s | Pool 11-30 s | Net 0-30 s | Top wallet | First print |
|---|---|---|---|---|---|---|---|---|
| 2025-10-24 | CPI | 2 | $13,796 | $0 | $138 | $132 | 99% | +29 s |
| 2025-10-29 | FOMC | 1 | $574,840 | $73 | $649 | $687 | 33% | +5 s |
| 2025-12-10 | FOMC | 1 | $796,388 | $1,491 | $751 | $2,131 | 19% | +4 s |
| 2025-12-16 | Jobs | 2 | $18,515 | $0 | $2,636 | $2,531 | 64% | +13 s |
| 2025-12-18 | CPI | 2 | $6,324 | $0 | $1,661 | $1,603 | 86% | +12 s |
| 2026-01-09 | Jobs | 2 | $1,166 | $0 | $81 | $78 | 51% | +22 s |
| 2026-01-13 | CPI | 2 | $14,405 | $0 | $2,590 | $2,486 | 84% | +13 s |
| 2026-01-28 | FOMC | 1 | $977,249 | $586 | $393 | $930 | 51% | +8 s |
| 2026-02-11 | Jobs | 2 | $10,086 | $0 | $1,476 | $1,428 | 53% | +15 s |
| 2026-02-13 | CPI | 2 | $14,637 | $0 | $231 | $220 | 79% | +11 s |
| 2026-03-06 | Jobs | 1 | $6,588 | $0 | $299 | $286 | 54% | +11 s |
| 2026-03-18 | FOMC | 1 | $636,088 | $200 | $503 | $668 | 62% | +5 s |
| 2026-04-03 | Jobs | 1 | $23,932 | $118 | $2,184 | $2,206 | 57% | +9 s |
| 2026-04-10 | CPI | 3 | $20,718 | $0 | $1,023 | $975 | 85% | +7 s |
| 2026-04-29 | FOMC | 1 | $218,490 | $297 | $230 | $500 | 30% | +0 s |
| 2026-05-08 | Jobs | 2 | $5,854 | $584 | $8 | $570 | 82% | +6 s |
| 2026-05-12 | CPI | 2 | $19,775 | $623 | $18 | $615 | 86% | +6 s |
| 2026-06-10 | CPI | 4 | $11,846 | $82 | $1,375 | $1,401 | 24% | +9 s |
| 2026-06-11 | PPI | 1 | $5,750 | $79 | $0 | $76 | 86% | +6 s |
| 2026-06-17 | FOMC | 1 | $508,003 | $91 | $1,480 | $1,493 | 49% | +4 s |
| 2026-07-02 | Jobs | 2 | $21,771 | $1,111 | $48 | $1,114 | 45% | +4 s |
| 2026-07-14 | CPI | 3 | $44,074 | $4,706 | $93 | $4,657 | 54% | +5 s |
| 2026-07-15 | PPI | 1 | $2,156 | $116 | $0 | $113 | 48% | +5 s |
| 2026-07-29 | FOMC | 1 | $659,978 | $27,981 | $5,871 | $32,396 | 25% | +3 s |
| 2026-08-07 | Jobs | 2 | $6,561 | $824 | $0 | $794 | 60% | +6 s |
| 2026-08-12 | CPI | 4 | $28,740 | $2,168 | $25 | $2,112 | 30% | +6 s |
| 2026-08-13 | PPI | 1 | $1,150 | $6 | $0 | $6 | 50% | +6 s |
| 2026-09-04 | Jobs | 2 | $5,062 | $89 | $339 | $410 | 46% | +7 s |
| 2026-09-10 | PPI | 1 | $6,104 | $39 | $0 | $37 | 49% | +6 s |
| 2026-09-11 | CPI | 4 | $27,914 | $768 | $318 | $1,042 | 23% | +4 s |
| 2026-09-16 | FOMC | 1 | $160,967 | $5,690 | $228 | $5,640 | 55% | +0 s |
| 2026-10-02 | Jobs | 2 | $2,998 | $57 | $485 | $522 | 64% | +6 s |
| 2026-10-14 | CPI | 4 | $37,407 | $5,582 | $3,274 | $8,649 | 40% | +6 s |
| 2026-10-15 | PPI | 1 | $3,872 | $0 | $268 | $258 | 76% | +10 s |

The "+0 s" FOMC prints are most likely trades matched just before the decision and settled at
it (see Contamination) **[estimate]**.

## Confidence: 7/10

That this route cannot reach $50/day on its own: 7/10. The pool sizes are measured and reproduce the
earlier check. The capture shares, and so the $/day, are estimates. To reach 9:
1. **Kalshi's pool at the same releases** (public trade history for its CPI, jobs and Fed markets over the
   same 12 months). This is the one thing that could flip the verdict, if Kalshi's pool is 3× or more.
2. **One bounded live timing test** on a release (needs Nick's go-ahead and the Polymarket account
   active): a tiny pre-armed order on one bracket, to measure our release-to-match time against the
   first prints. That turns rows A-C into one measured row.
3. Optional: matching time instead of block time for the first prints (from the CLOB, if Polymarket
   exposes it), to pin the "+6 s ≈ 1-3 s" conversion.

---

## Addendum (26 Oct, 06:00Z): Nick's depth point, and Kalshi

Nick: "$38 is near enough because we typically undercount the depth at the ask." Tested on existing
data plus public snapshots, desk only, no server, no orders. Scripts: `scripts/macro12m/small.py`,
`book.py`, `kal.py`.

### Where trade prints could undercount the pool (MECE)

| Source | Effect on the pool | How checked |
|---|---|---|
| 1. One order filled across many wallets or makers | **None.** The pool sums every taker print, however it is split. | by construction |
| 2. Prints under $10 dropped in the FOMC re-pull | **+0.2%** | **[measured]** on 7 CPI, PPI and jobs events (14 Oct, 10 Sep, 2 Oct 2026): $19 of $9,437 came from prints under $10 |
| 3. Stale depth resting at the release but cancelled before anyone hit it | **Unknown; at most about 2-5× the printed pool on BLS releases** | **[estimate]** from live books, below. Public data has no historical order books, so this cannot be measured after the fact |

Only item 3 matters, and only a bot faster than the makers' own cancels can reach it, so it can only
change row A of the $/day table (fast, sub-second). Rows B and C are unchanged.

### Bounding item 3 with today's books **[measured snapshot, estimated use]**

For the next release of each family I took the live Polymarket book (26 Oct, 05:5xZ) and asked: if every
resting order stayed through the release and was hit, what would takers earn? (Expected value, using the
book's own mid as the probability; levels within 10c of the touch.)

| Next release (Polymarket) | Full-book pool if nothing is cancelled | Printed pool on comparable past days | Ratio |
|---|---|---|---|
| Oct CPI, 4 events (11 Nov) | $6.3k | $1.8k median, $3.4k mean (last four 4-event CPI days) | 1.9-3.5× |
| Oct jobs, 2 events (6 Nov) | $2.6k | about $0.7k (last five jobs days) | about 3.7× |
| Oct PPI (14 Nov) | $0.5k | about $0.1k (last five PPI days) | about 5× |
| FOMC (28 Oct) | $235k | $1.3k median | not usable: almost all of it is the 1-3% chance of a surprise against very large bids at 0.97+, which professional makers would pull |

These are upper bounds: the books were read 2-3 weeks before the BLS releases, and makers usually thin
their quotes in the minutes before a release. Some of the gap is depth pulled before the release
(which nobody can hit), not depth cancelled after it.

One piece of evidence points the other way, towards little missed depth before May: from October to
April, stale quotes were still being taken 11-30 s after the release, so makers were not cancelling
quickly then. Since May the prints come in at +4-6 s, and how fast makers now cancel is not visible.

### Kalshi **[measured]**

**Kalshi has no release-second pool.** Its CPI, core CPI, payrolls, unemployment and Fed markets close
1-5 minutes before the release (CPI and jobs at 12:25 or 12:29Z for a 12:30Z release; Fed decision at
17:55 or 17:59Z for 18:00Z). On 14 Kalshi events checked (Aug-Sep 2026: KXCPI, KXCPIYOY, KXCPICORE,
KXCPICOREYOY, KXPAYROLLS, KXU3, KXFEDDECISION, KXFED), there were 0 trades in the 5 minutes after the
release. Kalshi has no PPI series. So Kalshi cannot change the verdict. Earlier Kalshi months use a
different ticker format and were not checked, but the close-before-release rule looks like a design choice.

### Pool range with the adjustment, and the kill test again **[estimate]**

Kill test as set: 30% capture of the net pool without the largest day, averaged over 365 days, must reach
$50/day.

| Case | Net pool without the largest day | $/day at 30% | Kill test |
|---|---|---|---|
| Measured prints only (+0.2%) | $46.5k | $38 | fail |
| Break-even | $60.8k (1.31× the prints) | $50 | just passes |
| Middle: half the book bound (CPI 1.75×, jobs 1.85×, PPI 2.5×, FOMC 1.5×) | about $80k | about $65 | passes |
| Upper bound: full book (CPI 3.5×, jobs 3.7×, PPI 5×, FOMC 2×) | about $146k | about $120 | passes |

**Re-stated verdict:** the kill test passes **if at least 31% more stale depth was resting and reachable
at the release than what printed.** The live books say the depth is there weeks before a release (2-5× on
BLS releases), so this is plausible, but it is not measured at the release second. And it only applies to
a sub-second bot that beats the makers' cancels, while a 30% share for a new entrant is already the
optimistic end. At our realistic speeds (rows B and C) nothing changes: about $3-21/day.

So I'd move this from "kill" to **"unproven: passes only for a top-speed build and only if the hidden
depth is real"**. Kalshi adds nothing.

**Confidence 5/10** that the adjusted test passes; 8/10 that it does not pass at 1-3 s speed. To reach 9:
record the full Polymarket book from 10 s before to 30 s after two or three releases (FOMC 28 Oct,
jobs 6 Nov, CPI 11 Nov) and compare resting stale depth with what printed. It is read-only, needs no
orders, and runs in the remote sandbox for 1 minute per release, not on our server. It needs Nick's
go-ahead because it is live data capture.
