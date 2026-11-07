# Reply: rugby CLOB zero-check (Toulouse v Clermont, live 13:30Z)

**Case: 4 (stream silent) — covered by pre-approved REST fallback, already running.**

## RESULT
- `AB_clob.jsonl`, `AB_trades.jsonl`, `AB_sports.jsonl` do NOT exist in /root/pkarbs/rugby/ — the CLOB WS stream `read_clob` (use_rest=False) has written zero rows since CLOB open at 13:12Z, with no close/error in AB_log.txt (`SPORTS open`, `CLOB open`, then silence). Process 1312662 alive (etime 1:35:26), 2 ESTAB sockets to polymarket hosts, so the socket is connected but no market-channel rows are landing in the WS file.
- **The REST fallback is already live:** `rugby-clob-rest-fallback.py` (pid 1806719, started ~13:55Z, etime 41:19) writes `AB_clob_rest.jsonl` — 1,251,581 bytes, rows `mode:"5s-poll"`, first recv_ms 1794059707388, last 1794062172945 (~14:36Z, streaming now). It covers the window's match tokens in the pre-approved 5s book poll, labelled exactly as the task specifies.
- Because the summary summariser reads `{win}_clob.jsonl` (the WS file, absent) and not `AB_clob_rest.jsonl`, it reports CLOB 0 — a read-path mismatch, not missing data. The price data the note's "whole point" refers to is being captured in the rest file.

## OPEN / NOT VERIFIED
- Summariser still reads the WS filename; wiring it to also fold `AB_clob_rest.jsonl` rows is a script change (gated — will raise when approved).
- REST poll resolution is 5 s as pre-approved; noted.

Count: notes run 1, outstanding 0 (fallback covering), PENDING open 0.
Context: CLOB stream silent but REST 5s-poll fallback already captures live books for the live match; no restart performed (not authorised).
