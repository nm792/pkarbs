# Live catch-up check, 23 Nov 2026 ~14:00-16:00Z (Reviewer)
Rule: `CATCHUP-RULE.md` live section (2049e5a5). Code `live_catchup.py`; output `live_catchup_result.json`. Logs: `live_2026-11-23_book.jsonl.gz` (2 s), `live_2026-11-23_book_v2.jsonl.gz` and `live_2026-11-24_book_v2.jsonl.gz` (1 s, with the Polymarket perp's own bid/ask). Read-only; nothing traded. 15-min check passed at 14:20Z (rows 0.5 and 1/s, 0 errors, perp and book timestamps changing).

## Result: no trade was possible today; the test day was unusable, not negative
- 23 Nov event: the perp opened about 3-4% above Friday's close, so the market was decided all session (Up 0.93-0.989 ask; Down 0.02-0.08). 11 perp moves of >= 10 bp; the model's probability jump was about 0 every time, so there was nothing stale to buy. Every move was skipped ("ask already caught up"). Quote lag (stale token's mid covering half the jump), v2 log: 53, 57, 68, 390, 508 s, 2 not within 30 min, 4 at 0 s. On a dead book this means little.
- 24 Nov event (opened 13:00Z): the book was empty for all 2 hours: only 0.02 bids and 0.98 asks on both tokens, no market maker. 12 moves, no trade possible.
- Controls: planted 30 s quote move measured as 30.0-30.7 s on every move in all three logs. Planted stale ask + catch-up at 30 s: captured on the 24 Nov log at +3.1c per share mean (12 trades; e.g. dp 0.133 gave +11.3c). On 23 Nov it shows -0.2c, because the jump is about 0 on a decided market. The trade code finds an edge when one exists.

## Next (read-only, no cost)
Rerun both loggers over tomorrow's US open (24 Nov ~13:20-17:20Z), when the 24 Nov market is live and undecided.
