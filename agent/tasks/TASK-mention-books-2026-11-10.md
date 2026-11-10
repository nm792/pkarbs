# TASK: record order books of new mention markets (Kalshi and Polymarket) every 5 minutes

From: Claude in the PK arbs thread "Find and test MrBeast-style markets" (10 Nov 2026, 15:30Z), asked for by the coordinator. Status: OPEN. Paper only, no orders.

## Why
The mentions rule (per-word base rate, first-hour BUY prints) is measured on past trades only. Fills, depth and spread at market creation are unknown, and that decides whether it can ever trade at size. Kalshi has about 258 Trump events and 1,000+ in the other mention series; Polymarket 1,363 events ($376M).

## Question (one only)
Does `live/mentions/record_mention_books.py` run on the server every 5 minutes and save books for markets in their first 3 hours?

## Pass / fail, fixed before running
- PASS: `python3 live/mentions/test_record_mention_books.py` prints `8 of 8 checks pass`; one run prints a line with `"ev": "done"`; over the first 48 hours at least one `books_YYYYMMDD.jsonl.gz` has lines with venue `kalshi` and (if a new Polymarket mention market opened) venue `polymarket`, each with a non-empty book.
- FAIL: anything else. Report the last 20 lines and stop. No retries beyond one. A run with 0 targets is normal when no market opened in the last 3 hours.
- Read-only public HTTPS (Kalshi API, Polymarket gamma and CLOB), 0.15 s between calls, no keys, no orders.

## Run
```
cd <repo> && git pull
python3 live/mentions/test_record_mention_books.py
mkdir -p /root/mentions/books
python3 live/mentions/record_mention_books.py /root/mentions/books
```
If PASS add a cron entry every 5 minutes: `*/5 * * * * cd <repo> && timeout 240 python3 live/mentions/record_mention_books.py /root/mentions/books >> /root/mentions/books/run.log 2>&1` (one process at a time, memory cap 200M). Keep for 10 weeks. Data is a few MB a day.

## Report
1. Daily at 00:50Z commit `/root/mentions/books/*.jsonl.gz` to `rn1/mentions/books/` on the default branch.
2. First run: `agent/status/mention-books.md` (PASS/FAIL, last 20 lines) and `agent/outbox/2026-11-10-mention-books.md`.
3. The thread does the analysis. Raw data is never deleted before it is committed.
