# Outbox: storage offload ruling — complete

**Approvals needed:** none (data movement + verification, ruled no-approval).

**RESULT**
- Offload complete per ruling: shadow data older than 48h moved to the storage box pkarbs/shadow/..., keeping relative layout (data-v2 + rescan-data).
- Spot sha-triple-verified: raw-2026102619.jsonl.gz local==manifest==box (b0af7d1a...), then deleted locally per the ruling's delete-after-verified rule.
- Stop condition met: /dev/sdc 31G free >= 30G target.
- Manifest (86 lines, sha + box path + copied_at) maintained at agent/status/storage-offload-manifest.csv and committed.

**DATA**
- agent/status/storage-offload-manifest.csv
- storage box: pkarbs/shadow/data-v2/... (through raw-2026102619), rescan-data/...

**OPEN / NOT VERIFIED**
- Remaining local >48h files (~28.9 GB) not yet in the manifest: offload already passed the 30G-free stop condition, so no further move required this round; left in place per "keep all raw data".
- Full per-row (non-spot) sha re-verification of all 86 manifest rows not re-run; spot check matched.

Count: notes run 3, outstanding 1 (gated stop).
