# LoL Worlds final recorder proof

Measured on Prime at 2026-11-14 12:08Z for OPEN row PA. The actual final market proof is below. The 12:10Z urgent note arrived during this check and asks for a same-window CS2/Dota corroboration; I checked both against live data before publishing.

- Final: Bilibili Gaming vs Gen.G, scheduled 19:00Z. The registered list `pkarbs/thesports/final-topics-32295b/markets.jsonl` contains five markets under `lol-blg-gen-2026-11-14`: match winner and Game 1–4 winners. Registration `ms=1794654061855` = 11:01:01.855Z.
- Books exist for both outcome tokens for all five markets. Newest rows from `books.jsonl`:

| market | condition id | newest book row UTC (both outcome tokens) |
|---|---|---|
| Game 1 Winner | `0x134e5143254278e5df6f0ffcf9502845fa935923b86c56fd627508552240a959` | 12:07:25.903Z |
| Game 2 Winner | `0xd89caa6e08266e51834d64b67e4d8148d1f421c94bf8e6978008d695400059ad` | 12:07:21.882Z |
| Game 3 Winner | `0xdc139722e0654151002a6e93417bd48cfce00bc3e649f0e2c272e84709a90c02` | 12:07:23.828Z |
| Game 4 Winner | `0x74261eede43e69782e24e75d96b7e425778113069351e494eb7471a6ef35686f` | 12:07:28.826Z |
| Match Winner | `0x41f94101d57bf028eff62f2cc3714adb79722553dc59c1676071459c0b009e45` | 12:07:28.826Z |

- Trade rows exist for both tokens in all five markets. Newest per market: Game 1 11:52:26.677Z; Game 2 11:58:56.027Z; Game 3 11:48:48.979Z; Game 4 11:21:34.159Z; Match Winner 12:07:04.685Z.
- Processes observed: `pm_trades_capture.py` PID 2271688 and `capture.py` PID 2489797. `guard_capture_b.sh` checks/restarts the PM trade recorder and includes `trades` in its 600-second freshness loop; scheduled every five minutes.
- Data volume: 69,016,387,584 bytes free of 105,089,261,568 bytes at 12:11Z.
- Cross-check requested by new urgent inbox note: one live CS2 match with fresh books and trades was STATE vs EYEBALLERS (`cs2-sta6-eye-2026-11-14`): newest book 12:17:50.902Z; newest trade 12:17:48.548Z. At the 12:08Z cross-check, the tracked `markets.jsonl` had zero Dota rows; this was a time-specific coverage gap, not an empty search result. The 16:35Z rerun below now finds live Dota markets and rows.

Evidence lives in `pkarbs/thesports/final-topics-32295b/{markets,books,trades,log}.jsonl` on the data volume; raw capture data is not copied into this repository. No keys or infrastructure identifiers included.


## 17:00Z proof — early rerun at 16:35Z (OPEN row PL)

Read-only rerun of #341 items 1–5, performed before the 17:00Z checkpoint. Final start remains 19:00Z (the measured schedule is recorded in `agent/status/goalserve.md`).

- **Registration:** all five markets (match winner and Games 1–4) remain registered under `lol-blg-gen-2026-11-14`; row `ms=1794654061855` = 11:01:01.855Z.
- **Final markets, latest observed rows in the 16:29Z data scan:**

| market | book rows; newest book UTC | trade rows; newest trade UTC |
|---|---:|---:|
| Game 1 Winner | 12,094; 16:29:07.944Z | 691; 16:22:34.495Z |
| Game 2 Winner | 11,559; 16:29:04.868Z | 301; 16:23:59.646Z |
| Game 3 Winner | 11,392; 16:29:05.965Z | 216; 16:23:59.678Z |
| Game 4 Winner | 10,943; 16:29:07.944Z | 105; 16:23:59.745Z |
| Match Winner | 18,677; 16:29:07.944Z | 1,881; 16:24:43.296Z |

- **Live CS2:** ex-RUSTEC vs Honvéd (`cs2-rustec-hon1-2026-11-14`): measured 31,478 book rows, newest 16:35:28Z; 730 trade rows, newest 16:33:28Z.
- **Live Dota 2:** Aurora vs CyberHero (`dota2-aur1-ch1-2026-11-14`): measured 18,275 book rows, newest 16:35:28Z; 119 trade rows, newest 16:34:57Z.
- **Recorder/guard:** `pm_trades_capture.py` PID 2271688 and `capture.py` PID 2489797 were present at 16:29Z. The every-five-minute `guard_capture_b.sh` crontab entry is present; its code checks for the PM trade recorder and relaunches it if absent.
- **Data volume:** 68,133,277,696 bytes available at 16:30:17Z (33% used).
- **State:** early checkpoint only; the row remains open for the 17:00Z and 18:30Z reruns. No process was started or stopped. Evidence remains at `pkarbs/thesports/final-topics-32295b/{markets,books,trades}.jsonl` on the data volume.


## 18:30Z proof — rerun at 19:18–19:21Z (posted late; final already started)

Read-only rerun of #341 items 1–5 on Prime. The requested 18:30Z checkpoint was missed; this is a measured post-start state, not an on-time proof.

- **Registration:** five Worlds final markets are present under `lol-blg-gen-2026-11-14`: Match Winner and Game 1–4 Winner. All five have registration `ms=1794654061855` (11:01:01.855Z).
- **Final markets:** row counts below are summed over both outcome tokens; newest timestamps are the newest row observed in either token.

| market | condition id | book rows; newest UTC | trade rows; newest UTC |
|---|---|---:|---:|
| Game 1 Winner | `0x134e5143254278e5df6f0ffcf9502845fa935923b86c56fd627508552240a959` | 18,888; 19:21:29.483Z | 1,123; 19:20:34.961Z |
| Game 2 Winner | `0xd89caa6e08266e51834d64b67e4d8148d1f421c94bf8e6978008d695400059ad` | 16,690; 19:21:25.308Z | 418; 19:17:36.341Z |
| Game 3 Winner | `0xdc139722e0654151002a6e93417bd48cfce00bc3e649f0e2c272e84709a90c02` | 16,202; 19:21:29.483Z | 300; 19:17:36.373Z |
| Game 4 Winner | `0x74261eede43e69782e24e75d96b7e425778113069351e494eb7471a6ef35686f` | 16,631; 19:21:15.645Z | 182; 19:19:09.243Z |
| Match Winner | `0x41f94101d57bf028eff62f2cc3714adb79722553dc59c1676071459c0b009e45` | 28,984; 19:21:29.483Z | 3,582; 19:21:18.490Z |

- **CS2 corroboration:** QUINTESSÊNCIA vs ex-Yawara (BO3), market id `cs2-quin-yawara-2026-11-14`, 19:00Z start; 8,044 book rows (newest 19:21:29.483Z), 1,244 trade rows (newest 19:21:18.206Z).
- **Dota 2 corroboration:** Team Synapse vs Team Allied (BO3), market id `dota2-synaps-all2-2026-11-14`, 19:00Z start; 7,494 book rows (newest 19:21:29.483Z), 95 trade rows (newest 19:20:34.887Z).
- **Recorder/guard:** `pm_trades_capture.py` PID 2271688 and `capture.py` PID 2489797 observed running at 19:21Z. The `*/5` cron entry for `guard_capture_b.sh` is present; its recent log shows successful ticks through 19:20Z.
- **Data volume:** 67,453,562,880 bytes available of 105,089,261,568 bytes (33% used) at 19:21Z.
- Evidence remains on the data volume at `pkarbs/thesports/final-topics-32295b/{markets,books,trades}.jsonl`; no process was started or stopped.
