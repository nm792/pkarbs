# Forward test rerun with 429 backoff (11 Nov 2026, 08:55Z)

Re-pulled all 10 frozen Kalshi series (markets, then first-2h trades for forward markets) with exponential backoff and Retry-After handling (`fpull.py`; the 429s that occurred were retried and recovered, see `fpull_429_retries.log`; market counts match the 10 Nov pulls plus the new events). Market lists are complete: KXNBAMENTION 6,545, KXNFLMENTION 1,543, KXTRUMPMENTION 7,543 (+25), KXVANCEMENTION 1,992 (+17), others unchanged.

## Forward result: 0 scored events (not enough data yet, not a failure)
Forward sample = events opened at or after 2026-11-10T15:00Z.
- Kalshi: **2 events opened, 0 resolved**: KXVANCEMENTION-26NOV11 (17 markets) and KXTRUMPMENTION-26NOV11 (25 markets), both opened 2026-11-11 01:30Z. Nothing else has opened on the 10 frozen series since the freeze. The last events on the other series opened before the freeze (KXTRUMPSAY 9 Nov, KXMAMDANIMENTION 6 Nov, KXTRUMPMENTIONB 2 Nov, KXBERNIEMENTION 30 Oct, KXSECPRESSMENTION 13 Oct); KXNBAMENTION's last event was 10 Jun 2026, KXNFLMENTION's 23 Apr 2026, KXWCMENTION's 16 Jul 2026 (these three series look dormant).
- Polymarket (mention-markets tag): **0 events with a market start at or after the freeze**; the newest event started 9 Nov 15:26Z.
- So the earlier zeros were empty because of 429s, but the rerun shows the true answer is also empty: no forward event has resolved. The test's 100-event decision rule is a long way off at this rate (about 2 events in 18 hours on the frozen series).

## Provisional paper entries (outcome pending, for later scoring)
Using the frozen rule (3c, first-hour first qualifying BUY print, base rate from all resolved events so far):
- KXVANCEMENTION-26NOV11: first qualifying print "Marine" YES at 0.41, 2 contracts, q=0.56 (edge 0.15); 100 qualifying prints in the hour.
- KXTRUMPMENTION-26NOV11: first qualifying print "Space Force" YES at 0.27, 1 contract, q=0.369 (edge 0.099); 170 qualifying prints.
Print sizes are tiny (1-2 contracts). These are logged only; score them when both events resolve.

## Note
The forward series list in the pre-registration covers 10 of 465 Kalshi mention series (earnings calls and many others are not included), which is why few events qualify. Changing the list mid-test would break the pre-registration; if more forward events are wanted, a new pre-registered arm is needed.
