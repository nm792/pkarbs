# IT note (R-082, R-083, R-084): own-token book recorder for LIGUE 1, SERIE A, then EPL, LALIGA, ATP, NFL, COLLEGE FOOTBALL. 24 Nov 2026. Paper only, no orders.

Code: it/pm_sport_books.js at reviewer 8271841d0b (health checker updated after). It now takes league = fl1 | sea | epl | lal | atp | nfl | cfb (and the old nhl | nba | tennis). One league per recorder process, one output dir per league. An unknown league name exits 3 (before, a typo silently recorded NHL).

## What it records
- Both tokens of every moneyline market of each GAME event (slug league-aaa-bbb-YYYY-MM-DD; suffix events such as -player-props, -exact-score do not match). A soccer game has 3 moneyline markets (home, draw, away), each with a Yes and a No token: 6 tokens per game, each token's OWN book (YES and NO never derived from each other, SETTLED A1). ATP, NFL and CFB: 2 tokens per game.
- IN-PLAY WINDOW ONLY: a game's tokens are subscribed from 15 minutes before the start time and rows are written until start + 2.75 h (soccer), + 4 h (NFL, CFB), + 4.5 h (ATP); nothing is written after that. Gamma series ids from /sports: fl1 10195, sea 10203, epl 10188, lal 10193, atp 10365, nfl 12185, cfb 12756. Discovery runs every 5 minutes with limit=50 (Gamma answers 406 to series queries at limit=100, 24 Nov).
- Same row format as P106e (recv_ms, asset, outcome, best bid/ask and top 3 levels; level 2-3 at most once per 10 s per token). It still drops last_trade_price (no own-token prints, G1).

## Tests (run on my side; local fake Gamma and fake websocket; the real websocket is blocked in my sandbox, so UNVERIFIED on the real socket until IT's pre-flight)
- node it/test_pm_sport_books.js: 12 original + 7 league checks (3 moneylines x 2 tokens, suffix events excluded, no league leakage, each league entry complete, unknown league exits 3). Mutation: using the old slug rule for new leagues fails it.
- node it/test_pm_sport_books_live.js: 8 original + 4 soccer checks (game started 10 min ago gives PASS with 6 tokens; game 3 h before start records nothing; game 5 h after start records nothing; NBA mode never picks a soccer slug).
- bash it/test_nba_health.sh: 6 checks. The health checker now counts writers per output dir (several league recorders run side by side); the first version of that fix matched /o against /o2 and the new test caught it.
- Live Gamma read, 24 Nov 03:4xZ: the slugs and counts above come from the real API (series_id), e.g. epl-not-che-2026-11-27, fl1-sbr-pfc-2026-11-27, sea-cag-mil-2026-11-30, atp-pham-bolt-2026-11-24. No Ligue 1, Serie A, EPL or LaLiga game is in play today (Tuesday): first matches Fri 27 Nov. Pre-flight tokens > 0 on a live matchday therefore cannot be run for soccer before Fri 27 Nov; the same code path is provable TODAY on ATP (23 matches listed for 24 Nov).

## Pre-flight (R-058), run before any start (exit 0 only if tokens = 2 x markets > 0 and rows > 0)
ATP today, during play (proves the series_id path and websocket):
  node pm_sport_books.js /mnt/HC_Volume_107257520/pkarbs/pmsport/preflight-atp-$(date -u +%H%M) '' 10 atp preflight 60
Soccer on Friday 27 Nov, 10-20 minutes after a kickoff (kickoff times: read markets.jsonl start after the first discovery; not known to me):
  node pm_sport_books.js /mnt/HC_Volume_107257520/pkarbs/pmsport/preflight-fl1-$(date -u +%H%M) '' 10 fl1 preflight 60   (same for sea, epl, lal)

## Start (single instance per dir; cron every 5 min is safe, the keeper checks pidfile + /proc cmdline). In-play leagues are idle between games, so set ALLOW_IDLE=1 or the recorder exits 4 after 120 s with no tokens:
  ALLOW_IDLE=1 bash nba_keepalive.sh /mnt/HC_Volume_107257520/pkarbs/pmsport/fl1  2026-12-24T00:00:00Z 10 fl1
  (and sea, then epl, lal; atp, nfl, cfb after those). Order of priority: fl1, sea, epl, lal, atp, nfl, cfb.
Health read (R-037, within 15 min of each start or restart): bash nba_health.sh /mnt/HC_Volume_107257520/pkarbs/pmsport/fl1 60 . Read it DURING a match window: with no game live the tokens and growth lines legitimately fail. Pid and writers checks apply always.

## Expected write (R-068/R-069, VOL2 headroom): upper bound about 0.3 GB/day on average, about 0.7 GB on a peak day, about 9 GB per 30 days, for all new leagues together
Basis: the P106e rate of about 2.8 MB per token per day (Reviewer's comparator: about 90 MB/day for 16 NBA markets = 32 tokens), applied PER TOKEN PER GAME-DAY even though only 3-4.5 h of the day are recorded (so an upper bound; the real figure should be lower, UNVERIFIED until a matchday is recorded). Token counts from Gamma on 24 Nov (6 per soccer game, 2 otherwise): 4 soccer leagues about 39 games a week = 234 tokens a week = about 94 MB/day average (a Sunday with 17 games = 100 tokens = 280 MB); ATP 46-104 tokens on a normal day (listed 23 Nov: 52 matches) = 130-290 MB/day; NFL about 32 tokens a week = 13 MB/day average; college football about 116 tokens on a Saturday = about 46 MB/day average. Sum average about 0.29 GB/day, plus NBA about 0.09 GB/day already running. Free space on VOL2: I cannot read it; IT to paste df for /mnt/HC_Volume_107257520 before the start and say whether 9 GB per 30 days fits (keeper stops itself below 10 GB free).

## Caveat on what this data cannot do
No trade prints (G1). Fill and queue questions still need prints (Data API v2 by condition_id, fail-closed client scan/nba_paper/pm_data_api_v2.py) or the Nautilus paper node's own fills.
