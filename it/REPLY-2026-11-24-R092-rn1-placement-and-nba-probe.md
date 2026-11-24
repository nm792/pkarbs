# IT note (R-092 C5 and C2): RN1 placement pull on Prime, and the NBA trade-feed probe for tonight's first tip-off. 24 Nov 2026. Read only, paper, no orders.

## C5. RN1 placement pull (needs the P106e books, which exist only on Prime; the books are not in any repo, I checked)
Question: where is each RN1 NBA MAKER fill priced relative to that token's OWN best bid/ask just before the fill (inside the spread / at the bid / below / at or above the ask)?
Inputs (reviewer branch, it/rn1_placement/): rn1_nba_maker_fills.jsonl.gz (33,503 RN1 NBA maker fills 20 Oct to 24 Nov 03:30Z; 1,650 of them, $97K, fall after P106e started at 23 Nov 08:58Z; earlier fills have no book and are counted as no_book), rn1_placement.py, test_rn1_placement.py (7 planted checks).
Commands (python3, no extra packages):
  cd it/rn1_placement && python3 test_rn1_placement.py            # must print PASS (7 checks)
  gunzip -k rn1_nba_maker_fills.jsonl.gz
  python3 rn1_placement.py rn1_nba_maker_fills.jsonl /mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-23/books.jsonl.gz 0.01
Paste the printed table (6 lines: inside, at_bid, below_bid_within_2c, below_bid_deeper, at_or_above_ask, no_book, with fills and notional). If the NBA recorder wrote a second dated directory, run it once per directory and add the counts.
Tick: 0.01 is assumed for NBA; if the market tick is 0.001 the 'inside' and 'at_bid' classes shift: IT to read one NBA token's minimum_tick_size from CLOB /markets and say it; I re-run with the right tick on the pasted rows if needed.
Expected write: NONE to the recorder dirs (read only). Memory: loads one day of best-bid/ask rows (about 90 MB compressed input for 16 markets, expected a few hundred MB of RAM); CPU a few minutes; stdout under 1 KB; the gunzip adds about 2 MB. Run under the IT caps (R-039), niceness 10. R-058 pre-flight: not a recorder, no start; the test above is the pre-flight.
Why this matters: gate v5 condition B says this result must be reported BEFORE any node start.

## C2. NBA trade-feed probe, first tip-off tonight (waits on NEEDS-NICK-4 per the Reviewer; the commands are ready)
Needs Node >= 22 (checked here: v22.23.4). Files (reviewer branch, it/nba_feed_probe/): trade_feed_probe.js, test_trade_feed_probe.js, nba_tonight_probe_cmds.py. Pre-flight: `node test_trade_feed_probe.js` must print PASS.
Tonight's games (Gamma series 10345, read 24 Nov): first tip-off Pistons-Magic 00:00Z 25 Nov, then Celtics-Wizards 01:00Z, Mavericks-Nuggets 03:00Z. Run each command 10-20 minutes after tip-off, once per game, 60 s:
# nba-det-orl-2026-11-24  start 2026-11-25 00:00Z  condition 0x8d5e15cc4185a45f01d7d46510f86e0a8560d88b5da3ccf66e098f45cdbdac8b  outcomes Pistons / Magic
#   run at 00:12Z (12 min after tip-off):
node trade_feed_probe.js 57878434040874713377262663992504728401068187924828379814258805891323437610700 46454651182934053778214292179591917844435022725644968824673700259503617552367 60
# nba-bos-was-2026-11-24  start 2026-11-25 01:00Z  condition 0xfb2b9fd76dba99a26e40f4d9e6bbc7a5c6d77c44410f8d24382da0e59341afbb  outcomes Celtics / Wizards
#   run at 01:12Z (12 min after tip-off):
node trade_feed_probe.js 94004132125268206838763221079560078687011651942130211860206971061416461617511 113311699584008945073152174039056382519750258981413232581144648193688063761056 60
# nba-dal-den-2026-11-24  start 2026-11-25 03:00Z  condition 0xfe6f58d4fa395aee480b05a7e9fb186603a067034a0db6159fc868f66450a77b  outcomes Mavericks / Nuggets
#   run at 03:12Z (12 min after tip-off):
node trade_feed_probe.js 19352919711117841849904957464716363791926094852620053199829666780950651761831 71569428935755944256858527466033076863429157187423558408590841490868448921499 60

Pass criterion: the last line is 'TRADE FEED PASS' (exit 0): both tokens acknowledged and at least one last_trade_price in 60 s. Exit 5 = a token not acknowledged, exit 6 = no prints (game idle or feed carries none), exit 4 = socket failed. Paste the JSON line (per-token counts) too. Regenerate the commands for later dates with `python3 nba_tonight_probe_cmds.py` (read only, Gamma only).
Expected write: none (stdout only; the probe stores nothing). Not a recorder, no start, no health read needed; it opens one websocket for 60 s.
