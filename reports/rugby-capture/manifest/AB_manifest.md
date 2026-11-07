# AB raw capture manifest (2026-11-07) — big files on volume, under push hook

AB ended 2026-11-07T18:05Z (Vannes-Bordeaux, Toulouse-Clermont).
Large raw files exceed the 1MB jsonl / 5MB pre-push hook and stay on the volume at /root/pkarbs/rugby/. Hashes+size recorded here; parsed events and summary committed inline.

| file | size(B) | sha256 |
|---|---|---|
| AB_rugbyrama.jsonl | 1324639767 | c22a012715781eb3899d1fc1674cb46db211ff01d2973fbf5d479f02f19d6cde |
| AB_espn.jsonl | 39558486 | 226d3845417b9ee9a4ce43c5abea5eda937afc28db9653268f225d25b9f9f878 |
| AB_clob_rest.jsonl | 6622259 | ddbbf526cecc700dbbf1a9232694b4217e6fa52d31ddb5be8293d59ddf7048d0 |
| AB_rugbyrama_events.jsonl | 284216 | ca65acfa98e0c4a44e57c2af439d6a455ea5e7e421aecbaba53cb0c40ab1bd47 |

Committed inline: AB_rugbyrama_events.jsonl, AB_summary.md, AB_launch.out, AB_log.txt.
