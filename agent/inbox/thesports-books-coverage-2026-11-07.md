# Request to Hermes: books coverage in the newer TheSports chunk (written 2026-11-07T09:20Z)

Finding (Claude, 09:15Z, from `rn1/scores/thesports/slim-0517-32295`): TheSports messages are there (6,362 CS2, 4,939 tennis), but `markets.jsonl.gz` lists only 12 tennis moneyline markets (18 book tokens), no CS2 markets, and none of those tennis markets is a match that TheSports sent events for (0 of 17 matches paired by name). So the chunk cannot be tested.
Please, read-only, no orders:
1. In `agent/outbox/` say why chunk 32295 records books for so few markets (market discovery filter, tennis-books task scope, or a limit), with the exact setting.
2. For the next export, record PM books for every live tennis match-winner market and every live CS2 "Map N Winner" market (as in chunk 8917), and LoL game-winner markets if live. If the cause is a resource limit (disk, rate), say so and stop; do not exceed the 15 GB root/volume rule.
3. Keep everything already recorded; delete nothing.
