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
- Cross-check requested by new urgent inbox note: one live CS2 match with fresh books and trades was STATE vs EYEBALLERS (`cs2-sta6-eye-2026-11-14`): newest book 12:17:50.902Z; newest trade 12:17:48.548Z. The tracked `markets.jsonl` currently has zero Dota rows, so there is no Dota market to report; this is an observed coverage gap, not an empty search result.

Evidence lives in `pkarbs/thesports/final-topics-32295b/{markets,books,trades,log}.jsonl` on the data volume; raw capture data is not copied into this repository. No keys or infrastructure identifiers included.
