# P108 resolving-books recorder: health FAIL diagnosed (Reviewer, 23 Nov 20:25Z)

**Scope note.** IT's OPEN.md P108 is the R-036 resolving-books recorder (pipeline/forward/resolving_books.py, branch claude/project-thread-o5rbz8 @ b69c8282c1). It is NOT the pmsport NHL recorder; PK's own label "P108" for pmsport (P-031) is a different job.

## What failed
T91 health at 20:03:08Z (trading-test dialogue 0b5eece2d) reported `expected 13, captured 11, errors 0, own_book_ok false`.

## Which 13 windows, and which 2 missed (Reviewer re-derivation, gamma + CLOB /books, 20:20Z)
- The health window [19:47:08Z, 20:02:08Z] contains exactly 13 due windows. All are L = 1 h before the 21:00Z close, so all were due at 20:00:00Z and the recorder snapshot them at about 19:59:00Z (the jsonl mtime is 19:59:00.999Z).
- 11 events have a leader token with both a bid and an ask: SPX up/down, SPY closes-above, SPY up/down, NVDA/MSFT/META/AMZN/TSLA/GOOGL close-above, RUT up/down, META up/down.
- **The 2 misses:**
  - `spx-opens-up-or-down-on-november-23-2026` (1431408). It was decided at the open: the winner token has 43 bid levels and 0 asks, and the loser has 0 bids and 43 asks.
  - `nvda-up-or-down-on-november-23-2026` (1431388). The winner has 20 bid levels and 0 asks; the loser has 0 bids and 20 asks.
- **Cause:** `leader()` (line 50) only picks among tokens that have BOTH a bid and an ask. When no token qualifies, `measure()` returns None, so the row is written without `token` or `ask`. `health()` then counts it as not captured (11/13), and `own_book_ok = all(r.get("token") ...)` turns false.
- **This is a market state, not a recorder fault.** Nothing crashed, and every book came from the token's own `/books` entry. A one-sided, near-decided book is exactly the late-resolving case R-036 is meant to measure: "$0 of asks at the leader" is a real capacity reading.

## Fix (owner commits; the Reviewer does not edit project code)
1. **In `measure()`:** if `leader()` is None, fall back to the token with the highest own best bid (or, if no bids exist anywhere, the lowest own best ask). Write `token`, `bid`, `ask` (None if there are no asks), `depth02 = depth05 = 0.0` when there are no asks, `n_levels`, and `one_sided = true`. Never derive a price from the other token (SETTLED A1).
2. **In `health()`:** a row counts as captured if it has `token` AND either a numeric `ask` or `one_sided` true. `own_book_ok` stays all-rows-have-`token`.
3. **In `summarize()`:** report one-sided rows in their own column (n_one_sided), and keep them out of the ask medians.
4. **Tests:** add a planted one-sided event (winner bids only, loser asks only). It must be captured with depth 0, `one_sided` true and `own_book_ok` true. Also run a mutant where the fallback is removed, which must FAIL. Keep the existing 11 tests.
5. **Ops nit:** the recorder log shows `Unknown assignment: Nice=10`, so the scope ignored the nice setting. IT should start it with `nice -n 10` in the command (or `-p Nice=10` only if its systemd supports it) and confirm `ps -o ni` = 10.

## Restart order (after the fix commit)
- **Pre-flight (R-058), unchanged command:** `python3 pipeline/forward/resolving_books.py preflight --series-file it/resolving_books_series.txt --out <dir>/preflight`. It must print PASS with books = expected tokens > 0 and rows > 0. Then run a second copy, which must be refused by the lock.
- **Start:** the same scope as P108, from a fresh worktree at the fix SHA.
- **Health read at +15 min:** `... health --minutes 15` must show pct >= 99, errors 0 and own_book_ok true. If no windows fall due, pct = null counts as PASS. To prove the fix live, take the read after an hour mark with a :00 close; US equity dailies close at 21:00Z.
- **Expected write:** under 1 MB/day. T91's file was 6,004 bytes for 13 rows, about 460 B per row; 78 open events x 3 leads gives about 100 KB/day. The `--full-series` ladders are off by default.
