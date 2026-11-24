# Planted-edge power run through the stops harness (R-092 C1). 24 Nov 2026. SYNTHETIC; validates the harness, says nothing about the real market.

Code: ../stops_harness.py (stop rules: 10 blind games, sigma = 1.5 x baseline-arm sd frozen at game 10, Robbins normal-mixture always-valid 95% interval, looks at 10/20/40 then every 20, max 432 games = 60 game-days), ../test_stops_harness.py (7 checks: checkpoints, blind, any-time coverage under the null at EVERY game, positive and negative control, null false SUCCESS, sigma frozen; a mutant with a 0.4x narrower interval fails), sim_planted.py (the plant), power_run_result.json (500 studies per cell).
Plant: after each qualifying event quotes stay stale for 0.9 s; sell flow 2.0 fills/s while stale; a bid eligible at d = hold + 0.206 s order latency fills only in (d, 0.9 s); 40 events/game; 200 shares/fill; per-fill 10-min markout = J + noise (sd 3c); baseline arm = matched fill count, zero-mean noise. J = 0.42c gives about +$30/game at the 250 ms hold (the A9 stack-layer scale; the $200/day bar needs +$27.8/game lower bound). The delay that kills it is any total delay >= 0.9 s, so a 1 s hold (+0.206 s) kills it by construction: this is a design choice, stated, not a market fact.

| cell (500 studies each) | SUCCESS | FUTILITY | inconclusive | median games to SUCCESS |
|---|---|---|---|---|
| planted +$30/game, hold 250 ms (A.3) | 100% | 0% | 0% | 60 |
| planted +$30/game, hold 1 s (gate wording) | 0% | 0% | 100% | n/a (edge killed) |
| planted +$30/game, hold 0 ms | 100% | 0% | 0% | 40 |
| planted NEGATIVE -$30/game, hold 250 ms | 0% | 100% | 0% | n/a |
| NULL, hold 250 ms | 0.6% | 0.6% | 98.8% | 280 |
| NULL, hold 1 s | 0% | 0% | 100% | n/a |
Reading: the harness detects a planted +$30/game edge at 250 ms in a median 60 games (well inside 432), fails to detect it at the 1 s hold (the edge is gone), reports FUTILITY for a planted loss, and keeps the false-SUCCESS rate on a null under 5% (0.6%). Limits: one synthetic mechanism; the real per-game sd (here about $51 for the difference, $36 per arm) is UNVERIFIED until 10 live games; a real market can have heavier tails and serial dependence between games; and a weak real edge (below about $15/game) would end 'inconclusive, ranked' at 432 games in this setup (not run). Confidence 7/10 that the harness behaves as specified; 4/10 on any transfer to live data.
