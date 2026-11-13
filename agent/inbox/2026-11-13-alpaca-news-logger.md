# Inbox: Alpaca news WebSocket logger (queued, waits for the key)

From: Claude, PK arbs project, 13 Nov 2026 ~05:05Z. Nick approved creating a free Alpaca account in his name. Only Nick can sign up (email and identity); he will send you the paper-account API key and secret in your direct chat. NEVER put them in Git, issues or notes.

When the key lands:
1. Put ALPACA_KEY and ALPACA_SECRET in /etc/pkarbs/alpaca.env (mode 600), not in the repo.
2. pip install websockets; run weekend-perps/news_ws_logger.py (branch claude/project-thread-ogfnfn, PR #273) as a restarting service: `--out /vol2/news/alpaca_news_YYYYMMDD.jsonl.gz` (one file per day, rotate at 00:00Z). Smoke test 5 min first: report in outbox/alpaca-news-smoke-2026-11-13.md the auth result, message count, example message (fields and timestamp precision), and the median (recv time minus created_at). If auth or the stream is refused, write the exact error and stop.
3. Run alongside the Polymarket-perps and Hyperliquid 1 s price capture (same host clock) so leads can be computed under feeds/STANDARD-feed-latency-test.md v1. Data to /vol2 only (charter).
4. Step 1 for the Massive trial key is separate: agent/TASK-news-push-latency-test-2026-11-13.md.
