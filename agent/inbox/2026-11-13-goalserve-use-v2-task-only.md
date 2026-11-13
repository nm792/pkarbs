# To Hermes: Goalserve key installed, thanks. Start the v2 task, NOT the old trial task (13 Nov 2026)

Your 02:19Z status says "start TASK-goalserve-trial Part A". That file (agent/tasks/TASK-goalserve-trial-2026-11-12.md) is SUPERSEDED and marked DO NOT RUN. Its assumptions were wrong (Pinnacle odds, WebSocket for esports and cricket).

Run agent/tasks/TASK-goalserve-v2-2026-11-12.md instead:
1. Tennis and NHL: WebSocket (wss://live.goalserve.com/ws/{sport}?tkn=...), inplay-{sport}.gz polled every 0.5 s, livescore at 1 s. Odds are bet365 only.
2. Esports (LoL, CS2, Dota 2): inplay-esports.gz at 0.5 s only. No WebSocket for esports, cricket or rugby.
3. Cricket and rugby: livescore at 1 s, log the observed refresh interval.
4. Benchmark is the Polymarket price only, per feeds/STANDARD-feed-latency-test.md. Never write the key or the IP into any file, log or status.
5. LoL Worlds final is 14 Nov: start the esports capture first, then tennis and NHL.
6. Post agent/status/goalserve.md within 30 min of capture start, then every 30 min while blocked.
