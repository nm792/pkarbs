# URGENT (live match): AB summary shows CLOB 0 messages and 0 trades (project thread, 13:50Z)

Thanks for the kill and the committed summaries. Toulouse v Clermont (13:30Z) is live (ESPN STATUS_FIRST_HALF, Rugbyrama 5-0 at 1'). But every summary block since 13:2xZ shows `CLOB msgs 0`, `stream msgs 0`, bid/ask `-/-`, trades 0, sports WS rutopft 0. The log tail only shows "CLOB open" at start, no close or error. The price clock is the whole point of this capture, so please check now and commit the answer in this round, not the next:

1. `ls -l rugby/AB_clob.jsonl rugby/AB_trades.jsonl rugby/AB_sports.jsonl` and `wc -l`; `head -c 600` of the first and last line of AB_clob.jsonl.
2. If AB_clob.jsonl is empty or stopped growing: is the surviving process (pid 1312662) still receiving on the CLOB socket? The kill of 6 others may have been done on the wrong process if the one kept was started before a CLOB reconnect. Check `ss -tnp | grep 1312662` for a connection to the CLOB WS host and the last CLOB log line.
3. If the file has rows but the summary says 0: tell me the row format (the initial snapshot may be a JSON list, which the summariser accepts; `price_changes` with `best_bid`/`best_ask` otherwise) and I will fix the summary.
4. If the stream is really silent: the REST fallback (GET clob.polymarket.com/book?token_id=..., every 5 s) is pre-approved for this window. Label the figures "5 s poll resolution" as the task says. Do not restart the whole capture to do this; run it as a separate bounded process for the match tokens of Toulouse v Clermont and RC Vannes v Bordeaux first (kicked off 13:30Z), the 15:35Z matches after.
Report in agent/status/rugby-top14-capture.md and tell me which of the four cases it is.
