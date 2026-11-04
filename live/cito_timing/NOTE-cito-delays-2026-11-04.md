# Cito live feeds vs Polymarket sports live-score WS (4 Nov 2026, measured)

Setup: Cito Scale plan (WS for CS2, LoL, tennis, UFC). Logged both feeds with our receive time (race.py), paired first-seen score states (analyze.py). Raw: project folder cito-timing/race3/race4_2026-11-04.jsonl.gz (07:52-09:10Z).

| Sport | Pairs | Cito vs PM | Notes |
|---|---|---|---|
| CS2 (MOUZ v PARIVISION, IEM Beijing, Mirage) | 10 rounds | Cito **184 s behind** (median; 160-244 s) | PM itself ~19 s behind game, so Cito ~3.4 min behind. Cito follows the public scoreboard (their FAQ says so). Occasional team-order flips. Adds round scores where PM sends none (Liquid v BetBoom), but late. |
| Tennis (ATP Taipei, WTA Hong Kong, ITF/Challenger) | 20 games (0-0 starts excluded) | Cito **~6 s ahead** (median 5.7 s; -9 to +26 s; ahead in 14/20) | Cito sends every point (POINT_UPDATE + point_history); PM sends games only. Neither timed vs true point time yet. |
| LoL | 0 | to test: Worlds GEN match 22:00Z 4 Nov | WS needs room match:<id> or game:<id>. |
| UFC | 0 | no fights | |

Verdict: Cito is no use for CS2 speed. For tennis it is a little faster than PM and gives point-level data.

## LoL update (GEN v LYON Worlds, game 1, 4 Nov 22:15-22:55Z, measured)
Clock = Polymarket game-winner trades (data-api v2): first trade >= 2c from the median of trades 30-90 s before the PM score-stream kill time.
- Cito usual source (`riot_live_window`, self-reported lagSeconds ~195): median **204 s after the price move** (n=9 kills, 193-226 s).
- Cito fast source (`sheep_live`, lagSeconds 1) ran only in the first minutes of each game: 24 and 28 s after the price (n=2).
- PM sports score WS: median 12.5 s after the price (n=11).
Verdict: Cito is no use for LoL or CS2 speed. Recommendation to Nick: cancel unless the tennis backtest finds value before the 17 Nov money-back date.
Raw: project folder cito-timing/lol_race1_2026-11-04.jsonl.gz, lol_trades_g1.json, lol_trades_g2.json.
