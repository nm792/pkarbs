# APPROVED: two changes to rugby-top14-capture.py (Nick, 7 Nov 2026 15:04:27Z)

Nick's own words, copied by the server: "Ok to both" (message cmsg_01Te5Ysv754GBskR25k8ZXLmYDiFyYHfgdLfTNdXA4d5Fp), in reply to the question whether to (1) stop the launcher starting duplicate rugby captures and (2) fix the silent CLOB price stream. This approves the two script changes below and nothing else.

The patch is already in the repo (agent/tasks/rugby-top14-capture.py on the default branch after the merge of this note's PR). Pull it; you do not need to write code.

1. **Single-instance guard.** At start, `main()` takes an exclusive flock on `rugby/<window>.lock`; a second launch of the same window prints "already running" and exits 0, so a dispatch loop cannot start duplicates. Also, the log is no longer truncated by a second launch (it was why the AB log showed only 3 lines). Tested locally with two simultaneous launches: the second exited.
2. **CLOB stream.** Two bugs found by reading the code, tested against a local fake server only (not against Polymarket): (a) the first message on the market channel is a JSON LIST of books, and `{**obj}` on a list raises, and the plain-text `PONG` reply fails `json.loads`; both go to the except branch, and after 3 attempts the task returned silently. Now lists, dicts and PONG are handled and unparsable text is recorded. (b) The market channel drops idle clients; a `PING` text is now sent every 10 s. Retries no longer stop after 3. Whether this was the actual cause of the silent stream is unknown, settled by the probe below.
3. The 5-minute summariser now also reads `AB_clob_rest.jsonl` (your REST fallback), so its CLOB counts and bid/ask are non-zero.

When to apply:
- Do NOT restart today's AB mid-match. AB keeps running on the old code with the REST poll.
- Windows D and C tomorrow (13:45Z, 19:50Z) must start on the new code with the lock. Keep your REST fallback running next to the stream in those windows until the stream is confirmed.
- Safe-point check of the stream fix today: run a separate bounded probe (5 minutes, one process, nice -n 19) that imports `read_clob` from the new script with output to `rugby/probe_clob.jsonl`, on the 15:35Z tokens while those matches are live, without touching AB. Report rows per minute and first-message type in the status file. If it records rows, the stream is fixed; if it is silent, say so and keep the REST poll.
Report in agent/status/rugby-top14-capture.md and agent/outbox. The thread relays it to Nick.
