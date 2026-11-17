# Dota 2 live capture — final status (2026-11-17 20:45Z)

- Capture stopped at 07:26:57Z when its 90,000-second timeout expired; configured end was 20:30Z. PIDs 1700947/1700948 were absent at 20:43Z. The window was short by 13h03m05s; books last advanced at 22:59:59Z on 16 Nov.
- Final local valid JSONL rows / malformed: books 107,624 / 0; league_games 15,904 / 0; opendota_live 2,723 / 0; realtime 145,268 / 0; rt_polls 325,064 / 0; sportsws 7,158 / 0. Other streams last advanced 17 Nov 07:25:56–07:26:55Z.
- PASS is not established: required per-series in-game-minute and 200-poll coverage calculations are absent, and capture ended early. No pass claim.
- Final 20:35Z publisher failed on first transfer (rsync exit 12, box authentication denied). No final copy verified. The pushed manifest remains 75 chunks / 562,819 rows at commit `53daee4ac232962914b78668dd1d3f2aa8acddb5` (02:42:56Z). Later local output was not pushed.
- Both publisher crontab lines removed at 20:44Z after final failure; backup `/root/crontab.pre-dota-final-20261117T204421Z.txt`. No capture process was restarted.
- Code reference: `daf1447d6767634ae4b390d2a79047f6d0bc958b`.
