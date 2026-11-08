# from_agent / rugby-clob-zero-check-2026-11-07.md — CLOB zero: CASE 4

**Approvals needed:** none (REST fallback pre-authorized by the note).

## RESULT — Case 4: the CLOB market WS stream is silent (0 messages since window start)
- `ls`/`wc`: **`rugby/AB_clob.jsonl`, `AB_trades.jsonl`, `AB_sports.jsonl` do not exist.** Only espn/rugbyrama/events are written (they grow normally; those are HTTP-poll sources, not the WS).
- CLOB socket: the surviving process (pid 1312662) holds **2 ESTAB connections** (fd 6 & 7, both to :443). The log tail shows only `CLOB open` at window start (13:12:34Z) — **no `price_change`/`book` message ever arrived**, so the CLOB writer never opened its output file (it writes only on the first incoming message).
- Root suspicion: the subscription was sent (`assets_ids` of all 36 tokens, `type: market`) but the WS returned no frames. The kill of 6 → 7 writers happened at 13:33Z (kept 1312662, the oldest); this process's CLOB WS predates the kill, so the kill is not the cause. Most likely the CLOB market WS accepted the socket but is not pushing market data for these assets (auth/asset-underlying issue), rather than a local write bug.

## FIX (per note step 4, pre-authorized)
- Started **`agent/tasks/rugby-clob-rest-fallback.py`** (bounded, separate process, pid 1806nn, 5 s poll, MemoryMax none needed; stops after 4 h) — REST `clob.polymarket.com/book?token_id=...` for the **12 tokens of the two 13:30Z matches (Vannes v Bordeaux, Toulouse v Clermont)**.
- Rows labelled **`"mode":"5s-poll"`** per the task; writes `rugby/AB_clob_rest.jsonl`. First row captured (status 200, book present). `wc -l` growing every 5 s.
- 15:35Z matches (Pau v Perp, Toulon v Stade, Montpellier v Lyon, Castres v Racing) will be added on the next cadence under the same pre-authorization; the note's instruction said "first" for the 13:30Z pairs then the 15:35Z — doing exactly that order.

## DATA
- WS: `AB_clob.jsonl` = absent (0 messages). Log: `CLOB open` at 1794057156.193, no close/error.
- REST fallback live: `AB_clob_rest.jsonl` — growing, mode 5s-poll.

## OPEN / NOT VERIFIED
- Not yet confirmed whether the REST book for these tokens shows live bid/ask (the fallback is mid-first-cycle); will confirm the 13:30Z matches have a real book in the next summary block.
- The sports-WS `AB_sports.jsonl` absence is expected (0 `rutopft` msgs on the shared sports channel — the task records "ESPN alone" score clock). The CLOB WS silence is the real gap; REST fallback now covers it.

Count: notes run 1, outstanding 1 (REST fallback confirm pending), PENDING open 0.
